#!/usr/bin/env python3
"""
Binance Leaderboard Analyzer

Analiza snapshots del leaderboard aplicando la metodología de Akira Traders:
- Filtra por perfil de riesgo (hard filters)
- Calcula métricas derivadas (RAR, Consistency, Recovery Factor)
- Aplica sistema de scoring ponderado
- Genera ranking de candidatos
- Exporta análisis en JSON

Uso:
    # Analizar snapshot más reciente con perfil moderado
    python leaderboard_analyzer.py --profile moderate

    # Analizar snapshot específico
    python leaderboard_analyzer.py --snapshot leaderboard_WEEKLY_20251109.json

    # Exportar top 10 candidatos
    python leaderboard_analyzer.py --profile moderate --top 10 --output results.json
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from statistics import mean, stdev


class LeaderboardAnalyzer:
    """
    Analizador de traders del Binance Leaderboard.

    Aplica la metodología de Akira Traders para:
    - Filtrado por perfil de riesgo
    - Cálculo de métricas derivadas
    - Scoring ponderado
    - Ranking de candidatos
    """

    # Perfiles de riesgo (de docs/methodology.md)
    PROFILE_LIMITS = {
        'conservative': {
            'min_roi': 10.0,
            'max_roi': 30.0,
            'max_drawdown': 10.0,
            'min_win_rate': 60.0,
            'min_leverage': 1.0,
            'max_leverage': 2.0,
            'min_followers': 200,
            'min_days_active': 180
        },
        'moderate': {
            'min_roi': 20.0,
            'max_roi': 60.0,
            'max_drawdown': 20.0,
            'min_win_rate': 55.0,
            'min_leverage': 1.0,
            'max_leverage': 3.0,
            'min_followers': 100,
            'min_days_active': 90
        },
        'aggressive': {
            'min_roi': 40.0,
            'max_roi': 200.0,
            'max_drawdown': 35.0,
            'min_win_rate': 50.0,
            'min_leverage': 2.0,
            'max_leverage': 5.0,
            'min_followers': 50,
            'min_days_active': 60
        }
    }

    # Pesos del sistema de scoring (de docs/methodology.md)
    SCORING_WEIGHTS = {
        'conservative': {
            'max_dd': 0.30,
            'win_rate': 0.25,
            'roi': 0.15,
            'consistency': 0.20,
            'rar': 0.10
        },
        'moderate': {
            'max_dd': 0.25,
            'win_rate': 0.20,
            'roi': 0.25,
            'consistency': 0.15,
            'rar': 0.15
        },
        'aggressive': {
            'max_dd': 0.20,
            'win_rate': 0.15,
            'roi': 0.30,
            'consistency': 0.10,
            'rar': 0.25
        }
    }

    def __init__(self, data_dir: str = "data/leaderboard"):
        """
        Inicializa el analyzer.

        Args:
            data_dir: Directorio donde están los snapshots
        """
        self.data_dir = Path(data_dir)
        if not self.data_dir.exists():
            raise ValueError(f"Data directory not found: {data_dir}")

        self.stats = {
            'traders_analyzed': 0,
            'traders_passed_filters': 0,
            'traders_failed_filters': 0,
            'avg_score': 0.0
        }

    def load_snapshot(self, filename: Optional[str] = None) -> Dict:
        """
        Carga un snapshot del leaderboard.

        Args:
            filename: Nombre del archivo (None = más reciente)

        Returns:
            Dict con datos del snapshot
        """
        if filename:
            snapshot_path = self.data_dir / filename
            if not snapshot_path.exists():
                raise FileNotFoundError(f"Snapshot not found: {filename}")
        else:
            # Obtener el más reciente
            snapshots = sorted(
                self.data_dir.glob('leaderboard_*.json'),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            if not snapshots:
                raise FileNotFoundError("No snapshots found in data directory")
            snapshot_path = snapshots[0]

        print(f"📂 Loading snapshot: {snapshot_path.name}")

        with open(snapshot_path, 'r', encoding='utf-8') as f:
            snapshot = json.load(f)

        traders = snapshot.get('data', {}).get('data', [])
        metadata = snapshot.get('metadata', {})

        print(f"✅ Loaded {len(traders)} traders")
        print(f"   Period: {metadata.get('period', 'N/A')}")
        print(f"   Collected: {metadata.get('collected_at', 'N/A')}")

        return snapshot

    def apply_hard_filters(
        self,
        traders: List[Dict],
        profile: str
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Aplica filtros obligatorios según perfil de riesgo.

        Args:
            traders: Lista de traders del leaderboard
            profile: Perfil de riesgo (conservative, moderate, aggressive)

        Returns:
            Tupla de (traders que pasan, traders que fallan)
        """
        limits = self.PROFILE_LIMITS.get(profile)
        if not limits:
            raise ValueError(f"Invalid profile: {profile}")

        passed = []
        failed = []

        for trader in traders:
            roi = trader.get('roi', 0)
            win_rate = trader.get('winRate', 0)
            leverage = trader.get('avgLeverage', 0)
            followers = trader.get('followerCount', 0)

            # Hard filters (eliminatorios)
            reasons = []

            if roi < limits['min_roi']:
                reasons.append(f"ROI too low ({roi}% < {limits['min_roi']}%)")
            if roi > limits['max_roi']:
                reasons.append(f"ROI too high ({roi}% > {limits['max_roi']}%)")
            if win_rate < limits['min_win_rate']:
                reasons.append(f"Win rate too low ({win_rate}% < {limits['min_win_rate']}%)")
            if leverage < limits['min_leverage']:
                reasons.append(f"Leverage too low ({leverage}x < {limits['min_leverage']}x)")
            if leverage > limits['max_leverage']:
                reasons.append(f"Leverage too high ({leverage}x > {limits['max_leverage']}x)")
            if followers < limits['min_followers']:
                reasons.append(f"Insufficient followers ({followers} < {limits['min_followers']})")

            if reasons:
                failed.append({**trader, 'rejection_reasons': reasons})
            else:
                passed.append(trader)

        self.stats['traders_analyzed'] = len(traders)
        self.stats['traders_passed_filters'] = len(passed)
        self.stats['traders_failed_filters'] = len(failed)

        print(f"\n🔍 Hard Filters ({profile}):")
        print(f"   ✅ Passed: {len(passed)}")
        print(f"   ❌ Failed: {len(failed)}")

        return passed, failed

    def calculate_derived_metrics(self, trader: Dict, profile: str) -> Dict:
        """
        Calcula métricas derivadas para un trader.

        Args:
            trader: Datos del trader
            profile: Perfil de riesgo

        Returns:
            Dict con métricas derivadas
        """
        roi = trader.get('roi', 0)
        win_rate = trader.get('winRate', 0)
        leverage = trader.get('avgLeverage', 0)
        pnl = trader.get('pnl', 0)

        # Estimación de Max Drawdown (no disponible en API de Leaderboard)
        # Usamos una heurística basada en leverage y volatilidad
        # En un sistema real, esto vendría del historial de trades
        estimated_max_dd = min(
            leverage * 2.5,  # Aproximación: leverage * factor
            abs(roi) * 0.3   # O 30% del ROI (conservador)
        )

        # Risk-Adjusted Return (RAR)
        # RAR = ROI / Max DD
        rar = roi / estimated_max_dd if estimated_max_dd > 0 else 0

        # Consistency Score (simplificado sin datos históricos)
        # En un sistema real, usaríamos ROI 7d, 30d, 90d
        # Por ahora, basamos en win_rate como proxy de consistencia
        consistency = win_rate / 100.0

        # Recovery Factor
        # RF = ROI Total / Max DD
        recovery_factor = roi / estimated_max_dd if estimated_max_dd > 0 else 0

        # Profit Factor (estimado)
        # Basado en win rate y PnL promedio
        avg_win = pnl / trader.get('rank', 1) if trader.get('rank') else pnl
        profit_factor = (avg_win * (win_rate / 100)) / max(avg_win * (1 - win_rate / 100), 1)

        return {
            'estimated_max_dd': round(estimated_max_dd, 2),
            'rar': round(rar, 2),
            'consistency': round(consistency, 2),
            'recovery_factor': round(recovery_factor, 2),
            'profit_factor': round(profit_factor, 2)
        }

    def normalize_metric(
        self,
        value: float,
        min_val: float,
        max_val: float,
        reverse: bool = False
    ) -> float:
        """
        Normaliza una métrica a escala 0-100.

        Args:
            value: Valor a normalizar
            min_val: Valor mínimo del rango
            max_val: Valor máximo del rango
            reverse: True si menor es mejor (ej: drawdown)

        Returns:
            Valor normalizado 0-100
        """
        if max_val == min_val:
            return 50.0

        normalized = (value - min_val) / (max_val - min_val) * 100

        if reverse:
            normalized = 100 - normalized

        return max(0, min(100, normalized))

    def calculate_score(
        self,
        trader: Dict,
        derived_metrics: Dict,
        profile: str
    ) -> Tuple[float, Dict]:
        """
        Calcula score ponderado para un trader.

        Args:
            trader: Datos del trader
            derived_metrics: Métricas derivadas
            profile: Perfil de riesgo

        Returns:
            Tupla de (score total, breakdown de scores)
        """
        weights = self.SCORING_WEIGHTS[profile]
        limits = self.PROFILE_LIMITS[profile]

        # Normalizar métricas a 0-100
        dd_score = self.normalize_metric(
            derived_metrics['estimated_max_dd'],
            0,
            limits['max_drawdown'],
            reverse=True  # Menor DD es mejor
        )

        wr_score = self.normalize_metric(
            trader.get('winRate', 0),
            limits['min_win_rate'],
            100,
            reverse=False
        )

        roi_score = self.normalize_metric(
            trader.get('roi', 0),
            limits['min_roi'],
            limits['max_roi'],
            reverse=False
        )

        cons_score = derived_metrics['consistency'] * 100

        rar_score = self.normalize_metric(
            derived_metrics['rar'],
            0,
            10,  # RAR > 10 es excepcional
            reverse=False
        )

        # Score ponderado
        total_score = (
            dd_score * weights['max_dd'] +
            wr_score * weights['win_rate'] +
            roi_score * weights['roi'] +
            cons_score * weights['consistency'] +
            rar_score * weights['rar']
        )

        breakdown = {
            'dd_score': round(dd_score, 2),
            'wr_score': round(wr_score, 2),
            'roi_score': round(roi_score, 2),
            'cons_score': round(cons_score, 2),
            'rar_score': round(rar_score, 2),
            'total_score': round(total_score, 2)
        }

        return total_score, breakdown

    def analyze_traders(
        self,
        snapshot: Dict,
        profile: str = 'moderate'
    ) -> Dict:
        """
        Analiza todos los traders de un snapshot.

        Args:
            snapshot: Datos del snapshot
            profile: Perfil de riesgo

        Returns:
            Dict con análisis completo
        """
        print(f"\n{'='*70}")
        print(f"🔬 Analizando Leaderboard - Perfil: {profile.upper()}")
        print(f"{'='*70}\n")

        traders = snapshot.get('data', {}).get('data', [])

        # Aplicar filtros
        passed, failed = self.apply_hard_filters(traders, profile)

        # Analizar traders que pasaron filtros
        analyzed_traders = []

        for trader in passed:
            # Calcular métricas derivadas
            derived = self.calculate_derived_metrics(trader, profile)

            # Calcular score
            total_score, score_breakdown = self.calculate_score(
                trader,
                derived,
                profile
            )

            # Combinar todo
            analyzed = {
                **trader,
                'profile': profile,
                'derived_metrics': derived,
                'scores': score_breakdown,
                'recommendation': self._get_recommendation(total_score, profile)
            }

            analyzed_traders.append(analyzed)

        # Ordenar por score descendente
        analyzed_traders.sort(key=lambda x: x['scores']['total_score'], reverse=True)

        # Estadísticas
        if analyzed_traders:
            scores = [t['scores']['total_score'] for t in analyzed_traders]
            self.stats['avg_score'] = round(mean(scores), 2)
            self.stats['max_score'] = round(max(scores), 2)
            self.stats['min_score'] = round(min(scores), 2)

        result = {
            'metadata': {
                'analyzed_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'profile': profile,
                'source_snapshot': snapshot.get('metadata', {}),
                'analyzer_version': '1.0.0'
            },
            'stats': self.stats,
            'candidates': analyzed_traders,
            'rejected': failed
        }

        print(f"\n📊 Análisis Completado:")
        print(f"   Candidatos aprobados: {len(analyzed_traders)}")
        print(f"   Score promedio: {self.stats.get('avg_score', 0)}")
        if analyzed_traders:
            print(f"   Mejor score: {analyzed_traders[0]['scores']['total_score']} ({analyzed_traders[0]['nickName']})")

        return result

    def _get_recommendation(self, score: float, profile: str) -> str:
        """
        Genera recomendación basada en score.

        Args:
            score: Score total del trader
            profile: Perfil de riesgo

        Returns:
            Texto de recomendación
        """
        if score >= 80:
            return "STRONG BUY - Excelente candidato"
        elif score >= 70:
            return "BUY - Buen candidato"
        elif score >= 60:
            return "HOLD - Considerar para diversificación"
        elif score >= 50:
            return "WATCH - Monitorear evolución"
        else:
            return "PASS - No cumple criterios"

    def export_results(
        self,
        results: Dict,
        output_file: str,
        top_n: Optional[int] = None
    ) -> None:
        """
        Exporta resultados a archivo JSON.

        Args:
            results: Resultados del análisis
            output_file: Ruta del archivo de salida
            top_n: Limitar a top N candidatos (None = todos)
        """
        if top_n:
            results['candidates'] = results['candidates'][:top_n]

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        size_kb = output_path.stat().st_size / 1024
        print(f"\n💾 Resultados exportados: {output_path.name} ({size_kb:.1f} KB)")
        print(f"   Candidatos incluidos: {len(results['candidates'])}")


def main():
    """Función principal para CLI"""
    parser = argparse.ArgumentParser(
        description="Binance Leaderboard Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Analizar snapshot más reciente con perfil moderado
  python leaderboard_analyzer.py --profile moderate

  # Analizar snapshot específico
  python leaderboard_analyzer.py --snapshot leaderboard_WEEKLY_20251109.json

  # Exportar top 10 candidatos
  python leaderboard_analyzer.py --profile moderate --top 10 --output results.json

  # Perfil conservador con export
  python leaderboard_analyzer.py --profile conservative --output conservative_analysis.json
        """
    )

    parser.add_argument(
        '--snapshot',
        help='Snapshot específico a analizar (default: más reciente)'
    )

    parser.add_argument(
        '--profile',
        choices=['conservative', 'moderate', 'aggressive'],
        default='moderate',
        help='Perfil de riesgo (default: moderate)'
    )

    parser.add_argument(
        '--top',
        type=int,
        help='Limitar resultados a top N candidatos'
    )

    parser.add_argument(
        '--output',
        '-o',
        help='Archivo de salida JSON (default: no export)'
    )

    parser.add_argument(
        '--data-dir',
        default='data/leaderboard',
        help='Directorio de snapshots (default: data/leaderboard)'
    )

    args = parser.parse_args()

    try:
        # Inicializar analyzer
        analyzer = LeaderboardAnalyzer(data_dir=args.data_dir)

        # Cargar snapshot
        snapshot = analyzer.load_snapshot(args.snapshot)

        # Analizar
        results = analyzer.analyze_traders(snapshot, args.profile)

        # Exportar si se especificó output
        if args.output:
            analyzer.export_results(results, args.output, args.top)
        else:
            # Mostrar top candidatos en consola
            print(f"\n{'='*70}")
            print(f"🏆 Top Candidatos ({args.profile.upper()}):")
            print(f"{'='*70}\n")

            display_count = args.top if args.top else min(10, len(results['candidates']))

            for i, candidate in enumerate(results['candidates'][:display_count], 1):
                print(f"{i}. {candidate['nickName']} (Rank #{candidate['rank']})")
                print(f"   Score: {candidate['scores']['total_score']}/100")
                print(f"   ROI: {candidate['roi']}% | WR: {candidate['winRate']}% | Leverage: {candidate['avgLeverage']}x")
                print(f"   RAR: {candidate['derived_metrics']['rar']} | Consistency: {candidate['derived_metrics']['consistency']}")
                print(f"   Recommendation: {candidate['recommendation']}")
                print()

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

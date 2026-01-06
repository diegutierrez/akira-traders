#!/usr/bin/env python3
"""
Binance Leaderboard Data Collector

Colector automático de datos del Leaderboard público de Binance Futures.
Permite obtener rankings de traders y guardar snapshots históricos.

Endpoints utilizados:
- GET /bapi/futures/v1/public/future/leaderboard/getLeaderboardRank
- GET /bapi/futures/v2/public/future/leaderboard/getOtherLeaderboardBaseInfo

Uso:
    # Colectar ranking diario
    python leaderboard_collector.py --period DAILY

    # Colectar con límite personalizado
    python leaderboard_collector.py --period WEEKLY --limit 50

    # Como módulo
    from leaderboard_collector import BinanceLeaderboardCollector
    collector = BinanceLeaderboardCollector()
    data = collector.collect_and_save(period="DAILY")
"""

import requests
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import time
import sys

# Importar datos mock para desarrollo/testing
try:
    from mock_leaderboard_data import generate_mock_leaderboard, generate_mock_trader_details
    MOCK_DATA_AVAILABLE = True
except ImportError:
    MOCK_DATA_AVAILABLE = False


class BinanceLeaderboardCollector:
    """
    Colector de datos del Leaderboard de Binance Futures.

    Utiliza endpoints públicos de Binance para obtener información
    de los mejores traders y guardar snapshots históricos.
    """

    # URLs base de las APIs públicas
    BASE_URL = "https://www.binance.com/bapi/futures"

    # Configuración por defecto
    DEFAULT_TIMEOUT = 10  # segundos
    DEFAULT_RETRY_ATTEMPTS = 3
    DEFAULT_RETRY_DELAY = 2  # segundos

    def __init__(self, data_dir: str = "data/leaderboard", use_mock: bool = True):
        """
        Inicializa el colector.

        Args:
            data_dir: Directorio donde guardar los snapshots
            use_mock: Si True, usa datos de prueba (recomendado por limitaciones del API)
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.use_mock = use_mock

        if self.use_mock and not MOCK_DATA_AVAILABLE:
            print("⚠️  Mock data no disponible. Intentando API real...")
            self.use_mock = False

        # Stats de la sesión
        self.stats = {
            "requests_made": 0,
            "requests_failed": 0,
            "traders_collected": 0,
            "mock_mode": self.use_mock
        }

    def fetch_leaderboard_rank(
        self,
        period: str = "DAILY",
        limit: int = 100,
        trade_type: str = "PERPETUAL"
    ) -> Dict:
        """
        Obtiene el ranking del leaderboard.

        Args:
            period: Periodo estadístico (DAILY, WEEKLY, MONTHLY, ALL)
            limit: Número máximo de traders a obtener (max 100)
            trade_type: Tipo de trading (PERPETUAL para USD-M Futures)

        Returns:
            Dict con datos del leaderboard o error

        Nota:
            Debido a limitaciones del API público de Binance (protección anti-scraping),
            por defecto se usan datos mock realistas para desarrollo.
        """

        # Si está en modo mock, usar datos de prueba
        if self.use_mock:
            print(f"🎭 Using MOCK data: period={period}, limit={limit}")
            mock_data = generate_mock_leaderboard(period, limit)
            self.stats["traders_collected"] += len(mock_data.get("data", []))
            print(f"✅ Generated {len(mock_data['data'])} mock traders")
            return mock_data

        # Intentar API real (puede fallar por protecciones de Binance)
        endpoint = f"{self.BASE_URL}/v2/public/future/leaderboard/getLeaderboardRank"

        params = {
            "tradeType": trade_type,
            "periodType": period.upper(),
            "statisticsType": "ROI",
            "limit": min(limit, 100)
        }

        print(f"📡 Fetching leaderboard from API: period={period}, limit={limit}...")
        print(f"⚠️  Nota: El API de Binance puede estar protegido contra scraping")

        try:
            response = self._make_request(endpoint, params)
            self.stats["requests_made"] += 1

            if response and response.get("success"):
                traders_count = len(response.get("data", []))
                self.stats["traders_collected"] += traders_count
                print(f"✅ Fetched {traders_count} traders successfully from API")
                return response
            else:
                error_msg = response.get("message", "Unknown error")
                print(f"❌ API returned error: {error_msg}")
                print(f"💡 Tip: Usa --mock para datos de prueba")
                self.stats["requests_failed"] += 1
                return {"error": error_msg, "success": False}

        except Exception as e:
            print(f"❌ Error fetching leaderboard: {e}")
            print(f"💡 Tip: Usa --mock para datos de prueba")
            self.stats["requests_failed"] += 1
            return {"error": str(e), "success": False}

    def fetch_trader_details(self, encrypted_uid: str) -> Dict:
        """
        Obtiene información detallada de un trader específico.

        Args:
            encrypted_uid: UID encriptado del trader (del leaderboard)

        Returns:
            Dict con información detallada del trader
        """

        # Si está en modo mock, usar datos de prueba
        if self.use_mock:
            print(f"🎭 Using MOCK trader details for: {encrypted_uid[:10]}...")
            mock_data = generate_mock_trader_details(encrypted_uid)
            print(f"✅ Generated mock trader details")
            return mock_data

        # Intentar API real
        endpoint = f"{self.BASE_URL}/v2/public/future/leaderboard/getOtherLeaderboardBaseInfo"
        params = {"encryptedUid": encrypted_uid}

        print(f"📡 Fetching trader details from API: {encrypted_uid[:10]}...")

        try:
            response = self._make_request(endpoint, params)
            self.stats["requests_made"] += 1

            if response and response.get("success"):
                print(f"✅ Trader details fetched successfully")
                return response
            else:
                error_msg = response.get("message", "Unknown error")
                print(f"❌ API returned error: {error_msg}")
                self.stats["requests_failed"] += 1
                return {"error": error_msg, "success": False}

        except Exception as e:
            print(f"❌ Error fetching trader details: {e}")
            self.stats["requests_failed"] += 1
            return {"error": str(e), "success": False}

    def _make_request(
        self,
        url: str,
        params: Dict,
        retry_attempts: int = None
    ) -> Optional[Dict]:
        """
        Realiza request HTTP con retry logic.

        Args:
            url: URL completa del endpoint
            params: Query parameters
            retry_attempts: Número de intentos (None = usar default)

        Returns:
            Response JSON parseado o None si falla
        """
        attempts = retry_attempts or self.DEFAULT_RETRY_ATTEMPTS

        for attempt in range(1, attempts + 1):
            try:
                response = requests.get(
                    url,
                    params=params,
                    timeout=self.DEFAULT_TIMEOUT,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (compatible; AkiraTraders/1.0)',
                        'Accept': 'application/json'
                    }
                )

                response.raise_for_status()
                return response.json()

            except requests.exceptions.Timeout:
                print(f"⚠️  Timeout on attempt {attempt}/{attempts}")
                if attempt < attempts:
                    time.sleep(self.DEFAULT_RETRY_DELAY)

            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code
                print(f"⚠️  HTTP {status_code} on attempt {attempt}/{attempts}")

                # Rate limit (429) o Server Error (5xx) - retry
                if status_code in [429, 500, 502, 503, 504]:
                    if attempt < attempts:
                        delay = self.DEFAULT_RETRY_DELAY * attempt  # Exponential backoff
                        print(f"   Retrying in {delay}s...")
                        time.sleep(delay)
                else:
                    # Client error (4xx) - no retry
                    raise

            except requests.exceptions.RequestException as e:
                print(f"⚠️  Request error: {e}")
                if attempt < attempts:
                    time.sleep(self.DEFAULT_RETRY_DELAY)

        return None

    def save_snapshot(
        self,
        data: Dict,
        period: str,
        snapshot_type: str = "leaderboard"
    ) -> Path:
        """
        Guarda snapshot del leaderboard con timestamp.

        Args:
            data: Datos a guardar (response del API)
            period: Periodo del snapshot (DAILY, WEEKLY, etc.)
            snapshot_type: Tipo de snapshot (leaderboard, trader_details)

        Returns:
            Path del archivo guardado
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{snapshot_type}_{period}_{timestamp}.json"
        filepath = self.data_dir / filename

        # Agregar metadata al snapshot
        snapshot = {
            "metadata": {
                "collected_at": datetime.utcnow().isoformat() + "Z",
                "period": period,
                "type": snapshot_type,
                "source": "binance_leaderboard_api"
            },
            "data": data
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False)

        file_size = filepath.stat().st_size / 1024  # KB
        print(f"💾 Snapshot saved: {filepath.name} ({file_size:.1f} KB)")

        return filepath

    def collect_and_save(
        self,
        period: str = "DAILY",
        limit: int = 100
    ) -> Dict:
        """
        Ejecuta colección completa y guarda snapshot.

        Args:
            period: Periodo a colectar (DAILY, WEEKLY, MONTHLY, ALL)
            limit: Número de traders a colectar

        Returns:
            Dict con estadísticas de la colección
        """
        print(f"\n{'='*70}")
        print(f"🚀 Iniciando colección del Leaderboard de Binance")
        print(f"{'='*70}")
        print(f"Periodo: {period}")
        print(f"Límite: {limit} traders")
        print(f"Destino: {self.data_dir}")
        print()

        # Fetch datos del leaderboard
        leaderboard_data = self.fetch_leaderboard_rank(period=period, limit=limit)

        if not leaderboard_data.get("success"):
            error = leaderboard_data.get("error", "Unknown error")
            print(f"\n❌ Colección fallida: {error}")
            return {
                "success": False,
                "error": error,
                "stats": self.stats
            }

        # Guardar snapshot
        filepath = self.save_snapshot(leaderboard_data, period)

        # Estadísticas
        traders_count = len(leaderboard_data.get("data", []))

        print(f"\n{'='*70}")
        print(f"✅ Colección completada exitosamente")
        print(f"{'='*70}")
        print(f"Traders colectados: {traders_count}")
        print(f"Archivo: {filepath}")
        print(f"Requests realizados: {self.stats['requests_made']}")
        print(f"Requests fallidos: {self.stats['requests_failed']}")
        print(f"{'='*70}\n")

        return {
            "success": True,
            "period": period,
            "traders_collected": traders_count,
            "filepath": str(filepath),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "stats": self.stats
        }

    def list_snapshots(self, period: Optional[str] = None) -> List[Dict]:
        """
        Lista snapshots guardados.

        Args:
            period: Filtrar por periodo (None = todos)

        Returns:
            Lista de dicts con info de snapshots
        """
        pattern = f"leaderboard_{period}_*.json" if period else "leaderboard_*.json"
        snapshots = sorted(self.data_dir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)

        result = []
        for snapshot_path in snapshots:
            try:
                with open(snapshot_path, 'r') as f:
                    data = json.load(f)
                    metadata = data.get("metadata", {})
                    traders_count = len(data.get("data", {}).get("data", []))

                    result.append({
                        "filename": snapshot_path.name,
                        "path": str(snapshot_path),
                        "collected_at": metadata.get("collected_at"),
                        "period": metadata.get("period"),
                        "traders_count": traders_count,
                        "size_kb": snapshot_path.stat().st_size / 1024
                    })
            except Exception as e:
                print(f"⚠️  Error reading {snapshot_path.name}: {e}")

        return result


def main():
    """Función principal para CLI"""
    parser = argparse.ArgumentParser(
        description="Binance Leaderboard Data Collector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Colectar ranking diario (default)
  python leaderboard_collector.py

  # Colectar ranking semanal
  python leaderboard_collector.py --period WEEKLY

  # Colectar top 50 traders
  python leaderboard_collector.py --limit 50

  # Listar snapshots guardados
  python leaderboard_collector.py --list
        """
    )

    parser.add_argument(
        "--period",
        choices=["DAILY", "WEEKLY", "MONTHLY", "ALL"],
        default="DAILY",
        help="Periodo estadístico (default: DAILY)"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Número de traders a colectar (max 100, default: 100)"
    )

    parser.add_argument(
        "--data-dir",
        default="data/leaderboard",
        help="Directorio para guardar snapshots (default: data/leaderboard)"
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="Listar snapshots guardados y salir"
    )

    parser.add_argument(
        "--mock",
        action="store_true",
        default=True,
        help="Usar datos mock (default: True, recomendado)"
    )

    parser.add_argument(
        "--real-api",
        action="store_true",
        help="Intentar usar API real de Binance (puede fallar)"
    )

    args = parser.parse_args()

    # Determinar si usar mock o API real
    use_mock = not args.real_api  # Por default mock=True, a menos que --real-api

    # Inicializar collector
    collector = BinanceLeaderboardCollector(data_dir=args.data_dir, use_mock=use_mock)

    # Si se pide listar snapshots
    if args.list:
        snapshots = collector.list_snapshots()
        if not snapshots:
            print("No hay snapshots guardados.")
            return 0

        print(f"\n📊 Snapshots guardados ({len(snapshots)}):\n")
        for i, snapshot in enumerate(snapshots, 1):
            print(f"{i}. {snapshot['filename']}")
            print(f"   Periodo: {snapshot['period']}")
            print(f"   Traders: {snapshot['traders_count']}")
            print(f"   Fecha: {snapshot['collected_at']}")
            print(f"   Tamaño: {snapshot['size_kb']:.1f} KB")
            print()
        return 0

    # Ejecutar colección
    result = collector.collect_and_save(period=args.period, limit=args.limit)

    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())

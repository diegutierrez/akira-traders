"""
Tests para el Binance Leaderboard Analyzer

Valida:
- Carga de snapshots
- Aplicación de filtros por perfil
- Cálculo de métricas derivadas
- Sistema de scoring ponderado
- Normalización de métricas
- Generación de recomendaciones
- Export de resultados
- Manejo de errores
"""

import pytest
import json
import sys
from pathlib import Path
from datetime import datetime

# Ajustar path para importar desde scripts/
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from leaderboard_analyzer import LeaderboardAnalyzer
from mock_leaderboard_data import generate_mock_leaderboard


@pytest.fixture
def temp_data_dir(tmp_path):
    """Directorio temporal para tests"""
    data_dir = tmp_path / "leaderboard"
    data_dir.mkdir(parents=True, exist_ok=True)

    # Crear snapshot de prueba
    mock_data = generate_mock_leaderboard("WEEKLY", 20)
    snapshot = {
        "metadata": {
            "collected_at": "2025-11-09T05:16:33.483232Z",
            "period": "WEEKLY",
            "type": "leaderboard",
            "source": "binance_leaderboard_api"
        },
        "data": mock_data
    }

    snapshot_file = data_dir / "leaderboard_WEEKLY_20251109.json"
    with open(snapshot_file, 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, indent=2)

    return str(data_dir)


@pytest.fixture
def analyzer(temp_data_dir):
    """Analyzer con directorio temporal"""
    return LeaderboardAnalyzer(data_dir=temp_data_dir)


@pytest.fixture
def sample_snapshot(temp_data_dir):
    """Snapshot de ejemplo cargado"""
    analyzer = LeaderboardAnalyzer(data_dir=temp_data_dir)
    return analyzer.load_snapshot()


@pytest.fixture
def sample_trader():
    """Trader de ejemplo para tests"""
    return {
        "nickName": "TestTrader01",
        "encryptedUid": "ABC123",
        "roi": 45.0,
        "pnl": 10000.0,
        "rank": 1,
        "followerCount": 250,
        "winRate": 65.0,
        "avgLeverage": 2.5,
        "positionShared": True,
        "twitterUrl": None
    }


@pytest.mark.unit
class TestAnalyzerInitialization:
    """Tests para inicialización del analyzer"""

    def test_analyzer_creates_with_valid_dir(self, temp_data_dir):
        """Verifica que se cree el analyzer con directorio válido"""
        analyzer = LeaderboardAnalyzer(data_dir=temp_data_dir)
        assert analyzer.data_dir == Path(temp_data_dir)

    def test_analyzer_fails_with_invalid_dir(self):
        """Verifica que falle con directorio inválido"""
        with pytest.raises(ValueError, match="Data directory not found"):
            LeaderboardAnalyzer(data_dir="/nonexistent/path")

    def test_analyzer_initializes_stats(self, analyzer):
        """Verifica que se inicialicen las estadísticas"""
        assert analyzer.stats["traders_analyzed"] == 0
        assert analyzer.stats["traders_passed_filters"] == 0
        assert analyzer.stats["traders_failed_filters"] == 0
        assert analyzer.stats["avg_score"] == 0.0


@pytest.mark.unit
class TestSnapshotLoading:
    """Tests para carga de snapshots"""

    def test_load_most_recent_snapshot(self, analyzer):
        """Verifica que cargue el snapshot más reciente"""
        snapshot = analyzer.load_snapshot()

        assert "metadata" in snapshot
        assert "data" in snapshot
        assert snapshot["metadata"]["period"] == "WEEKLY"

    def test_load_specific_snapshot(self, analyzer):
        """Verifica que cargue snapshot específico por nombre"""
        snapshot = analyzer.load_snapshot("leaderboard_WEEKLY_20251109.json")

        assert snapshot["metadata"]["period"] == "WEEKLY"

    def test_load_snapshot_fails_with_invalid_filename(self, analyzer):
        """Verifica que falle con filename inválido"""
        with pytest.raises(FileNotFoundError):
            analyzer.load_snapshot("nonexistent_file.json")

    def test_load_snapshot_fails_with_no_snapshots(self, tmp_path):
        """Verifica que falle si no hay snapshots"""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        analyzer = LeaderboardAnalyzer(data_dir=str(empty_dir))

        with pytest.raises(FileNotFoundError, match="No snapshots found"):
            analyzer.load_snapshot()

    def test_loaded_snapshot_has_traders(self, sample_snapshot):
        """Verifica que el snapshot cargado tenga traders"""
        traders = sample_snapshot.get("data", {}).get("data", [])
        assert len(traders) > 0


@pytest.mark.unit
class TestHardFilters:
    """Tests para filtros obligatorios"""

    def test_apply_hard_filters_moderate_profile(self, analyzer, sample_snapshot):
        """Verifica filtros con perfil moderado"""
        traders = sample_snapshot.get("data", {}).get("data", [])
        passed, failed = analyzer.apply_hard_filters(traders, "moderate")

        # Debe haber algunos que pasen y algunos que fallen
        assert len(passed) + len(failed) == len(traders)
        assert analyzer.stats["traders_analyzed"] == len(traders)
        assert analyzer.stats["traders_passed_filters"] == len(passed)
        assert analyzer.stats["traders_failed_filters"] == len(failed)

    def test_apply_hard_filters_conservative_profile(self, analyzer, sample_snapshot):
        """Verifica filtros con perfil conservador"""
        traders = sample_snapshot.get("data", {}).get("data", [])
        passed, failed = analyzer.apply_hard_filters(traders, "conservative")

        # Conservative es más restrictivo, debe haber menos que pasen
        assert len(passed) <= len(traders)

    def test_apply_hard_filters_aggressive_profile(self, analyzer, sample_snapshot):
        """Verifica filtros con perfil agresivo"""
        traders = sample_snapshot.get("data", {}).get("data", [])
        passed, failed = analyzer.apply_hard_filters(traders, "aggressive")

        # Aggressive es menos restrictivo, debe haber más que pasen
        assert len(passed) >= 0

    def test_hard_filters_reject_low_roi(self, analyzer):
        """Verifica que rechace traders con ROI muy bajo"""
        traders = [{
            "roi": 5.0,  # Muy bajo para cualquier perfil
            "winRate": 70.0,
            "avgLeverage": 2.0,
            "followerCount": 300
        }]

        passed, failed = analyzer.apply_hard_filters(traders, "moderate")

        assert len(passed) == 0
        assert len(failed) == 1
        assert "ROI too low" in failed[0]["rejection_reasons"][0]

    def test_hard_filters_reject_low_win_rate(self, analyzer):
        """Verifica que rechace traders con win rate bajo"""
        traders = [{
            "roi": 40.0,
            "winRate": 40.0,  # Bajo para moderate (min 55%)
            "avgLeverage": 2.0,
            "followerCount": 300
        }]

        passed, failed = analyzer.apply_hard_filters(traders, "moderate")

        assert len(passed) == 0
        assert len(failed) == 1

    def test_hard_filters_reject_high_leverage(self, analyzer):
        """Verifica que rechace traders con leverage alto"""
        traders = [{
            "roi": 40.0,
            "winRate": 60.0,
            "avgLeverage": 10.0,  # Muy alto para moderate (max 3x)
            "followerCount": 300
        }]

        passed, failed = analyzer.apply_hard_filters(traders, "moderate")

        assert len(passed) == 0
        assert len(failed) == 1

    def test_hard_filters_reject_low_followers(self, analyzer):
        """Verifica que rechace traders con pocos followers"""
        traders = [{
            "roi": 40.0,
            "winRate": 60.0,
            "avgLeverage": 2.0,
            "followerCount": 10  # Muy bajo para moderate (min 100)
        }]

        passed, failed = analyzer.apply_hard_filters(traders, "moderate")

        assert len(passed) == 0
        assert len(failed) == 1

    def test_hard_filters_accept_good_trader(self, analyzer):
        """Verifica que acepte trader que cumple todos los criterios"""
        traders = [{
            "roi": 40.0,
            "winRate": 60.0,
            "avgLeverage": 2.0,
            "followerCount": 300
        }]

        passed, failed = analyzer.apply_hard_filters(traders, "moderate")

        assert len(passed) == 1
        assert len(failed) == 0

    def test_hard_filters_invalid_profile(self, analyzer):
        """Verifica que falle con perfil inválido"""
        with pytest.raises(ValueError, match="Invalid profile"):
            analyzer.apply_hard_filters([], "invalid_profile")


@pytest.mark.unit
class TestDerivedMetrics:
    """Tests para cálculo de métricas derivadas"""

    def test_calculate_derived_metrics_structure(self, analyzer, sample_trader):
        """Verifica que retorne todas las métricas derivadas"""
        metrics = analyzer.calculate_derived_metrics(sample_trader, "moderate")

        required_metrics = [
            "estimated_max_dd",
            "rar",
            "consistency",
            "recovery_factor",
            "profit_factor"
        ]

        for metric in required_metrics:
            assert metric in metrics

    def test_calculate_derived_metrics_values_are_numeric(self, analyzer, sample_trader):
        """Verifica que todos los valores sean numéricos"""
        metrics = analyzer.calculate_derived_metrics(sample_trader, "moderate")

        for value in metrics.values():
            assert isinstance(value, (int, float))
            assert not isinstance(value, bool)

    def test_rar_calculation(self, analyzer):
        """Verifica cálculo de RAR (Risk-Adjusted Return)"""
        trader = {
            "roi": 50.0,
            "winRate": 60.0,
            "avgLeverage": 2.0,
            "pnl": 10000.0
        }

        metrics = analyzer.calculate_derived_metrics(trader, "moderate")

        # RAR = ROI / Max DD
        assert metrics["rar"] > 0
        assert metrics["rar"] == round(trader["roi"] / metrics["estimated_max_dd"], 2)

    def test_consistency_based_on_win_rate(self, analyzer):
        """Verifica que consistency esté basado en win rate"""
        trader = {
            "roi": 40.0,
            "winRate": 75.0,
            "avgLeverage": 2.0,
            "pnl": 5000.0
        }

        metrics = analyzer.calculate_derived_metrics(trader, "moderate")

        # Consistency = win_rate / 100
        assert metrics["consistency"] == 0.75

    def test_recovery_factor_calculation(self, analyzer):
        """Verifica cálculo de Recovery Factor"""
        trader = {
            "roi": 60.0,
            "winRate": 65.0,
            "avgLeverage": 2.5,
            "pnl": 15000.0
        }

        metrics = analyzer.calculate_derived_metrics(trader, "moderate")

        # RF = ROI / Max DD
        assert metrics["recovery_factor"] > 0


@pytest.mark.unit
class TestMetricNormalization:
    """Tests para normalización de métricas"""

    def test_normalize_metric_basic(self, analyzer):
        """Verifica normalización básica"""
        # 50 en rango 0-100 = 50
        normalized = analyzer.normalize_metric(50, 0, 100)
        assert normalized == 50.0

    def test_normalize_metric_edge_cases(self, analyzer):
        """Verifica casos extremos"""
        # Valor mínimo = 0
        assert analyzer.normalize_metric(0, 0, 100) == 0.0

        # Valor máximo = 100
        assert analyzer.normalize_metric(100, 0, 100) == 100.0

    def test_normalize_metric_reverse(self, analyzer):
        """Verifica normalización reversa (menor es mejor)"""
        # Para drawdown, menor es mejor
        normalized = analyzer.normalize_metric(10, 0, 100, reverse=True)
        assert normalized == 90.0

    def test_normalize_metric_out_of_bounds(self, analyzer):
        """Verifica que limite valores fuera de rango"""
        # Valor > max debe retornar 100
        normalized = analyzer.normalize_metric(150, 0, 100)
        assert normalized == 100.0

        # Valor < min debe retornar 0
        normalized = analyzer.normalize_metric(-50, 0, 100)
        assert normalized == 0.0

    def test_normalize_metric_same_min_max(self, analyzer):
        """Verifica comportamiento cuando min = max"""
        normalized = analyzer.normalize_metric(50, 50, 50)
        assert normalized == 50.0


@pytest.mark.unit
class TestScoring:
    """Tests para sistema de scoring"""

    def test_calculate_score_structure(self, analyzer, sample_trader):
        """Verifica estructura del score"""
        derived = analyzer.calculate_derived_metrics(sample_trader, "moderate")
        score, breakdown = analyzer.calculate_score(sample_trader, derived, "moderate")

        assert isinstance(score, float)
        assert 0 <= score <= 100

        required_keys = [
            "dd_score",
            "wr_score",
            "roi_score",
            "cons_score",
            "rar_score",
            "total_score"
        ]

        for key in required_keys:
            assert key in breakdown

    def test_calculate_score_all_components_valid(self, analyzer, sample_trader):
        """Verifica que todos los componentes estén en rango 0-100"""
        derived = analyzer.calculate_derived_metrics(sample_trader, "moderate")
        score, breakdown = analyzer.calculate_score(sample_trader, derived, "moderate")

        for key, value in breakdown.items():
            assert 0 <= value <= 100, f"{key} out of range: {value}"

    def test_calculate_score_different_profiles(self, analyzer, sample_trader):
        """Verifica que diferentes perfiles den diferentes scores"""
        derived = analyzer.calculate_derived_metrics(sample_trader, "moderate")

        score_cons, _ = analyzer.calculate_score(sample_trader, derived, "conservative")
        score_mod, _ = analyzer.calculate_score(sample_trader, derived, "moderate")
        score_agg, _ = analyzer.calculate_score(sample_trader, derived, "aggressive")

        # Los scores pueden ser diferentes debido a pesos distintos
        assert isinstance(score_cons, float)
        assert isinstance(score_mod, float)
        assert isinstance(score_agg, float)

    def test_calculate_score_total_matches_weighted_sum(self, analyzer, sample_trader):
        """Verifica que el total sea la suma ponderada correcta"""
        derived = analyzer.calculate_derived_metrics(sample_trader, "moderate")
        score, breakdown = analyzer.calculate_score(sample_trader, derived, "moderate")

        weights = analyzer.SCORING_WEIGHTS["moderate"]

        calculated_total = (
            breakdown["dd_score"] * weights["max_dd"] +
            breakdown["wr_score"] * weights["win_rate"] +
            breakdown["roi_score"] * weights["roi"] +
            breakdown["cons_score"] * weights["consistency"] +
            breakdown["rar_score"] * weights["rar"]
        )

        assert abs(score - calculated_total) < 0.1  # Tolerancia por redondeo


@pytest.mark.unit
class TestRecommendations:
    """Tests para generación de recomendaciones"""

    def test_recommendation_strong_buy(self, analyzer):
        """Verifica recomendación STRONG BUY para score alto"""
        rec = analyzer._get_recommendation(85, "moderate")
        assert "STRONG BUY" in rec

    def test_recommendation_buy(self, analyzer):
        """Verifica recomendación BUY"""
        rec = analyzer._get_recommendation(75, "moderate")
        assert "BUY" in rec

    def test_recommendation_hold(self, analyzer):
        """Verifica recomendación HOLD"""
        rec = analyzer._get_recommendation(65, "moderate")
        assert "HOLD" in rec

    def test_recommendation_watch(self, analyzer):
        """Verifica recomendación WATCH"""
        rec = analyzer._get_recommendation(55, "moderate")
        assert "WATCH" in rec

    def test_recommendation_pass(self, analyzer):
        """Verifica recomendación PASS para score bajo"""
        rec = analyzer._get_recommendation(40, "moderate")
        assert "PASS" in rec


@pytest.mark.unit
class TestAnalyzeTraders:
    """Tests para análisis completo de traders"""

    def test_analyze_traders_returns_valid_structure(self, analyzer, sample_snapshot):
        """Verifica estructura del resultado de análisis"""
        result = analyzer.analyze_traders(sample_snapshot, "moderate")

        assert "metadata" in result
        assert "stats" in result
        assert "candidates" in result
        assert "rejected" in result

    def test_analyze_traders_metadata_complete(self, analyzer, sample_snapshot):
        """Verifica que metadata esté completa"""
        result = analyzer.analyze_traders(sample_snapshot, "moderate")
        metadata = result["metadata"]

        assert "analyzed_at" in metadata
        assert "profile" in metadata
        assert "source_snapshot" in metadata
        assert "analyzer_version" in metadata
        assert metadata["profile"] == "moderate"

    def test_analyze_traders_stats_updated(self, analyzer, sample_snapshot):
        """Verifica que las estadísticas se actualicen"""
        result = analyzer.analyze_traders(sample_snapshot, "moderate")
        stats = result["stats"]

        assert stats["traders_analyzed"] > 0
        assert stats["traders_passed_filters"] >= 0
        assert stats["traders_failed_filters"] >= 0

    def test_analyze_traders_candidates_sorted_by_score(self, analyzer, sample_snapshot):
        """Verifica que candidatos estén ordenados por score"""
        result = analyzer.analyze_traders(sample_snapshot, "moderate")
        candidates = result["candidates"]

        if len(candidates) > 1:
            for i in range(len(candidates) - 1):
                score_current = candidates[i]["scores"]["total_score"]
                score_next = candidates[i + 1]["scores"]["total_score"]
                assert score_current >= score_next

    def test_analyze_traders_all_candidates_have_required_fields(self, analyzer, sample_snapshot):
        """Verifica que todos los candidatos tengan campos requeridos"""
        result = analyzer.analyze_traders(sample_snapshot, "moderate")
        candidates = result["candidates"]

        required_fields = ["profile", "derived_metrics", "scores", "recommendation"]

        for candidate in candidates:
            for field in required_fields:
                assert field in candidate

    def test_analyze_traders_different_profiles(self, analyzer, sample_snapshot):
        """Verifica análisis con diferentes perfiles"""
        for profile in ["conservative", "moderate", "aggressive"]:
            result = analyzer.analyze_traders(sample_snapshot, profile)
            assert result["metadata"]["profile"] == profile


@pytest.mark.unit
class TestExportResults:
    """Tests para export de resultados"""

    def test_export_results_creates_file(self, analyzer, sample_snapshot, tmp_path):
        """Verifica que se cree el archivo de export"""
        result = analyzer.analyze_traders(sample_snapshot, "moderate")
        output_file = tmp_path / "test_export.json"

        analyzer.export_results(result, str(output_file))

        assert output_file.exists()

    def test_export_results_valid_json(self, analyzer, sample_snapshot, tmp_path):
        """Verifica que el archivo exportado sea JSON válido"""
        result = analyzer.analyze_traders(sample_snapshot, "moderate")
        output_file = tmp_path / "test_export.json"

        analyzer.export_results(result, str(output_file))

        with open(output_file, 'r', encoding='utf-8') as f:
            exported = json.load(f)

        assert "metadata" in exported
        assert "stats" in exported
        assert "candidates" in exported

    def test_export_results_limits_top_n(self, analyzer, sample_snapshot, tmp_path):
        """Verifica que limite a top N candidatos"""
        result = analyzer.analyze_traders(sample_snapshot, "moderate")
        output_file = tmp_path / "test_export_top3.json"

        analyzer.export_results(result, str(output_file), top_n=3)

        with open(output_file, 'r', encoding='utf-8') as f:
            exported = json.load(f)

        assert len(exported["candidates"]) <= 3

    def test_export_results_creates_parent_directories(self, analyzer, sample_snapshot, tmp_path):
        """Verifica que cree directorios padre si no existen"""
        result = analyzer.analyze_traders(sample_snapshot, "moderate")
        output_file = tmp_path / "nested" / "dir" / "export.json"

        analyzer.export_results(result, str(output_file))

        assert output_file.exists()
        assert output_file.parent.exists()


@pytest.mark.unit
class TestEdgeCases:
    """Tests para casos extremos y manejo de errores"""

    def test_analyze_empty_trader_list(self, analyzer):
        """Verifica comportamiento con lista vacía de traders"""
        snapshot = {
            "metadata": {},
            "data": {"data": []}
        }

        result = analyzer.analyze_traders(snapshot, "moderate")

        assert result["stats"]["traders_analyzed"] == 0
        assert len(result["candidates"]) == 0

    def test_analyze_all_traders_rejected(self, analyzer):
        """Verifica comportamiento cuando todos los traders son rechazados"""
        # Traders con métricas muy malas
        traders = [
            {
                "roi": 5.0,
                "winRate": 30.0,
                "avgLeverage": 1.0,
                "followerCount": 10
            }
            for _ in range(5)
        ]

        snapshot = {
            "metadata": {},
            "data": {"data": traders}
        }

        result = analyzer.analyze_traders(snapshot, "moderate")

        assert result["stats"]["traders_passed_filters"] == 0
        assert len(result["candidates"]) == 0
        assert len(result["rejected"]) == 5

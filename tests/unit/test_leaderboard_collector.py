"""
Tests para el Binance Leaderboard Collector

Valida:
- Generación de datos mock con estructura correcta
- Guardado de snapshots con metadata
- Listado de snapshots existentes
- Manejo de errores
- Funcionalidad del CLI
"""

import pytest
import json
import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

# Ajustar path para importar desde scripts/
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from leaderboard_collector import BinanceLeaderboardCollector
from mock_leaderboard_data import generate_mock_leaderboard, generate_mock_trader_details


@pytest.fixture
def temp_data_dir(tmp_path):
    """Directorio temporal para tests"""
    data_dir = tmp_path / "leaderboard"
    data_dir.mkdir(parents=True, exist_ok=True)
    return str(data_dir)


@pytest.fixture
def collector(temp_data_dir):
    """Collector con directorio temporal"""
    return BinanceLeaderboardCollector(data_dir=temp_data_dir, use_mock=True)


@pytest.mark.unit
class TestMockDataGeneration:
    """Tests para generación de datos mock"""

    def test_generate_mock_leaderboard_structure(self):
        """Verifica que los datos mock tengan la estructura correcta del API"""
        data = generate_mock_leaderboard(period="WEEKLY", limit=10)

        # Estructura principal
        assert "code" in data
        assert "message" in data
        assert "messageDetail" in data
        assert "data" in data
        assert "success" in data

        # Valores esperados
        assert data["code"] == "000000"
        assert data["success"] is True
        assert isinstance(data["data"], list)
        assert len(data["data"]) == 10

    def test_generate_mock_leaderboard_trader_fields(self):
        """Verifica que cada trader tenga todos los campos requeridos"""
        data = generate_mock_leaderboard(period="DAILY", limit=5)

        required_fields = [
            "nickName", "encryptedUid", "roi", "pnl", "rank",
            "followerCount", "winRate", "avgLeverage", "positionShared", "twitterUrl"
        ]

        for trader in data["data"]:
            for field in required_fields:
                assert field in trader, f"Campo {field} faltante en trader"

    def test_generate_mock_leaderboard_ranking_order(self):
        """Verifica que los traders estén ordenados por ROI descendente"""
        data = generate_mock_leaderboard(period="WEEKLY", limit=20)
        traders = data["data"]

        # Verificar orden de ranks
        for i, trader in enumerate(traders, 1):
            assert trader["rank"] == i

        # Verificar orden de ROI
        rois = [t["roi"] for t in traders]
        assert rois == sorted(rois, reverse=True)

    def test_generate_mock_leaderboard_metric_ranges(self):
        """Verifica que las métricas estén en rangos realistas"""
        data = generate_mock_leaderboard(period="MONTHLY", limit=50)

        for trader in data["data"]:
            # ROI realista
            assert 10.0 <= trader["roi"] <= 200.0

            # Win rate realista
            assert 50.0 <= trader["winRate"] <= 75.0

            # Leverage realista
            assert 1.0 <= trader["avgLeverage"] <= 5.0

            # Followers no negativos
            assert trader["followerCount"] >= 1

            # Rank válido
            assert 1 <= trader["rank"] <= 50

    def test_generate_mock_leaderboard_limit_respected(self):
        """Verifica que se respete el límite de traders"""
        for limit in [5, 10, 25, 50, 100]:
            data = generate_mock_leaderboard(period="DAILY", limit=limit)
            assert len(data["data"]) == limit

    def test_generate_mock_trader_details_structure(self):
        """Verifica estructura de detalles de trader individual"""
        uid = "TEST1234567890ABCDEF"
        data = generate_mock_trader_details(uid)

        assert data["success"] is True
        assert data["code"] == "000000"
        assert "data" in data

        trader_data = data["data"]
        assert trader_data["encryptedUid"] == uid
        assert "nickName" in trader_data
        assert "roi30d" in trader_data
        assert "roi90d" in trader_data
        assert "maxDrawdown" in trader_data
        assert "sharpeRatio" in trader_data
        assert "followerCount" in trader_data
        assert "dailyData" in trader_data
        assert "topPositions" in trader_data


@pytest.mark.unit
class TestCollectorInitialization:
    """Tests para inicialización del collector"""

    def test_collector_creates_data_directory(self, temp_data_dir):
        """Verifica que se cree el directorio de datos"""
        collector = BinanceLeaderboardCollector(data_dir=temp_data_dir, use_mock=True)
        assert Path(temp_data_dir).exists()

    def test_collector_default_mock_mode(self, temp_data_dir):
        """Verifica que por defecto se use modo mock"""
        collector = BinanceLeaderboardCollector(data_dir=temp_data_dir)
        assert collector.use_mock is True

    def test_collector_stats_initialization(self, collector):
        """Verifica que las estadísticas se inicialicen correctamente"""
        assert collector.stats["requests_made"] == 0
        assert collector.stats["requests_failed"] == 0
        assert collector.stats["traders_collected"] == 0
        assert collector.stats["mock_mode"] is True


@pytest.mark.unit
class TestLeaderboardFetching:
    """Tests para obtención de leaderboard"""

    def test_fetch_leaderboard_mock_mode(self, collector):
        """Verifica que fetch en modo mock retorne datos válidos"""
        data = collector.fetch_leaderboard_rank(period="WEEKLY", limit=15)

        assert data["success"] is True
        assert len(data["data"]) == 15
        assert collector.stats["traders_collected"] == 15

    def test_fetch_leaderboard_different_periods(self, collector):
        """Verifica que funcione con diferentes periodos"""
        for period in ["DAILY", "WEEKLY", "MONTHLY", "ALL"]:
            data = collector.fetch_leaderboard_rank(period=period, limit=10)
            assert data["success"] is True
            assert len(data["data"]) == 10

    def test_fetch_leaderboard_different_limits(self, collector):
        """Verifica que funcione con diferentes límites"""
        for limit in [5, 10, 25, 50, 100]:
            data = collector.fetch_leaderboard_rank(period="DAILY", limit=limit)
            assert len(data["data"]) == limit


@pytest.mark.unit
class TestSnapshotSaving:
    """Tests para guardado de snapshots"""

    def test_save_snapshot_creates_file(self, collector):
        """Verifica que se cree el archivo de snapshot"""
        mock_data = generate_mock_leaderboard("WEEKLY", 10)
        filepath = collector.save_snapshot(mock_data, "WEEKLY")

        assert filepath.exists()
        assert filepath.suffix == ".json"
        assert "leaderboard_WEEKLY_" in filepath.name

    def test_save_snapshot_valid_json(self, collector):
        """Verifica que el snapshot sea JSON válido"""
        mock_data = generate_mock_leaderboard("DAILY", 5)
        filepath = collector.save_snapshot(mock_data, "DAILY")

        with open(filepath, 'r') as f:
            snapshot = json.load(f)

        assert "metadata" in snapshot
        assert "data" in snapshot

    def test_save_snapshot_metadata(self, collector):
        """Verifica que el snapshot tenga metadata correcta"""
        mock_data = generate_mock_leaderboard("MONTHLY", 20)
        filepath = collector.save_snapshot(mock_data, "MONTHLY")

        with open(filepath, 'r') as f:
            snapshot = json.load(f)

        metadata = snapshot["metadata"]
        assert metadata["period"] == "MONTHLY"
        assert metadata["type"] == "leaderboard"
        assert metadata["source"] == "binance_leaderboard_api"
        assert "collected_at" in metadata

        # Verificar formato de timestamp
        timestamp = datetime.fromisoformat(metadata["collected_at"].replace("Z", "+00:00"))
        assert isinstance(timestamp, datetime)

    def test_save_snapshot_preserves_data(self, collector):
        """Verifica que los datos se preserven correctamente"""
        mock_data = generate_mock_leaderboard("WEEKLY", 15)
        filepath = collector.save_snapshot(mock_data, "WEEKLY")

        with open(filepath, 'r') as f:
            snapshot = json.load(f)

        assert snapshot["data"] == mock_data


@pytest.mark.unit
class TestListSnapshots:
    """Tests para listado de snapshots"""

    def test_list_snapshots_empty(self, collector):
        """Verifica que retorne lista vacía si no hay snapshots"""
        snapshots = collector.list_snapshots()
        assert snapshots == []

    def test_list_snapshots_with_data(self, collector):
        """Verifica que liste snapshots existentes"""
        # Crear algunos snapshots
        for period in ["DAILY", "WEEKLY", "MONTHLY"]:
            mock_data = generate_mock_leaderboard(period, 10)
            collector.save_snapshot(mock_data, period)

        snapshots = collector.list_snapshots()
        assert len(snapshots) == 3

    def test_list_snapshots_structure(self, collector):
        """Verifica la estructura de la información de snapshots"""
        mock_data = generate_mock_leaderboard("WEEKLY", 5)
        collector.save_snapshot(mock_data, "WEEKLY")

        snapshots = collector.list_snapshots()
        assert len(snapshots) == 1

        snapshot_info = snapshots[0]
        assert "filename" in snapshot_info
        assert "path" in snapshot_info
        assert "collected_at" in snapshot_info
        assert "period" in snapshot_info
        assert "traders_count" in snapshot_info
        assert "size_kb" in snapshot_info

    def test_list_snapshots_filter_by_period(self, collector):
        """Verifica que filtre por periodo correctamente"""
        # Crear snapshots de diferentes periodos
        for period in ["DAILY", "WEEKLY", "MONTHLY", "ALL"]:
            mock_data = generate_mock_leaderboard(period, 10)
            collector.save_snapshot(mock_data, period)

        # Verificar filtro WEEKLY
        weekly_snapshots = collector.list_snapshots(period="WEEKLY")
        assert len(weekly_snapshots) == 1
        assert weekly_snapshots[0]["period"] == "WEEKLY"

        # Verificar filtro DAILY
        daily_snapshots = collector.list_snapshots(period="DAILY")
        assert len(daily_snapshots) == 1
        assert daily_snapshots[0]["period"] == "DAILY"

        # Verificar que todos los snapshots existen sin filtro
        all_snapshots = collector.list_snapshots()
        assert len(all_snapshots) == 4

    def test_list_snapshots_traders_count(self, collector):
        """Verifica que cuente correctamente los traders"""
        mock_data = generate_mock_leaderboard("DAILY", 25)
        collector.save_snapshot(mock_data, "DAILY")

        snapshots = collector.list_snapshots()
        assert snapshots[0]["traders_count"] == 25


@pytest.mark.unit
class TestCollectAndSave:
    """Tests para flujo completo de colección y guardado"""

    def test_collect_and_save_success(self, collector):
        """Verifica flujo exitoso de colección"""
        result = collector.collect_and_save(period="WEEKLY", limit=20)

        assert result["success"] is True
        assert result["period"] == "WEEKLY"
        assert result["traders_collected"] == 20
        assert "filepath" in result
        assert "timestamp" in result
        assert "stats" in result

    def test_collect_and_save_creates_file(self, collector, temp_data_dir):
        """Verifica que se cree el archivo"""
        result = collector.collect_and_save(period="DAILY", limit=10)

        filepath = Path(result["filepath"])
        assert filepath.exists()
        assert filepath.parent == Path(temp_data_dir)

    def test_collect_and_save_updates_stats(self, collector):
        """Verifica que se actualicen las estadísticas"""
        collector.collect_and_save(period="MONTHLY", limit=30)

        assert collector.stats["traders_collected"] == 30

    def test_collect_and_save_different_periods(self, collector):
        """Verifica que funcione con diferentes periodos"""
        for period in ["DAILY", "WEEKLY", "MONTHLY"]:
            result = collector.collect_and_save(period=period, limit=5)
            assert result["success"] is True
            assert result["period"] == period


@pytest.mark.unit
class TestTraderDetails:
    """Tests para obtención de detalles de trader"""

    def test_fetch_trader_details_mock(self, collector):
        """Verifica obtención de detalles en modo mock"""
        uid = "ABC123DEF456"
        data = collector.fetch_trader_details(uid)

        assert data["success"] is True
        assert data["data"]["encryptedUid"] == uid

    def test_fetch_trader_details_structure(self, collector):
        """Verifica estructura de detalles"""
        data = collector.fetch_trader_details("TEST123")

        trader_data = data["data"]
        required_fields = ["encryptedUid", "nickName", "roi30d", "roi90d",
                          "maxDrawdown", "followerCount", "dailyData"]

        for field in required_fields:
            assert field in trader_data


@pytest.mark.unit
class TestErrorHandling:
    """Tests para manejo de errores"""

    def test_collector_without_mock_data_available(self, temp_data_dir):
        """Verifica comportamiento si mock data no está disponible"""
        with patch('leaderboard_collector.MOCK_DATA_AVAILABLE', False):
            collector = BinanceLeaderboardCollector(
                data_dir=temp_data_dir,
                use_mock=True
            )
            # Debería desactivar mock automáticamente
            assert collector.use_mock is False

    def test_invalid_snapshot_reading(self, collector, temp_data_dir):
        """Verifica manejo de snapshots corruptos"""
        # Crear archivo JSON inválido
        invalid_file = Path(temp_data_dir) / "leaderboard_WEEKLY_invalid.json"
        invalid_file.write_text("{ invalid json }")

        # No debería crashear
        snapshots = collector.list_snapshots()
        # El archivo inválido no debería aparecer en la lista
        # (o debería manejarse con gracia)

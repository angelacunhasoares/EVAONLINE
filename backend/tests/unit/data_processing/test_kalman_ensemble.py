from pathlib import Path
from unittest.mock import MagicMock, patch
import time

import numpy as np
import pandas as pd
import pytest

from backend.core.data_processing.climate_ensemble import ClimateKalmanEnsemble
from backend.core.data_processing.kalman_filters import (
    AdaptiveKalmanFilter,
    SimpleKalmanFilter,
)
from backend.core.data_processing.historical_loader import HistoricalDataLoader


class TestAdaptiveKalmanFilter:
    """Testes para AdaptiveKalmanFilter"""

    def test_initialization(self):
        """Testa inicialização com valores padrão"""
        kf = AdaptiveKalmanFilter()
        assert kf.normal == 5.0
        assert kf.std == 1.0
        assert kf.state.estimate == 5.0

    def test_update_with_valid_value(self):
        """Testa atualização com valor válido"""
        kf = AdaptiveKalmanFilter(normal=5.0, std=1.0)
        result = kf.update(5.5)
        assert isinstance(result, float)
        assert result == pytest.approx(5.3, abs=0.1)

    def test_update_with_nan(self):
        """Testa atualização com NaN"""
        kf = AdaptiveKalmanFilter(normal=5.0)
        result = kf.update(np.nan)
        assert result == 5.0  # Deve retornar estimate atual

    def test_outlier_detection(self):
        """Testa detecção de outliers"""
        kf = AdaptiveKalmanFilter(normal=5.0, std=1.0, p01=2.0, p99=8.0)
        # Valor muito baixo (outlier)
        result = kf.update(1.0)
        assert result == pytest.approx(5.0, abs=0.5)  # Deve ser pouco afetado


class TestSimpleKalmanFilter:
    """Testes para SimpleKalmanFilter"""

    def test_initialization(self):
        """Testa inicialização"""
        kf = SimpleKalmanFilter(10.0)
        assert kf.estimate == 10.0
        assert kf.error == 1.0

    def test_update(self):
        """Testa atualização simples"""
        kf = SimpleKalmanFilter(5.0)
        result = kf.update(6.0)
        assert result == pytest.approx(5.57, abs=0.1)

    def test_update_batch(self):
        """Testa processamento em lote"""
        kf = SimpleKalmanFilter(5.0)
        values = np.array([5.0, 6.0, 7.0])
        results = kf.update_batch(values)
        assert len(results) == 3
        assert all(isinstance(r, float) for r in results)


class TestHistoricalDataLoader:
    """Testes para HistoricalDataLoader"""

    def setup_method(self):
        """Setup para cada teste"""
        self.loader = HistoricalDataLoader()

    @patch("backend.core.data_processing.kalman_ensemble.Path")
    def test_load_city_coords_success(self, mock_path):
        """Testa carregamento bem-sucedido de coordenadas"""
        mock_path.return_value.resolve.return_value.parent.parent.parent.parent = Path(
            "/fake"
        )
        mock_path.return_value.parent.parent.parent.parent.__truediv__ = (
            lambda x, y: Path(f"/fake/{y}")
        )

        # Mock do arquivo CSV
        with patch("pandas.read_csv") as mock_read_csv:
            mock_read_csv.return_value = pd.DataFrame(
                {
                    "city": ["SaoPaulo", "RioDeJaneiro"],
                    "lat": [-23.55, -22.90],
                    "lon": [-46.63, -43.17],
                    "region": ["brasil", "brasil"],
                }
            )
            coords = self.loader._load_city_coords()
            assert "SaoPaulo" in coords
            assert coords["SaoPaulo"][0] == -23.55

    def test_get_reference_for_location_with_cache(self):
        """Testa busca com cache"""
        # Adiciona ao cache
        self.loader._cache.set((0.0, 0.0), {"test": "data"})

        has_ref, ref = self.loader.get_reference_for_location(0.0, 0.0)
        assert has_ref is True
        assert ref == {"test": "data"}

    @patch(
        "backend.core.data_processing.kalman_ensemble.detect_geographic_region"
    )
    @patch("backend.core.data_processing.kalman_ensemble.haversine_distance")
    def test_get_reference_for_location_no_match(
        self, mock_distance, mock_region
    ):
        """Testa quando não encontra referência"""
        mock_region.return_value = "global"
        mock_distance.return_value = 300.0  # Distância muito grande

        has_ref, ref = self.loader.get_reference_for_location(0.0, 0.0)
        assert has_ref is False
        assert ref is None


class TestClimateKalmanEnsemble:
    """Testes para ClimateKalmanEnsemble"""

    def setup_method(self):
        """Setup para cada teste"""
        self.ensemble = ClimateKalmanEnsemble()

    def test_initialization(self):
        """Testa inicialização"""
        assert self.ensemble.loader is not None
        assert self.ensemble.kalman_precip is None

    def test_validate_climate_data_valid(self):
        """Testa validação de dados válidos"""
        df = pd.DataFrame({"T2M": [20.0, 25.0], "RH2M": [50.0, 60.0]})
        # Não deve lançar exceção
        self.ensemble._validate_climate_data(df, "test_source")

    def test_validate_climate_data_invalid(self):
        """Testa validação de dados inválidos"""
        df = pd.DataFrame(
            {
                "T2M": [100.0],  # Valor inválido (muito alto)
            }
        )
        # A validação deve registrar warning mas não lançar exceção
        # O log é registrado via loguru, então apenas verificamos que não lança exceção
        try:
            self.ensemble._validate_climate_data(df, "test_source")
        except Exception as e:
            pytest.fail(
                f"_validate_climate_data lançou exceção inesperada: {e}"
            )

    def test_create_empty_result(self):
        """Testa criação de resultado vazio"""
        result = self.ensemble._create_empty_result()
        assert result.empty
        expected_cols = [
            "date",
            "T2M_MAX",
            "T2M_MIN",
            "T2M",
            "RH2M",
            "WS2M",
            "ALLSKY_SFC_SW_DWN",
            "PRECTOTCORR",
            "fusion_mode",
        ]
        assert list(result.columns) == expected_cols

    def test_detect_region_with_priority_usa(self):
        """Testa detecção de região USA"""
        with patch(
            "backend.core.data_processing.kalman_ensemble.detect_geographic_region"
        ) as mock_region:
            mock_region.return_value = "usa"
            info = self.ensemble._detect_region_with_priority(40.0, -100.0)
            assert info["name"] == "USA"
            assert "nws_forecast" in info["source_weights"]

    def test_detect_region_with_priority_global(self):
        """Testa detecção de região global"""
        with patch(
            "backend.core.data_processing.kalman_ensemble.detect_geographic_region"
        ) as mock_region:
            mock_region.return_value = "global"
            info = self.ensemble._detect_region_with_priority(0.0, 0.0)
            assert info["name"] == "GLOBAL"
            assert "openmeteo_forecast" in info["source_weights"]

    def test_prepare_multi_source_data(self):
        """Testa preparação de dados multi-fonte"""
        df = pd.DataFrame(
            {
                "date": ["2023-01-01", "2023-01-02"],
                "T2M": [20.0, 21.0],
                "source": ["source1", "source2"],
            }
        )
        result = self.ensemble._prepare_multi_source_data(df)
        assert isinstance(result.index, pd.DatetimeIndex)

    def test_fuse_variable_single_source(self):
        """Testa fusão com fonte única"""
        sources_data = {"source1": 20.0}
        source_weights = {"source1": 1.0}
        result = self.ensemble._fuse_variable(
            "T2M", sources_data, source_weights, "source1"
        )
        assert result == 20.0

    def test_fuse_variable_two_sources(self):
        """Testa fusão com duas fontes"""
        sources_data = {"source1": 20.0, "source2": 22.0}
        source_weights = {"source1": 0.6, "source2": 0.4}
        result = self.ensemble._fuse_variable(
            "T2M", sources_data, source_weights, "source1", "source2"
        )
        expected = 0.6 * 20.0 + 0.4 * 22.0
        assert result == pytest.approx(expected)

    def test_smart_variable_fusion(self):
        """Testa fusão inteligente de variáveis"""
        group = pd.DataFrame(
            {"T2M": [20.0, 22.0], "source": ["source1", "source2"]}
        )
        source_weights = {"source1": 0.6, "source2": 0.4}

        result = self.ensemble._smart_variable_fusion(
            group, source_weights, "source1", "source2"
        )
        assert "T2M" in result
        assert isinstance(result["T2M"], float)

    def test_auto_fuse_multi_source_empty_input(self):
        """Testa fusão multi-fonte com input vazio"""
        result = self.ensemble.auto_fuse_multi_source(pd.DataFrame(), 0.0, 0.0)
        assert result.empty

    def test_auto_fuse_basic(self):
        """Testa fusão básica entre NASA e OpenMeteo"""
        nasa_df = pd.DataFrame(
            {
                "date": pd.date_range("2023-01-01", periods=3),
                "T2M_MAX": [25.0, 26.0, 27.0],
                "T2M_MIN": [15.0, 16.0, 17.0],
                "T2M": [20.0, 21.0, 22.0],
                "RH2M": [50.0, 51.0, 52.0],
                "WS2M": [3.0, 3.1, 3.2],
                "ALLSKY_SFC_SW_DWN": [200.0, 210.0, 220.0],
                "PRECTOTCORR": [0.0, 1.0, 2.0],
            }
        )
        om_df = pd.DataFrame(
            {
                "date": pd.date_range("2023-01-01", periods=3),
                "T2M_MAX": [24.0, 25.0, 26.0],
                "T2M_MIN": [14.0, 15.0, 16.0],
                "T2M": [19.0, 20.0, 21.0],
                "RH2M": [49.0, 50.0, 51.0],
                "WS2M": [2.9, 3.0, 3.1],
                "ALLSKY_SFC_SW_DWN": [190.0, 200.0, 210.0],
                "PRECTOTCORR": [0.5, 1.5, 2.5],
            }
        )

        result = self.ensemble.auto_fuse(nasa_df, om_df, 0.0, 0.0)
        assert len(result) == 3
        assert "fusion_mode" in result.columns

    def test_reset(self):
        """Testa reset do estado"""
        self.ensemble.kalman_precip = MagicMock()
        self.ensemble.kalman_eto = MagicMock()
        self.ensemble.current_month = 1

        self.ensemble.reset()
        assert self.ensemble.kalman_precip is None
        assert self.ensemble.kalman_eto is None
        assert self.ensemble.current_month is None


# Testes de integração
class TestIntegration:
    """Testes de integração"""

    def test_full_fusion_pipeline(self):
        """Testa pipeline completo de fusão"""
        # Criar dados de teste mais realistas
        dates = pd.date_range("2023-01-01", periods=5)

        nasa_df = pd.DataFrame(
            {
                "date": dates,
                "T2M": [15.0, 16.0, 17.0, 18.0, 19.0],
                "T2M_MAX": [20.0, 21.0, 22.0, 23.0, 24.0],
                "T2M_MIN": [10.0, 11.0, 12.0, 13.0, 14.0],
                "RH2M": [60.0, 61.0, 62.0, 63.0, 64.0],
                "WS2M": [2.0, 2.1, 2.2, 2.3, 2.4],
                "ALLSKY_SFC_SW_DWN": [200.0, 210.0, 220.0, 230.0, 240.0],
                "PRECTOTCORR": [0.0, 1.0, 2.0, 0.5, 0.0],
            }
        )

        om_df = pd.DataFrame(
            {
                "date": dates,
                "T2M": [14.5, 15.5, 16.5, 17.5, 18.5],
                "T2M_MAX": [19.5, 20.5, 21.5, 22.5, 23.5],
                "T2M_MIN": [9.5, 10.5, 11.5, 12.5, 13.5],
                "RH2M": [59.0, 60.0, 61.0, 62.0, 63.0],
                "WS2M": [1.9, 2.0, 2.1, 2.2, 2.3],
                "ALLSKY_SFC_SW_DWN": [195.0, 205.0, 215.0, 225.0, 235.0],
                "PRECTOTCORR": [0.1, 0.9, 1.8, 0.4, 0.1],
            }
        )

        ensemble = ClimateKalmanEnsemble()
        result = ensemble.auto_fuse(
            nasa_df, om_df, -23.55, -46.63
        )  # São Paulo

        # Verificações básicas
        assert len(result) > 0
        assert "fusion_mode" in result.columns
        assert all(
            col in result.columns for col in ["T2M", "RH2M", "PRECTOTCORR"]
        )

        # Verificar que valores estão na faixa esperada
        assert result["T2M"].mean() == pytest.approx(16.5, abs=2.0)
        assert result["RH2M"].mean() == pytest.approx(61.0, abs=5.0)


class TestPerformance:
    """Testes de performance e carga"""

    @patch("backend.core.utils.geo_utils.detect_geographic_region")
    @patch("backend.core.utils.geo_utils.haversine_distance")
    @patch("backend.core.utils.geo_utils.is_same_hemisphere")
    def test_multi_source_performance(
        self, mock_same_hemisphere, mock_distance, mock_detect_region
    ):
        """Testa performance com dados simulados de 6 fontes"""
        # Mock das funções geográficas
        mock_detect_region.return_value = "usa"
        mock_distance.return_value = 100.0
        mock_same_hemisphere.return_value = True

        ensemble = ClimateKalmanEnsemble()

        # Criar dados simulados para 6 fontes x 365 dias
        sources = [
            "nws_forecast",
            "met_norway",
            "openmeteo_forecast",
            "nasa_power",
            "ecmwf",
            "gfs",
        ]

        test_data = []
        for day in range(365):
            date = pd.Timestamp("2024-01-01") + pd.Timedelta(days=day)
            for source in sources:
                test_data.append(
                    {
                        "date": date,
                        "source": source,
                        "T2M_MAX": 25 + np.random.normal(0, 3),
                        "T2M_MIN": 15 + np.random.normal(0, 2),
                        "T2M": 20 + np.random.normal(0, 2.5),
                        "RH2M": 60 + np.random.normal(0, 10),
                        "WS2M": 3 + np.random.exponential(1),
                        "ALLSKY_SFC_SW_DWN": 20 + np.random.normal(0, 5),
                        "PRECTOTCORR": np.random.exponential(2),
                    }
                )

        df = pd.DataFrame(test_data)

        # Testar performance
        start = time.time()
        result = ensemble.auto_fuse_multi_source(df, lat=40.0, lon=-74.0)
        elapsed = time.time() - start

        print(f"✅ Fusão de {len(df)} linhas (6 fontes x 365 dias)")
        print(f"   Tempo total: {elapsed:.2f}s")
        print(f"   Linhas resultantes: {len(result)}")
        memory_mb = result.memory_usage(deep=True).sum() / 1024 / 1024
        print(f"   Memória usada: {memory_mb:.1f} MB")

        # Verificações de performance
        assert elapsed < 2.0, f"Fusão muito lenta: {elapsed:.2f}s"
        assert len(result) > 300, f"Poucos dados resultantes: {len(result)}"
        assert (
            result.memory_usage(deep=True).sum() < 50 * 1024 * 1024
        ), "Uso excessivo de memória"

        # Verificações de qualidade
        assert "fusion_mode" in result.columns
        assert all(
            col in result.columns for col in ["T2M", "RH2M", "PRECTOTCORR"]
        )

        return result

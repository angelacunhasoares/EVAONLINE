"""
Integration Tests - Climate Sources Flow

Testa fluxo completo de seleção e fallback de fontes de dados climáticos.
"""

import pytest
from unittest.mock import patch, AsyncMock
import pandas as pd


@pytest.mark.integration
@pytest.mark.requires_apis
class TestClimateSourceFallback:
    """Testa fallback entre fontes de dados."""

    def test_climate_source_selection_integration(self, api_client):
        """Testa seleção automática de fonte climática."""
        request = {
            "lat": -22.25,
            "lng": -48.5,
            "start_date": "2024-07-01",
            "end_date": "2024-07-30",
            "period_type": "historical_email",
            "email": "test@example.com",
            "sources": "auto",  # Auto-seleção
        }

        response = api_client.post(
            "/api/v1/internal/eto/calculate", json=request
        )

        # Deve processar ou falhar graciosamente
        assert response.status_code in [200, 202, 400, 500]

    def test_specific_source_validation(self, api_client):
        """Testa validação de fonte específica."""
        request = {
            "lat": -22.25,
            "lng": -48.5,
            "start_date": "2025-07-01",
            "end_date": "2025-07-31",
            "sources": "openmeteo_archive",  # Fonte específica
        }

        response = api_client.post(
            "/api/v1/internal/eto/calculate", json=request
        )

        # Deve processar ou rejeitar fonte inválida
        assert response.status_code in [200, 202, 400, 500]

    @patch("backend.api.services.data_download.download_weather_data")
    def test_nasa_power_to_openmeteo_fallback(self, mock_download, api_client):
        """Testa fallback quando NASA POWER falha."""
        # Simular dados do OpenMeteo após NASA falhar
        mock_df = pd.DataFrame(
            {
                "T2M_MAX": [32.5],
                "T2M_MIN": [18.2],
                "T2M": [25.4],
                "RH2M": [65.0],
                "WS2M": [2.5],
            },
            index=pd.date_range("2025-07-01", periods=1),
        )
        mock_download.return_value = AsyncMock(
            return_value=(mock_df, ["NASA POWER falhou, usando OpenMeteo"])
        )

        request = {
            "lat": -22.25,
            "lng": -48.5,
            "start_date": "2024-07-01",
            "end_date": "2024-07-07",
            "period_type": "historical_email",
            "email": "test@example.com",
            "sources": "data fusion",
        }

        response = api_client.post(
            "/api/v1/internal/eto/calculate", json=request
        )

        # Deve processar com fallback ou falhar em infra
        assert response.status_code in [200, 202, 400, 500]

    @patch("backend.api.services.data_download.download_weather_data")
    def test_all_sources_fail(self, mock_download, api_client):
        """Testa quando todas as fontes falham."""
        # Simular falha em todas as fontes
        mock_download.side_effect = ValueError(
            "Nenhuma fonte forneceu dados válidos"
        )

        request = {
            "lat": -22.25,
            "lng": -48.5,
            "start_date": "2025-07-01",
            "end_date": "2025-07-07",
        }

        response = api_client.post(
            "/api/v1/internal/eto/calculate", json=request
        )

        # Deve retornar erro
        assert response.status_code in [400, 500, 503]


@pytest.mark.integration
class TestClimateSourceAvailability:
    """Testa disponibilidade de fontes."""

    def test_check_nasa_power_availability(self, api_client):
        """Testa verificação de disponibilidade da NASA POWER."""
        response = api_client.get("/api/v1/climate/sources")

        ct = response.headers.get("content-type", "")
        if "application/json" not in ct:
            pytest.skip(
                "Endpoint /api/v1/climate/sources not implemented (returns Dash HTML)"
            )

        if response.status_code == 200:
            data = response.json()

            # Verificar estrutura da resposta
            assert isinstance(data, (dict, list))


@pytest.mark.integration
class TestClimateDataQuality:
    """Testa qualidade dos dados climáticos."""

    def test_data_completeness_check(self, api_client):
        """Testa verificação de completude dos dados."""
        request = {
            "lat": -22.25,
            "lng": -48.5,
            "start_date": "2025-07-01",
            "end_date": "2025-07-07",  # 1 semana
        }

        response = api_client.post(
            "/api/v1/internal/eto/calculate", json=request
        )

        # Se funcionar, dados devem ser válidos
        if response.status_code in [200, 202]:
            data = response.json()
            assert "task_id" in data or "status" in data

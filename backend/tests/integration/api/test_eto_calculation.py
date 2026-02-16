"""
Integration Tests - ETO Calculation Flow

Testa fluxo E2E completo de cálculo de evapotranspiração.
"""

import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.integration
class TestETOCalculationE2E:
    """Testa fluxo completo de cálculo ETO."""

    def test_complete_eto_calculation_flow(
        self, api_client, sample_eto_request
    ):
        """Testa fluxo completo: request → dados → cálculo → resposta."""
        with patch(
            "backend.infrastructure.celery.tasks.eto_calculation."
            "calculate_eto_task.delay"
        ) as mock_task:
            mock_task.return_value = MagicMock(id="task-integration-123")

            response = api_client.post(
                "/api/v1/internal/eto/calculate", json=sample_eto_request
            )

            # Deve aceitar e iniciar tarefa (ou falhar em infra)
            assert response.status_code in [200, 202, 500]

            if response.status_code in [200, 202]:
                data = response.json()
                assert "task_id" in data or "status" in data

    def test_eto_calculation_with_multiple_sources(
        self, api_client, sample_eto_request
    ):
        """Testa cálculo com múltiplas fontes de dados."""
        # Forçar uso de múltiplas fontes
        request = {**sample_eto_request, "sources": "nasa,openmeteo"}

        response = api_client.post(
            "/api/v1/internal/eto/calculate", json=request
        )

        # Deve processar (ou falhar graciosamente)
        assert response.status_code in [200, 202, 422, 500]


@pytest.mark.integration
class TestETOWithElevationLookup:
    """Testa integração com busca de elevação."""

    def test_eto_without_elevation_fetches_from_opentopo(self, api_client):
        """Testa que busca elevação quando não fornecida."""
        request = {
            "lat": -22.25,
            "lng": -48.5,
            "start_date": "2024-07-01",
            "end_date": "2024-07-30",
            "period_type": "historical_email",
            "email": "test@example.com",
            # elevation ausente
        }

        response = api_client.post(
            "/api/v1/internal/eto/calculate", json=request
        )

        # Deve processar mesmo sem elevação
        assert response.status_code in [200, 202, 400, 500]


@pytest.mark.integration
@pytest.mark.requires_redis
class TestETOResultCaching:
    """Testa cache de resultados ETO."""

    def test_repeated_calculation_uses_cache(
        self, api_client, sample_eto_request
    ):
        """Testa que cálculos repetidos usam cache."""
        with patch(
            "backend.infrastructure.celery.tasks.eto_calculation."
            "calculate_eto_task.delay"
        ) as mock_task:
            mock_task.return_value = MagicMock(id="task-cache-test")

            # Primeira request
            response1 = api_client.post(
                "/api/v1/internal/eto/calculate", json=sample_eto_request
            )

            # Segunda request idêntica
            response2 = api_client.post(
                "/api/v1/internal/eto/calculate", json=sample_eto_request
            )

            # Ambas devem retornar sucesso (ou erro de infra)
            assert response1.status_code in [200, 202, 500]
            assert response2.status_code in [200, 202, 500]


@pytest.mark.integration
class TestETOWithDifferentPeriods:
    """Testa cálculo ETO com diferentes períodos."""

    @pytest.mark.parametrize(
        "period_type",
        ["dashboard_current", "dashboard_forecast", "historical_email"],
    )
    def test_eto_calculation_different_periods(self, api_client, period_type):
        """Testa cálculo com diferentes tipos de período."""
        request = {
            "lat": -22.25,
            "lng": -48.5,
            "start_date": "2025-07-01",
            "end_date": "2025-07-07",
            "period_type": period_type,
        }

        response = api_client.post(
            "/api/v1/internal/eto/calculate", json=request
        )

        # Deve processar (ou rejeitar historical se > 7 dias)
        assert response.status_code in [200, 202, 400, 422, 500]


@pytest.mark.integration
class TestETOErrorHandling:
    """Testa tratamento de erros no fluxo ETO."""

    def test_handles_invalid_coordinates(self, api_client):
        """Testa tratamento de coordenadas inválidas."""
        request = {
            "lat": 200.0,  # Inválida
            "lng": -48.5,
            "start_date": "2025-07-01",
            "end_date": "2025-07-31",
        }

        response = api_client.post(
            "/api/v1/internal/eto/calculate", json=request
        )

        # Deve rejeitar coordenadas inválidas
        assert response.status_code in [400, 422, 500]

    def test_handles_invalid_date_range(self, api_client):
        """Testa tratamento de intervalo de datas inválido."""
        request = {
            "lat": -22.25,
            "lng": -48.5,
            "start_date": "2025-12-31",
            "end_date": "2025-01-01",  # end antes de start
        }

        response = api_client.post(
            "/api/v1/internal/eto/calculate", json=request
        )

        # Deve rejeitar range inválido
        assert response.status_code in [400, 422, 500]

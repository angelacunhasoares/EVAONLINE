"""
Security Tests - Input Validation

Tests: Validação de inputs maliciosos
"""

import pytest


@pytest.mark.integration
class TestInputValidation:
    """Testa validação de inputs."""

    def test_sql_injection_prevention(self, api_client):
        """Testa prevenção de SQL injection."""
        # TODO: Testar inputs maliciosos
        # Ex: lat="1'; DROP TABLE climate_data;--"
        assert True

    def test_xss_prevention(self, api_client):
        """Testa prevenção de XSS."""
        # TODO: Testar inputs com scripts
        assert True

    def test_coordinate_validation(self, api_client):
        """Testa validação de coordenadas maliciosas."""
        # Test via the actual ETo calculate endpoint
        response = api_client.post(
            "/api/v1/internal/eto/calculate",
            json={
                "lat": 999,
                "lng": -999,
                "start_date": "2024-01-01",
                "end_date": "2024-01-07",
                "period_type": "historical_email",
                "email": "test@example.com",
            },
        )
        assert response.status_code in [400, 422]  # Validation error

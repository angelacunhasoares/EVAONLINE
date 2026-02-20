"""
Cliente HTTP para integração com API backend.

Fornece métodos para chamar endpoints da API FastAPI
de forma assíncrona nos callbacks do Dash.

Endpoints disponíveis no backend (verificados em routes/__init__.py):
- GET  /health, /health/detailed, /health/ready
- POST /internal/eto/calculate
- GET  /internal/eto/status/{task_id}
- GET  /climate/sources
- POST /visitors/increment
- GET  /visitors/stats
- POST /geolocation/track
"""

import logging
from typing import Any, Dict, Optional

import httpx
from config.settings.app_config import get_legacy_settings

logger = logging.getLogger(__name__)


class APIClient:
    """
    Cliente HTTP para comunicação com backend FastAPI.

    Cada instância cria um httpx.AsyncClient próprio.
    Usar como context manager para garantir cleanup:

        async with APIClient() as client:
            result = await client.calculate_eto(payload)
    """

    def __init__(self, base_url: Optional[str] = None):
        settings = get_legacy_settings()
        port = getattr(settings, "api", {}).get("PORT", 8000)
        self.base_url = (
            base_url or f"http://localhost:{port}{settings.API_V1_PREFIX}"
        )
        self.client = httpx.AsyncClient(timeout=30.0)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    # ===========================================
    # MÉTODOS HTTP GENÉRICOS
    # ===========================================

    async def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Faz requisição GET para API."""
        try:
            url = f"{self.base_url}{endpoint}"
            logger.debug(f"🔍 GET {url}")
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"❌ Erro GET {endpoint}: {e}")
            raise

    async def post(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Faz requisição POST para API."""
        try:
            url = f"{self.base_url}{endpoint}"
            logger.debug(f"📤 POST {url}")
            response = await self.client.post(url, json=data or {})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"❌ Erro POST {endpoint}: {e}")
            raise

    # ===========================================
    # ENDPOINTS QUE EXISTEM NO BACKEND
    # ===========================================

    async def calculate_eto(
        self, location_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calcula ETo para localização específica.
        Backend: POST /internal/eto/calculate
        """
        return await self.post("/internal/eto/calculate", location_data)

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Verifica status de uma tarefa de cálculo.
        Backend: GET /internal/eto/status/{task_id}
        """
        return await self.get(f"/internal/eto/status/{task_id}")

    async def get_climate_sources(self) -> Dict[str, Any]:
        """
        Busca fontes de dados climáticos disponíveis.
        Backend: GET /climate/sources
        """
        return await self.get("/climate/sources")

    async def health_check(self) -> Dict[str, Any]:
        """
        Verifica saúde da aplicação.
        Backend: GET /health
        """
        return await self.get("/health")

    async def health_detailed(self) -> Dict[str, Any]:
        """
        Verifica saúde detalhada (Redis, DB, APIs).
        Backend: GET /health/detailed
        """
        return await self.get("/health/detailed")

    async def increment_visitor(self) -> Dict[str, Any]:
        """
        Incrementa contador de visitantes.
        Backend: POST /visitors/increment
        """
        return await self.post("/visitors/increment")

    async def get_visitor_stats(self) -> Dict[str, Any]:
        """
        Busca estatísticas de visitantes.
        Backend: GET /visitors/stats
        """
        return await self.get("/visitors/stats")

    async def track_geolocation(
        self, location_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Registra geolocalização do usuário.
        Backend: POST /geolocation/track
        """
        return await self.post("/geolocation/track", location_data)


# ===========================================
# FUNÇÕES UTILITÁRIAS PARA CALLBACKS
# ===========================================


async def fetch_eto_calculation(
    location_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Função utilitária para calcular ETo nos callbacks."""
    async with APIClient() as client:
        return await client.calculate_eto(location_data)

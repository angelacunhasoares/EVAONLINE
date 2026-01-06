"""
ETo Calculation Routes
"""

import time
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from loguru import logger

from backend.database.connection import get_db
from backend.database.models.user_favorites import UserFavorites

# Importar 5 módulos de clima
from backend.api.services.climate_validation import ClimateValidationService
from backend.api.services.climate_source_availability import (
    OperationMode,
)
from backend.api.services.climate_source_manager import ClimateSourceManager

# Importar task Celery para cálculos assíncronos
from backend.infrastructure.celery.tasks.eto_calculation import (
    calculate_eto_task,
)

# Mapeamento de period_type para OperationMode
# Centraliza conversão de strings antigas para novo enum
OPERATION_MODE_MAPPING = {
    "historical_email": OperationMode.HISTORICAL_EMAIL,
    "dashboard_current": OperationMode.DASHBOARD_CURRENT,
    "dashboard_forecast": OperationMode.DASHBOARD_FORECAST,
}

eto_router = APIRouter(prefix="/internal/eto", tags=["ETo"])


# ============================================================================
# SCHEMAS
# ============================================================================


class EToCalculationRequest(BaseModel):
    """Request para cálculo ETo."""

    lat: float
    lng: float
    start_date: str
    end_date: str
    sources: Optional[str] = "auto"
    period_type: Optional[str] = "dashboard"  # historical, dashboard, forecast
    elevation: Optional[float] = None
    estado: Optional[str] = None
    cidade: Optional[str] = None
    email: Optional[str] = (
        None  # Email para notificações (modo historical_email)
    )
    visitor_id: Optional[str] = None  # ID único do visitante
    session_id: Optional[str] = None  # ID da sessão
    file_format: Optional[str] = "excel"  # excel ou csv


class LocationInfoRequest(BaseModel):
    """Request para informações de localização."""

    lat: float
    lng: float


class FavoriteRequest(BaseModel):
    """Request para favoritos."""

    user_id: str = "default"
    name: str
    lat: float
    lng: float
    cidade: Optional[str] = None
    estado: Optional[str] = None


# ============================================================================
# ENDPOINTS ESSENCIAIS (5)
# ============================================================================


@eto_router.post("/calculate")
async def calculate_eto(
    request: EToCalculationRequest,
    db: Session = Depends(get_db),  # type: ignore[arg-type] # noqa: B008
) -> Dict[str, Any]:
    """
    🚀 Cálculo ETo assíncrono com progresso em tempo real.

    Inicia tarefa Celery e retorna task_id para monitoramento via WebSocket.

    Suporta:
    - Múltiplas fontes de dados
    - Auto-detecção de melhor fonte
    - Fusão de dados (Kalman)
    - Cache automático
    - Progresso em tempo real via WebSocket

    Modos de operação (period_type):
    - historical_email: 1-90 dias (apenas NASA POWER e OpenMeteo Archive)
    - dashboard_current: 7-30 dias (todas as APIs disponíveis)
    - dashboard_forecast: hoje até hoje+5d (apenas APIs de previsão)

    Resposta:
    {
        "status": "accepted",
        "task_id": "abc-123-def",
        "websocket_url": "/ws/task_status/abc-123-def",
        "message": "Cálculo iniciado. Use WebSocket para progresso.",
        "estimated_duration_seconds": "5-30"
    }

    Monitore progresso: WebSocket /ws/task_status/{task_id}
    """
    try:
        # 0. Normalizar period_type para OperationMode
        period_type_str = (request.period_type or "dashboard_current").lower()

        # Usar mapeamento centralizado
        operation_mode = OPERATION_MODE_MAPPING.get(
            period_type_str, OperationMode.DASHBOARD_CURRENT
        )

        # 1. Usar ClimateValidationService (agora aceita "auto")
        validator = ClimateValidationService()

        # Determine source for validation (use "auto" if not specified)
        source_to_validate = request.sources if request.sources else "auto"

        is_valid, validation_result = validator.validate_all(
            lat=request.lat,
            lon=request.lng,
            start_date=request.start_date,
            end_date=request.end_date,
            variables=["et0_fao_evapotranspiration"],
            source=source_to_validate,
            mode=operation_mode.value,
        )

        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Validação falhou: "
                    f"{validation_result.get('errors', {})}"
                ),
            )

        # 2. Usar ClimateSourceManager para seleção
        manager = ClimateSourceManager()

        if request.sources == "auto" or not request.sources:
            # Auto-seleção: obter TODAS as fontes compatíveis para fusão
            compatible_sources = manager.get_available_sources_by_mode(
                lat=request.lat,
                lon=request.lng,
                mode=operation_mode,
            )

            if not compatible_sources:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Nenhuma fonte disponível para modo "
                        f"{operation_mode.value} na localização fornecida"
                    ),
                )

            # Usar TODAS as fontes disponíveis para fusão Kalman
            selected_sources = compatible_sources
            logger.info(
                f"Auto-seleção (fusão): {operation_mode.value} em "
                f"({request.lat}, {request.lng}) → {selected_sources} "
                f"(opções: {compatible_sources})"
            )
        else:
            # Fonte especificada: verificar se é compatível
            specified_source = request.sources
            compatible_sources = manager.get_available_sources_by_mode(
                lat=request.lat,
                lon=request.lng,
                mode=operation_mode,
            )

            if specified_source not in compatible_sources:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Fonte '{specified_source}' incompatível com modo "
                        f"{operation_mode.value}. Fontes válidas: "
                        f"{compatible_sources}"
                    ),
                )

            # Usar apenas a fonte especificada (sem fusão)
            selected_sources = [specified_source]
            logger.info(f"Fonte especificada: {specified_source}")

        # 4. Obter elevação (se não fornecida)
        elevation = request.elevation
        if elevation is None:
            logger.info(
                f"Elevação não fornecida para ({request.lat}, {request.lng}), "
                f"será obtida via API"
            )

        # 5. Iniciar cálculo ETo assíncrono (Celery task)
        # Em vez de processar sincronamente, delegar para worker
        task = calculate_eto_task.delay(  # type: ignore[attr-defined]
            lat=request.lat,
            lon=request.lng,
            start_date=request.start_date,
            end_date=request.end_date,
            sources=selected_sources,  # Lista de fontes (uma ou várias)
            elevation=elevation,
            mode=operation_mode.value,  # String do modo
            email=request.email,  # Email para notificações
            visitor_id=request.visitor_id,  # ID único do visitante
            session_id=request.session_id,  # ID da sessão
            file_format=request.file_format,  # Formato: excel ou csv
        )

        task_id = task.id
        logger.info(
            f"✅ Task ETo iniciada: {task_id} para "
            f"({request.lat}, {request.lng}) - Fontes: {selected_sources}"
        )

        # 6. Retornar task_id para monitoramento via WebSocket
        return {
            "status": "accepted",
            "task_id": task_id,
            "message": (
                "Cálculo ETo iniciado. Use WebSocket "
                "para acompanhar progresso."
            ),
            "websocket_url": f"/ws/task_status/{task_id}",
            "sources": selected_sources,
            "operation_mode": operation_mode.value,
            "location": {
                "lat": request.lat,
                "lng": request.lng,
                "elevation_m": elevation,
            },
            "estimated_duration_seconds": "5-30",
            # Estimativa baseada no período
        }

    except HTTPException:
        # Re-raise HTTPException to preserve status code (400, 404, etc)
        raise
    except ValueError as ve:
        raise HTTPException(
            status_code=400, detail=f"Formato de data inválido: {str(ve)}"
        )
    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"ETo calculation failed: {str(e)}"
        )


@eto_router.post("/location-info")
async def get_location_info(request: LocationInfoRequest) -> Dict[str, Any]:
    """
    ✅ Informações de localização (timezone, elevação).
    """
    try:
        # TODO: Implementar busca real de timezone e elevação
        # Por enquanto, retorna estrutura básica
        return {
            "status": "success",
            "location": {
                "lat": request.lat,
                "lng": request.lng,
                "timezone": "America/Sao_Paulo",  # Placeholder
                "elevation_m": None,  # Placeholder
            },
            "timestamp": time.time(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get location info: {str(e)}"
        )


@eto_router.post("/favorites/add")
async def add_favorite(
    request: FavoriteRequest,
    db: Session = Depends(get_db),  # type: ignore[arg-type] # noqa: B008
) -> Dict[str, Any]:
    """
    ✅ Adicionar favorito.
    """
    try:
        # Verificar duplicata
        existing = (
            db.query(UserFavorites)
            .filter_by(
                user_id=request.user_id, lat=request.lat, lng=request.lng
            )
            .first()
        )

        if existing:
            return {
                "status": "exists",
                "message": "Favorito já existe",
                "favorite_id": existing.id,
            }

        # Criar novo favorito
        favorite = UserFavorites(
            user_id=request.user_id,
            name=request.name,
            lat=request.lat,
            lng=request.lng,
            cidade=request.cidade,
            estado=request.estado,
        )
        db.add(favorite)
        db.commit()
        db.refresh(favorite)

        return {
            "status": "success",
            "message": "Favorito adicionado",
            "favorite_id": favorite.id,
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to add favorite: {str(e)}"
        )


@eto_router.get("/favorites/list")
async def list_favorites(
    user_id: str = "default",
    db: Session = Depends(get_db),  # type: ignore[arg-type] # noqa: B008
) -> Dict[str, Any]:
    """
    ✅ Listar favoritos do usuário.
    """
    try:
        favorites = (
            db.query(UserFavorites)
            .filter_by(user_id=user_id)
            .order_by(UserFavorites.created_at.desc())
            .all()
        )

        return {
            "status": "success",
            "total": len(favorites),
            "favorites": [
                {
                    "id": f.id,
                    "name": f.name,
                    "lat": f.lat,
                    "lng": f.lng,
                    "cidade": f.cidade,
                    "estado": f.estado,
                    "created_at": f.created_at.isoformat(),
                }
                for f in favorites
            ],
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list favorites: {str(e)}"
        )


@eto_router.delete("/favorites/remove/{favorite_id}")
async def remove_favorite(
    favorite_id: int,
    user_id: str = "default",
    db: Session = Depends(get_db),  # type: ignore[arg-type] # noqa: B008
) -> Dict[str, Any]:
    """
    ✅ Remover favorito.
    """
    try:
        favorite = (
            db.query(UserFavorites)
            .filter_by(id=favorite_id, user_id=user_id)
            .first()
        )

        if not favorite:
            raise HTTPException(
                status_code=404, detail="Favorito não encontrado"
            )

        db.delete(favorite)
        db.commit()

        return {
            "status": "success",
            "message": "Favorito removido",
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to remove favorite: {str(e)}"
        )

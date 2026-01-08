"""
Task Celery para cálculo ETo com progresso em tempo real.

Integra:
- ClimateSourceManager: Seleção de fontes por localização
- EToProcessingService: Pipeline completo de ETo
- WebSocket: Broadcasting de progresso
"""

from celery.utils.log import get_task_logger
from datetime import datetime
from typing import Any

logger = get_task_logger(__name__)

# Importar celery_app para garantir conexão correta
from backend.infrastructure.celery.celery_config import celery_app


@celery_app.task(
    bind=True,
    name="backend.infrastructure.celery.tasks.calculate_eto_task",
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,  # Max 10 minutos entre retries
    retry_jitter=True,
    ignore_result=False,  # Garantir que resultado seja salvo no Redis
    track_started=True,  # Track status STARTED
)
def calculate_eto_task(
    self,
    lat: float,
    lon: float,
    start_date: str,
    end_date: str,
    sources: list[str] | None = None,
    elevation: float | None = None,
    mode: str | None = None,
    email: str | None = None,
    visitor_id: str | None = None,
    session_id: str | None = None,
    file_format: str = "excel",
    enable_fusion: bool = False,  # 🔀 Flag para fusão Kalman
) -> dict[str, Any]:
    """
    Calcula ETo para localização com progresso em tempo real.

    Args:
        self: Contexto Celery (bind=True)
        lat, lon: Coordenadas
        start_date, end_date: Período (YYYY-MM-DD)
        sources: Fontes climáticas (None = auto-select)
        elevation: Elevação em metros (None = buscar via OpenTopo)
        mode: Modo de operação (None = auto-detect)
        enable_fusion: Se True, aplica fusão Kalman (Smart Fusion)

    Returns:
        Dict com resultado completo:
        {
            "summary": {...},
            "et0_series": [...],
            "quality_metrics": {...},
            "sources_used": [...],
            "task_id": "abc-123",
            "processing_time_seconds": 12.5
        }

    Raises:
        ValidationError: Se parâmetros inválidos
        APIError: Se todas as fontes falharem
    """
    import asyncio
    from backend.core.eto_calculation.eto_services import EToProcessingService
    from backend.api.services.climate_validation import (
        ClimateValidationService,
    )
    from backend.api.services.climate_source_manager import (
        ClimateSourceManager,
    )
    from backend.api.services.climate_source_availability import (
        OperationMode,
    )

    task_id = self.request.id
    start_time = datetime.now()

    try:
        # ========== STEP 0: EMAIL INICIAL (modo historical_email) ==========
        if mode and "email" in mode.lower() and email:
            from backend.core.utils.email_utils import (
                send_html_email,
                validate_email,
            )
            from backend.core.utils.email_templates import (
                create_processing_started_email,
            )

            if validate_email(email):
                # Criar email HTML profissional (estilo INMET/BDMEP)
                subject, html_body = create_processing_started_email(
                    task_id=task_id,
                    latitude=lat,
                    longitude=lon,
                    start_date=start_date,
                    end_date=end_date,
                    started_at=start_time,
                    file_format=file_format,
                )

                send_html_email(
                    to=email,
                    subject=subject,
                    html_body=html_body,
                )
                logger.info(f"📧 Email inicial HTML enviado para {email}")

        # ========== STEP 1: VALIDAÇÃO (5%) ==========
        logger.info(f"⏳ [5%] Validando parâmetros...")

        # Validar coordenadas
        if not ClimateValidationService.validate_coordinates(lat, lon)[0]:
            raise ValueError(f"Coordenadas inválidas: ({lat}, {lon})")

        # Converter datas
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        # Auto-detectar modo se não fornecido
        if mode is None:
            detected_mode, error = (
                ClimateValidationService.detect_mode_from_dates(
                    start_date, end_date
                )
            )
            if detected_mode:
                mode = detected_mode
                logger.info(f"✅ Modo auto-detectado: {mode}")
            else:
                mode = OperationMode.DASHBOARD_CURRENT.value
                logger.warning(f"⚠️  Modo não detectado, usando padrão: {mode}")

        logger.info(
            f"📍 Task {task_id}: ETo para ({lat}, {lon}) "
            f"de {start_date} a {end_date} - Modo: {mode}"
        )

        # ========== STEP 2: SELEÇÃO DE FONTES (10%) ==========
        logger.info("[10%] Selecionando melhores fontes climáticas...")

        manager = ClimateSourceManager()
        source_info = manager.get_sources_for_data_download(
            lat=lat,
            lon=lon,
            start_date=start_dt,
            end_date=end_dt,
            mode=mode,
            preferred_sources=sources,
        )

        selected_sources = source_info["sources"]
        region = source_info["location_info"]["region"]

        logger.info(
            f"🔍 Fontes selecionadas para {region}: {selected_sources}"
        )

        # ========== STEP 3: PROCESSAMENTO ETo (20-90%) ==========
        logger.info(
            f"[20%] Processando dados de {len(selected_sources)} fontes "
            f"({region})..."
        )

        # Inicializar serviço de processamento
        service = EToProcessingService()

        # ========== STEP 4: CÁLCULO ETo (60-90%) ==========
        logger.info("[60%] Calculando ETo (FAO-56 Penman-Monteith)...")

        # O process_location já faz download + processamento completo
        result = asyncio.run(
            service.process_location(
                latitude=lat,
                longitude=lon,
                start_date=start_date,
                end_date=end_date,
                sources=selected_sources,
                elevation=elevation,
                enable_fusion=enable_fusion,  # 🔀 Passar flag de fusão
            )
        )

        # ========== STEP 5: SALVAR NO BANCO (80-90%) ==========
        logger.info("[80%] Salvando dados no banco...")

        # Salvar dados climáticos com ETo no banco
        from backend.database.data_storage import save_climate_data
        from backend.database.connection import get_db

        try:
            db = next(get_db())
            # Preparar dados para salvar
            climate_records = []
            if "et0_series" in result:
                for record in result["et0_series"]:
                    climate_records.append(
                        {
                            "latitude": lat,
                            "longitude": lon,
                            "elevation": result.get("elevation", {}).get(
                                "value", elevation
                            ),
                            "date": record.get("date"),
                            "raw_data": record,
                            "eto_mm_day": record.get("et0_mm_day"),
                            "eto_method": "penman_monteith_fao56",
                        }
                    )

            if climate_records:
                saved_count = save_climate_data(
                    data=climate_records,
                    source_api=(
                        selected_sources[0] if selected_sources else "fusion"
                    ),
                )
                logger.info(f"💾 Salvos {saved_count} registros no banco")
        except Exception as save_error:
            logger.warning(f"⚠️ Erro ao salvar no banco: {save_error}")
        finally:
            db.close()

        # ========== STEP 6: ENVIO DE EMAIL (modo historical_email) ==========
        email_sent = False
        if mode and "email" in mode.lower() and email:
            logger.info("[90%] Gerando arquivo e enviando por email...")

            try:
                import pandas as pd
                from pathlib import Path
                from backend.core.utils.email_utils import (
                    send_html_email_with_attachment,
                    validate_email,
                )
                from backend.core.utils.email_templates import (
                    create_data_ready_email,
                )

                # Validar email fornecido
                if not validate_email(email):
                    logger.warning(f"⚠️ Email inválido: {email}")
                else:
                    # Usar visitor_id ou session_id existente, ou gerar novo
                    if visitor_id:
                        user_identifier = visitor_id.replace("visitor_", "")[
                            :8
                        ]
                    elif session_id:
                        user_identifier = session_id.replace("sess_", "")[:8]
                    else:
                        # Fallback: gerar ID baseado no email
                        import hashlib

                        user_identifier = hashlib.md5(
                            email.encode()
                        ).hexdigest()[:8]

                    logger.info(
                        f"📋 ID usuário: {user_identifier} "
                        f"(visitor: {bool(visitor_id)}, "
                        f"session: {bool(session_id)})"
                    )

                    # Determinar extensão do arquivo
                    file_ext = "xlsx" if file_format == "excel" else "csv"

                    # Gerar arquivo no formato escolhido
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    lat_str = f"{abs(lat):.4f}{'N' if lat >= 0 else 'S'}"
                    lon_str = f"{abs(lon):.4f}{'E' if lon >= 0 else 'W'}"
                    filename = (
                        f"EVAonline_ETo_{user_identifier}_{lat_str}_"
                        f"{lon_str}_{start_date}_{end_date}_{timestamp}.{file_ext}"
                    )

                    # Criar diretório temporário se não existir
                    temp_dir = Path("temp")
                    temp_dir.mkdir(exist_ok=True)
                    file_path = temp_dir / filename

                    # Converter et0_series para DataFrame
                    et0_series = result.get("et0_series", [])
                    df_result = pd.DataFrame(et0_series)

                    # Salvar no formato escolhido
                    if not df_result.empty:
                        if file_format == "excel":
                            df_result.to_excel(file_path, index=False)
                        else:
                            df_result.to_csv(file_path, index=False)
                        logger.info(
                            f"📊 Arquivo {file_format.upper()} gerado: "
                            f"{file_path}"
                        )

                        # Calcular tempo de processamento
                        processing_time = (
                            datetime.now() - start_time
                        ).total_seconds()

                        # Calcular estatísticas resumidas
                        eto_values = [
                            r.get("et0_mm_day", 0)
                            for r in et0_series
                            if r.get("et0_mm_day") is not None
                        ]
                        summary_stats = None
                        if eto_values:
                            summary_stats = {
                                "eto_mean": sum(eto_values) / len(eto_values),
                                "eto_max": max(eto_values),
                                "eto_min": min(eto_values),
                                "eto_total": sum(eto_values),
                            }

                        # Criar email HTML profissional
                        subject, html_body = create_data_ready_email(
                            task_id=task_id,
                            latitude=lat,
                            longitude=lon,
                            start_date=start_date,
                            end_date=end_date,
                            days_processed=len(et0_series),
                            processing_time_seconds=processing_time,
                            sources_used=selected_sources,
                            file_format=file_format,
                            elevation=result.get("elevation", {}).get("value"),
                            summary_stats=summary_stats,
                        )

                        # Enviar email HTML com anexo
                        email_sent = send_html_email_with_attachment(
                            to=email,
                            subject=subject,
                            html_body=html_body,
                            attachment_path=str(file_path),
                        )

                        if email_sent:
                            logger.info(
                                f"✅ Email HTML com anexo enviado para {email}"
                            )
                        else:
                            logger.warning(
                                f"⚠️ Falha ao enviar email para {email}"
                            )

                        # Limpar arquivo temporário após envio bem-sucedido
                        # (mantém por segurança caso precise reenviar)
                    else:
                        logger.warning("⚠️ Nenhum dado para enviar")

            except Exception as email_error:
                logger.error(
                    f"❌ Erro ao gerar arquivo/enviar email: {email_error}",
                    exc_info=True,
                )

        # ========== STEP 7: FINALIZAÇÃO (95-100%) ==========
        logger.info("[95%] Preparando resultado final...")

        processing_time = (datetime.now() - start_time).total_seconds()

        final_result = {
            **result,  # Usar todo o resultado do service
            "task_id": task_id,
            "processing_time_seconds": round(processing_time, 2),
            "mode": mode,
            "email_sent": email_sent,  # Indicar se email foi enviado
        }

        logger.info(
            f"✅ [100%] Task {task_id} completed in {processing_time:.2f}s "
            f"for ({lat}, {lon})"
        )

        return final_result

    except Exception as e:
        logger.error(f"❌ Task {task_id} failed: {e}", exc_info=True)

        # Enviar email de erro se possível
        if mode and "email" in mode.lower() and email:
            try:
                from backend.core.utils.email_utils import (
                    send_html_email,
                    validate_email,
                )
                from backend.core.utils.email_templates import (
                    create_processing_error_email,
                )

                if validate_email(email):
                    subject, html_body = create_processing_error_email(
                        task_id=task_id,
                        latitude=lat,
                        longitude=lon,
                        start_date=start_date,
                        end_date=end_date,
                        error_message=str(e),
                    )
                    send_html_email(
                        to=email, subject=subject, html_body=html_body
                    )
                    logger.info(f"📧 Email de erro enviado para {email}")
            except Exception as email_err:
                logger.error(f"Falha ao enviar email de erro: {email_err}")

        # Retry automático (max 3 tentativas)
        raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))

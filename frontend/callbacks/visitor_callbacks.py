"""
Callbacks para contador de visitantes em tempo real.

Fluxo:
1. update_visitor_counter: Atualiza display no footer a cada 10 segundos
2. increment_visitor_on_page_load: Incrementa na primeira visita da sessão
3. translate_visitor_labels: Traduz labels quando idioma muda

Integração Backend:
- POST /visitors/increment → VisitorCounterService.increment_visitor()
- GET  /visitors/stats    → VisitorCounterService.get_stats()

Stores usados:
- visitor-counter-interval (base_layout.py): Interval de 10s
- app-session-id (base_layout.py): Session ID único por aba
- language-store (base_layout.py): Idioma atual

IDs de Output (footer.py):
- visitor-count: Total de visitantes
- visitor-count-hourly: Visitantes na última hora
- visitor-label: Label "Visitors:" / "Visitantes:"
- visitor-hourly-label: Label "Last hour:" / "Última hora:"
"""

import logging

import requests
from dash import Input, Output, State, callback, no_update

from config.settings.app_config import get_legacy_settings
from shared_utils.get_translations import t

logger = logging.getLogger(__name__)

# URL da API backend (configurável para produção/Docker)
try:
    _settings = get_legacy_settings()
    _port = getattr(_settings, "api", {}).get("PORT", 8000)
    _prefix = getattr(_settings, "API_V1_PREFIX", "/api/v1")
    API_BASE_URL = f"http://localhost:{_port}{_prefix}"
    logger.info(f"🔗 Visitor API URL: {API_BASE_URL}")
except Exception:
    API_BASE_URL = "http://localhost:8000/api/v1"
    logger.warning(f"⚠️ Usando API_BASE_URL fallback: {API_BASE_URL}")


# ============================================================================
# CALLBACK 1: Atualizar display do contador (a cada 10 segundos)
# ============================================================================
@callback(
    [
        Output("visitor-count", "children"),
        Output("visitor-count-hourly", "children"),
    ],
    Input("visitor-counter-interval", "n_intervals"),
)
def update_visitor_counter(n_intervals):
    """
    Atualiza o contador de visitantes no footer a cada intervalo.

    Chamado pelo dcc.Interval configurado em base_layout.py (10s).
    Consulta GET /visitors/stats para obter contagem atual.
    """
    try:
        response = requests.get(f"{API_BASE_URL}/visitors/stats", timeout=3)

        if response.status_code == 200:
            data = response.json()
            total = data.get("total_visitors", 0)
            hourly = data.get("current_hour_visitors", 0)

            if n_intervals and n_intervals % 30 == 0:
                logger.info(
                    f"📊 Visitantes: {total} total, {hourly} última hora"
                )

            return f"{total:,}", f"{hourly:,}"

        logger.warning(f"API retornou status {response.status_code}")
        return no_update, no_update

    except requests.exceptions.Timeout:
        logger.debug("⏱️ Timeout ao buscar estatísticas de visitantes")
        return no_update, no_update
    except requests.exceptions.ConnectionError:
        if not n_intervals or n_intervals <= 1:
            logger.warning("🔌 Backend não disponível para visitor stats")
        return "offline", "offline"
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar contador: {e}")
        return no_update, no_update


# ============================================================================
# CALLBACK 2: Incrementar visitante (uma vez por sessão)
# ============================================================================
@callback(
    Output("visitor-counter-interval", "n_intervals", allow_duplicate=True),
    Input("url", "pathname"),
    State("app-session-id", "data"),
    prevent_initial_call=True,
)
def increment_visitor_on_page_load(pathname, session_id):
    """
    Incrementa o contador quando usuário acessa a página principal.

    Só incrementa na "/". Backend deduplica por session_id.
    """
    if pathname not in ("/", None):
        return no_update

    try:
        payload = {}
        if session_id:
            payload["session_id"] = session_id

        response = requests.post(
            f"{API_BASE_URL}/visitors/increment",
            json=payload,
            timeout=3,
        )

        if response.status_code == 200:
            data = response.json()
            is_new = data.get("is_new_visitor", True)
            total = data.get("total_visitors", "?")
            sid_display = session_id[:16] if session_id else "N/A"

            if is_new:
                logger.info(
                    f"👤 Novo visitante: total={total}"
                    f" (sessão: {sid_display}...)"
                )
            else:
                logger.debug(
                    f"👤 Visitante recorrente: total={total}"
                    f" (sessão: {sid_display}...)"
                )
        else:
            logger.warning(
                f"⚠️ Falha ao registrar visitante:"
                f" status {response.status_code}"
            )

    except requests.exceptions.ConnectionError:
        logger.debug("🔌 Backend não disponível para increment visitor")
    except Exception as e:
        logger.debug(f"Erro ao registrar visitante: {e}")

    return no_update


# ============================================================================
# CALLBACK 3: Tradução dos labels do visitor counter
# ============================================================================
@callback(
    [
        Output("visitor-label", "children"),
        Output("visitor-hourly-label", "children"),
    ],
    Input("language-store", "data"),
)
def translate_visitor_labels(lang):
    """Traduz labels do contador de visitantes quando idioma muda."""
    if not lang:
        lang = "en"

    visitors_text = t(lang, "footer", "visitors", default="Visitors")
    last_hour_text = t(lang, "footer", "last_hour", default="Last hour")

    return (
        f"{visitors_text}: ",
        f" | {last_hour_text}: ",
    )


logger.info("✅ Callbacks de contador de visitantes registrados")

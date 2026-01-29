"""
Callbacks para página ETo.

Integração com 6 fontes climáticas do backend:
- Open-Meteo Archive: Histórico (1990 → hoje-2d)
- Open-Meteo Forecast: Previsão/Recent (hoje-29d → hoje+5d)
- NASA POWER: Histórico global (1990 → hoje-2d)
- MET Norway: Previsão global (hoje → hoje+5d)
- NWS Forecast: Previsão USA (hoje → hoje+5d)
- NWS Stations: Observações USA (hoje-2d → hoje)

Validações (api_limits.py):
- Histórico: 1990-01-01 (padrão EVA), min 1 dia e máx 90 dias
- Real-time: min 7 dias e máx 30 dias
- Forecast: até +5 dias
"""

import logging
from datetime import datetime, timedelta
from urllib.parse import parse_qs

import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dcc, html, no_update

logger = logging.getLogger(__name__)

# Importar OperationModeDetector
from frontend.utils.mode_detector import (
    OperationModeDetector,
    parse_date_from_ui,
)

# Importar helper do backend para fontes disponíveis
try:
    from backend.api.services.climate_source_selector import (
        get_available_sources_for_frontend,
    )
except ImportError:
    logger.warning(
        "⚠️ Não foi possível importar get_available_sources_for_frontend"
    )
    get_available_sources_for_frontend = None


def decimal_to_dms(decimal_coord, is_latitude=True):
    """
    Converte coordenada decimal para formato DMS (Degrees-Minutes-Seconds).

    Args:
        decimal_coord: Coordenada em decimal (-90 a 90 para lat, -180 a 180 para lon)
        is_latitude: True se for latitude, False se for longitude

    Returns:
        String formatada: "45°30'15.25"N" ou "120°15'30.50"W"
    """
    direction = ""
    if is_latitude:
        direction = "N" if decimal_coord >= 0 else "S"
    else:
        direction = "E" if decimal_coord >= 0 else "W"

    abs_coord = abs(decimal_coord)
    degrees = int(abs_coord)
    minutes = int((abs_coord - degrees) * 60)
    seconds = ((abs_coord - degrees) * 60 - minutes) * 60

    return f"{degrees}°{minutes}'{seconds:.2f}\"{direction}"


@callback(
    [
        Output("location-display", "children"),
        Output("parsed-coordinates", "data"),
    ],
    Input("navigation-coordinates", "data"),
)
def update_location_from_store(coords_data):
    """
    Atualiza exibição da localização com coordenadas do Store GLOBAL.

    Recebe: {"lat": float, "lon": float} do sessionStorage
    """
    # Log para debug
    logger.info(
        f"🔍 update_location_from_store chamado com coords_data: {coords_data}"
    )

    if not coords_data:
        logger.warning("⚠️ coords_data está vazio")
        return (
            html.Div(
                [
                    html.I(
                        className="bi bi-exclamation-circle me-2",
                        style={"color": "#856404"},
                    ),
                    html.Span(
                        "Nenhuma localização selecionada. ",
                        style={"color": "#856404"},
                    ),
                    dbc.Button(
                        [
                            html.I(className="bi bi-arrow-left me-2"),
                            "Voltar ao mapa",
                        ],
                        href="/",
                        color="warning",
                        size="sm",
                        outline=True,
                        className="ms-2",
                    ),
                ],
                className="d-flex align-items-center",
            ),
            None,
        )

    try:
        lat = coords_data.get("lat")
        lon = coords_data.get("lon")

        logger.info(f"🎯 lat={lat}, lon={lon}")

        if lat and lon:
            lat_f = float(lat)
            lon_f = float(lon)

            logger.info(f"✅ Coordenadas válidas: {lat_f}, {lon_f}")

            # Converter para DMS usando helper
            lat_dms = decimal_to_dms(lat_f, is_latitude=True)
            lon_dms = decimal_to_dms(lon_f, is_latitude=False)

            display = html.Div(
                [
                    html.Div(
                        [
                            html.I(
                                className="bi bi-geo-alt-fill me-2",
                                style={"fontSize": "1.2rem"},
                            ),
                            html.Div(
                                [
                                    html.Strong(
                                        "Coordenadas Selecionadas:",
                                        className="d-block",
                                    ),
                                    html.Span(
                                        f"Lat: {lat_dms} | Lon: {lon_dms}",
                                        className="d-block text-muted small",
                                    ),
                                    html.Span(
                                        f"Decimal: {lat_f:.6f}, {lon_f:.6f}",
                                        className="text-muted small",
                                    ),
                                ],
                                className="flex-grow-1",
                            ),
                        ],
                        className="d-flex align-items-start",
                    ),
                    dbc.Button(
                        [html.I(className="bi bi-pencil me-2"), "Alterar"],
                        href="/",
                        color="secondary",
                        size="sm",
                        outline=True,
                        className="ms-auto",
                    ),
                ],
                className="d-flex align-items-center justify-content-between w-100",
            )

            # Retornar display E coordenadas no Store
            return display, {"lat": lat_f, "lon": lon_f}
        else:
            logger.warning(
                f"⚠️ Coordenadas ausentes ou inválidas: lat={lat}, lon={lon}"
            )
            return (
                html.Div(
                    [
                        html.I(
                            className="bi bi-exclamation-circle me-2",
                            style={"color": "#856404"},
                        ),
                        html.Span(
                            "Coordenadas não encontradas na URL. ",
                            style={"color": "#856404"},
                        ),
                        dbc.Button(
                            [
                                html.I(className="bi bi-arrow-left me-2"),
                                "Voltar ao mapa",
                            ],
                            href="/",
                            color="warning",
                            size="sm",
                            outline=True,
                            className="ms-2",
                        ),
                    ],
                    className="d-flex align-items-center",
                ),
                None,
            )

    except Exception as e:
        logger.error(f"❌ Erro ao parsear URL params: {e}", exc_info=True)
        return (
            html.Div(
                [
                    html.I(
                        className="bi bi-exclamation-triangle me-2",
                        style={"color": "#721c24"},
                    ),
                    html.Span(
                        f"Erro ao processar coordenadas: {str(e)}",
                        style={"color": "#721c24"},
                    ),
                    dbc.Button(
                        [
                            html.I(className="bi bi-arrow-left me-2"),
                            "Voltar ao mapa",
                        ],
                        href="/",
                        color="danger",
                        size="sm",
                        outline=True,
                        className="ms-2",
                    ),
                ],
                className="d-flex align-items-center",
            ),
            None,
        )


@callback(
    Output("location-input-container", "children"),
    [
        Input("location-mode-radio", "value"),
        Input("url", "search"),
    ],
)
def render_location_input(mode, search):
    """
    Renderiza interface de entrada de coordenadas baseado no modo selecionado.

    - map: Exibe coordenadas recebidas via URL (ou alerta se não houver)
    - manual: Campos de entrada para lat/lon + botão validar
    """
    if mode == "map":
        # Modo mapa: mostra coordenadas da URL ou alerta
        if not search:
            return dbc.Alert(
                [
                    html.I(className="bi bi-info-circle me-2"),
                    html.Span(
                        "Clique no mapa da página inicial para selecionar uma localização."
                    ),
                ],
                color="info",
                className="mb-0",
            )

        # Parse URL params
        try:
            params = parse_qs(search.lstrip("?"))
            lat = float(params.get("lat", [None])[0])
            lon = float(params.get("lon", [None])[0])

            # Converter para DMS
            lat_dms = decimal_to_dms(lat, is_latitude=True)
            lon_dms = decimal_to_dms(lon, is_latitude=False)

            return html.Div(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Strong("Latitude:"),
                                    html.Br(),
                                    html.Span(f"{lat_dms} ({lat:.6f}°)"),
                                ],
                                width=6,
                            ),
                            dbc.Col(
                                [
                                    html.Strong("Longitude:"),
                                    html.Br(),
                                    html.Span(f"{lon_dms} ({lon:.6f}°)"),
                                ],
                                width=6,
                            ),
                        ],
                        className="mb-3",
                    ),
                    dbc.Button(
                        [
                            html.I(className="bi bi-arrow-left me-2"),
                            "Alterar no Mapa",
                        ],
                        href="/",
                        color="primary",
                        size="sm",
                        outline=True,
                    ),
                ],
            )
        except (ValueError, TypeError, KeyError):
            return dbc.Alert(
                [
                    html.I(className="bi bi-exclamation-triangle me-2"),
                    html.Span(
                        "Coordenadas inválidas. Clique no mapa para selecionar uma localização."
                    ),
                    html.Br(),
                    dbc.Button(
                        [
                            html.I(className="bi bi-arrow-left me-2"),
                            "Ir ao Mapa",
                        ],
                        href="/",
                        color="warning",
                        size="sm",
                        outline=True,
                        className="mt-2",
                    ),
                ],
                color="warning",
                className="mb-0",
            )

    else:  # mode == "manual"
        return html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label(
                                    "Latitude (°):",
                                    html_for="manual-lat-input",
                                ),
                                dbc.Input(
                                    id="manual-lat-input",
                                    type="number",
                                    placeholder="-90.0 a 90.0",
                                    min=-90,
                                    max=90,
                                    step=0.000001,
                                    className="mb-2",
                                ),
                                html.Small(
                                    "Valores negativos = Sul",
                                    className="text-muted",
                                ),
                            ],
                            md=6,
                        ),
                        dbc.Col(
                            [
                                dbc.Label(
                                    "Longitude (°):",
                                    html_for="manual-lon-input",
                                ),
                                dbc.Input(
                                    id="manual-lon-input",
                                    type="number",
                                    placeholder="-180.0 a 180.0",
                                    min=-180,
                                    max=180,
                                    step=0.000001,
                                    className="mb-2",
                                ),
                                html.Small(
                                    "Valores negativos = Oeste",
                                    className="text-muted",
                                ),
                            ],
                            md=6,
                        ),
                    ],
                    className="mb-3",
                ),
                dbc.Button(
                    [
                        html.I(className="bi bi-check-circle me-2"),
                        "Validar Coordenadas",
                    ],
                    id="validate-coords-button",
                    color="success",
                    outline=True,
                    className="w-100",
                ),
                html.Div(id="coord-validation-feedback", className="mt-2"),
            ]
        )


@callback(
    Output("fusion-info-card", "children"),
    [
        Input("data-type-radio", "value"),
        Input("navigation-coordinates", "data"),
    ],
    prevent_initial_call=True,
)
def update_fusion_info(data_type, coords_data):
    """
    Atualiza info de fusão automática baseado no modo selecionado.

    🔀 FUSÃO AUTOMÁTICA - Fontes por modo:
    - historical: NASA POWER + Open-Meteo Archive
    - recent: NASA POWER + Open-Meteo Archive + Open-Meteo Forecast
    - forecast: Open-Meteo Forecast + MET Norway (+ NWS se EUA)
    """
    if not data_type:
        return dbc.Alert(
            [
                html.I(className="bi bi-info-circle me-2"),
                "Select a Data Type above to see the data sources.",
            ],
            color="info",
            className="mb-0 small",
        )

    # Verificar se está nos EUA
    in_usa = False
    if coords_data:
        lat = coords_data.get("lat", 0)
        lon = coords_data.get("lon", 0)
        in_usa = -125 <= lon <= -65 and 25 <= lat <= 50

    # Definir fontes por modo
    fusion_sources = {
        "historical": {
            "icon": "📅",
            "label": "Historical Mode",
            "sources": ["NASA POWER", "Open-Meteo Archive"],
            "description": "Data fusion from satellite and reanalysis models (1990-present)",
        },
        "recent": {
            "icon": "📊",
            "label": "Recent Mode",
            "sources": [
                "NASA POWER",
                "Open-Meteo Archive",
                "Open-Meteo Forecast",
            ],
            "description": "Combines historical and forecast data for the best recent coverage",
        },
        "forecast": {
            "icon": "🔮",
            "label": "Forecast Mode",
            "sources": ["Open-Meteo Forecast", "MET Norway"]
            + (["NWS Forecast"] if in_usa else []),
            "description": "Multi-model ensemble forecast (6 days)"
            + (" with NWS for USA" if in_usa else ""),
        },
    }

    config = fusion_sources.get(data_type, fusion_sources["recent"])

    # Criar lista de fontes como badges
    source_badges = [
        dbc.Badge(src, color="light", text_color="dark", className="me-1 mb-1")
        for src in config["sources"]
    ]

    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(
                    [
                        html.Span(config["icon"], className="me-2"),
                        html.Strong(config["label"]),
                    ],
                    className="mb-2",
                ),
                html.Div(source_badges, className="mb-2"),
                html.Small(config["description"], className="text-muted"),
            ],
            className="py-2 px-3",
        ),
        className="border-success",
        style={"borderLeft": "3px solid var(--bs-success)"},
    )


# ============================================================================
# CALLBACKS DE COMPATIBILIDADE (mantidos para não quebrar referências)
# ============================================================================


@callback(
    [
        Output("source-selection-info", "children", allow_duplicate=True),
    ],
    Input("validate-coords-button", "n_clicks"),
    [
        State("manual-lat-input", "value"),
        State("manual-lon-input", "value"),
    ],
    prevent_initial_call=True,
)
def validate_manual_coordinates(n_clicks, lat, lon):
    """
    Valida coordenadas inseridas manualmente.
    SIMPLIFICADO: Não precisa mais popular dropdown de fontes.
    """
    if not n_clicks:
        return [""]

    # Validar entrada básica
    if lat is None or lon is None:
        return [""]

    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        return [""]

    return [""]  # Fusão automática, não precisa popular dropdown


@callback(
    [
        Output("source-selection-info", "children", allow_duplicate=True),
    ],
    Input("parsed-coordinates", "data"),
    prevent_initial_call="initial_duplicate",
)
def populate_sources_from_url(coords_data):
    """
    SIMPLIFICADO: Não precisa mais popular dropdown.
    Fusão é automática.
    """
    return [""]


@callback(
    Output("source-description", "children"),
    Input("data-type-radio", "value"),
)
def update_source_description(data_type):
    """
    SIMPLIFICADO: Fusão automática, não precisa descrição de fonte individual.
    """
    return ""


# ============================================================================
# CALLBACKS REMOVIDOS - Fusão Automática
# ============================================================================
# O callback filter_sources_by_mode foi REMOVIDO.
# A fusão é agora SEMPRE automática baseada no modo selecionado.
# As fontes são determinadas pelo backend em get_available_sources_by_mode()
# ============================================================================


@callback(
    Output("conditional-form", "children"),
    Input("data-type-radio", "value"),
)
def render_conditional_form(data_type):
    """
    Renderiza formulário condicional baseado no tipo de dados.

    - Histórico: date range (1990 → ontem)
    - Atual: últimos N dias (1-7)
    """
    if data_type == "historical":
        return html.Div(
            [
                html.Label(
                    "Período de Análise:",
                    className="fw-bold mb-3",
                    style={"fontSize": "1.1rem"},
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Label("Data Inicial:", className="mb-2"),
                                dcc.DatePickerSingle(
                                    id="start-date-historical",
                                    min_date_allowed=datetime(1990, 1, 1),
                                    max_date_allowed=datetime.now()
                                    - timedelta(days=1),
                                    initial_visible_month=datetime.now()
                                    - timedelta(days=30),
                                    date=datetime.now() - timedelta(days=30),
                                    display_format="DD/MM/YYYY",
                                    placeholder="Selecione a data",
                                    className="w-100",
                                ),
                            ],
                            md=6,
                        ),
                        dbc.Col(
                            [
                                html.Label("Data Final:", className="mb-2"),
                                dcc.DatePickerSingle(
                                    id="end-date-historical",
                                    min_date_allowed=datetime(1990, 1, 1),
                                    max_date_allowed=datetime.now()
                                    - timedelta(days=1),
                                    initial_visible_month=datetime.now(),
                                    date=datetime.now() - timedelta(days=1),
                                    display_format="DD/MM/YYYY",
                                    placeholder="Selecione a data",
                                    className="w-100",
                                ),
                            ],
                            md=6,
                        ),
                    ],
                    className="mb-3",
                ),
                # MANDATORY Email field for historical data
                html.Div(
                    [
                        html.Label(
                            [
                                "E-mail ",
                                html.Span("*", style={"color": "red"}),
                            ],
                            className="mb-2 fw-bold",
                        ),
                        dbc.Input(
                            id="email-historical",
                            type="email",
                            placeholder="seu.email@exemplo.com",
                            className="w-100",
                            required=True,
                        ),
                        dbc.FormFeedback(
                            "Por favor, insira um e-mail valido",
                            type="invalid",
                        ),
                        html.Small(
                            "Obrigatorio para envio de relatorio",
                            className="text-info d-block mt-1",
                        ),
                    ],
                    className="mb-3",
                ),
                # File format selection
                html.Div(
                    [
                        html.Label(
                            "Formato do arquivo",
                            className="mb-2 fw-bold",
                        ),
                        dbc.RadioItems(
                            id="file-format-historical",
                            options=[
                                {
                                    "label": " Excel (.xlsx)",
                                    "value": "excel",
                                },
                                {
                                    "label": " CSV (.csv)",
                                    "value": "csv",
                                },
                            ],
                            value="csv",
                            inline=False,
                            className="mb-2",
                        ),
                        html.Small(
                            "Formato dos dados enviados por email",
                            className="text-muted d-block",
                        ),
                    ],
                    className="mb-3",
                ),
                html.Small(
                    "Dados historicos: 01/01/1990 ate ontem",
                    className="text-muted d-block",
                ),
                html.Small(
                    "Limite: 90 dias por requisicao",
                    className="text-warning d-block",
                ),
                # Hidden field for callback compatibility
                dbc.Input(
                    id="days-current",
                    value="7",
                    type="hidden",
                    style={"display": "none"},
                ),
            ]
        )

    # ========================================================================
    # MODO 2: RECENT
    # ========================================================================
    elif data_type == "recent":
        return html.Div(
            [
                html.Label(
                    "Período de Análise:",
                    className="fw-bold mb-3",
                    style={"fontSize": "1.1rem"},
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Label("Últimos dias:", className="mb-2"),
                                dbc.Select(
                                    id="days-current",
                                    options=[
                                        {
                                            "label": "Últimos 7 dias",
                                            "value": "7",
                                        },
                                        {
                                            "label": "Últimos 14 dias",
                                            "value": "14",
                                        },
                                        {
                                            "label": "Últimos 21 dias",
                                            "value": "21",
                                        },
                                        {
                                            "label": "Últimos 30 dias",
                                            "value": "30",
                                        },
                                    ],
                                    value="7",
                                    className="w-100",
                                ),
                            ],
                            md=6,
                        ),
                    ],
                    className="mb-3",
                ),
                html.Small(
                    "💡 Dados recentes: mínimo 7 dias, máximo 30 dias",
                    className="text-muted",
                ),
                html.Br(),
                html.Small(
                    "📡 Fontes: Open-Meteo Forecast, NASA POWER, "
                    "Open-Meteo Archive",
                    className="text-info",
                ),
                # Hidden fields for callback compatibility
                dbc.Input(
                    id="start-date-historical",
                    type="hidden",
                    style={"display": "none"},
                ),
                dbc.Input(
                    id="end-date-historical",
                    type="hidden",
                    style={"display": "none"},
                ),
                dbc.Input(
                    id="email-historical",
                    type="hidden",
                    style={"display": "none"},
                ),
                dbc.Input(
                    id="file-format-historical",
                    value="excel",
                    type="hidden",
                    style={"display": "none"},
                ),
            ]
        )

    # ========================================================================
    # MODO 3: FORECAST
    # ========================================================================
    else:  # forecast
        return html.Div(
            [
                dbc.Alert(
                    [
                        html.I(className="bi bi-info-circle me-2"),
                        html.Strong("Previsão de 5 dias"),
                        html.Br(),
                        "Será calculado ETo para os próximos 5 dias com base "
                        "em dados de previsão meteorológica.",
                    ],
                    color="info",
                    className="mb-3",
                ),
                html.Small(
                    "🔮 Período: hoje até hoje+5 dias (padrão EVAonline)",
                    className="text-muted",
                ),
                html.Br(),
                html.Small(
                    "📡 Fontes: Open-Meteo Forecast, MET Norway, "
                    "NWS Forecast (se USA)",
                    className="text-info",
                ),
                # Hidden fields for callback compatibility
                dbc.Input(
                    id="days-current",
                    value="6",
                    type="hidden",
                    style={"display": "none"},
                ),
                dbc.Input(
                    id="start-date-historical",
                    type="hidden",
                    style={"display": "none"},
                ),
                dbc.Input(
                    id="end-date-historical",
                    type="hidden",
                    style={"display": "none"},
                ),
                dbc.Input(
                    id="email-historical",
                    type="hidden",
                    style={"display": "none"},
                ),
                dbc.Input(
                    id="file-format-historical",
                    value="csv",
                    type="hidden",
                    style={"display": "none"},
                ),
            ]
        )


@callback(
    [
        Output("eto-results-container", "children"),
        Output("operation-mode-indicator", "children"),
        Output("validation-alert", "children"),
        Output("current-task-id", "data"),
        Output("progress-interval", "disabled"),
        Output("current-operation-mode", "data"),
    ],
    Input("calculate-eto-btn", "n_clicks"),
    [
        State("navigation-coordinates", "data"),
        State("data-type-radio", "value"),
        State("start-date-historical", "date"),
        State("end-date-historical", "date"),
        State("email-historical", "value"),
        State("file-format-historical", "value"),
        State("days-current", "value"),
        State("app-session-id", "data"),
    ],
    prevent_initial_call=True,
)
def calculate_eto(
    n_clicks,
    coords_data,
    data_type,
    start_date_hist,
    end_date_hist,
    email_hist,
    file_format_hist,
    days_current,
    session_id,
):
    """
    Calcula ETo com detecção automática de modo operacional.

    Usa OperationModeDetector para validar e preparar requisição.

    Mapeamento UI → Backend:
    - "historical" → HISTORICAL_EMAIL (1-90 days, requires email)
    - "recent" → DASHBOARD_CURRENT (7/14/21/30 days)
    - "forecast" → DASHBOARD_FORECAST (6 days fixed)

    Args:
        session_id: ID único da sessão do usuário (gerado automaticamente)

    Returns:
        Tuple (results_container, mode_indicator, validation_alert)
    """
    import uuid

    logger.info("🧮 calculate_eto callback triggered")

    if n_clicks is None or n_clicks == 0:
        logger.warning("⚠️ Aborting - n_clicks empty or zero")
        return None, None, None, None, True, None

    # Garantir session_id único para esta sessão
    if not session_id:
        session_id = f"sess_{uuid.uuid4().hex}"
        logger.info(f"🆕 Nova sessão gerada: {session_id}")
    else:
        logger.info(f"🔑 Sessão existente: {session_id}")

    logger.info("✅ Proceeding with validation...")

    # ========================================================================
    # 1. VALIDATE COORDINATES (from Store)
    # ========================================================================
    if not coords_data:
        logger.error("❌ coords_data empty")
        error_alert = dbc.Alert(
            [
                html.I(className="bi bi-exclamation-triangle me-2"),
                html.Strong("Erro: "),
                "Coordenadas não encontradas.",
            ],
            color="danger",
        )
        return None, None, error_alert, None, True, None

    try:
        lat = float(coords_data.get("lat"))
        lon = float(coords_data.get("lon"))

        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            logger.error(f"❌ Invalid coords: lat={lat}, lon={lon}")
            error_alert = dbc.Alert(
                [
                    html.I(className="bi bi-exclamation-triangle me-2"),
                    html.Strong("Erro: "),
                    "Coordenadas inválidas.",
                ],
                color="danger",
            )
            return None, None, error_alert, None, True, None

    except (ValueError, TypeError, KeyError) as e:
        logger.error(f"❌ Error parsing coordinates: {e}")
        error_alert = dbc.Alert(
            [
                html.I(className="bi bi-exclamation-triangle me-2"),
                html.Strong("Erro: "),
                "Falha ao processar coordenadas.",
            ],
            color="danger",
        )
        return None, None, error_alert, None, True, None

    # ========================================================================
    # 2. DETECT OPERATION MODE & VALIDATE
    # ========================================================================
    try:
        # UI selection agora vem diretamente do data_type radio
        ui_selection = data_type  # "historical", "recent", ou "forecast"
        logger.info(f"🎯 UI Selection: {ui_selection}")

        # Parse dates
        start_date = None
        end_date = None
        period_days = None

        if ui_selection == "historical":
            # Validate email for historical mode
            if not email_hist or "@" not in email_hist:
                error_alert = dbc.Alert(
                    [
                        html.I(className="bi bi-exclamation-triangle me-2"),
                        html.Strong("Erro: "),
                        "E-mail válido obrigatório para dados históricos.",
                    ],
                    color="warning",
                )
                return None, None, error_alert, None, True, None

            # Parse historical dates
            start_date = parse_date_from_ui(start_date_hist)
            end_date = parse_date_from_ui(end_date_hist)
            logger.info(f"📅 Historical: {start_date} → {end_date}")

            # Validar datas
            if not start_date or not end_date:
                error_alert = dbc.Alert(
                    [
                        html.I(className="bi bi-exclamation-triangle me-2"),
                        html.Strong("Erro: "),
                        "Por favor, selecione as datas inicial e final.",
                    ],
                    color="warning",
                )
                return None, None, error_alert, None, True, None

            # Validar que data inicial não é maior que data final
            if start_date > end_date:
                error_alert = dbc.Alert(
                    [
                        html.I(className="bi bi-calendar-x me-2"),
                        html.Strong("Erro de período: "),
                        "A data inicial não pode ser posterior à data final. ",
                        f"Você selecionou: {start_date} até {end_date}.",
                    ],
                    color="danger",
                )
                return None, None, error_alert, None, True, None

            # Validar que data não é anterior a 1990
            from datetime import date as dt_date

            min_date = dt_date(1990, 1, 1)
            if start_date < min_date:
                error_alert = dbc.Alert(
                    [
                        html.I(className="bi bi-database-x me-2"),
                        html.Strong("Período não disponível: "),
                        f"O EVAonline possui dados a partir de 01/01/1990. ",
                        f"A data inicial selecionada ({start_date}) é anterior a este limite. ",
                        "Por favor, selecione uma data a partir de 1990.",
                    ],
                    color="warning",
                )
                return None, None, error_alert, None, True, None

        elif ui_selection == "recent":
            # Parse period from dropdown
            period_days = int(days_current)
            logger.info(f"📅 Recent: last {period_days} days")

        else:  # forecast
            logger.info("📅 Forecast: next 6 days (fixed)")

        # Use OperationModeDetector to prepare request
        payload = OperationModeDetector.prepare_api_request(
            ui_selection=ui_selection,
            latitude=lat,
            longitude=lon,
            start_date=start_date,
            end_date=end_date,
            period_days=period_days,
            email=email_hist if ui_selection == "historical" else None,
        )

        # Adicionar formato de arquivo para modo historical
        if ui_selection == "historical" and file_format_hist:
            payload["file_format"] = file_format_hist
            logger.info(f"📎 File format: {file_format_hist}")

        # Detect mode for visual indicator
        backend_mode, mode_config = OperationModeDetector.detect_mode(
            ui_selection, start_date, end_date, period_days
        )

        logger.info(f"✅ Mode detected: {backend_mode}")
        logger.info(f"📦 Payload: {payload}")

        # Create mode indicator badge
        mode_colors = {
            "HISTORICAL_EMAIL": "primary",
            "DASHBOARD_CURRENT": "success",
            "DASHBOARD_FORECAST": "warning",
        }
        mode_indicator = dbc.Badge(
            [
                html.I(className="bi bi-info-circle me-1"),
                f"Modo: {backend_mode}",
            ],
            color=mode_colors.get(backend_mode, "secondary"),
            className="mb-3 p-2",
        )

    except ValueError as e:
        logger.error(f"❌ Validation error: {e}")
        error_alert = dbc.Alert(
            [
                html.I(className="bi bi-exclamation-triangle me-2"),
                html.Strong("Erro de validação: "),
                str(e),
            ],
            color="danger",
        )
        return None, None, error_alert, None, True, None

    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        error_alert = dbc.Alert(
            [
                html.I(className="bi bi-exclamation-octagon-fill me-2"),
                html.Strong("Erro inesperado: "),
                str(e),
            ],
            color="danger",
        )
        return None, None, error_alert, None, True, None

    # ========================================================================
    # 3. CALL BACKEND API
    # ========================================================================
    import requests

    try:
        logger.info("🔄 Sending request to backend...")

        # 🔀 FUSÃO AUTOMÁTICA: Não enviar "sources", backend decide automaticamente
        # O backend irá selecionar as melhores fontes baseado no period_type
        # Ver: climate_source_manager.get_available_sources_by_mode()

        # Adicionar session_id para identificação única do usuário
        payload["session_id"] = session_id
        payload["visitor_id"] = session_id  # Para compatibilidade

        logger.info(f"📦 Final payload (auto-fusion): {payload}")

        # Make POST request
        response = requests.post(
            "http://localhost:8000/api/v1/internal/eto/calculate",
            json=payload,
            timeout=30,
        )

        # Check status
        if response.status_code == 200:
            logger.info("✅ Task submitted to backend!")
            task_response = response.json()

            # Backend retorna task_id, não resultado direto
            if task_response.get("status") == "accepted":
                task_id = task_response.get("task_id")
                logger.info(f"📋 Task ID: {task_id}")

                # Iniciar monitoramento via interval callback
                # Retornar: results=None, mode_indicator, alert=None,
                #          task_id, interval_disabled=False, operation_mode
                return (
                    None,
                    mode_indicator,
                    None,
                    task_id,
                    False,  # Habilitar interval
                    backend_mode,  # Salvar o modo de operação
                )

            # Se não foi aceito
            error_alert = dbc.Alert(
                [
                    html.I(className="bi bi-exclamation-triangle me-2"),
                    html.Strong("Erro: "),
                    f"Task não foi aceita: {task_response}",
                ],
                color="danger",
            )
            return None, mode_indicator, error_alert, None, True, None

        else:
            logger.error(f"❌ Backend error {response.status_code}")
            error_alert = dbc.Alert(
                [
                    html.I(className="bi bi-exclamation-triangle me-2"),
                    html.Strong(f"Erro {response.status_code}: "),
                    response.text[:200],
                ],
                color="danger",
            )
            return None, mode_indicator, error_alert, None, True, None

    except requests.Timeout:
        logger.error("⏱️ Request timeout")
        error_alert = dbc.Alert(
            [
                html.I(className="bi bi-clock-fill me-2"),
                html.Strong("Timeout: "),
                "Backend demorou muito (>30s).",
            ],
            color="warning",
        )
        return None, mode_indicator, error_alert, None, True, None

    except requests.ConnectionError:
        logger.error("🔌 Connection error")
        error_alert = dbc.Alert(
            [
                html.I(className="bi bi-plug-fill me-2"),
                html.Strong("Erro de conexão: "),
                "Não foi possível conectar ao backend.",
            ],
            color="danger",
        )
        return None, mode_indicator, error_alert, None, True, None

    except Exception as e:
        logger.error(f"💥 Unexpected error: {str(e)}")
        error_alert = dbc.Alert(
            [
                html.I(className="bi bi-exclamation-octagon-fill me-2"),
                html.Strong("Erro inesperado: "),
                str(e),
            ],
            color="danger",
        )
        return None, mode_indicator, error_alert, None, True, None


@callback(
    [
        Output("eto-progress-container", "children"),
        Output("eto-results-container", "children", allow_duplicate=True),
        Output("progress-interval", "disabled", allow_duplicate=True),
        Output("current-task-id", "data", allow_duplicate=True),
        Output("calculation-success-status", "children"),
        Output("eto-results-data", "data"),  # Store para dados de download
    ],
    Input("progress-interval", "n_intervals"),
    [
        State("current-task-id", "data"),
        State("current-operation-mode", "data"),
    ],
    prevent_initial_call=True,
)
def update_progress(n_intervals, task_id, operation_mode):
    """Atualiza indicador de progresso consultando status da task no Redis.

    Para modo HISTORICAL_EMAIL: Não exibe dados na interface, apenas confirmação.
    Para outros modos (DASHBOARD_CURRENT, DASHBOARD_FORECAST): Exibe dados normalmente.
    """
    if not task_id:
        return None, no_update, True, None, no_update, no_update

    try:
        import redis
        import json
        import os

        # Usar variável de ambiente ou padrão para Docker
        redis_host = os.getenv("REDIS_HOST", "redis")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))

        r = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=0,
            decode_responses=True,
        )

        result_key = f"celery-task-meta-{task_id}"
        result_data = r.get(result_key)

        logger.info(f"🔍 Checking task {task_id}, mode: {operation_mode}")

        if not result_data:
            # Task ainda não iniciou ou não tem dados - mostrar spinner elegante
            progress_indicator = html.Div(
                [
                    html.Div(
                        [
                            dbc.Spinner(
                                color="success",
                                type="grow",
                                size="sm",
                                spinner_class_name="me-2",
                            ),
                            html.Span(
                                "Baixando dados e calculando ETo...",
                                className="text-success fw-semibold",
                            ),
                        ],
                        className="d-flex align-items-center",
                    ),
                ],
                className="p-3 bg-light rounded-3 border",
            )
            return (
                progress_indicator,
                no_update,
                False,
                task_id,
                no_update,
                no_update,
            )

        result = json.loads(result_data)
        status = result.get("status")
        logger.info(f"📊 Task status: {status}")

        if status == "SUCCESS":
            task_result = result.get("result", {})
            days_calculated = len(task_result.get("et0_series", []))
            logger.info(
                f"✅ Task SUCCESS - {days_calculated} days, mode: {operation_mode}"
            )

            # ================================================================
            # MODO HISTORICAL_EMAIL: Apenas confirmação, sem exibir dados
            # ================================================================
            if operation_mode == "HISTORICAL_EMAIL":
                logger.info("📧 Modo HISTORICAL_EMAIL - exibindo confirmação")
                email_sent = task_result.get("email_sent", True)

                if email_sent:
                    success_content = dbc.Card(
                        [
                            dbc.CardHeader(
                                [
                                    html.I(
                                        className="bi bi-envelope-check me-2"
                                    ),
                                    html.Strong("📧 Dados Enviados por Email"),
                                ],
                                className="bg-success text-white",
                            ),
                            dbc.CardBody(
                                [
                                    dbc.Alert(
                                        [
                                            html.I(
                                                className="bi bi-check-circle-fill me-2"
                                            ),
                                            html.Strong(
                                                "Processamento concluído com sucesso!"
                                            ),
                                        ],
                                        color="success",
                                        className="mb-3",
                                    ),
                                    html.P(
                                        [
                                            html.I(
                                                className="bi bi-calendar-check me-2"
                                            ),
                                            f"Período processado: {days_calculated} dias",
                                        ],
                                        className="mb-2",
                                    ),
                                    html.P(
                                        [
                                            html.I(
                                                className="bi bi-envelope me-2"
                                            ),
                                            "Os dados foram enviados para o email informado.",
                                        ],
                                        className="mb-2",
                                    ),
                                    html.P(
                                        [
                                            html.I(
                                                className="bi bi-info-circle me-2"
                                            ),
                                            html.Small(
                                                "Verifique sua caixa de entrada e spam. "
                                                "O arquivo está anexado no formato solicitado.",
                                                className="text-muted",
                                            ),
                                        ],
                                        className="mb-0",
                                    ),
                                    html.Hr(),
                                    html.P(
                                        [
                                            html.I(
                                                className="bi bi-clock-history me-2"
                                            ),
                                            f"Tempo de processamento: {task_result.get('processing_time_seconds', 'N/A')}s",
                                        ],
                                        className="text-muted small mb-0",
                                    ),
                                ]
                            ),
                        ],
                        className="mt-3 shadow",
                    )
                else:
                    success_content = dbc.Alert(
                        [
                            html.I(
                                className="bi bi-exclamation-triangle me-2"
                            ),
                            html.Strong("Processamento concluído, "),
                            "mas houve um problema ao enviar o email. ",
                            "Verifique as configurações SMTP.",
                        ],
                        color="warning",
                        className="mt-3",
                    )

                # Success status for sidebar
                sidebar_success = dbc.Alert(
                    [
                        html.I(className="bi bi-check-circle-fill me-2"),
                        html.Strong(f"✅ {days_calculated} dias processados"),
                    ],
                    color="success",
                    className="py-2 px-3 mb-0",
                )

                return None, success_content, True, None, sidebar_success, None

            # ================================================================
            # OUTROS MODOS (DASHBOARD_CURRENT, DASHBOARD_FORECAST):
            # Exibir dados na interface normalmente
            # ================================================================
            logger.info(
                f"📊 Modo {operation_mode} - exibindo dados na interface"
            )

            import pandas as pd
            from backend.core.data_results.results_layout import (
                create_results_tabs,
            )

            # Convert result to DataFrame
            et0_data = task_result.get("et0_series", [])
            logger.info(f"📈 Dados recebidos: {len(et0_data)} registros")

            if not et0_data:
                error_card = dbc.Alert(
                    [
                        html.I(className="bi bi-exclamation-triangle me-2"),
                        "Nenhum dado retornado pelo backend.",
                    ],
                    color="warning",
                )
                return None, error_card, True, None, no_update, None

            # Create DataFrame with standardized column names
            df_records = []
            for record in et0_data:
                df_records.append(
                    {
                        "date": pd.to_datetime(record.get("date")),
                        "T2M_MAX": record.get("tmax_c", 0),
                        "T2M_MIN": record.get("tmin_c", 0),
                        "T2M": record.get("tmed_c", 0),
                        "RH2M": record.get("humidity_pct", 0),
                        "WS2M": record.get("wind_ms", 0),
                        "ALLSKY_SFC_SW_DWN": record.get("radiation_mj_m2", 0),
                        "PRECTOTCORR": record.get("precip_mm", 0),
                        "eto_evaonline": record.get("et0_mm_day", 0),
                        "eto_openmeteo": record.get(
                            "eto_openmeteo", record.get("et0_mm_day", 0)
                        ),  # Fallback se não houver
                    }
                )

            df = pd.DataFrame(df_records)

            # Get sources used
            sources_used = task_result.get("sources_used", [])

            # Create results with new tab system
            try:
                # Preparar dados para download (armazenar no Store)
                download_data = {
                    "records": et0_data,
                    "sources_used": sources_used,
                    "mode": operation_mode,
                    "days": days_calculated,
                }

                # Botões de download
                download_buttons = html.Div(
                    [
                        html.Hr(className="my-3"),
                        html.Div(
                            [
                                html.I(className="bi bi-download me-2"),
                                html.Strong("Download dos Dados:"),
                            ],
                            className="mb-2",
                        ),
                        dbc.ButtonGroup(
                            [
                                dbc.Button(
                                    [
                                        html.I(
                                            className="bi bi-filetype-csv me-2"
                                        ),
                                        "Download CSV",
                                    ],
                                    id="btn-download-csv",
                                    color="success",
                                    outline=True,
                                    className="me-2",
                                ),
                                dbc.Button(
                                    [
                                        html.I(
                                            className="bi bi-file-earmark-spreadsheet me-2"
                                        ),
                                        "Download Excel",
                                    ],
                                    id="btn-download-excel",
                                    color="primary",
                                    outline=True,
                                ),
                            ],
                            className="w-100",
                        ),
                    ],
                    className="mt-3 p-3 bg-light rounded",
                )

                results_content = html.Div(
                    [
                        # Tabs with results (success message moved to sidebar)
                        create_results_tabs(
                            df, sources=sources_used, lang="pt"
                        ),
                        # Download buttons
                        download_buttons,
                    ],
                    className="results-container",
                )

                # Success status for sidebar
                sidebar_success = dbc.Alert(
                    [
                        html.I(className="bi bi-check-circle-fill me-2"),
                        html.Strong(
                            f"✅ Sucesso! {days_calculated} dias calculados"
                        ),
                    ],
                    color="success",
                    className="py-2 px-3 mb-0",
                )

                # Desabilitar interval e limpar task_id
                return (
                    None,
                    results_content,
                    True,
                    None,
                    sidebar_success,
                    download_data,
                )

            except Exception as e:
                logger.error(f"Error creating results tabs: {e}")
                # Fallback to simple table
                error_card = dbc.Alert(
                    [
                        html.I(className="bi bi-exclamation-triangle me-2"),
                        f"Erro ao criar visualização: {str(e)}",
                    ],
                    color="warning",
                )
                return None, error_card, True, None, no_update, None

        elif status == "FAILURE":
            # Handle FAILURE status
            error_msg = result.get("result", "Erro desconhecido")
            warnings = []

            error_card = dbc.Card(
                [
                    dbc.CardHeader(
                        [
                            html.I(
                                className="bi bi-exclamation-triangle me-2"
                            ),
                            html.Strong("❌ Erro no cálculo"),
                        ],
                        className="bg-danger text-white",
                    ),
                    dbc.CardBody(
                        [
                            html.P(
                                [
                                    html.Strong("Erro: "),
                                    html.Span(str(error_msg)),
                                ]
                            ),
                            html.Hr() if warnings else None,
                            (
                                html.Div(
                                    [
                                        html.H6("⚠️ Avisos:"),
                                        html.Ul(
                                            [
                                                html.Li(warning)
                                                for warning in warnings[
                                                    :5
                                                ]  # Max 5 warnings
                                            ]
                                        ),
                                    ]
                                )
                                if warnings
                                else None
                            ),
                            html.Hr(),
                            html.P(
                                "Por favor, tente novamente ou contate o suporte.",
                                className="mb-0 text-muted",
                            ),
                        ]
                    ),
                ],
                className="mt-3",
            )
            return None, error_card, True, None, no_update, None

        elif status == "PENDING" or status == "STARTED":
            # Task em execução - mostrar indicador elegante com percentual
            elapsed = n_intervals * 2  # 2 segundos por intervalo
            estimated_progress = min(95, 10 + (elapsed / 60) * 85)

            progress_indicator = html.Div(
                [
                    # Linha com spinner e mensagem
                    html.Div(
                        [
                            dbc.Spinner(
                                color="success",
                                type="border",
                                size="sm",
                                spinner_class_name="me-3",
                            ),
                            html.Div(
                                [
                                    html.Span(
                                        "Baixando dados e calculando ETo...",
                                        className="fw-semibold text-dark",
                                    ),
                                    html.Br(),
                                    html.Small(
                                        f"Tempo estimado: {max(1, 30 - elapsed)}s",
                                        className="text-muted",
                                    ),
                                ],
                            ),
                            html.Div(
                                html.Span(
                                    f"{int(estimated_progress)}%",
                                    className="fw-bold text-success fs-5",
                                ),
                                className="ms-auto",
                            ),
                        ],
                        className="d-flex align-items-center mb-3",
                    ),
                    # Barra de progresso fina e elegante
                    dbc.Progress(
                        value=estimated_progress,
                        color="success",
                        className="mb-0",
                        style={"height": "8px", "borderRadius": "4px"},
                    ),
                ],
                className="p-3 bg-light rounded-3 border",
            )

            return (
                progress_indicator,
                no_update,
                False,
                task_id,
                no_update,
                no_update,
            )

        else:
            # Status desconhecido - manter consultando
            logger.warning(f"⚠️ Status desconhecido: {status}")
            return None, no_update, False, task_id, no_update, no_update

    except Exception as e:
        logger.error(f"Erro ao atualizar progresso: {e}")
        return None, no_update, False, task_id, no_update, no_update


# ============================================================================
# CALLBACKS DE DOWNLOAD CSV E EXCEL
# ============================================================================


@callback(
    Output("download-csv", "data"),
    Input("btn-download-csv", "n_clicks"),
    State("eto-results-data", "data"),
    prevent_initial_call=True,
)
def download_csv(n_clicks, results_data):
    """Gera download de arquivo CSV."""
    if not n_clicks or not results_data:
        return no_update

    import pandas as pd
    from datetime import datetime

    records = results_data.get("records", [])
    if not records:
        return no_update

    # Criar DataFrame
    df = pd.DataFrame(records)

    # Formatar nome do arquivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"EVAonline_ETo_{timestamp}.csv"

    return dcc.send_data_frame(df.to_csv, filename, index=False)


@callback(
    Output("download-excel", "data"),
    Input("btn-download-excel", "n_clicks"),
    State("eto-results-data", "data"),
    prevent_initial_call=True,
)
def download_excel(n_clicks, results_data):
    """Gera download de arquivo Excel."""
    if not n_clicks or not results_data:
        return no_update

    import pandas as pd
    from datetime import datetime
    import io

    records = results_data.get("records", [])
    if not records:
        return no_update

    # Criar DataFrame
    df = pd.DataFrame(records)

    # Formatar nome do arquivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"EVAonline_ETo_{timestamp}.xlsx"

    # Criar buffer Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="ETo_Data")
    output.seek(0)

    return dcc.send_bytes(output.getvalue(), filename)


logger.info("✅ Página ETo carregada com sucesso")

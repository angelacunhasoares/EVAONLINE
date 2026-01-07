"""
Pagina HOME unificada do EVAonline.

Layout simples com sidebar + mapa (estilo Iris k-means example).
Estrutura: HOME | DOCUMENTATION | ABOUT | GITHUB

Features:
- Sidebar com configuracoes de calculo (nao usa Offcanvas)
- Mapa mundial interativo ocupando area principal
- Resultados exibidos abaixo do mapa
"""

import logging

import dash_bootstrap_components as dbc
from dash import dcc, html

from ..components.world_map_leaflet import create_world_map

logger = logging.getLogger(__name__)


def create_sidebar_card():
    """
    Cria sidebar profissional com design moderno.
    Estilo clean com gradientes, icones e espacamento otimizado.
    """
    return html.Div(
        [
            # Header com gradiente
            html.Div(
                [
                    html.Div(
                        [
                            html.I(
                                className="bi bi-droplet-half",
                                style={"fontSize": "1.8rem"},
                            ),
                        ],
                        className="me-3",
                    ),
                    html.Div(
                        [
                            html.H5(
                                "ETo Calculator",
                                className="mb-0 fw-bold",
                            ),
                            html.Small(
                                "FAO-56 Penman-Monteith",
                                className="opacity-75",
                            ),
                        ],
                    ),
                ],
                className="d-flex align-items-center p-3 text-white",
                style={
                    "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                    "borderRadius": "12px 12px 0 0",
                },
            ),
            # Corpo da sidebar
            html.Div(
                [
                    # Secao 1: Tipo de Dados
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.I(
                                        className="bi bi-database me-2 text-primary"
                                    ),
                                    html.Span(
                                        "Data Type",
                                        className="fw-semibold text-dark",
                                    ),
                                ],
                                className="mb-3",
                            ),
                            dbc.RadioItems(
                                id="data-type-radio",
                                options=[
                                    {
                                        "label": html.Div(
                                            [
                                                html.I(
                                                    className="bi bi-calendar-range me-2 text-info"
                                                ),
                                                html.Span("Historical"),
                                                html.Small(
                                                    " (1990-today)",
                                                    className="text-muted ms-1",
                                                ),
                                            ],
                                            className="d-flex align-items-center",
                                        ),
                                        "value": "historical",
                                    },
                                    {
                                        "label": html.Div(
                                            [
                                                html.I(
                                                    className="bi bi-clock-history me-2 text-success"
                                                ),
                                                html.Span("Recent"),
                                                html.Small(
                                                    " (7-30 days)",
                                                    className="text-muted ms-1",
                                                ),
                                            ],
                                            className="d-flex align-items-center",
                                        ),
                                        "value": "recent",
                                    },
                                    {
                                        "label": html.Div(
                                            [
                                                html.I(
                                                    className="bi bi-cloud-sun me-2 text-warning"
                                                ),
                                                html.Span("Forecast"),
                                                html.Small(
                                                    " (5 days)",
                                                    className="text-muted ms-1",
                                                ),
                                            ],
                                            className="d-flex align-items-center",
                                        ),
                                        "value": "forecast",
                                    },
                                ],
                                value=None,
                                className="custom-radio-group",
                                inputClassName="me-2",
                                labelClassName="py-2 px-3 rounded-3 mb-2 d-block border",
                                labelCheckedClassName="bg-light border-primary",
                            ),
                        ],
                        className="mb-4",
                    ),
                    # Secao 2: Fonte de Dados
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.I(
                                        className="bi bi-cloud-download me-2 text-primary"
                                    ),
                                    html.Span(
                                        "Climate Source",
                                        className="fw-semibold text-dark",
                                    ),
                                ],
                                className="mb-2",
                            ),
                            html.Div(
                                id="source-selection-info",
                                className="small text-muted mb-2",
                            ),
                            dbc.Select(
                                id="climate-source-dropdown",
                                placeholder="Select data type first...",
                                disabled=True,
                                className="mb-2",
                                style={"borderRadius": "8px"},
                            ),
                            html.Small(
                                id="source-description",
                                className="text-muted fst-italic",
                            ),
                        ],
                        className="mb-4 pb-3 border-bottom",
                    ),
                    # Secao 3: Formulario Condicional
                    html.Div(
                        id="conditional-form",
                        className="mb-3",
                    ),
                    # Botao de Calcular - Estilo moderno
                    dbc.Button(
                        [
                            html.I(className="bi bi-calculator-fill me-2"),
                            "CALCULATE ETo",
                        ],
                        id="calculate-eto-btn",
                        color="success",
                        className="w-100 py-2 fw-semibold",
                        style={
                            "borderRadius": "10px",
                            "boxShadow": "0 4px 15px rgba(40, 167, 69, 0.3)",
                            "transition": "all 0.3s ease",
                        },
                        n_clicks=0,
                        disabled=True,
                    ),
                    # Feedback areas
                    html.Div(id="validation-alert", className="mt-3"),
                    html.Div(id="operation-mode-indicator", className="mt-2"),
                    html.Div(
                        id="calculation-success-status", className="mt-2"
                    ),
                    html.Div(id="eto-progress-container", className="mt-2"),
                ],
                className="p-3",
                style={
                    "backgroundColor": "#ffffff",
                    "minHeight": "400px",
                },
            ),
        ],
        style={
            "borderRadius": "12px",
            "boxShadow": "0 10px 40px rgba(0,0,0,0.1)",
            "overflow": "hidden",
            "border": "none",
        },
    )


def create_map_card():
    """Cria card com o mapa mundial - estilo moderno."""
    return html.Div(
        [
            # Header com gradiente verde
            html.Div(
                [
                    html.Div(
                        [
                            html.I(
                                className="bi bi-geo-alt-fill",
                                style={"fontSize": "1.8rem"},
                            ),
                        ],
                        className="me-3",
                    ),
                    html.Div(
                        [
                            html.H5(
                                "Select Location",
                                className="mb-0 fw-bold",
                            ),
                            html.Small(
                                "Click on the map or use geolocation",
                                className="opacity-75",
                            ),
                        ],
                    ),
                ],
                className="d-flex align-items-center p-3 text-white",
                style={
                    "background": "linear-gradient(135deg, #11998e 0%, #38ef7d 100%)",
                    "borderRadius": "12px 12px 0 0",
                },
            ),
            # Corpo do card
            html.Div(
                [
                    # Mapa
                    create_world_map(),
                    # Info de Selecao
                    html.Div(
                        id="current-selection-info",
                        className="mt-2",
                    ),
                ],
                className="p-2",
                style={"backgroundColor": "#ffffff"},
            ),
        ],
        style={
            "borderRadius": "12px",
            "boxShadow": "0 10px 40px rgba(0,0,0,0.1)",
            "overflow": "hidden",
            "border": "none",
        },
    )


# =============================================================================
# LAYOUT PRINCIPAL - DESIGN MODERNO
# =============================================================================
home_layout = dbc.Container(
    [
        # Espacamento superior
        html.Div(className="py-2"),
        # Layout Principal: Sidebar (4 cols) + Mapa (8 cols)
        dbc.Row(
            [
                # SIDEBAR (4 colunas)
                dbc.Col(
                    create_sidebar_card(),
                    lg=4,
                    md=5,
                    className="mb-3",
                ),
                # MAPA (8 colunas)
                dbc.Col(
                    create_map_card(),
                    lg=8,
                    md=7,
                    className="mb-3",
                ),
            ],
            align="start",
            className="g-4",  # Gap entre colunas
        ),
        # Linha de Resultados (abaixo do mapa)
        dbc.Row(
            [
                dbc.Col(
                    html.Div(id="eto-results-container"),
                    width=12,
                ),
            ],
        ),
        # =================================================================
        # STORES E COMPONENTES OCULTOS
        # =================================================================
        dcc.Store(id="favorites-store", storage_type="local", data=[]),
        dcc.Store(id="home-favorites-count", data=0),
        dcc.Store(id="sidebar-state", storage_type="session", data=True),
        dcc.Store(id="selected-location-data", data=None),
        dcc.Store(id="current-location", data=None),
        dcc.Store(id="map-click-data", data=None),
        dcc.Store(id="parsed-coordinates", data=None),
        dcc.Store(id="current-task-id"),
        dcc.Store(id="current-operation-mode"),
        dcc.Interval(
            id="progress-interval",
            interval=2000,
            n_intervals=0,
            disabled=True,
        ),
        # Hidden elements for callback compatibility
        html.Div(
            [
                html.Div(id="location-display"),
                html.Div(id="location-input-container"),
                html.Div(id="coord-validation-feedback"),
                html.Div(id="selected-coords-display"),
                html.Div(id="favorites-list-container"),
                html.Div(id="empty-favorites-alert"),
                html.Div(id="favorites-count-badge"),
                dbc.RadioItems(
                    id="location-mode-radio",
                    value="map",
                ),
                dbc.Button(id="add-favorite-btn"),
                dbc.Button(id="clear-favorites-button"),
                dbc.Button(id="favorite-button", n_clicks=0),
                dbc.RadioItems(id="file-format-historical", value="csv"),
                dcc.Store(id="favorites-data", data=[]),
            ],
            style={"display": "none"},
        ),
        # Toast Container
        html.Div(
            id="toast-container",
            style={
                "position": "fixed",
                "top": "80px",
                "right": "20px",
                "zIndex": 9999,
                "minWidth": "300px",
            },
        ),
    ],
    fluid=True,
    className="px-4",
)

logger.info("Home page (unified) loaded successfully")

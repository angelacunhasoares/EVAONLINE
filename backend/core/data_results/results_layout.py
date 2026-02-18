"""
Results Layout with Tabs - Table/Statistics and Graphics.

Two-tab structure:
- Tab 1: Complete table with climate variables + ETos + statistics
- Tab 2: Statistical and comparison graphics
"""

import dash_bootstrap_components as dbc
from dash import dcc, html

from backend.core.data_results.results_graphs import (
    plot_eto_vs_radiation,
    plot_eto_vs_temperature,
    plot_heatmap,
    plot_temp_rad_prec,
)
from backend.core.data_results.results_statistical import (
    create_deficit_chart_section,
    display_descriptive_stats,
    display_eto_summary,
    display_normality_test,
)
from backend.core.data_results.results_tables import (
    display_results_table,
)


def create_results_tabs(df, sources=None, lang: str = "pt"):
    """
    Create results layout with two tabs.

    Args:
        df: DataFrame with results
        sources: List of data sources used
        lang: Language for translations

    Returns:
        dbc.Tabs component with two tabs
    """
    if sources is None:
        sources = []

    # Tab 1: Table & Statistics
    tab1_content = dbc.Card(
        dbc.CardBody(
            [
                # Title
                html.H4(
                    [
                        html.I(className="bi bi-table me-2"),
                        "Resultados - Tabela de Dados",
                    ],
                    className="results-section-title",
                ),
                # Climate data table
                html.Div(
                    [
                        html.H5(
                            [
                                html.I(className="bi bi-table me-2"),
                                "Dados Climáticos Diários",
                            ],
                            className="results-table-title",
                        ),
                        display_results_table(df, lang),
                    ],
                    className="mb-5",
                ),
                # Descriptive statistics
                html.Div(
                    [
                        html.H5(
                            [
                                html.I(className="bi bi-calculator me-2"),
                                "Estatísticas Descritivas",
                            ],
                            className="results-table-title",
                        ),
                        display_descriptive_stats(df, lang),
                    ],
                    className="mb-5",
                ),
                # ETo summary
                html.Div(
                    [
                        html.H5(
                            [
                                html.I(className="bi bi-droplet me-2"),
                                "Resumo de ETo e Balanço Hídrico",
                            ],
                            className="results-table-title",
                        ),
                        display_eto_summary(df, lang),
                    ],
                    className="mb-5",
                ),
                # Normality test
                html.Div(
                    [
                        html.H5(
                            [
                                html.I(className="bi bi-graph-up me-2"),
                                "Teste de Normalidade (Shapiro-Wilk)",
                            ],
                            className="results-table-title",
                        ),
                        display_normality_test(df, lang),
                    ],
                    className="mb-4",
                ),
            ]
        ),
        className="mt-3 shadow-sm",
    )

    # Tab 2: Graphics
    tab2_content = dbc.Card(
        dbc.CardBody(
            [
                # Title
                html.H4(
                    [
                        html.I(className="bi bi-graph-up me-2"),
                        "Resultados - Análises Gráficas",
                    ],
                    className="results-section-title",
                ),
                # Déficit Hídrico Section
                html.Div(
                    [
                        html.H5(
                            [
                                html.I(className="bi bi-droplet-half me-2"),
                                "Déficit Hídrico",
                            ],
                            className="results-table-title",
                        ),
                        create_deficit_chart_section(df, lang),
                    ],
                    className="mb-5",
                ),
                # Climate graphics
                html.Div(
                    [
                        html.H5(
                            [
                                html.I(
                                    className="bi bi-thermometer-half me-2"
                                ),
                                "Análises Climáticas",
                            ],
                            className="results-table-title",
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H6(
                                            "ETo vs Temperatura",
                                            className="text-center mb-2",
                                        ),
                                        dcc.Graph(
                                            figure=plot_eto_vs_temperature(
                                                df, lang
                                            ),
                                            config={"displayModeBar": False},
                                            style={"height": "400px"},
                                        ),
                                    ],
                                    md=12,
                                    lg=6,
                                    className="mb-3",
                                ),
                                dbc.Col(
                                    [
                                        html.H6(
                                            "ETo vs Radiação",
                                            className="text-center mb-2",
                                        ),
                                        dcc.Graph(
                                            figure=plot_eto_vs_radiation(
                                                df, lang
                                            ),
                                            config={"displayModeBar": False},
                                            style={"height": "400px"},
                                        ),
                                    ],
                                    md=12,
                                    lg=6,
                                    className="mb-3",
                                ),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H6(
                                            "Temperatura, Radiação e Precipitação",
                                            className="text-center mb-2",
                                        ),
                                        dcc.Graph(
                                            figure=plot_temp_rad_prec(
                                                df, lang
                                            ),
                                            config={"displayModeBar": False},
                                            style={"height": "400px"},
                                        ),
                                    ],
                                    md=12,
                                    className="mb-3",
                                ),
                            ]
                        ),
                    ],
                    className="mb-5",
                ),
                # Correlation heatmap
                html.Div(
                    [
                        html.H5(
                            [
                                html.I(className="bi bi-grid-3x3 me-2"),
                                "Mapa de Calor - Correlações",
                            ],
                            className="results-table-title",
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dcc.Graph(
                                            figure=plot_heatmap(df, lang),
                                            config={"displayModeBar": False},
                                            style={"height": "450px"},
                                        ),
                                    ],
                                    md=12,
                                ),
                            ]
                        ),
                    ],
                    className="mb-4",
                ),
            ]
        ),
        className="mt-3 shadow-sm",
    )

    # Create tabs
    tabs = dbc.Tabs(
        [
            dbc.Tab(
                tab1_content,
                label="📊 Tabela & Estatísticas",
                tab_id="tab-table",
            ),
            dbc.Tab(
                tab2_content,
                label="📈 Gráficos",
                tab_id="tab-graphics",
            ),
        ],
        id="results-tabs",
        active_tab="tab-table",
        className="mb-3 nav-tabs results-tabs",
    )

    return tabs


def create_results_layout_simplified(df, sources=None, lang: str = "pt"):
    """
    Create simplified results layout with tabs (no comparison metrics).

    Focus on climate statistics and analysis, not validation metrics.
    Validation metrics (R², MAE, KGE, etc.) are for historical validation
    (EVAonline vs Xavier vs Open-Meteo), not for dashboard display.

    Args:
        df: DataFrame with results
        sources: List of data sources
        lang: Language

    Returns:
        dbc.Container with tabs layout
    """
    layout = dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [create_results_tabs(df, sources, lang)],
                        xs=12,
                        className="mb-3",
                    ),
                ]
            )
        ],
        fluid=True,
        className="results-layout",
    )

    return layout

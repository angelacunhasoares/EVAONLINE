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
from shared_utils.get_translations import t


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
                        t(lang, "results", "data_table_title", default="Results - Data Table"),
                    ],
                    className="results-section-title",
                ),
                # Climate data table
                html.Div(
                    [
                        html.H5(
                            [
                                html.I(className="bi bi-table me-2"),
                                t(lang, "results", "daily_climate_data", default="Daily Climate Data"),
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
                                t(lang, "statistics", "descriptive", default="Descriptive Statistics"),
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
                                t(lang, "results", "eto_summary_title", default="ETo Summary and Water Balance"),
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
                                t(lang, "results", "normality_test_shapiro", default="Normality Test (Shapiro-Wilk)"),
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
                        t(lang, "results", "graphical_analysis", default="Results - Graphical Analysis"),
                    ],
                    className="results-section-title",
                ),
                # Déficit Hídrico Section
                html.Div(
                    [
                        html.H5(
                            [
                                html.I(className="bi bi-droplet-half me-2"),
                                t(lang, "results", "water_deficit_title", default="Water Deficit"),
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
                                t(lang, "results", "climate_analysis", default="Climate Analysis"),
                            ],
                            className="results-table-title",
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H6(
                                            t(lang, "charts", "eto_vs_temp", default="ETo vs Temperature"),
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
                                            t(lang, "charts", "eto_vs_rad", default="ETo vs Solar Radiation"),
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
                                            t(lang, "charts", "temp_rad_prec", default="Temperature, Radiation & Precipitation"),
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
                                t(lang, "results", "correlation_heatmap", default="Heatmap - Correlations"),
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
                label=f"\U0001f4ca {t(lang, 'results', 'tab_table_stats', default='Table & Statistics')}",
                tab_id="tab-table",
            ),
            dbc.Tab(
                tab2_content,
                label=f"\U0001f4c8 {t(lang, 'results', 'tab_charts', default='Charts')}",
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

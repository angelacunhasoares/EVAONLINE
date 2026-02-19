import logging

import dash_bootstrap_components as dbc
from dash import html

logger = logging.getLogger(__name__)

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def _create_quick_start_section():
    """How to use EVAonline - Quick and objective guide."""
    return dbc.Row(
        [
            dbc.Col(
                [
                    html.H2(
                        "🚀 Quick Start",
                        id="quick-start",
                        className="mb-4",
                        style={"color": "#2c3e50"},
                    ),
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H5(
                                        "3 Steps to Calculate ETo",
                                        className="mb-4",
                                    ),
                                    # Step 1
                                    dbc.Card(
                                        [
                                            dbc.CardBody(
                                                [
                                                    html.Div(
                                                        [
                                                            dbc.Badge(
                                                                "1",
                                                                color="primary",
                                                                className="me-3",
                                                                style={
                                                                    "fontSize": "1.2rem",
                                                                    "padding": "8px 14px",
                                                                    "borderRadius": "50%",
                                                                },
                                                            ),
                                                            html.Div(
                                                                [
                                                                    html.H6(
                                                                        "Select a Location",
                                                                        className="mb-1",
                                                                    ),
                                                                    html.Small(
                                                                        [
                                                                            "Click anywhere on the interactive map, or type coordinates manually. "
                                                                            "The system automatically detects: ",
                                                                            html.Strong(
                                                                                "SRTM elevation"
                                                                            ),
                                                                            " (30m resolution via OpenTopoData), ",
                                                                            html.Strong(
                                                                                "timezone"
                                                                            ),
                                                                            ", and ",
                                                                            html.Strong(
                                                                                "region"
                                                                            ),
                                                                            " (USA detection for extra data sources).",
                                                                        ],
                                                                        className="text-muted",
                                                                    ),
                                                                ]
                                                            ),
                                                        ],
                                                        className="d-flex align-items-start",
                                                    )
                                                ]
                                            )
                                        ],
                                        className="mb-2 border-start border-primary border-3",
                                    ),
                                    # Step 2
                                    dbc.Card(
                                        [
                                            dbc.CardBody(
                                                [
                                                    html.Div(
                                                        [
                                                            dbc.Badge(
                                                                "2",
                                                                color="primary",
                                                                className="me-3",
                                                                style={
                                                                    "fontSize": "1.2rem",
                                                                    "padding": "8px 14px",
                                                                    "borderRadius": "50%",
                                                                },
                                                            ),
                                                            html.Div(
                                                                [
                                                                    html.H6(
                                                                        "Choose Operation Mode & Period",
                                                                        className="mb-1",
                                                                    ),
                                                                    html.Small(
                                                                        [
                                                                            "Select ",
                                                                            html.Strong(
                                                                                "Historical Data"
                                                                            ),
                                                                            " (1990→present, 2-day delay, up to 90 days, email required), ",
                                                                            html.Strong(
                                                                                "Recent Data"
                                                                            ),
                                                                            " (last 7/14/21/30 days, instant results), or ",
                                                                            html.Strong(
                                                                                "Forecast"
                                                                            ),
                                                                            " (today → today+5, irrigation planning). "
                                                                            "The system auto-detects the best mode based on your date selection.",
                                                                        ],
                                                                        className="text-muted",
                                                                    ),
                                                                ]
                                                            ),
                                                        ],
                                                        className="d-flex align-items-start",
                                                    )
                                                ]
                                            )
                                        ],
                                        className="mb-2 border-start border-primary border-3",
                                    ),
                                    # Step 3
                                    dbc.Card(
                                        [
                                            dbc.CardBody(
                                                [
                                                    html.Div(
                                                        [
                                                            dbc.Badge(
                                                                "3",
                                                                color="primary",
                                                                className="me-3",
                                                                style={
                                                                    "fontSize": "1.2rem",
                                                                    "padding": "8px 14px",
                                                                    "borderRadius": "50%",
                                                                },
                                                            ),
                                                            html.Div(
                                                                [
                                                                    html.H6(
                                                                        "Click Calculate ETo",
                                                                        className="mb-1",
                                                                    ),
                                                                    html.Small(
                                                                        [
                                                                            "The system automatically: fetches data from multiple APIs, "
                                                                            "applies preprocessing (outlier detection, gap filling), "
                                                                            "fuses sources via ",
                                                                            html.Strong(
                                                                                "Adaptive Kalman Filter"
                                                                            ),
                                                                            ", calculates ETo using ",
                                                                            html.Strong(
                                                                                "FAO-56 Penman-Monteith"
                                                                            ),
                                                                            ", and displays interactive results. "
                                                                            "Real-time progress is shown via WebSocket.",
                                                                        ],
                                                                        className="text-muted",
                                                                    ),
                                                                ]
                                                            ),
                                                        ],
                                                        className="d-flex align-items-start",
                                                    )
                                                ]
                                            )
                                        ],
                                        className="mb-3 border-start border-primary border-3",
                                    ),
                                    dbc.Alert(
                                        [
                                            html.I(
                                                className="bi bi-lightning-charge-fill me-2"
                                            ),
                                            html.Strong("Fully Automatic: "),
                                            "Source selection, data fusion, preprocessing, and ETo calculation "
                                            "are entirely automatic. No manual configuration needed.",
                                        ],
                                        color="success",
                                        className="mb-0",
                                    ),
                                ]
                            )
                        ],
                        className="mb-4 shadow-sm",
                    ),
                ],
                width=12,
            )
        ]
    )


def _create_operation_modes_section():
    """Describes the 3 operational modes."""
    return dbc.Row(
        [
            dbc.Col(
                [
                    html.H2(
                        "📊 Operation Modes",
                        id="modos",
                        className="mb-4",
                        style={"color": "#2c3e50"},
                    ),
                    html.P(
                        "EVAonline operates in three modes, automatically selected "
                        "based on the date range you choose. Each mode uses different "
                        "data sources optimized for that time period.",
                        className="text-muted mb-3",
                    ),
                    dbc.Row(
                        [
                            # Historical
                            dbc.Col(
                                dbc.Card(
                                    [
                                        dbc.CardHeader(
                                            [
                                                html.I(
                                                    className="bi bi-clock-history me-2"
                                                ),
                                                html.Strong("Historical Data"),
                                            ],
                                            style={
                                                "background": "linear-gradient(135deg, #1565c0, #0d47a1)",
                                                "color": "white",
                                            },
                                        ),
                                        dbc.CardBody(
                                            [
                                                html.P(
                                                    "Long-term historical analysis for past periods.",
                                                    className="mb-3",
                                                ),
                                                html.Ul(
                                                    [
                                                        html.Li(
                                                            [
                                                                html.Strong(
                                                                    "Period: "
                                                                ),
                                                                "1990 → present ",
                                                                dbc.Badge(
                                                                    "2-day delay",
                                                                    color="warning",
                                                                    className="ms-1",
                                                                    pill=True,
                                                                ),
                                                            ]
                                                        ),
                                                        html.Li(
                                                            [
                                                                html.Strong(
                                                                    "Max request: "
                                                                ),
                                                                "90 days per request",
                                                            ]
                                                        ),
                                                        html.Li(
                                                            [
                                                                html.Strong(
                                                                    "Sources: "
                                                                ),
                                                                "NASA POWER + Open-Meteo Archive",
                                                            ]
                                                        ),
                                                        html.Li(
                                                            [
                                                                html.Strong(
                                                                    "Delivery: "
                                                                ),
                                                                "Processed asynchronously via Celery; "
                                                                "results sent by email (CSV/Excel)",
                                                            ]
                                                        ),
                                                    ],
                                                    className="small",
                                                ),
                                                dbc.Badge(
                                                    "Email required",
                                                    color="info",
                                                    className="mt-2 me-1",
                                                ),
                                                dbc.Badge(
                                                    "Async processing",
                                                    color="secondary",
                                                    className="mt-2",
                                                ),
                                            ]
                                        ),
                                    ],
                                    className="h-100 shadow-sm",
                                ),
                                md=4,
                                className="mb-3",
                            ),
                            # Recent
                            dbc.Col(
                                dbc.Card(
                                    [
                                        dbc.CardHeader(
                                            [
                                                html.I(
                                                    className="bi bi-calendar-check me-2"
                                                ),
                                                html.Strong("Recent Data"),
                                            ],
                                            style={
                                                "background": "linear-gradient(135deg, #2e7d32, #1b5e20)",
                                                "color": "white",
                                            },
                                        ),
                                        dbc.CardBody(
                                            [
                                                html.P(
                                                    "Recent climate data up to today.",
                                                    className="mb-3",
                                                ),
                                                html.Ul(
                                                    [
                                                        html.Li(
                                                            [
                                                                html.Strong(
                                                                    "Period: "
                                                                ),
                                                                "Last 7, 14, 21, or 30 days → today",
                                                            ]
                                                        ),
                                                        html.Li(
                                                            [
                                                                html.Strong(
                                                                    "Sources: "
                                                                ),
                                                                "NASA POWER + Open-Meteo Archive + "
                                                                "Open-Meteo Forecast (gap filling)",
                                                            ]
                                                        ),
                                                        html.Li(
                                                            [
                                                                html.Strong(
                                                                    "Delivery: "
                                                                ),
                                                                "Interactive dashboard with real-time progress",
                                                            ]
                                                        ),
                                                        html.Li(
                                                            [
                                                                html.Strong(
                                                                    "Gap filling: "
                                                                ),
                                                                "Open-Meteo Forecast fills the 2-day Archive delay",
                                                            ]
                                                        ),
                                                    ],
                                                    className="small",
                                                ),
                                                dbc.Badge(
                                                    "Instant results",
                                                    color="success",
                                                    className="mt-2",
                                                ),
                                            ]
                                        ),
                                    ],
                                    className="h-100 shadow-sm",
                                ),
                                md=4,
                                className="mb-3",
                            ),
                            # Forecast
                            dbc.Col(
                                dbc.Card(
                                    [
                                        dbc.CardHeader(
                                            [
                                                html.I(
                                                    className="bi bi-cloud-sun me-2"
                                                ),
                                                html.Strong("Forecast"),
                                            ],
                                            style={
                                                "background": "linear-gradient(135deg, #7b1fa2, #4a148c)",
                                                "color": "white",
                                            },
                                        ),
                                        dbc.CardBody(
                                            [
                                                html.P(
                                                    "ETo forecast for the next days.",
                                                    className="mb-3",
                                                ),
                                                html.Ul(
                                                    [
                                                        html.Li(
                                                            [
                                                                html.Strong(
                                                                    "Period: "
                                                                ),
                                                                "Today → today + 5 days (6 days total)",
                                                            ]
                                                        ),
                                                        html.Li(
                                                            [
                                                                html.Strong(
                                                                    "Sources (Global): "
                                                                ),
                                                                "Open-Meteo Forecast + MET Norway (YR.no)",
                                                            ]
                                                        ),
                                                        html.Li(
                                                            [
                                                                html.Strong(
                                                                    "Sources (USA): "
                                                                ),
                                                                "adds NWS Forecast + NWS Stations (NOAA)",
                                                            ]
                                                        ),
                                                        html.Li(
                                                            [
                                                                html.Strong(
                                                                    "Delivery: "
                                                                ),
                                                                "Interactive dashboard in real-time",
                                                            ]
                                                        ),
                                                    ],
                                                    className="small",
                                                ),
                                                dbc.Badge(
                                                    "Irrigation planning",
                                                    color="warning",
                                                    text_color="dark",
                                                    className="mt-2 me-1",
                                                ),
                                                dbc.Badge(
                                                    "4 sources (USA)",
                                                    color="info",
                                                    className="mt-2",
                                                ),
                                            ]
                                        ),
                                    ],
                                    className="h-100 shadow-sm",
                                ),
                                md=4,
                                className="mb-3",
                            ),
                        ]
                    ),
                    # Mode auto-detection note
                    dbc.Alert(
                        [
                            html.I(className="bi bi-info-circle-fill me-2"),
                            html.Strong("Auto-Detection: "),
                            "The system automatically selects the mode based on your dates. "
                            "Historical mode has a 2-day delay (data not yet available). "
                            "Recent mode covers up to today. "
                            "Forecast mode is for future dates.",
                        ],
                        color="light",
                        className="mt-2",
                    ),
                ],
                width=12,
            )
        ],
        className="mb-4",
    )


def _create_usa_stations_section():
    """USA NWS Stations automatic detection section."""
    return dbc.Row(
        [
            dbc.Col(
                [
                    html.H2(
                        "🇺🇸 USA Weather Stations (NOAA)",
                        id="usa-stations",
                        className="mb-4",
                        style={"color": "#2c3e50"},
                    ),
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.H5(
                                                        "Automatic NOAA Station Detection",
                                                        className="mb-3",
                                                    ),
                                                    html.P(
                                                        [
                                                            "When you select a point in the ",
                                                            html.Strong(
                                                                "Continental United States"
                                                            ),
                                                            " (lat 24°–49°N, lon 66°–125°W), EVAonline "
                                                            "automatically activates two additional data sources:",
                                                        ]
                                                    ),
                                                    html.Ol(
                                                        [
                                                            html.Li(
                                                                [
                                                                    html.Strong(
                                                                        "NWS Forecast: "
                                                                    ),
                                                                    "Official NOAA weather forecast for the grid point",
                                                                ]
                                                            ),
                                                            html.Li(
                                                                [
                                                                    html.Strong(
                                                                        "NWS Stations: "
                                                                    ),
                                                                    "Finds the nearest active station from ~1,800 NOAA stations",
                                                                ]
                                                            ),
                                                            html.Li(
                                                                "Fetches hourly real-time observations from that station"
                                                            ),
                                                            html.Li(
                                                                "Aggregates hourly data to daily values (Tmax, Tmin, RH, wind, etc.)"
                                                            ),
                                                            html.Li(
                                                                "Includes station data in the Kalman fusion as an additional source"
                                                            ),
                                                        ]
                                                    ),
                                                    dbc.Alert(
                                                        [
                                                            html.I(
                                                                className="bi bi-broadcast-pin me-2"
                                                            ),
                                                            html.Strong(
                                                                "Available in: "
                                                            ),
                                                            "Forecast mode only. When activated, an info card "
                                                            "displays station name, ID, distance, elevation, "
                                                            "and the latest observation values.",
                                                        ],
                                                        color="info",
                                                    ),
                                                ],
                                                md=7,
                                            ),
                                            dbc.Col(
                                                [
                                                    html.H6(
                                                        "Station Info Card Displays:",
                                                        className="mb-3",
                                                    ),
                                                    dbc.ListGroup(
                                                        [
                                                            dbc.ListGroupItem(
                                                                [
                                                                    html.I(
                                                                        className="bi bi-building me-2 text-primary"
                                                                    ),
                                                                    "Station name and ID (e.g., KDEN)",
                                                                ]
                                                            ),
                                                            dbc.ListGroupItem(
                                                                [
                                                                    html.I(
                                                                        className="bi bi-geo-alt me-2 text-danger"
                                                                    ),
                                                                    "Distance to selected point (km)",
                                                                ]
                                                            ),
                                                            dbc.ListGroupItem(
                                                                [
                                                                    html.I(
                                                                        className="bi bi-arrow-up me-2 text-success"
                                                                    ),
                                                                    "Station elevation (m)",
                                                                ]
                                                            ),
                                                            dbc.ListGroupItem(
                                                                [
                                                                    html.I(
                                                                        className="bi bi-thermometer-half me-2 text-warning"
                                                                    ),
                                                                    "Current temperature, humidity, wind",
                                                                ]
                                                            ),
                                                            dbc.ListGroupItem(
                                                                [
                                                                    html.I(
                                                                        className="bi bi-clock me-2 text-info"
                                                                    ),
                                                                    "Latest observation time (local)",
                                                                ]
                                                            ),
                                                        ],
                                                        flush=True,
                                                    ),
                                                    html.Hr(),
                                                    html.Small(
                                                        [
                                                            html.Strong(
                                                                "Coverage: "
                                                            ),
                                                            "Continental USA (excluding Alaska, Hawaii). "
                                                            "Bounding box: 24°N–49°N, 66°W–125°W.",
                                                        ],
                                                        className="text-muted",
                                                    ),
                                                ],
                                                md=5,
                                            ),
                                        ]
                                    ),
                                ]
                            )
                        ],
                        className="mb-4 shadow-sm border-info",
                    ),
                ],
                width=12,
            )
        ]
    )


def _create_results_section():
    """Describes all result tabs, tables, charts and statistics."""
    return dbc.Row(
        [
            dbc.Col(
                [
                    html.H2(
                        "📈 Results & Visualizations",
                        id="resultados",
                        className="mb-4",
                        style={"color": "#2c3e50"},
                    ),
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H5(
                                        "What You Get After Calculation",
                                        className="mb-4",
                                    ),
                                    # Result Tabs
                                    html.H6(
                                        "🗂️ Result Tabs",
                                        className="mb-2 text-primary",
                                    ),
                                    html.P(
                                        "Results are organized in tabs for easy navigation:",
                                        className="text-muted mb-2",
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        [
                                                            html.Strong(
                                                                "📋 Summary"
                                                            ),
                                                            html.Ul(
                                                                [
                                                                    html.Li(
                                                                        "Total ETo accumulated (mm)"
                                                                    ),
                                                                    html.Li(
                                                                        "Mean daily ETo (mm/day)"
                                                                    ),
                                                                    html.Li(
                                                                        "Max and min daily values"
                                                                    ),
                                                                    html.Li(
                                                                        "Days processed"
                                                                    ),
                                                                    html.Li(
                                                                        "Irrigation recommendations"
                                                                    ),
                                                                    html.Li(
                                                                        "Data sources used + fusion info"
                                                                    ),
                                                                ],
                                                                className="small mb-0",
                                                            ),
                                                        ]
                                                    ),
                                                    className="h-100",
                                                ),
                                                md=3,
                                                className="mb-2",
                                            ),
                                            dbc.Col(
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        [
                                                            html.Strong(
                                                                "📊 Data Tables"
                                                            ),
                                                            html.Ul(
                                                                [
                                                                    html.Li(
                                                                        "Daily complete data (all variables)"
                                                                    ),
                                                                    html.Li(
                                                                        "Tmax, Tmin, Tmean (°C)"
                                                                    ),
                                                                    html.Li(
                                                                        "Relative humidity (%)"
                                                                    ),
                                                                    html.Li(
                                                                        "Wind speed at 2m (m/s)"
                                                                    ),
                                                                    html.Li(
                                                                        "Solar radiation (MJ/m²/day)"
                                                                    ),
                                                                    html.Li(
                                                                        "Precipitation (mm), ETo (mm/day)"
                                                                    ),
                                                                ],
                                                                className="small mb-0",
                                                            ),
                                                        ]
                                                    ),
                                                    className="h-100",
                                                ),
                                                md=3,
                                                className="mb-2",
                                            ),
                                            dbc.Col(
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        [
                                                            html.Strong(
                                                                "📉 Charts"
                                                            ),
                                                            html.Ul(
                                                                [
                                                                    html.Li(
                                                                        "ETo vs Temperature (time series)"
                                                                    ),
                                                                    html.Li(
                                                                        "ETo vs Solar Radiation"
                                                                    ),
                                                                    html.Li(
                                                                        "Temperature, Radiation & Precipitation"
                                                                    ),
                                                                    html.Li(
                                                                        "ETo Heatmap (daily/weekly)"
                                                                    ),
                                                                    html.Li(
                                                                        "Box Plot (variable distribution)"
                                                                    ),
                                                                    html.Li(
                                                                        "Scatter plots (ETo correlations)"
                                                                    ),
                                                                ],
                                                                className="small mb-0",
                                                            ),
                                                        ]
                                                    ),
                                                    className="h-100",
                                                ),
                                                md=3,
                                                className="mb-2",
                                            ),
                                            dbc.Col(
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        [
                                                            html.Strong(
                                                                "📐 Statistics"
                                                            ),
                                                            html.Ul(
                                                                [
                                                                    html.Li(
                                                                        "Mean, median, std deviation"
                                                                    ),
                                                                    html.Li(
                                                                        "Quartiles (Q1, Q3)"
                                                                    ),
                                                                    html.Li(
                                                                        "Normality test (Shapiro-Wilk)"
                                                                    ),
                                                                    html.Li(
                                                                        "Trend analysis"
                                                                    ),
                                                                    html.Li(
                                                                        "Seasonality analysis"
                                                                    ),
                                                                    html.Li(
                                                                        "Correlation matrix"
                                                                    ),
                                                                ],
                                                                className="small mb-0",
                                                            ),
                                                        ]
                                                    ),
                                                    className="h-100",
                                                ),
                                                md=3,
                                                className="mb-2",
                                            ),
                                        ]
                                    ),
                                    html.Hr(),
                                    # Interactive Charts
                                    html.H6(
                                        "📉 Interactive Charts (Plotly)",
                                        className="mt-3 mb-2 text-primary",
                                    ),
                                    html.P(
                                        "All charts are fully interactive: zoom, pan, hover for values, "
                                        "and download as PNG. Built with Plotly.",
                                        className="text-muted small mb-3",
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        [
                                                            html.I(
                                                                className="bi bi-graph-up text-primary",
                                                                style={
                                                                    "fontSize": "1.5rem"
                                                                },
                                                            ),
                                                            html.P(
                                                                "ETo vs Temperature",
                                                                className="mb-0 mt-2 small fw-bold",
                                                            ),
                                                            html.Small(
                                                                "Time series: Tmax, Tmin, and ETo overlay",
                                                                className="text-muted",
                                                            ),
                                                        ],
                                                        className="text-center p-3",
                                                    ),
                                                    className="h-100",
                                                ),
                                                md=3,
                                                className="mb-2",
                                            ),
                                            dbc.Col(
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        [
                                                            html.I(
                                                                className="bi bi-sun text-warning",
                                                                style={
                                                                    "fontSize": "1.5rem"
                                                                },
                                                            ),
                                                            html.P(
                                                                "ETo vs Radiation",
                                                                className="mb-0 mt-2 small fw-bold",
                                                            ),
                                                            html.Small(
                                                                "Correlation between ETo and solar radiation",
                                                                className="text-muted",
                                                            ),
                                                        ],
                                                        className="text-center p-3",
                                                    ),
                                                    className="h-100",
                                                ),
                                                md=3,
                                                className="mb-2",
                                            ),
                                            dbc.Col(
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        [
                                                            html.I(
                                                                className="bi bi-droplet text-info",
                                                                style={
                                                                    "fontSize": "1.5rem"
                                                                },
                                                            ),
                                                            html.P(
                                                                "Multivariate Panel",
                                                                className="mb-0 mt-2 small fw-bold",
                                                            ),
                                                            html.Small(
                                                                "Temp, Radiation & Precipitation combined",
                                                                className="text-muted",
                                                            ),
                                                        ],
                                                        className="text-center p-3",
                                                    ),
                                                    className="h-100",
                                                ),
                                                md=3,
                                                className="mb-2",
                                            ),
                                            dbc.Col(
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        [
                                                            html.I(
                                                                className="bi bi-grid-3x3 text-danger",
                                                                style={
                                                                    "fontSize": "1.5rem"
                                                                },
                                                            ),
                                                            html.P(
                                                                "ETo Heatmap",
                                                                className="mb-0 mt-2 small fw-bold",
                                                            ),
                                                            html.Small(
                                                                "Daily/weekly heat map of ETo values",
                                                                className="text-muted",
                                                            ),
                                                        ],
                                                        className="text-center p-3",
                                                    ),
                                                    className="h-100",
                                                ),
                                                md=3,
                                                className="mb-2",
                                            ),
                                        ]
                                    ),
                                    html.Hr(),
                                    # Downloads
                                    html.H6(
                                        "💾 Data Export",
                                        className="mt-3 mb-2 text-primary",
                                    ),
                                    html.Div(
                                        [
                                            dbc.Badge(
                                                [
                                                    html.I(
                                                        className="bi bi-filetype-csv me-1"
                                                    ),
                                                    "Download CSV",
                                                ],
                                                color="success",
                                                className="me-2 p-2",
                                            ),
                                            dbc.Badge(
                                                [
                                                    html.I(
                                                        className="bi bi-file-earmark-excel me-1"
                                                    ),
                                                    "Download Excel",
                                                ],
                                                color="success",
                                                className="me-2 p-2",
                                            ),
                                            dbc.Badge(
                                                [
                                                    html.I(
                                                        className="bi bi-envelope me-1"
                                                    ),
                                                    "Email (Historical mode)",
                                                ],
                                                color="info",
                                                className="p-2",
                                            ),
                                        ]
                                    ),
                                ]
                            )
                        ],
                        className="mb-4 shadow-sm",
                    ),
                ],
                width=12,
            )
        ]
    )


def _create_variables_section():
    """Explains each climate variable used in ETo calculation."""
    variables = [
        {
            "symbol": "T2M",
            "name": "Mean Temperature",
            "unit": "°C",
            "desc": "Air temperature at 2m height, daily mean",
        },
        {
            "symbol": "T2M_MAX",
            "name": "Maximum Temperature",
            "unit": "°C",
            "desc": "Daily maximum air temperature at 2m",
        },
        {
            "symbol": "T2M_MIN",
            "name": "Minimum Temperature",
            "unit": "°C",
            "desc": "Daily minimum air temperature at 2m",
        },
        {
            "symbol": "RH2M",
            "name": "Relative Humidity",
            "unit": "%",
            "desc": "Mean relative humidity at 2m height",
        },
        {
            "symbol": "WS2M",
            "name": "Wind Speed",
            "unit": "m/s",
            "desc": "Wind speed at 2m height (converted from 10m using FAO-56 Eq. 47, factor 0.748)",
        },
        {
            "symbol": "ALLSKY_SFC_SW_DWN",
            "name": "Solar Radiation",
            "unit": "MJ/m²/day",
            "desc": "All-sky surface downward shortwave radiation, adjusted for elevation",
        },
        {
            "symbol": "PRECTOTCORR",
            "name": "Precipitation",
            "unit": "mm/day",
            "desc": "Total corrected precipitation",
        },
        {
            "symbol": "ETo",
            "name": "Reference Evapotranspiration",
            "unit": "mm/day",
            "desc": "Calculated using FAO-56 Penman-Monteith equation",
        },
    ]

    rows = []
    for v in variables:
        rows.append(
            html.Tr(
                [
                    html.Td(
                        html.Code(v["symbol"]),
                        className="fw-bold",
                    ),
                    html.Td(v["name"]),
                    html.Td(
                        dbc.Badge(
                            v["unit"],
                            color="light",
                            text_color="dark",
                        )
                    ),
                    html.Td(
                        html.Small(
                            v["desc"],
                            className="text-muted",
                        )
                    ),
                ]
            )
        )

    return dbc.Row(
        [
            dbc.Col(
                [
                    html.H2(
                        "🔬 Climate Variables",
                        id="variables",
                        className="mb-4",
                        style={"color": "#2c3e50"},
                    ),
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.P(
                                        "These are the climate variables used in the "
                                        "FAO-56 Penman-Monteith ETo calculation:",
                                        className="text-muted mb-3",
                                    ),
                                    dbc.Table(
                                        [
                                            html.Thead(
                                                html.Tr(
                                                    [
                                                        html.Th("Symbol"),
                                                        html.Th("Name"),
                                                        html.Th("Unit"),
                                                        html.Th("Description"),
                                                    ]
                                                )
                                            ),
                                            html.Tbody(rows),
                                        ],
                                        bordered=True,
                                        hover=True,
                                        responsive=True,
                                        size="sm",
                                    ),
                                ]
                            )
                        ],
                        className="mb-4 shadow-sm",
                    ),
                ],
                width=12,
            )
        ]
    )


def _create_data_sources_section():
    """Data sources — updated with all 6 real sources."""
    sources = [
        {
            "icon": "bi-cloud-sun",
            "name": "Open-Meteo Archive",
            "coverage": "Global (ERA5-Land reanalysis)",
            "resolution": "0.1° (~11 km)",
            "period": "1990 → present (2-day delay)",
            "variables": "T, RH, Wind, Radiation, Precipitation",
            "license": "CC-BY 4.0",
            "color": "primary",
            "modes": ["Historical", "Recent"],
            "url": "https://open-meteo.com/",
        },
        {
            "icon": "bi-cloud-arrow-down",
            "name": "Open-Meteo Forecast",
            "coverage": "Global (multi-model ensemble)",
            "resolution": "0.1° (~11 km)",
            "period": "today − 29d → today + 16d",
            "variables": "T, RH, Wind, Radiation, Precipitation",
            "license": "CC-BY 4.0",
            "color": "success",
            "modes": ["Recent (gap fill)", "Forecast"],
            "url": "https://open-meteo.com/",
        },
        {
            "icon": "bi-rocket-takeoff",
            "name": "NASA POWER",
            "coverage": "Global (MERRA-2 satellite + reanalysis)",
            "resolution": "0.5° (~55 km)",
            "period": "1981 → today (no delay)",
            "variables": "T, RH, Wind, Radiation",
            "license": "Public Domain",
            "color": "danger",
            "modes": ["Historical", "Recent"],
            "url": "https://power.larc.nasa.gov/",
        },
        {
            "icon": "bi-snow2",
            "name": "MET Norway (YR.no)",
            "coverage": "Global (Nordic focus)",
            "resolution": "1 km (Nordic), 10 km (Global)",
            "period": "today → today + 5 days",
            "variables": "T, RH, Wind, Precipitation",
            "license": "CC-BY 4.0",
            "color": "info",
            "modes": ["Forecast"],
            "url": "https://api.met.no/",
        },
        {
            "icon": "bi-flag",
            "name": "NWS Forecast (NOAA)",
            "coverage": "🇺🇸 Continental USA only",
            "resolution": "2.5 km grid",
            "period": "today → today + 6 days",
            "variables": "T, RH, Wind, Precipitation",
            "license": "Public Domain",
            "color": "warning",
            "modes": ["Forecast (USA)"],
            "url": "https://www.weather.gov/",
        },
        {
            "icon": "bi-broadcast-pin",
            "name": "NWS Stations (NOAA)",
            "coverage": "🇺🇸 ~1,800 active stations",
            "resolution": "Point observations",
            "period": "Hourly real-time observations",
            "variables": "T, RH, Wind, Radiation, Precipitation",
            "license": "Public Domain",
            "color": "dark",
            "modes": ["Forecast (USA)"],
            "url": "https://www.weather.gov/",
        },
    ]

    source_cards = []
    for src in sources:
        modes_badges = [
            dbc.Badge(
                m,
                color="light",
                text_color="dark",
                className="me-1",
            )
            for m in src["modes"]
        ]

        source_cards.append(
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.Div(
                                    [
                                        html.I(
                                            className=f"bi {src['icon']} me-2",
                                            style={"fontSize": "1.3rem"},
                                        ),
                                        html.Strong(src["name"]),
                                    ],
                                    className="mb-2",
                                ),
                                html.P(
                                    html.Small(
                                        src["coverage"],
                                        className="text-muted",
                                    ),
                                    className="mb-1",
                                ),
                                html.P(
                                    [
                                        html.I(className="bi bi-grid me-1"),
                                        html.Small(src["resolution"]),
                                    ],
                                    className="mb-1",
                                ),
                                html.P(
                                    [
                                        html.I(
                                            className="bi bi-calendar me-1"
                                        ),
                                        html.Small(src["period"]),
                                    ],
                                    className="mb-1",
                                ),
                                html.P(
                                    [
                                        html.I(
                                            className="bi bi-thermometer-half me-1"
                                        ),
                                        html.Small(src["variables"]),
                                    ],
                                    className="mb-2",
                                ),
                                html.Div(
                                    [
                                        html.Small(
                                            "Modes: ",
                                            className="text-muted me-1",
                                        ),
                                        *modes_badges,
                                    ],
                                    className="mb-2",
                                ),
                                html.A(
                                    [
                                        html.I(
                                            className="bi bi-box-arrow-up-right me-1"
                                        ),
                                        "Official Website",
                                    ],
                                    href=src["url"],
                                    target="_blank",
                                    className="btn btn-outline-secondary btn-sm",
                                    rel="noopener noreferrer",
                                ),
                            ],
                            className="p-3",
                        )
                    ],
                    className=f"h-100 border-start border-{src['color']} border-3",
                ),
                md=4,
                className="mb-3",
            )
        )

    return dbc.Row(
        [
            dbc.Col(
                [
                    html.H2(
                        "📡 Data Sources (6 APIs)",
                        id="fontes-dados",
                        className="mb-4",
                        style={"color": "#2c3e50"},
                    ),
                    html.P(
                        "EVAonline automatically integrates data from 6 sources. "
                        "Source selection is based on the operation mode and geographic location.",
                        className="text-muted mb-3",
                    ),
                    dbc.Row(source_cards),
                    # Elevation source
                    dbc.Alert(
                        [
                            html.I(className="bi bi-mountains me-2"),
                            html.Strong("Elevation: "),
                            "SRTM 30m via ",
                            html.A(
                                "OpenTopoData",
                                href="https://www.opentopodata.org/",
                                target="_blank",
                                className="alert-link",
                            ),
                            " (not a climate source, but essential for FAO-56 "
                            "atmospheric pressure correction). "
                            "Fallback: ASTER 30m for latitudes > 60°N or < 60°S.",
                        ],
                        color="light",
                    ),
                ],
                width=12,
            )
        ],
        className="mb-4",
    )


def _create_features_section():
    """Automatic features of the system."""
    return dbc.Row(
        [
            dbc.Col(
                [
                    html.H2(
                        "⚡ Automatic Features",
                        id="funcionalidades",
                        className="mb-4",
                        style={"color": "#2c3e50"},
                    ),
                    dbc.Row(
                        [
                            _feature_card(
                                "bi-geo-alt-fill",
                                "SRTM Elevation",
                                "Altitude obtained automatically via OpenTopoData (SRTM 30m) "
                                "for atmospheric pressure correction in FAO-56.",
                                "danger",
                            ),
                            _feature_card(
                                "bi-clock",
                                "Timezone Detection",
                                "Automatically detected from coordinates. "
                                "All dates are adjusted to local time.",
                                "primary",
                            ),
                            _feature_card(
                                "bi-shuffle",
                                "Multi-Source Fusion",
                                "Adaptive Kalman Ensemble Filter fuses multiple sources "
                                "with variance-based weighting. Two modes: Adaptive (Brazil, "
                                "with Xavier climatology) and Simple (Global).",
                                "success",
                            ),
                            _feature_card(
                                "bi-activity",
                                "Real-Time Progress",
                                "Track calculation progress via WebSocket with progress bar "
                                "and step-by-step messages.",
                                "info",
                            ),
                            _feature_card(
                                "bi-water",
                                "Ocean Detection",
                                "Points over the ocean are automatically detected "
                                "and calculation is blocked with a clear warning.",
                                "warning",
                            ),
                            _feature_card(
                                "bi-wind",
                                "Wind Height Conversion",
                                "Wind converted from 10m to 2m height "
                                "using FAO-56 Equation 47 (factor: 0.748).",
                                "secondary",
                            ),
                            _feature_card(
                                "bi-shield-check",
                                "Data Preprocessing",
                                "Automatic outlier detection (IQR method), gap filling, "
                                "and regional validation limits (Brazil: Xavier et al.; "
                                "Global: conservative world limits).",
                                "dark",
                            ),
                            _feature_card(
                                "bi-lightning-charge",
                                "Redis Cache",
                                "Results cached in Redis for fast repeated queries. "
                                "API rate limiting to prevent abuse.",
                                "primary",
                            ),
                            _feature_card(
                                "bi-flag",
                                "USA Auto-Detection",
                                "Points in Continental USA automatically activate "
                                "NWS Forecast + NWS Stations as additional data sources.",
                                "danger",
                            ),
                        ]
                    ),
                ],
                width=12,
            )
        ],
        className="mb-4",
    )


def _feature_card(icon, title, description, color):
    """Individual feature card."""
    return dbc.Col(
        dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.I(
                            className=f"bi {icon} text-{color}",
                            style={"fontSize": "1.8rem"},
                        ),
                        html.H6(title, className="mt-2 mb-1"),
                        html.Small(description, className="text-muted"),
                    ],
                    className="text-center p-3",
                )
            ],
            className="h-100 shadow-sm",
        ),
        md=4,
        className="mb-3",
    )


def _create_faq_section():
    """FAQ / Troubleshooting section."""
    faqs = [
        {
            "q": "Why do I need to provide an email for Historical mode?",
            "a": "Historical data requests can take 1-5 minutes to process "
            "(fetching from multiple APIs, preprocessing, fusion, ETo calculation). "
            "The task runs asynchronously via Celery, and results are delivered "
            "by email with CSV/Excel attachment.",
        },
        {
            "q": "Why is there a 2-day delay for recent data?",
            "a": "Open-Meteo Archive (ERA5-Land reanalysis) has a ~2 day latency. "
            "EVAonline automatically uses Open-Meteo Forecast to fill this gap, "
            "so you always get complete data up to today.",
        },
        {
            "q": "What happens if I click on the ocean?",
            "a": "The system detects ocean points automatically and blocks the "
            "calculation with a clear warning. Only land locations are supported.",
        },
        {
            "q": "Why are there more sources available for USA locations?",
            "a": "The Continental USA is covered by NOAA's NWS Forecast (gridded) "
            "and ~1,800 active NWS Stations with real-time hourly observations. "
            "These provide additional data for the Kalman fusion ensemble.",
        },
        {
            "q": "What is the Kalman Ensemble Filter?",
            "a": "An Adaptive Kalman Filter that fuses data from multiple sources, "
            "weighting each by its estimated variance. For Brazil, it uses Xavier "
            "BR-DWGD climatology (27 cities) as bias correction reference. "
            "For other locations, a Simple mode operates without climatology.",
        },
        {
            "q": "How accurate is EVAonline?",
            "a": "Validated against 17 Brazilian weather stations (Xavier et al. 2016, 2022) "
            "over 30 years. The Kalman fusion consistently outperforms any single "
            "data source. Details available in the About page.",
        },
        {
            "q": "What is the maximum period I can request?",
            "a": "Historical: up to 90 days per request (1990→present, 2-day delay). "
            "Recent: 7, 14, 21, or 30 days (instant). "
            "Forecast: 6 days (today → today+5).",
        },
    ]

    accordion_items = []
    for i, faq in enumerate(faqs):
        accordion_items.append(
            dbc.AccordionItem(
                html.P(faq["a"], className="mb-0"),
                title=faq["q"],
                item_id=f"faq-{i}",
            )
        )

    return dbc.Row(
        [
            dbc.Col(
                [
                    html.H2(
                        "❓ FAQ",
                        id="faq",
                        className="mb-4",
                        style={"color": "#2c3e50"},
                    ),
                    dbc.Accordion(
                        accordion_items,
                        start_collapsed=True,
                        className="mb-4",
                    ),
                ],
                width=12,
            )
        ]
    )


def _create_license_section():
    """Software license."""
    return dbc.Row(
        [
            dbc.Col(
                [
                    html.H2(
                        "📄 License & Citation",
                        id="licenca",
                        className="mb-4",
                        style={"color": "#2c3e50"},
                    ),
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.H5(
                                                        "GNU AGPL v3.0",
                                                        className="mb-3",
                                                    ),
                                                    html.P(
                                                        [
                                                            "Copyright © 2024 ",
                                                            html.Strong(
                                                                "Angela Cristina Cunha Soares"
                                                            ),
                                                            ", Patricia A. A. Marques, Carlos D. Maciel",
                                                        ]
                                                    ),
                                                    html.Div(
                                                        [
                                                            dbc.Badge(
                                                                "✅ Free to use",
                                                                color="success",
                                                                className="me-2 mb-2",
                                                            ),
                                                            dbc.Badge(
                                                                "✅ Open source",
                                                                color="success",
                                                                className="me-2 mb-2",
                                                            ),
                                                            dbc.Badge(
                                                                "✅ Modify & distribute",
                                                                color="success",
                                                                className="mb-2",
                                                            ),
                                                        ]
                                                    ),
                                                ],
                                                md=6,
                                            ),
                                            dbc.Col(
                                                [
                                                    html.H5(
                                                        "📖 How to Cite",
                                                        className="mb-3",
                                                    ),
                                                    dbc.Alert(
                                                        [
                                                            html.Strong(
                                                                "Soares, A. C. C., "
                                                            ),
                                                            "Marques, P. A. A., Maciel, C. D. (2025). ",
                                                            html.Em(
                                                                "EVAonline: An online system for reference "
                                                                "evapotranspiration calculation using multi-source "
                                                                "data fusion."
                                                            ),
                                                            " SoftwareX.",
                                                        ],
                                                        color="light",
                                                        className="small",
                                                    ),
                                                ],
                                                md=6,
                                            ),
                                        ]
                                    ),
                                ]
                            )
                        ],
                        className="mb-4 shadow-sm",
                    ),
                ],
                width=12,
            )
        ]
    )


# =============================================================================
# MAIN LAYOUT
# =============================================================================

documentation_layout = html.Div(
    [
        dbc.Container(
            [
                # Quick Nav
                dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                dbc.Nav(
                                    [
                                        dbc.NavLink(
                                            "🚀 Quick Start",
                                            href="#quick-start",
                                            external_link=True,
                                            className="text-decoration-none",
                                        ),
                                        dbc.NavLink(
                                            "📊 Operation Modes",
                                            href="#modos",
                                            external_link=True,
                                            className="text-decoration-none",
                                        ),
                                        dbc.NavLink(
                                            "🇺🇸 USA Stations",
                                            href="#usa-stations",
                                            external_link=True,
                                            className="text-decoration-none",
                                        ),
                                        dbc.NavLink(
                                            "📈 Results",
                                            href="#resultados",
                                            external_link=True,
                                            className="text-decoration-none",
                                        ),
                                        dbc.NavLink(
                                            "🔬 Variables",
                                            href="#variables",
                                            external_link=True,
                                            className="text-decoration-none",
                                        ),
                                        dbc.NavLink(
                                            "📡 Data Sources",
                                            href="#fontes-dados",
                                            external_link=True,
                                            className="text-decoration-none",
                                        ),
                                        dbc.NavLink(
                                            "⚡ Features",
                                            href="#funcionalidades",
                                            external_link=True,
                                            className="text-decoration-none",
                                        ),
                                        dbc.NavLink(
                                            "❓ FAQ",
                                            href="#faq",
                                            external_link=True,
                                            className="text-decoration-none",
                                        ),
                                        dbc.NavLink(
                                            "📄 License",
                                            href="#licenca",
                                            external_link=True,
                                            className="text-decoration-none",
                                        ),
                                    ],
                                    pills=True,
                                    justified=True,
                                    className="flex-wrap",
                                )
                            ]
                        )
                    ],
                    className="mb-4 shadow-sm",
                ),
                # All sections
                _create_quick_start_section(),
                _create_operation_modes_section(),
                _create_usa_stations_section(),
                _create_results_section(),
                _create_variables_section(),
                _create_data_sources_section(),
                _create_features_section(),
                _create_faq_section(),
                _create_license_section(),
                # Footer
                html.Hr(className="mt-5"),
                html.P(
                    [
                        "© 2024-2025 EVAonline | ",
                        html.A(
                            "ESALQ/USP",
                            href="https://www.esalq.usp.br",
                            target="_blank",
                        ),
                        " | Made with ",
                        html.I(className="bi bi-heart-fill text-danger"),
                        " in Brazil",
                    ],
                    className="text-center text-muted small mb-4",
                ),
            ],
            fluid=False,
            className="py-4",
        )
    ],
    style={"backgroundColor": "#f8f9fa", "minHeight": "100vh"},
)

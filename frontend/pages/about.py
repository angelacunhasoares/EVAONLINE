"""
Página Sobre do EVAonline - Sistema de cálculo de evapotranspiração de referência.
"""

import logging

import dash_bootstrap_components as dbc
from dash import html

logger = logging.getLogger(__name__)

# Layout da página Sobre
about_layout = html.Div(
    [
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                # Cabeçalho
                                html.Div(
                                    [
                                        html.H1(
                                            "Sobre o EVAonline",
                                            className="text-center mb-3",
                                            style={
                                                "color": "#2c3e50",
                                                "fontWeight": "bold",
                                            },
                                        ),
                                        html.P(
                                            "Sistema para cálculo de evapotranspiração de referência",
                                            className="text-center lead text-muted mb-4",
                                        ),
                                        html.Hr(className="my-4"),
                                    ]
                                ),
                                # Card: Descrição do Projeto
                                dbc.Card(
                                    [
                                        dbc.CardHeader(
                                            [
                                                html.H5(
                                                    "📋 Sobre o Projeto",
                                                    className="mb-0",
                                                )
                                            ]
                                        ),
                                        dbc.CardBody(
                                            [
                                                html.P(
                                                    [
                                                        "O ",
                                                        html.Strong(
                                                            "EVAonline"
                                                        ),
                                                        " é um sistema desenvolvido para auxiliar no cálculo da evapotranspiração ",
                                                        "de referência (ETo) utilizando dados meteorológicos de múltiplas fontes ",
                                                        "com fusão por Ensemble Kalman Filter (EnKF).",
                                                    ]
                                                ),
                                                html.P(
                                                    [
                                                        "Esta ferramenta integra tecnologias modernas de web mapping, processamento ",
                                                        "de dados climáticos e algoritmos de fusão para fornecer estimativas ",
                                                        "precisas de ETo para qualquer localização no mundo.",
                                                    ]
                                                ),
                                            ]
                                        ),
                                    ],
                                    className="mb-4 shadow-sm",
                                ),
                                # Card: Funcionalidades Principais
                                dbc.Card(
                                    [
                                        dbc.CardHeader(
                                            [
                                                html.H5(
                                                    "🎯 Funcionalidades Principais",
                                                    className="mb-0",
                                                )
                                            ]
                                        ),
                                        dbc.CardBody(
                                            [
                                                dbc.ListGroup(
                                                    [
                                                        dbc.ListGroupItem(
                                                            [
                                                                html.Span(
                                                                    "🌍",
                                                                    className="me-2",
                                                                ),
                                                                "Mapa mundial interativo para seleção de localizações",
                                                            ]
                                                        ),
                                                        dbc.ListGroupItem(
                                                            [
                                                                html.Span(
                                                                    "📊",
                                                                    className="me-2",
                                                                ),
                                                                "Cálculo de ETo com múltiplas fontes de dados climáticos",
                                                            ]
                                                        ),
                                                        dbc.ListGroupItem(
                                                            [
                                                                html.Span(
                                                                    "🔍",
                                                                    className="me-2",
                                                                ),
                                                                "Fusão de dados via Ensemble Kalman Filter (EnKF)",
                                                            ]
                                                        ),
                                                        dbc.ListGroupItem(
                                                            [
                                                                html.Span(
                                                                    "📈",
                                                                    className="me-2",
                                                                ),
                                                                "Visualização de resultados e histórico",
                                                            ]
                                                        ),
                                                        dbc.ListGroupItem(
                                                            [
                                                                html.Span(
                                                                    "💾",
                                                                    className="me-2",
                                                                ),
                                                                "Exportação de dados em múltiplos formatos",
                                                            ]
                                                        ),
                                                        dbc.ListGroupItem(
                                                            [
                                                                html.Span(
                                                                    "⭐",
                                                                    className="me-2",
                                                                ),
                                                                "Sistema de favoritos para locais de interesse",
                                                            ]
                                                        ),
                                                        dbc.ListGroupItem(
                                                            [
                                                                html.Span(
                                                                    "🕐",
                                                                    className="me-2",
                                                                ),
                                                                "Detecção automática de fuso horário",
                                                            ]
                                                        ),
                                                    ],
                                                    flush=True,
                                                )
                                            ]
                                        ),
                                    ],
                                    className="mb-4 shadow-sm",
                                ),
                                # Card: Informações Técnicas
                                dbc.Card(
                                    [
                                        dbc.CardHeader(
                                            [
                                                html.H5(
                                                    "🛠️ Informações Técnicas",
                                                    className="mb-0",
                                                )
                                            ]
                                        ),
                                        dbc.CardBody(
                                            [
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                html.H6(
                                                                    "🌐 Frontend",
                                                                    className="fw-bold mb-3",
                                                                ),
                                                                html.Ul(
                                                                    [
                                                                        html.Li(
                                                                            "Dash Plotly - Framework web"
                                                                        ),
                                                                        html.Li(
                                                                            "Bootstrap 5 - Interface responsiva"
                                                                        ),
                                                                        html.Li(
                                                                            "Leaflet - Mapas interativos"
                                                                        ),
                                                                        html.Li(
                                                                            "React Components - Interatividade"
                                                                        ),
                                                                    ],
                                                                    className="mb-0",
                                                                ),
                                                            ],
                                                            md=6,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                html.H6(
                                                                    "⚙️ Backend",
                                                                    className="fw-bold mb-3",
                                                                ),
                                                                html.Ul(
                                                                    [
                                                                        html.Li(
                                                                            "FastAPI - API REST moderna"
                                                                        ),
                                                                        html.Li(
                                                                            "PostgreSQL + PostGIS - Banco geográfico"
                                                                        ),
                                                                        html.Li(
                                                                            "Redis Cache - Otimização de performance"
                                                                        ),
                                                                        html.Li(
                                                                            "Celery Workers - Processamento assíncrono"
                                                                        ),
                                                                    ],
                                                                    className="mb-0",
                                                                ),
                                                            ],
                                                            md=6,
                                                        ),
                                                    ]
                                                )
                                            ]
                                        ),
                                    ],
                                    className="mb-4 shadow-sm",
                                ),
                                # Card: Metodologia Científica
                                dbc.Card(
                                    [
                                        dbc.CardHeader(
                                            [
                                                html.H5(
                                                    "🔬 Metodologia Científica",
                                                    className="mb-0",
                                                )
                                            ]
                                        ),
                                        dbc.CardBody(
                                            [
                                                html.P(
                                                    [
                                                        html.Strong(
                                                            "Método de Cálculo: "
                                                        ),
                                                        "Penman-Monteith padrão FAO-56",
                                                    ]
                                                ),
                                                html.P(
                                                    [
                                                        html.Strong(
                                                            "Fusão de Dados: "
                                                        ),
                                                        "Ensemble Kalman Filter (EnKF) para integração de múltiplas fontes",
                                                    ]
                                                ),
                                                html.P(
                                                    [
                                                        html.Strong(
                                                            "Fontes de Dados: "
                                                        ),
                                                        "Open-Meteo, NASA POWER, estações meteorológicas locais",
                                                    ]
                                                ),
                                                html.P(
                                                    [
                                                        html.Strong(
                                                            "Precisão: "
                                                        ),
                                                        "Calibração baseada em dados históricos e validação cruzada",
                                                    ]
                                                ),
                                            ]
                                        ),
                                    ],
                                    className="mb-4 shadow-sm",
                                ),
                                # Card: Desenvolvimento e Contato
                                dbc.Card(
                                    [
                                        dbc.CardHeader(
                                            [
                                                html.H5(
                                                    "👥 Desenvolvimento",
                                                    className="mb-0",
                                                )
                                            ]
                                        ),
                                        dbc.CardBody(
                                            [
                                                html.P(
                                                    [
                                                        "Desenvolvido por ",
                                                        html.Strong(
                                                            "Angela Cristina Cunha Soares"
                                                        ),
                                                        " como parte de projeto de pesquisa na ",
                                                        html.Strong(
                                                            "ESALQ/USP."
                                                        ),
                                                    ]
                                                ),
                                                html.P(
                                                    [
                                                        "Código fonte disponível em: ",
                                                        html.A(
                                                            "GitHub Repository",
                                                            href="https://github.com/angelacunhasoares/EVAonline_SoftwareX",
                                                            target="_blank",
                                                            className="text-decoration-none",
                                                        ),
                                                    ]
                                                ),
                                                html.P(
                                                    [
                                                        "Para mais informações, dúvidas ou colaborações:"
                                                    ]
                                                ),
                                                html.Ul(
                                                    [
                                                        html.Li(
                                                            [
                                                                html.Strong(
                                                                    "Email: "
                                                                ),
                                                                "angelacunhasoares@usp.br",
                                                            ]
                                                        ),
                                                        html.Li(
                                                            [
                                                                html.Strong(
                                                                    "Instituição: "
                                                                ),
                                                                "ESALQ/USP - Escola Superior de Agricultura Luiz de Queiroz",
                                                            ]
                                                        ),
                                                        html.Li(
                                                            [
                                                                html.Strong(
                                                                    "Localização: "
                                                                ),
                                                                "Piracicaba, São Paulo, Brasil",
                                                            ]
                                                        ),
                                                    ]
                                                ),
                                            ]
                                        ),
                                    ],
                                    className="shadow-sm",
                                ),
                            ],
                            lg=10,
                            className="mx-auto",
                        )
                    ]
                )
            ],
            fluid=False,
            className="py-4",
        )
    ]
)

logger.info("✅ Página Sobre do EVAonline carregada com sucesso")

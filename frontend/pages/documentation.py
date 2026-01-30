import logging

import dash_bootstrap_components as dbc
from dash import html

logger = logging.getLogger(__name__)

# =============================================================================
# FUNÇÕES AUXILIARES (DEVEM VIR ANTES DO LAYOUT)
# =============================================================================


def _create_usage_section():
    """Cria seção de como usar o sistema."""
    return dbc.Row(
        [
            dbc.Col(
                [
                    html.H2(
                        "🎯 Como Usar o EVAonline",
                        id="como-usar",
                        className="mb-4",
                        style={"color": "#2c3e50"},
                    ),
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H5(
                                        "Guia Passo a Passo", className="mb-3"
                                    ),
                                    dbc.ListGroup(
                                        [
                                            dbc.ListGroupItem(
                                                [
                                                    html.Span(
                                                        "1.",
                                                        className="fw-bold me-2",
                                                    ),
                                                    html.Strong(
                                                        "Acesse o Mapa: "
                                                    ),
                                                    "Na página inicial, você verá um mapa mundial interativo",
                                                ]
                                            ),
                                            dbc.ListGroupItem(
                                                [
                                                    html.Span(
                                                        "2.",
                                                        className="fw-bold me-2",
                                                    ),
                                                    html.Strong(
                                                        "Selecione uma Localização: "
                                                    ),
                                                    "Clique em qualquer ponto do mapa ou use o botão de localização automática (📍)",
                                                ]
                                            ),
                                            dbc.ListGroupItem(
                                                [
                                                    html.Span(
                                                        "3.",
                                                        className="fw-bold me-2",
                                                    ),
                                                    html.Strong(
                                                        "Salve Favoritos (Opcional): "
                                                    ),
                                                    "Use o botão 'Salvar Favorito' para guardar locais de interesse (máx. 10)",
                                                ]
                                            ),
                                            dbc.ListGroupItem(
                                                [
                                                    html.Span(
                                                        "4.",
                                                        className="fw-bold me-2",
                                                    ),
                                                    html.Strong(
                                                        "Calcule ETo: "
                                                    ),
                                                    "Clique em 'Calcular ETo' para ir para a página de cálculos",
                                                ]
                                            ),
                                            dbc.ListGroupItem(
                                                [
                                                    html.Span(
                                                        "5.",
                                                        className="fw-bold me-2",
                                                    ),
                                                    html.Strong(
                                                        "Configure o Período: "
                                                    ),
                                                    "Selecione as datas inicial e final para o cálculo",
                                                ]
                                            ),
                                            dbc.ListGroupItem(
                                                [
                                                    html.Span(
                                                        "6.",
                                                        className="fw-bold me-2",
                                                    ),
                                                    html.Strong(
                                                        "Escolha a Fonte de Dados: "
                                                    ),
                                                    "Selecione entre Open-Meteo, NASA POWER ou dados locais",
                                                ]
                                            ),
                                            dbc.ListGroupItem(
                                                [
                                                    html.Span(
                                                        "7.",
                                                        className="fw-bold me-2",
                                                    ),
                                                    html.Strong(
                                                        "Execute o Cálculo: "
                                                    ),
                                                    "Clique em 'Calcular ETo' e aguarde os resultados",
                                                ]
                                            ),
                                        ],
                                        flush=True,
                                        className="mb-3",
                                    ),
                                    html.H5(
                                        "📝 Dicas Importantes",
                                        className="mt-4 mb-3",
                                    ),
                                    dbc.Alert(
                                        [
                                            html.Strong("💡 Dica: "),
                                            "Para melhores resultados, selecione períodos com dados climáticos completos disponíveis",
                                        ],
                                        color="info",
                                        className="mb-2",
                                    ),
                                    dbc.Alert(
                                        [
                                            html.Strong("🌍 Nota: "),
                                            "O sistema detecta automaticamente o fuso horário da localização selecionada",
                                        ],
                                        color="info",
                                        className="mb-2",
                                    ),
                                    dbc.Alert(
                                        [
                                            html.Strong("📊 Observação: "),
                                            "Resultados são calculados usando o método Penman-Monteith FAO-56 com fusão de dados por EnKF",
                                        ],
                                        color="info",
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


def _create_methodology_section():
    """Cria seção sobre a metodologia científica."""
    return dbc.Row(
        [
            dbc.Col(
                [
                    html.H2(
                        "🔬 Metodologia Científica",
                        id="metodologia",
                        className="mb-4",
                        style={"color": "#2c3e50"},
                    ),
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H5(
                                        "Método Penman-Monteith FAO-56",
                                        className="mb-3",
                                    ),
                                    html.P(
                                        [
                                            "O EVAonline utiliza o ",
                                            html.Strong(
                                                "método Penman-Monteith padrão FAO-56"
                                            ),
                                            ", recomendado pela Organização das Nações Unidas para Agricultura e Alimentação ",
                                            "como padrão internacional para cálculo da evapotranspiração de referência (ETo).",
                                        ],
                                        className="mb-3",
                                    ),
                                    html.H6(
                                        "📐 Fórmula Principal:",
                                        className="mt-4 mb-2",
                                    ),
                                    html.Div(
                                        [
                                            html.P(
                                                "ETo = [0.408Δ(Rₙ - G) + γ(900/(T + 273))u₂(eₛ - eₐ)] / [Δ + γ(1 + 0.34u₂)]",
                                                className="text-center font-monospace bg-light p-3 rounded mb-3",
                                            )
                                        ]
                                    ),
                                    html.H6(
                                        "📊 Variáveis Utilizadas:",
                                        className="mt-4 mb-2",
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.Ul(
                                                        [
                                                            html.Li(
                                                                [
                                                                    html.Strong(
                                                                        "Δ:"
                                                                    ),
                                                                    " Declividade da curva de pressão de vapor",
                                                                ]
                                                            ),
                                                            html.Li(
                                                                [
                                                                    html.Strong(
                                                                        "Rₙ:"
                                                                    ),
                                                                    " Radiação líquida à superfície",
                                                                ]
                                                            ),
                                                            html.Li(
                                                                [
                                                                    html.Strong(
                                                                        "G:"
                                                                    ),
                                                                    " Fluxo de calor no solo",
                                                                ]
                                                            ),
                                                        ]
                                                    )
                                                ],
                                                md=6,
                                            ),
                                            dbc.Col(
                                                [
                                                    html.Ul(
                                                        [
                                                            html.Li(
                                                                [
                                                                    html.Strong(
                                                                        "γ:"
                                                                    ),
                                                                    " Constante psicrométrica",
                                                                ]
                                                            ),
                                                            html.Li(
                                                                [
                                                                    html.Strong(
                                                                        "T:"
                                                                    ),
                                                                    " Temperatura média do ar",
                                                                ]
                                                            ),
                                                            html.Li(
                                                                [
                                                                    html.Strong(
                                                                        "u₂:"
                                                                    ),
                                                                    " Velocidade do vento a 2m",
                                                                ]
                                                            ),
                                                            html.Li(
                                                                [
                                                                    html.Strong(
                                                                        "eₛ - eₐ:"
                                                                    ),
                                                                    " Déficit de pressão de vapor",
                                                                ]
                                                            ),
                                                        ]
                                                    )
                                                ],
                                                md=6,
                                            ),
                                        ]
                                    ),
                                    html.H5(
                                        "🔄 Fusão de Dados com Ensemble Kalman Filter (EnKF)",
                                        className="mt-4 mb-3",
                                    ),
                                    html.P(
                                        [
                                            "O sistema utiliza ",
                                            html.Strong(
                                                "Ensemble Kalman Filter (EnKF)"
                                            ),
                                            " para fusão de dados de múltiplas fontes climáticas, ",
                                            "proporcionando estimativas mais robustas e precisas de ETo.",
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


def _create_data_source_card(
    title, source, source_url, description, license, coverage, resolution
):
    """Cria card padronizado para fonte de dados."""
    return dbc.Card(
        [
            dbc.CardHeader(html.Strong(title)),
            dbc.CardBody(
                [
                    html.P(
                        [
                            html.Strong("Fonte: "),
                            html.A(source, href=source_url, target="_blank"),
                        ]
                    ),
                    html.P([html.Strong("Descrição: "), description]),
                    html.P([html.Strong("Licença: "), license]),
                    html.P([html.Strong("Cobertura: "), coverage]),
                    html.P([html.Strong("Resolução: "), resolution]),
                ]
            ),
        ],
        className="mb-3 shadow-sm",
    )


def _create_data_sources_section():
    """Cria seção sobre fontes de dados."""
    return dbc.Row(
        [
            dbc.Col(
                [
                    html.H2(
                        "📡 Fontes de Dados",
                        id="fontes-dados",
                        className="mb-4",
                        style={"color": "#2c3e50"},
                    ),
                    # Open-Meteo
                    _create_data_source_card(
                        "🌤️ Open-Meteo",
                        "Dados Climáticos em Tempo Real e Históricos",
                        "https://open-meteo.com/",
                        "Dados meteorológicos históricos e em tempo real",
                        "CC-BY 4.0",
                        "Cobertura global",
                        "Dados desde 1940, atualização horária",
                    ),
                    # NASA POWER
                    _create_data_source_card(
                        "🛰️ NASA POWER",
                        "Prediction Of Worldwide Energy Resources",
                        "https://power.larc.nasa.gov/",
                        "Dados de satélite e reanálise",
                        "Domínio Público",
                        "Cobertura global",
                        "Dados diários desde 1981",
                    ),
                    # OpenStreetMap
                    _create_data_source_card(
                        "🗺️ OpenStreetMap",
                        "Dados de Mapas e Geocoding",
                        "https://www.openstreetmap.org/",
                        "Dados geoespaciais colaborativos",
                        "ODbL",
                        "Cobertura global",
                        "Dados vetoriais atualizados constantemente",
                    ),
                ],
                width=12,
            )
        ]
    )


def _create_license_section():
    """Cria seção sobre a licença do software."""
    return dbc.Row(
        [
            dbc.Col(
                [
                    html.H2(
                        "📄 Licença",
                        id="licenca",
                        className="mb-4",
                        style={"color": "#2c3e50"},
                    ),
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H5(
                                        "GNU Affero General Public License v3.0",
                                        className="mb-3",
                                    ),
                                    html.P(
                                        [
                                            "Copyright © 2024 ",
                                            html.Strong(
                                                "Angela Cristina Cunha Soares"
                                            ),
                                            ", Patricia A. A. Marques, Carlos D. Maciel",
                                        ],
                                        className="mb-3",
                                    ),
                                    dbc.Alert(
                                        [
                                            html.Strong(
                                                "🚀 Software de Código Aberto"
                                            ),
                                            html.Br(),
                                            "O EVAonline é licenciado sob a GNU Affero General Public License v3.0 (AGPL-3.0).",
                                        ],
                                        color="success",
                                        className="mb-3",
                                    ),
                                    html.Div(
                                        [
                                            dbc.Badge(
                                                "✅ Livre para usar",
                                                color="success",
                                                className="me-2 mb-2",
                                            ),
                                            dbc.Badge(
                                                "✅ Modificar e distribuir",
                                                color="success",
                                                className="me-2 mb-2",
                                            ),
                                            dbc.Badge(
                                                "✅ Código fonte permanece aberto",
                                                color="success",
                                                className="me-2 mb-2",
                                            ),
                                            dbc.Badge(
                                                "✅ Uso em rede requer divulgação",
                                                color="success",
                                                className="mb-2",
                                            ),
                                        ],
                                        className="mb-3",
                                    ),
                                    html.A(
                                        [
                                            html.I(
                                                className="fab fa-github me-2"
                                            ),
                                            "Licença completa no GitHub",
                                        ],
                                        href="https://github.com/angelacunhasoares/EVAonline_SoftwareX/blob/main/LICENSE",
                                        target="_blank",
                                        className="btn btn-outline-success btn-sm",
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


def _create_citation_section():
    """Cria seção sobre como citar o software."""
    return dbc.Row(
        [
            dbc.Col(
                [
                    html.H2(
                        "📖 Como Citar",
                        id="citacao",
                        className="mb-4",
                        style={"color": "#2c3e50"},
                    ),
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.P(
                                        "Se você usar o EVAonline em sua pesquisa, por favor cite:",
                                        className="mb-3",
                                    ),
                                    dbc.Alert(
                                        [
                                            html.Strong("Soares, A. C. C., "),
                                            "Marques, P. A. A., Maciel, C. D. (2024). ",
                                            html.Em(
                                                "EVAonline: Sistema online para cálculo de evapotranspiração de referência."
                                            ),
                                            " SoftwareX. [Em submissão]",
                                        ],
                                        color="light",
                                        className="mb-3",
                                    ),
                                    html.H6("BibTeX:", className="mt-4 mb-2"),
                                    html.Pre(
                                        """@article{soares2024evaonline,
                        title = {EVAonline: Sistema online para cálculo de evapotranspiração de referência},
                        author = {Soares, Angela Cristina Cunha and Marques, Patricia A. A. and Maciel, Carlos D.},
                        journal = {SoftwareX},
                        year = {2024},
                        note = {Em submissão}
                        }""",
                                        style={
                                            "backgroundColor": "#f8f9fa",
                                            "padding": "15px",
                                            "borderRadius": "5px",
                                            "fontSize": "12px",
                                            "overflow": "auto",
                                        },
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


def _create_contact_section():
    """Cria seção de contato."""
    return dbc.Row(
        [
            dbc.Col(
                [
                    html.H2(
                        "📧 Contato",
                        id="contato",
                        className="mb-4",
                        style={"color": "#2c3e50"},
                    ),
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.P(
                                        "Para dúvidas, relatórios de bugs ou colaborações, entre em contato:",
                                        className="mb-3",
                                    ),
                                    html.Ul(
                                        [
                                            html.Li(
                                                [
                                                    html.Strong(
                                                        "Ângela Cristina Cunha Soares: "
                                                    ),
                                                    html.A(
                                                        "angelacunhasoares@usp.br",
                                                        href="mailto:angelacunhasoares@usp.br",
                                                    ),
                                                ]
                                            ),
                                            html.Li(
                                                [
                                                    html.Strong(
                                                        "Patricia A. A. Marques: "
                                                    ),
                                                    html.A(
                                                        "paamarques@usp.br",
                                                        href="mailto:paamarques@usp.br",
                                                    ),
                                                ]
                                            ),
                                            html.Li(
                                                [
                                                    html.Strong(
                                                        "Carlos D. Maciel: "
                                                    ),
                                                    html.A(
                                                        "carlos.maciel@unesp.br",
                                                        href="mailto:carlos.maciel@unesp.br",
                                                    ),
                                                ]
                                            ),
                                        ],
                                        className="mb-3",
                                    ),
                                    html.P(
                                        [
                                            html.Strong(
                                                "Repositório do GitHub: "
                                            ),
                                            html.A(
                                                "EVAonline_SoftwareX",
                                                href="https://github.com/angelacunhasoares/EVAonline_SoftwareX",
                                                target="_blank",
                                            ),
                                        ]
                                    ),
                                    html.P(
                                        [
                                            html.Strong("Instituição: "),
                                            "ESALQ/USP - Escola Superior de Agricultura Luiz de Queiroz",
                                        ]
                                    ),
                                ]
                            )
                        ],
                        className="shadow-sm",
                    ),
                ],
                width=12,
            )
        ]
    )


# =============================================================================
# LAYOUT PRINCIPAL (DEVE VIR DEPOIS DAS FUNÇÕES)
# =============================================================================

# Layout da página Documentação
documentation_layout = html.Div(
    [
        dbc.Container(
            [
                # Cabeçalho
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H1(
                                    "📚 Documentação EVAonline",
                                    className="text-center mb-3",
                                    style={
                                        "color": "#2c3e50",
                                        "fontWeight": "bold",
                                    },
                                ),
                                html.P(
                                    "Documentação completa do sistema de cálculo de evapotranspiração de referência",
                                    className="text-center lead text-muted mb-4",
                                ),
                                html.Hr(className="my-4"),
                            ],
                            width=12,
                        )
                    ]
                ),
                # Navegação Rápida
                dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.H5(
                                    "🔍 Navegação Rápida", className="mb-3"
                                ),
                                dbc.Nav(
                                    [
                                        dbc.NavLink(
                                            "Como Usar",
                                            href="#como-usar",
                                            external_link=True,
                                        ),
                                        dbc.NavLink(
                                            "Metodologia",
                                            href="#metodologia",
                                            external_link=True,
                                        ),
                                        dbc.NavLink(
                                            "Fontes de Dados",
                                            href="#fontes-dados",
                                            external_link=True,
                                        ),
                                        dbc.NavLink(
                                            "Licença",
                                            href="#licenca",
                                            external_link=True,
                                        ),
                                        dbc.NavLink(
                                            "Citação",
                                            href="#citacao",
                                            external_link=True,
                                        ),
                                        dbc.NavLink(
                                            "Contato",
                                            href="#contato",
                                            external_link=True,
                                        ),
                                    ],
                                    pills=True,
                                    fill=True,
                                ),
                            ]
                        )
                    ],
                    className="mb-4 shadow-sm",
                ),
                # Seção: Como Usar
                _create_usage_section(),
                # Seção: Metodologia Científica
                _create_methodology_section(),
                # Seção: Fontes de Dados
                _create_data_sources_section(),
                # Seção: Licença
                _create_license_section(),
                # Seção: Citação
                _create_citation_section(),
                # Seção: Contato
                _create_contact_section(),
            ],
            fluid=False,
            className="py-4",
        )
    ]
)

logger.info("✅ Página Documentação do EVAonline carregada com sucesso")

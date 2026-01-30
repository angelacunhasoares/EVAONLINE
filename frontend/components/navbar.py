"""
Navbar profissional para ETO Calculator - Estilo Acadêmico.
Inclui logo, links internos + botão de tradução PT/EN.
"""

import dash_bootstrap_components as dbc
from dash import html


def create_navbar():
    """
    Cria navbar responsiva com estilo acadêmico profissional.
    Returns:
        dbc.Navbar: Navbar completa.
    """
    navbar = dbc.Navbar(
        [
            dbc.Container(
                [
                    # Brand com texto destacado (estilo acadêmico)
                    html.Div(
                        [
                            html.A(
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.I(
                                                    className="bi bi-droplet-fill me-2",
                                                    style={
                                                        "fontSize": "1.6rem",
                                                        "color": "#1a5f2a",
                                                    },
                                                ),
                                                html.Span(
                                                    "EVAonline",
                                                    style={
                                                        "fontSize": "1.6rem",
                                                        "fontWeight": "700",
                                                        "color": "#1a5f2a",
                                                        "letterSpacing": "-0.5px",
                                                    },
                                                ),
                                            ],
                                            style={
                                                "display": "flex",
                                                "alignItems": "center",
                                            },
                                        ),
                                        html.Div(
                                            "Web-based global reference EVApotranspiration estimate",
                                            style={
                                                "fontSize": "0.85rem",
                                                "fontWeight": "400",
                                                "color": "#5a6c7d",
                                                "lineHeight": "1.2",
                                                "marginTop": "2px",
                                                "marginLeft": "2px",
                                            },
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "flexDirection": "column",
                                    },
                                ),
                                href="/",
                                style={
                                    "textDecoration": "none",
                                },
                            ),
                        ],
                        className="navbar-brand",
                    ),
                    # Toggle para mobile - botão visível com ícone
                    dbc.Button(
                        html.I(
                            className="bi bi-list",
                            style={"fontSize": "1.5rem"},
                        ),
                        id="navbar-toggler",
                        className="d-lg-none",
                        color="secondary",
                        outline=True,
                        style={
                            "border": "1px solid #1a5f2a",
                            "color": "#1a5f2a",
                            "padding": "4px 10px",
                        },
                    ),
                    # Links principais + Botão de tradução (direita)
                    dbc.Collapse(
                        dbc.Nav(
                            [
                                # Links internos com estilo acadêmico
                                dbc.NavItem(
                                    dbc.NavLink(
                                        "HOME",
                                        href="/",
                                        id="nav-home",
                                        className="nav-link-academic",
                                        style={
                                            "fontWeight": "500",
                                            "fontSize": "0.9rem",
                                            "color": "#2c3e50",
                                            "textTransform": "uppercase",
                                            "letterSpacing": "0.5px",
                                            "padding": "8px 16px",
                                            "borderRadius": "4px",
                                            "transition": "all 0.2s ease",
                                        },
                                    )
                                ),
                                dbc.NavItem(
                                    dbc.NavLink(
                                        "DOCUMENTATION",
                                        href="/documentation",
                                        id="nav-documentation",
                                        className="nav-link-academic",
                                        style={
                                            "fontWeight": "500",
                                            "fontSize": "0.9rem",
                                            "color": "#2c3e50",
                                            "textTransform": "uppercase",
                                            "letterSpacing": "0.5px",
                                            "padding": "8px 16px",
                                            "borderRadius": "4px",
                                            "transition": "all 0.2s ease",
                                        },
                                    )
                                ),
                                dbc.NavItem(
                                    dbc.NavLink(
                                        "ABOUT",
                                        href="/about",
                                        id="nav-about",
                                        className="nav-link-academic",
                                        style={
                                            "fontWeight": "500",
                                            "fontSize": "0.9rem",
                                            "color": "#2c3e50",
                                            "textTransform": "uppercase",
                                            "letterSpacing": "0.5px",
                                            "padding": "8px 16px",
                                            "borderRadius": "4px",
                                            "transition": "all 0.2s ease",
                                        },
                                    )
                                ),
                                dbc.NavItem(
                                    dbc.NavLink(
                                        [
                                            html.I(
                                                className="bi bi-github me-2",
                                                style={"fontSize": "1rem"},
                                            ),
                                            "GITHUB",
                                        ],
                                        href="https://github.com/silvianesoares/EVAONLINE",
                                        target="_blank",
                                        id="nav-github",
                                        className="nav-link-academic",
                                        style={
                                            "fontWeight": "500",
                                            "fontSize": "0.9rem",
                                            "color": "#2c3e50",
                                            "textTransform": "uppercase",
                                            "letterSpacing": "0.5px",
                                            "padding": "8px 16px",
                                            "borderRadius": "4px",
                                            "display": "flex",
                                            "alignItems": "center",
                                            "transition": "all 0.2s ease",
                                        },
                                    )
                                ),
                                # Botão de Tradução (verde acadêmico)
                                dbc.NavItem(
                                    dbc.Button(
                                        html.Span(
                                            id="language-label",
                                            children="ENGLISH",
                                        ),
                                        id="language-toggle",
                                        className="ms-2",
                                        style={
                                            "backgroundColor": "#1a5f2a",
                                            "borderColor": "#1a5f2a",
                                            "fontWeight": "600",
                                            "fontSize": "0.85rem",
                                            "padding": "8px 20px",
                                            "textTransform": "uppercase",
                                            "letterSpacing": "0.5px",
                                            "borderRadius": "20px",
                                            "minWidth": "120px",
                                            "textAlign": "center",
                                            "boxShadow": "0 2px 4px rgba(26, 95, 42, 0.2)",
                                            "transition": "all 0.2s ease",
                                        },
                                    ),
                                    className="d-flex align-items-center",
                                ),
                            ],
                            className="ms-auto align-items-center",
                            navbar=True,
                        ),
                        id="navbar-collapse",
                        navbar=True,
                    ),
                ],
                fluid=False,
            ),
        ],
        color="light",
        className="navbar-expand-lg",
        style={
            "backgroundColor": "#ffffff",
            "borderBottom": "2px solid #e8f5e9",
            "padding": "10px 0",
            "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.06)",
        },
    )

    return navbar

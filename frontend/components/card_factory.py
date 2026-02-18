"""
Card Factory - Funções utilitárias para criação de cards padronizados.

Este módulo fornece funções reutilizáveis para criar componentes comuns
de UI, reduzindo duplicação de código em todo o projeto.
"""

from typing import List, Optional, Union

import dash_bootstrap_components as dbc
from dash import html


def create_standard_card(
    title: str,
    icon_class: str,
    body_content: Union[html.Div, List, dbc.CardBody],
    color: str = "primary",
    header_style: Optional[dict] = None,
    card_class: str = "mb-3 shadow-sm",
    card_id: Optional[str] = None,
) -> dbc.Card:
    """
    Cria card padronizado com header e body.

    Args:
        title: Título do card
        icon_class: Classe CSS do ícone (ex: "bi bi-clock", "fas fa-flask")
        body_content: Conteúdo do body (html.Div, lista ou dbc.CardBody)
        color: Cor do tema Bootstrap (primary, success, danger, etc.)
        header_style: Estilos CSS inline para o header (opcional)
        card_class: Classes CSS do card
        card_id: ID opcional para o card

    Returns:
        dbc.Card: Card formatado
    """
    default_header_style = {
        "background": f"linear-gradient(135deg, var(--bs-{color}), var(--bs-{color}-rgb))",
        "color": "white",
    }

    header = dbc.CardHeader(
        [
            html.I(className=f"{icon_class} me-2"),
            html.Strong(title),
        ],
        style=header_style or default_header_style,
    )

    # Se body_content já é CardBody, usar diretamente
    if isinstance(body_content, dbc.CardBody):
        body = body_content
    else:
        body = dbc.CardBody(body_content)

    card_props = {"className": card_class}
    if card_id:
        card_props["id"] = card_id

    return dbc.Card([header, body], **card_props)


def create_simple_card(
    title: str,
    icon_class: str,
    body_content: Union[html.Div, List],
    card_class: str = "mb-3 shadow-sm",
) -> dbc.Card:
    """
    Cria card simples com header H5 e body.

    Args:
        title: Título do card
        icon_class: Classe CSS do ícone
        body_content: Conteúdo do body
        card_class: Classes CSS do card

    Returns:
        dbc.Card: Card formatado
    """
    return dbc.Card(
        [
            dbc.CardHeader(
                html.H5(
                    [html.I(className=f"{icon_class} me-2"), title],
                    className="mb-0",
                )
            ),
            dbc.CardBody(body_content),
        ],
        className=card_class,
    )


def create_feature_list(
    items: List[str],
    icon: str = "✓",
    color: str = "success",
    item_class: str = "small",
) -> html.Ul:
    """
    Cria lista de features padronizada.

    Args:
        items: Lista de strings com os itens
        icon: Ícone/emoji para cada item (padrão: "✓")
        color: Cor do texto (success, danger, warning, etc.)
        item_class: Classes CSS adicionais para cada item

    Returns:
        html.Ul: Lista formatada
    """
    return html.Ul(
        [
            html.Li(
                f"{icon} {item}",
                className=f"{item_class} text-{color}",
            )
            for item in items
        ],
        className="mb-2",
    )


def create_bullet_list(
    items: List[str],
    bullet: str = "•",
    item_class: str = "small",
) -> html.Ul:
    """
    Cria lista com bullets padronizada.

    Args:
        items: Lista de strings com os itens
        bullet: Caractere do bullet (padrão: "•")
        item_class: Classes CSS para cada item

    Returns:
        html.Ul: Lista formatada
    """
    return html.Ul(
        [html.Li(f"{bullet} {item}", className=item_class) for item in items],
        className="mb-2",
    )


def create_info_badge(
    text: str,
    color: str = "primary",
    className: str = "",
    pill: bool = False,
) -> dbc.Badge:
    """
    Cria badge padronizado.

    Args:
        text: Texto do badge
        color: Cor Bootstrap (primary, success, danger, etc.)
        className: Classes CSS adicionais
        pill: Se True, usa formato pill arredondado

    Returns:
        dbc.Badge: Badge formatado
    """
    return dbc.Badge(
        text,
        color=color,
        pill=pill,
        className=f"me-2 mb-2 {className}".strip(),
    )


def create_step_card(
    step_number: int,
    title: str,
    description: Union[str, List],
    color: str = "primary",
    card_class: str = "mb-2 border-start border-3",
) -> dbc.Card:
    """
    Cria card de passo numerado (estilo wizard/tutorial).

    Args:
        step_number: Número do passo (1, 2, 3...)
        title: Título do passo
        description: Descrição (string ou lista de elementos)
        color: Cor do badge e borda
        card_class: Classes CSS do card

    Returns:
        dbc.Card: Card de passo formatado
    """
    if isinstance(description, str):
        desc_element = html.Small(description, className="text-muted")
    else:
        desc_element = html.Small(description, className="text-muted")

    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.Div(
                        [
                            dbc.Badge(
                                str(step_number),
                                color=color,
                                className="me-3",
                                style={
                                    "fontSize": "1.2rem",
                                    "padding": "8px 14px",
                                    "borderRadius": "50%",
                                },
                            ),
                            html.Div(
                                [
                                    html.H6(title, className="mb-1"),
                                    desc_element,
                                ]
                            ),
                        ],
                        className="d-flex align-items-start",
                    )
                ]
            )
        ],
        className=f"{card_class} border-{color}",
    )


def create_icon_feature_card(
    icon_class: str,
    title: str,
    description: str,
    color: str = "primary",
    card_class: str = "h-100 shadow-sm",
) -> dbc.Card:
    """
    Cria card de feature com ícone centralizado.

    Args:
        icon_class: Classe CSS do ícone (ex: "bi bi-geo-alt-fill")
        title: Título do feature
        description: Descrição curta
        color: Cor do ícone
        card_class: Classes CSS do card

    Returns:
        dbc.Card: Card de feature formatado
    """
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.I(
                        className=f"{icon_class} text-{color}",
                        style={"fontSize": "1.8rem"},
                    ),
                    html.H6(title, className="mt-2 mb-1"),
                    html.Small(description, className="text-muted"),
                ],
                className="text-center p-3",
            )
        ],
        className=card_class,
    )


def create_data_source_card(
    icon_class: str,
    name: str,
    coverage: str,
    resolution: str,
    period: str,
    variables: str,
    modes: List[str],
    border_color: str = "primary",
) -> dbc.Card:
    """
    Cria card de fonte de dados padronizado.

    Args:
        icon_class: Classe CSS do ícone
        name: Nome da fonte
        coverage: Cobertura geográfica
        resolution: Resolução espacial
        period: Período disponível
        variables: Variáveis disponíveis
        modes: Lista de modos de operação
        border_color: Cor da borda lateral

    Returns:
        dbc.Card: Card de fonte de dados formatado
    """
    modes_badges = [
        dbc.Badge(m, color="light", text_color="dark", className="me-1")
        for m in modes
    ]

    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.Div(
                        [
                            html.I(
                                className=f"bi {icon_class} me-2",
                                style={"fontSize": "1.3rem"},
                            ),
                            html.Strong(name),
                        ],
                        className="mb-2",
                    ),
                    html.P(
                        html.Small(coverage, className="text-muted"),
                        className="mb-1",
                    ),
                    html.P(
                        [
                            html.I(className="bi bi-grid me-1"),
                            html.Small(resolution),
                        ],
                        className="mb-1",
                    ),
                    html.P(
                        [
                            html.I(className="bi bi-calendar me-1"),
                            html.Small(period),
                        ],
                        className="mb-1",
                    ),
                    html.P(
                        [
                            html.I(className="bi bi-thermometer-half me-1"),
                            html.Small(variables),
                        ],
                        className="mb-2",
                    ),
                    html.Div(
                        [
                            html.Small("Modes: ", className="text-muted me-1"),
                            *modes_badges,
                        ]
                    ),
                ],
                className="p-3",
            )
        ],
        className=f"h-100 border-start border-{border_color} border-3",
    )


def create_alert_box(
    content: Union[str, List],
    icon_class: str = "bi bi-info-circle-fill",
    color: str = "info",
    className: str = "",
) -> dbc.Alert:
    """
    Cria caixa de alerta padronizada.

    Args:
        content: Conteúdo do alerta (string ou lista)
        icon_class: Classe CSS do ícone
        color: Cor do alerta (info, success, warning, danger, light)
        className: Classes CSS adicionais

    Returns:
        dbc.Alert: Alerta formatado
    """
    if isinstance(content, str):
        alert_content = [
            html.I(className=f"{icon_class} me-2"),
            content,
        ]
    else:
        alert_content = [
            html.I(className=f"{icon_class} me-2"),
            *content,
        ]

    return dbc.Alert(
        alert_content,
        color=color,
        className=className,
    )

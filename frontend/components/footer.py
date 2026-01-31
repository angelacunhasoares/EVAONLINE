"""
Componente de footer (rodapé) profissional para o ETO Calculator - Versão com 4 Colunas.
Colunas: Logo | Desenvolvedores | Parceiros | Links Importantes.
Inspirado em footers acadêmicos clean e responsivos.
"""

import logging
from datetime import datetime
from functools import lru_cache
from typing import Dict, List

import dash_bootstrap_components as dbc
from dash import html

logger = logging.getLogger(__name__)


class FooterManager:
    """Gerencia dados do footer com cache."""

    def __init__(self):
        self._current_year = datetime.now().year

    @property
    def current_year(self) -> int:
        return self._current_year

    @lru_cache(maxsize=1)
    def get_developer_data(self) -> List[Dict]:
        """Desenvolvedores com emails."""
        return [
            {
                "name": "Ângela S. M. C. Soares",
                "email": "angelasilviane@alumni.usp.br",
                "institution": "ESALQ/USP",
            },
            {
                "name": "Patricia A. A. Marques",
                "email": "paamarques@usp.br",
                "institution": "ESALQ/USP",
            },
            {
                "name": "Carlos D. Maciel",
                "email": "carlos.maciel@unesp.br",
                "institution": "UNESP",
            },
        ]

    @lru_cache(maxsize=1)
    def get_partner_data(self) -> Dict[str, str]:
        """Parceiros com URLs para logos."""
        return {
            "esalq": "https://www.esalq.usp.br/",
            "usp": "https://www.usp.br/",
            "fapesp": "https://fapesp.br/",
            "ibm": "https://www.ibm.com/br-pt",
            "c4ai": "https://c4ai.inova.usp.br/",
            "leb": "http://www.leb.esalq.usp.br/",
        }

    @lru_cache(maxsize=1)
    def get_logo_extensions(self) -> Dict[str, str]:
        """Extensões dos arquivos de logo (padrão: .svg)."""
        return {
            # Todos os logos agora são SVG
            "esalq": ".svg",
            "usp": ".svg",
            "fapesp": ".svg",
            "ibm": ".svg",
            "leb": ".svg",
        }

    def get_logo_path(self, partner: str) -> str:
        """Retorna o caminho completo do logo com a extensão correta."""
        extension = self.get_logo_extensions().get(partner, ".svg")
        return f"/assets/images/logo_{partner}{extension}"

    def get_email_link(self, email: str) -> str:
        """Link mailto simples."""
        return f"mailto:{email}"


# Instância global
footer_manager = FooterManager()


def create_footer(lang: str = "pt") -> html.Footer:
    """
    Cria footer profissional com 4 colunas responsivas.
    Args:
        lang: 'pt' ou 'en'.
    Returns:
        html.Footer: Footer columnar profissional.
    """
    logger.debug("🔄 Criando footer profissional com 3 colunas")
    try:
        texts = _get_footer_texts(lang)

        return html.Footer(
            [
                # Linha divisória sutil acima do footer
                html.Hr(className="m-0 footer-divider-top"),
                dbc.Container(
                    [
                        # ===== Linha Única: 3 Colunas =====
                        dbc.Row(
                            [
                                # Coluna 1: Desenvolvedores
                                dbc.Col(
                                    [
                                        html.H6(
                                            texts["developers"],
                                            className="mb-3 text-center footer-column-title",
                                        ),
                                        html.Ul(
                                            [
                                                html.Li(
                                                    [
                                                        html.Strong(
                                                            dev["name"],
                                                            className="d-block",
                                                        ),
                                                        html.Span(
                                                            f"{dev['institution']}",
                                                            className="text-muted small d-block mb-1",
                                                        ),
                                                        html.A(
                                                            dev["email"],
                                                            href=footer_manager.get_email_link(
                                                                dev["email"]
                                                            ),
                                                            className="footer-email-link small",
                                                        ),
                                                    ],
                                                    className="mb-3 list-unstyled",
                                                )
                                                for dev in footer_manager.get_developer_data()
                                            ],
                                            className="list-unstyled",
                                        ),
                                    ],
                                    md=4,
                                    className="mb-4 text-center",
                                ),
                                # Coluna 2: Parceiros (logos maiores)
                                dbc.Col(
                                    [
                                        html.H6(
                                            texts["partners"],
                                            className="mb-3 text-center footer-column-title",
                                        ),
                                        html.Div(
                                            [
                                                html.A(
                                                    html.Img(
                                                        src=footer_manager.get_logo_path(
                                                            partner
                                                        ),
                                                        alt=f"Logo {partner.upper()}",
                                                        className="footer-partner-logo logo-partner",
                                                    ),
                                                    href=url,
                                                    target="_blank",
                                                    rel="noopener noreferrer",
                                                    title=f"Visitar {partner.upper()}",
                                                    className="footer-partner-link",
                                                )
                                                for partner, url in footer_manager.get_partner_data().items()
                                            ],
                                            className="d-flex justify-content-center flex-wrap align-items-center",
                                        ),
                                    ],
                                    md=4,
                                    className="mb-4 text-center",
                                ),
                                # Coluna 3: Links Importantes (horizontal em uma linha)
                                dbc.Col(
                                    [
                                        html.H6(
                                            texts["links"],
                                            className="mb-3 text-center footer-column-title",
                                        ),
                                        html.Div(
                                            [
                                                html.A(
                                                    [
                                                        html.Img(
                                                            src="/assets/images/github.svg",
                                                            alt="GitHub",
                                                            className="footer-github-icon",
                                                        ),
                                                        html.Span(
                                                            "GitHub",
                                                            className="d-block small mt-1 footer-icon-label",
                                                        ),
                                                    ],
                                                    href=(
                                                        "https://github.com/"
                                                        "angelacunhasoares/"
                                                        "EVAonline_SoftwareX"
                                                    ),
                                                    target="_blank",
                                                    rel="noopener noreferrer",
                                                    title="Repositório GitHub",
                                                    className="footer-icon-link",
                                                ),
                                                html.A(
                                                    [
                                                        html.I(
                                                            className="bi bi-file-earmark-text footer-icon",
                                                        ),
                                                        html.Span(
                                                            "Licença",
                                                            className="d-block small mt-1 footer-icon-label",
                                                        ),
                                                    ],
                                                    href=(
                                                        "https://github.com/"
                                                        "angelacunhasoares/"
                                                        "EVAonline_SoftwareX?"
                                                        "tab=License-1-ov-file"
                                                    ),
                                                    target="_blank",
                                                    rel="noopener noreferrer",
                                                    title="Licença MIT",
                                                    className="footer-icon-link license-link",
                                                ),
                                                html.A(
                                                    [
                                                        html.I(
                                                            className="bi bi-book footer-icon",
                                                        ),
                                                        html.Span(
                                                            "Documentação",
                                                            className="d-block small mt-1 footer-icon-label",
                                                        ),
                                                    ],
                                                    href="/documentation",
                                                    title="Documentação",
                                                    className="footer-icon-link docs-link",
                                                ),
                                            ],
                                            className=(
                                                "d-flex justify-content-center "
                                                "align-items-center flex-wrap"
                                            ),
                                        ),
                                    ],
                                    md=4,
                                    className="mb-4 text-center",
                                ),
                            ],
                            className="py-4 justify-content-center",
                        ),
                        # Contador de Visitantes (tempo real)
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Div(
                                        [
                                            html.I(
                                                className="bi bi-people-fill me-2 footer-visitors",
                                            ),
                                            html.Span(
                                                "Visitantes: ",
                                                className="text-muted small",
                                            ),
                                            html.Strong(
                                                id="visitor-count",
                                                children="...",
                                                className="text-primary small",
                                            ),
                                            html.Span(
                                                " | Última hora: ",
                                                className="text-muted small ms-2",
                                            ),
                                            html.Strong(
                                                id="visitor-count-hourly",
                                                children="...",
                                                className="text-info small",
                                            ),
                                        ],
                                        className="text-center mb-2",
                                    ),
                                    width=12,
                                ),
                            ],
                        ),
                        # Linha de Copyright
                        html.Hr(className="my-2 footer-divider-copyright"),
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.P(
                                        [
                                            f"Copyright ©{footer_manager.current_year} ",
                                            html.Strong("EVAonline"),
                                            ". Open-source sob licença ",
                                            html.A(
                                                "AGPLv3",
                                                href="https://github.com/angelassilviane/EVAONLINE/blob/main/LICENSE",
                                                target="_blank",
                                                rel="noopener noreferrer",
                                                className="footer-license-link",
                                            ),
                                            ".",
                                        ],
                                        className="text-center mb-0 small text-muted",
                                    ),
                                    width=12,
                                ),
                            ],
                            className="mt-2",
                        ),
                    ],
                    fluid=False,
                    className="footer-container",
                ),
            ],
            className="bg-white footer-professional",
        )
    except Exception as e:
        logger.error(f"❌ Erro ao criar footer: {e}")
        return _create_fallback_footer()


def _get_footer_texts(lang: str) -> Dict:
    """Textos i18n."""
    texts = {
        "pt": {
            "developers": "Desenvolvedores",
            "partners": "Parceiros",
            "links": "Links Importantes",
        },
        "en": {
            "developers": "Developers",
            "partners": "Partners",
            "links": "Important Links",
        },
    }
    return texts.get(lang, texts["pt"])


def _create_fallback_footer():
    """Fallback simples."""
    return html.Footer(
        html.Div(
            html.P(
                "© 2025 ETO Calculator",
                className="text-center text-muted py-3 mb-0 small",
            ),
            className="bg-white border-top",
        )
    )


# Versão minimalista mantida para compatibilidade
def create_simple_footer(lang: str = "pt") -> html.Footer:
    """Versão minimalista."""
    texts = _get_footer_texts(lang)
    return html.Footer(
        dbc.Container(
            html.Div(
                [
                    html.P(
                        [
                            f"© {footer_manager.current_year} ETO Calculator | ",
                            html.A(
                                "Documentação",
                                href="/documentation",
                                className="text-muted",
                            ),
                            " | ",
                            html.A(
                                "Sobre", href="/about", className="text-muted"
                            ),
                            " | ",
                            html.A(
                                "ESALQ/USP",
                                href="https://www.esalq.usp.br/",
                                target="_blank",
                                className="text-muted",
                            ),
                        ],
                        className="text-center mb-0 small",
                    ),
                ],
                className="py-3",
            ),
            fluid=True,
            style={
                "paddingLeft": "40px",
                "paddingRight": "40px",
                "maxWidth": "100%",
            },
        ),
        className="bg-white border-top",
    )

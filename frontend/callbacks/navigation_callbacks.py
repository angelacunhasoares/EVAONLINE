"""
Callbacks para navegação entre páginas e controle de roteamento.

Features:
- Roteamento entre Home, Documentação e Sobre
- Toggle da navbar em dispositivos móveis
- Atualização dinâmica do título da página

NOTA: Navegação via NavLink usa href (browser nativo).
      Destaque de links ativos é feito em navbar_callbacks.py (via style).
"""

import logging

from dash import html
from dash.dependencies import Input, Output, State

# Layouts das páginas
from ..pages.home import home_layout
from ..pages.about import about_layout
from ..pages.documentation import documentation_layout

logger = logging.getLogger(__name__)


def register_navigation_callbacks(app):
    """
    Registra callbacks de navegação.

    Callbacks registrados:
    1. display_page: Roteamento baseado na URL
    2. toggle_navbar: Toggle da navbar em mobile
    3. clientside_callback: Atualização do título da página
    """

    # ================================================================
    # 1. ROTEAMENTO - Exibe página baseado na URL
    # ================================================================
    @app.callback(
        Output("page-content", "children"),
        Input("url", "pathname"),
    )
    def display_page(pathname):
        """
        Controla a exibição das páginas baseado na URL.

        Rotas:
        - /documentation → Página de documentação
        - /about → Página sobre
        - / (e qualquer outra) → Home (mapa + cálculo ETo)
        """
        logger.info(f"🧭 Navegando para: {pathname}")
        pages = {
            "/about": about_layout,
            "/documentation": documentation_layout,
        }
        # Qualquer rota não mapeada vai para home (incluindo "/" e "/eto-calculator")
        return pages.get(pathname, home_layout)

    # ================================================================
    # 2. TOGGLE NAVBAR - Dispositivos móveis
    # ================================================================
    @app.callback(
        Output("navbar-collapse", "is_open"),
        Input("navbar-toggler", "n_clicks"),
        State("navbar-collapse", "is_open"),
    )
    def toggle_navbar(n_clicks, is_open):
        """Alterna a navbar em dispositivos móveis."""
        if n_clicks:
            logger.debug("📱 Alternando estado da navbar")
            return not is_open
        return is_open

    # ================================================================
    # 3. TÍTULO DA PÁGINA - Clientside (sem round-trip ao servidor)
    # Usa Output dummy "url.hash" que não causa side effects
    # (hash é ignorado pelo Dash routing)
    # ================================================================
    app.clientside_callback(
        """
        function(pathname) {
            const titles = {
                '/': 'EVAonline: Home',
                '/eto-calculator': 'EVAonline: Calcular ETo',
                '/documentation': 'EVAonline: Documentation',
                '/about': 'EVAonline: About'
            };
            document.title = titles[pathname] || 'EVAonline';
            return window.dash_clientside.no_update;
        }
        """,
        Output("url", "hash"),
        Input("url", "pathname"),
    )

    logger.info("✅ Callbacks de navegação registrados com sucesso")

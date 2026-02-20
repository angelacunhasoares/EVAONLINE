"""
Registro centralizado de todos callbacks.
"""

import logging

logger = logging.getLogger(__name__)


def register_all_callbacks(app):
    """Registra todos callbacks ativos."""
    try:
        #  Callback principal da home (mapa leaflet + coordenadas)
        from .home_callbacks import (
            register_home_callbacks,
            register_layer_control_callbacks,
        )

        register_home_callbacks(app)
        register_layer_control_callbacks(app)  #  NOVO: Controle de camadas

        #  Callbacks de navegação (rotas)
        from .navigation_callbacks import register_navigation_callbacks

        register_navigation_callbacks(app)

        #  Callbacks da navbar (tradução PT/EN)
        from . import navbar_callbacks  # Importa para registrar os callbacks

        #  Callbacks da página ETo (com decoradores @callback)
        from . import eto_callbacks  # Importa para registrar automaticamente

        #  Callbacks de sessão (DEVE ser registrado ANTES do visitor_callbacks)
        from .cache_callbacks import register_cache_callbacks

        register_cache_callbacks(app)

        #  Callbacks do contador de visitantes (usa app-session-id)
        from . import (
            visitor_callbacks,
        )  # Importa para registrar automaticamente

        # from .selection_info_callbacks import (
        #     register_selection_info_callbacks
        # )
        # register_selection_info_callbacks(app)

        # from .location_sync_callbacks import register_location_sync_callbacks
        # register_location_sync_callbacks(app)

        logger.info(" Todos callbacks registrados!")
    except Exception as e:
        logger.error(f"❌ Erro ao registrar callbacks: {e}")
        raise

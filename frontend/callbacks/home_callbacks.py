"""
Callbacks para a página inicial - busca dados da API
"""

import json
import logging
import sys

import dash_bootstrap_components as dbc
import requests
from dash import Input, Output, State, html, callback_context
from dash.exceptions import PreventUpdate
from geopy.geocoders import Nominatim

from ..components.world_map_leaflet import (
    create_map_marker,
)

logger = logging.getLogger(__name__)

# Inicializar geocoder para reverse geocoding
geolocator = Nominatim(user_agent="evaonline_v1.0")


def register_home_callbacks(app):
    """Registra callbacks da página inicial."""

    @app.callback(
        Output("api-status-display", "children"),
        Input("interval-component", "n_intervals"),
    )
    def update_api_status(n_intervals):
        """Atualiza o status da API."""
        try:
            # Fazer chamada para a API de health
            response = requests.get(
                "http://localhost:8000/api/v1/health", timeout=5
            )
            data = response.json()

            # Criar cards com informações
            cards = [
                dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.H5(
                                    "Status da API", className="card-title"
                                ),
                                html.P(
                                    f"Serviço: {data.get('service', 'N/A')}",
                                    className="card-text",
                                ),
                                html.P(
                                    f"Versão: {data.get('version', 'N/A')}",
                                    className="card-text",
                                ),
                                html.P(
                                    f"Status: {data.get('status', 'N/A')}",
                                    className="card-text",
                                ),
                                dbc.Badge(
                                    (
                                        "Online"
                                        if data.get("status") == "ok"
                                        else "Offline"
                                    ),
                                    color=(
                                        "success"
                                        if data.get("status") == "ok"
                                        else "danger"
                                    ),
                                    className="mt-2",
                                ),
                            ]
                        )
                    ],
                    className="mb-3",
                )
            ]

            return cards

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao conectar com API: {e}")
            return dbc.Alert(
                f"Erro ao conectar com a API: {str(e)}",
                color="danger",
                className="mt-3",
            )
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            return dbc.Alert(
                f"Erro inesperado: {str(e)}", color="warning", className="mt-3"
            )

    @app.callback(
        Output("services-status-display", "children"),
        Input("interval-component", "n_intervals"),
    )
    def update_services_status(n_intervals):
        """Atualiza o status dos serviços."""
        try:
            # Fazer chamada para a API de status dos serviços
            response = requests.get(
                "http://localhost:8000/api/v1/api/internal/" "services/status",
                timeout=10,
            )
            data = response.json()

            # Criar cards para cada serviço
            service_cards = []

            for service_id, service_info in data.get("services", {}).items():
                status_color = (
                    "success"
                    if service_info.get("status") == "healthy"
                    else "danger"
                )

                card = dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.H6(
                                    service_info.get("name", service_id),
                                    className="card-title",
                                ),
                                html.P(
                                    f"Status: {service_info.get('status', 'unknown')}",
                                    className="card-text",
                                ),
                                dbc.Badge(
                                    (
                                        "Disponível"
                                        if service_info.get("available", False)
                                        else "Indisponível"
                                    ),
                                    color=status_color,
                                    className="mt-2",
                                ),
                            ]
                        )
                    ],
                    className="mb-2",
                )
                service_cards.append(card)

            # Card de resumo
            summary_card = dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.H5(
                                "Resumo dos Serviços", className="card-title"
                            ),
                            html.P(
                                f"Total: {data.get('total_services', 0)}",
                                className="card-text",
                            ),
                            html.P(
                                f"Saúde: {data.get('healthy_count', 0)}",
                                className="card-text",
                            ),
                        ]
                    )
                ],
                className="mb-3",
            )

            return [summary_card] + service_cards

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao conectar com API de serviços: {e}")
            return dbc.Alert(
                f"Erro ao conectar com a API de serviços: {str(e)}",
                color="danger",
                className="mt-3",
            )
        except Exception as e:
            logger.error(f"Erro inesperado nos serviços: {e}")
            return dbc.Alert(
                f"Erro inesperado: {str(e)}", color="warning", className="mt-3"
            )

    @app.callback(
        [
            Output("map-click-data", "data"),
            Output("selected-location-data", "data"),
            Output("navigation-coordinates", "data"),
            Output("marker-layer", "children"),
            Output("selected-coords-display", "children"),
            Output("calculate-eto-btn", "disabled"),
            Output("sidebar-location-display", "children"),
        ],
        Input("world-map", "clickData"),
        prevent_initial_call=True,
    )
    def handle_map_click(click_data):
        """
        Captura clique no mapa e habilita botões.

        Args:
            click_data: Dict com 'latlng' = [lat, lng] (lista de 2 números)

        Returns:
            tuple: (click_data, location_data, nav_coords, marker, coords_display, btn_disabled, sidebar_location)
        """
        # Display padrão para sidebar
        default_sidebar_location = dbc.Alert(
            [
                html.I(className="bi bi-hand-index-thumb me-2"),
                "Click on the map to select a point",
            ],
            color="secondary",
            className="mb-0 small py-2",
        )

        # DEBUG: Log sempre, mesmo se None
        logger.info(
            f"Callback disparado! click_data: "
            f"{json.dumps(click_data, indent=2) if click_data else 'None/Empty'}"
        )

        if not click_data or click_data == {}:
            logger.warning("click_data vazio ou None")
            debug_msg = html.Div(
                "Click on the map to select a location",
                className="alert alert-info small",
            )
            return (
                None,
                None,
                None,
                [],
                debug_msg,
                True,
                default_sidebar_location,
            )

        try:
            # Verifica estrutura do click_data
            if "latlng" not in click_data:
                logger.error(f"'latlng' ausente em click_data: {click_data}")
                error_msg = html.Div(
                    f"Error: Invalid structure - {click_data}",
                    className="alert alert-danger small",
                )
                return (
                    None,
                    None,
                    None,
                    [],
                    error_msg,
                    True,
                    default_sidebar_location,
                )

            latlng = click_data["latlng"]

            # dash-leaflet 1.x retorna latlng como LISTA [lat, lng]
            if isinstance(latlng, list) and len(latlng) >= 2:
                lat = latlng[0]
                lon = latlng[1]
            # Fallback para formato dict (versões antigas ou outras libs)
            elif isinstance(latlng, dict):
                lat = latlng.get("lat")
                lon = latlng.get("lng")
            else:
                logger.error(f"latlng malformado: {latlng}")
                error_msg = html.Div(
                    f"Error: Invalid latlng format - {latlng}",
                    className="alert alert-danger small",
                )
                return (
                    None,
                    None,
                    None,
                    [],
                    error_msg,
                    True,
                    default_sidebar_location,
                )

            logger.info(f"Click processed: LAT={lat:.6f}, LON={lon:.6f}")

            # Criar dados da localização
            location_data = {
                "lat": lat,
                "lon": lon,
            }

            # Criar marcador no mapa
            marker = create_map_marker(
                lat, lon, label=f"Lat: {lat:.4f}, Lon: {lon:.4f}"
            )

            # Criar display de coordenadas compacto
            coords_display = html.Div(
                [
                    html.Strong("Selected:"),
                    html.Br(),
                    html.Small(f"Lat: {lat:.6f}"),
                    html.Br(),
                    html.Small(f"Lon: {lon:.6f}"),
                ],
                className="text-center p-2 bg-light rounded",
            )

            # Criar display para o sidebar com coordenadas selecionadas
            sidebar_location = html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.I(
                                        className="bi bi-geo me-2 text-muted"
                                    ),
                                    html.Span(
                                        "Latitude:",
                                        className="text-muted small",
                                    ),
                                ],
                                className="d-flex align-items-center",
                            ),
                            html.Span(
                                f"{lat:.6f}°",
                                className="fw-bold text-success",
                            ),
                        ],
                        className="d-flex justify-content-between align-items-center mb-2",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.I(
                                        className="bi bi-geo me-2 text-muted"
                                    ),
                                    html.Span(
                                        "Longitude:",
                                        className="text-muted small",
                                    ),
                                ],
                                className="d-flex align-items-center",
                            ),
                            html.Span(
                                f"{lon:.6f}°",
                                className="fw-bold text-success",
                            ),
                        ],
                        className="d-flex justify-content-between align-items-center",
                    ),
                ],
                className="bg-light rounded p-2 border",
                style={"fontSize": "0.9rem"},
            )

            return (
                {"lat": lat, "lon": lon},  # map-click-data
                location_data,  # selected-location-data
                location_data,  # navigation-coordinates
                [marker],  # marker-layer
                coords_display,  # selected-coords-display
                True,  # calculate-eto-btn disabled - wait for data_type selection
                sidebar_location,  # sidebar-location-display
            )

        except KeyError as e:
            logger.error(f"KeyError em latlng: {e} - Dados: {click_data}")
            error_msg = html.Div(
                f"KeyError: {e}", className="alert alert-danger small"
            )
            return (
                None,
                None,
                None,
                [],
                error_msg,
                True,
                default_sidebar_location,
            )
        except Exception as e:
            logger.error(f"Erro geral: {e} - Stack: {sys.exc_info()}")
            error_msg = html.Div(
                f"Unexpected error: {str(e)}",
                className="alert alert-danger small",
            )
            return (
                None,
                None,
                None,
                [],
                error_msg,
                True,
                default_sidebar_location,
            )


def get_location_info(lat, lon):
    """
    Obtém informações geográficas usando reverse geocoding.

    Args:
        lat (float): Latitude
        lon (float): Longitude

    Returns:
        dict: Informações da localização
    """
    try:
        location = geolocator.reverse(
            f"{lat}, {lon}", language="pt", timeout=10
        )

        if not location:
            return {
                "city": "Local desconhecido",
                "country": "",
                "state": "",
                "timezone": "UTC",
                "display_name": f"Lat: {lat:.4f}, Lon: {lon:.4f}",
            }

        address = location.raw.get("address", {})

        # Extrair cidade (vários campos possíveis)
        city = (
            address.get("city")
            or address.get("town")
            or address.get("village")
            or address.get("municipality")
            or "Local desconhecido"
        )

        # Extrair país e estado
        country = address.get("country", "")
        state = address.get("state", "")

        return {
            "city": city,
            "country": country,
            "state": state,
            "timezone": "UTC",  # TODO: Calcular timezone real
            "display_name": location.address,
        }

    except Exception as e:
        logger.error(f"Erro no reverse geocoding: {e}")
        return {
            "city": "Erro ao obter localização",
            "country": "",
            "state": "",
            "timezone": "UTC",
            "display_name": f"Lat: {lat:.4f}, Lon: {lon:.4f}",
        }


def create_selection_info_card(location_data):
    """
    Cria card com coordenadas e botão de calcular ETo.

    Args:
        location_data (dict): Dados com 'lat' e 'lon'

    Returns:
        dbc.Card: Card com coordenadas e botão
    """
    lat = location_data.get("lat", 0)
    lon = location_data.get("lon", 0)

    card = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H5(
                        "Localizacao Selecionada",
                        className="card-title mb-3",
                    ),
                    html.Div(
                        [
                            html.P(
                                [
                                    html.Strong("Latitude: "),
                                    f"{lat:.6f}°",
                                ],
                                className="mb-2",
                            ),
                            html.P(
                                [
                                    html.Strong("Longitude: "),
                                    f"{lon:.6f}°",
                                ],
                                className="mb-3",
                            ),
                        ]
                    ),
                    # Botão de calcular
                    html.Div(
                        [
                            dbc.Button(
                                [
                                    html.I(className="bi bi-calculator me-2"),
                                    "Calcular ETo",
                                ],
                                id="calculate-eto-btn",
                                color="success",
                                size="sm",
                            ),
                        ],
                        className="d-flex gap-2",
                    ),
                ]
            )
        ],
        className="mt-3",
        color="light",
    )

    return card


# ========== CALLBACKS PARA CONTROLE CUSTOMIZADO DE CAMADAS ==========


def register_layer_control_callbacks(app):
    """Registra callbacks para o controle customizado de camadas."""
    # ✅ Importar apenas as funções que retornam listas de markers/componentes
    from ..components.world_map_leaflet import (
        load_brasil_geojson,
        load_matopiba_geojson,
        load_matopiba_cities_markers,
        load_piracicaba_marker,
    )

    # ✅ NOVO: Callback para controlar painel collapsible
    @app.callback(
        Output("layer-control-panel", "style"),
        [
            Input("layer-control-toggle", "n_clicks"),
            Input("layer-control-close", "n_clicks"),
        ],
        [State("layer-control-panel", "style")],
        prevent_initial_call=True,
    )
    def toggle_layer_panel(toggle_clicks, close_clicks, current_style):
        """Controla a visibilidade do painel de camadas collapsible."""
        ctx = callback_context

        if not ctx.triggered:
            return current_style

        # Identifica qual botão foi clicado
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if trigger_id == "layer-control-toggle":
            # Botao Toggle - alterna entre mostrar/ocultar
            if current_style.get("display") == "none":
                logger.info("Painel de camadas ABERTO")
                return {**current_style, "display": "block"}
            else:
                logger.info("Painel de camadas FECHADO (toggle)")
                return {**current_style, "display": "none"}

        elif trigger_id == "layer-control-close":
            # Botao Fechar - sempre oculta
            logger.info("Painel de camadas FECHADO (close)")
            return {**current_style, "display": "none"}

        return current_style

    @app.callback(
        Output("brasil-feature-group", "children"),
        Input("layer-brasil-toggle", "value"),
        prevent_initial_call=False,
    )
    def toggle_brasil_layer(selected):
        """Controla visibilidade da camada Brasil."""
        if selected and "brasil" in selected:
            brasil_geojson = load_brasil_geojson()
            # Retornar em lista para o FeatureGroup aceitar
            if brasil_geojson is not None:
                logger.debug(
                    f"Brasil GeoJSON carregado: {type(brasil_geojson)}"
                )
                return [brasil_geojson]
            else:
                logger.warning("Brasil GeoJSON retornou None")
                return []
        return []

    @app.callback(
        Output("matopiba-feature-group", "children"),
        Input("layer-matopiba-toggle", "value"),
        prevent_initial_call=False,
    )
    def toggle_matopiba_layer(selected):
        """Controla visibilidade da camada MATOPIBA."""
        if selected and "matopiba" in selected:
            matopiba_geojson = load_matopiba_geojson()
            # Retornar em lista para o FeatureGroup aceitar
            if matopiba_geojson is not None:
                logger.debug(
                    f"MATOPIBA GeoJSON carregado: {type(matopiba_geojson)}"
                )
                return [matopiba_geojson]
            else:
                logger.warning("MATOPIBA GeoJSON retornou None")
                return []
        return []

    @app.callback(
        Output("cities-feature-group", "children"),
        Input("layer-cities-toggle", "value"),
        prevent_initial_call=False,
    )
    def toggle_cities_layer(selected):
        """Controla visibilidade da camada de cidades."""
        if selected and "cities" in selected:
            cities_markers = load_matopiba_cities_markers()
            return cities_markers if cities_markers else []
        return []

    @app.callback(
        Output("piracicaba-feature-group", "children"),
        Input("layer-piracicaba-toggle", "value"),
        prevent_initial_call=False,
    )
    def toggle_piracicaba_layer(selected):
        """Controla visibilidade da camada Piracicaba."""
        if selected and "piracicaba" in selected:
            piracicaba_marker = load_piracicaba_marker()
            return [piracicaba_marker] if piracicaba_marker else []
        return []

    @app.callback(
        Output("navigation-coordinates", "data", allow_duplicate=True),
        Input("calculate-eto-btn", "n_clicks"),
        State("selected-location-data", "data"),
        prevent_initial_call=True,
    )
    def sync_coords_for_calculation(n_clicks, location_data):
        """
        Sincroniza coordenadas do mapa para o Store antes do calculo.

        NOTA: Na arquitetura unificada, NAO navegamos para outra pagina.
        O callback calculate_eto em eto_callbacks.py lera as coordenadas
        do navigation-coordinates Store.

        Args:
            n_clicks: Numero de cliques no botao
            location_data: Dict com {'lat': float, 'lon': float}

        Returns:
            dict: Coordenadas para o Store
        """
        logger.info(
            f"sync_coords_for_calculation: n_clicks={n_clicks}, location_data={location_data}"
        )

        if not n_clicks:
            logger.warning("Abortando - n_clicks vazio")
            raise PreventUpdate

        if not location_data:
            logger.warning("Sem coordenadas selecionadas")
            raise PreventUpdate

        lat = location_data.get("lat")
        lon = location_data.get("lon")

        if lat is not None and lon is not None:
            coords = {"lat": lat, "lon": lon}
            logger.info(f"Coordenadas sincronizadas para calculo: {coords}")
            return coords

        logger.warning("Coordenadas invalidas")
        raise PreventUpdate

    # =========================================================================
    # SIDEBAR TOGGLE CALLBACK
    # =========================================================================
    @app.callback(
        [
            Output("settings-sidebar", "is_open"),
            Output("main-content-area", "style"),
            Output("sidebar-state", "data"),
        ],
        Input("sidebar-toggle-btn", "n_clicks"),
        State("sidebar-state", "data"),
        prevent_initial_call=True,
    )
    def toggle_sidebar(n_clicks, current_state):
        """
        Alterna a visibilidade da sidebar de configuracoes.
        Ajusta a margem da area principal de acordo.
        """
        if not n_clicks:
            raise PreventUpdate

        new_state = not current_state if current_state is not None else False

        if new_state:
            # Sidebar aberta
            style = {
                "marginLeft": "320px",
                "transition": "margin-left 0.3s ease-in-out",
                "minHeight": "calc(100vh - 56px)",
            }
        else:
            # Sidebar fechada
            style = {
                "marginLeft": "0px",
                "transition": "margin-left 0.3s ease-in-out",
                "minHeight": "calc(100vh - 56px)",
            }

        logger.info(f"Sidebar toggled: {'open' if new_state else 'closed'}")
        return new_state, style, new_state

    logger.info("Callbacks de controle de camadas e sidebar registrados")

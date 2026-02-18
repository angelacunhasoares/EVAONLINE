"""
ETo Processing Service - EVAonline
ATUALIZADO PARA NOVA ARQUITETURA MODULAR (2025)

Agora usa:
- ClimateKalmanEnsemble → orquestrador principal
- ClimateFusion → fusão inteligente multi-fonte
- KalmanApplier → filtro Kalman em precipitação e ETo
- HistoricalDataLoader → referência climática local
"""

import math
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from loguru import logger

# Nova arquitetura modular
from backend.core.data_processing.climate_ensemble import ClimateKalmanEnsemble

# Serviços auxiliares
from backend.api.services.opentopo import OpenTopoClient
from backend.api.services.weather_utils import ElevationUtils
from backend.api.services.geographic_utils import GeographicUtils


class EToCalculationService:
    """Cálculo puro FAO-56 Penman-Monteith — sem I/O, sem fusão, sem Kalman"""

    STEFAN_BOLTZMANN = 4.903e-9
    ALBEDO = 0.23

    def __init__(self):
        self.logger = logger

    def _validate_measurements(self, measurements: Dict[str, float]) -> bool:
        required = [
            "T2M_MAX",
            "T2M_MIN",
            "T2M",
            "RH2M",
            "WS2M",
            "ALLSKY_SFC_SW_DWN",
            "latitude",
            "longitude",
            "date",
            "elevation_m",
        ]
        missing = [v for v in required if v not in measurements]
        if missing:
            raise ValueError(f"Variáveis ausentes: {', '.join(missing)}")

        if not GeographicUtils.is_valid_coordinate(
            measurements["latitude"], measurements["longitude"]
        ):
            raise ValueError("Coordenadas inválidas")

        if not (-500 <= measurements["elevation_m"] <= 9000):
            raise ValueError(
                f"Elevação inválida: {measurements['elevation_m']}m"
            )

        if measurements["T2M_MAX"] < measurements["T2M_MIN"]:
            raise ValueError("T2M_MAX < T2M_MIN")

        return True

    def calculate_et0(
        self,
        measurements: Dict[str, float],
        elevation_factors: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Calcula ETo FAO-56 Penman-Monteith.

        Args:
            measurements: Dados meteorológicos (T2M_MAX, T2M_MIN, T2M,
                         RH2M, WS2M, ALLSKY_SFC_SW_DWN, latitude,
                         elevation_m, date)
            elevation_factors: Dict com fatores de elevação pré-calculados
                              via ElevationUtils.get_elevation_correction
                              _factor(). Contém: pressure, gamma,
                              solar_factor

        Returns:
            Dict com et0_mm_day, quality, method, components

        Nota:
            Se elevation_factors não fornecido, calcula gamma internamente.
            RECOMENDADO: sempre fornecer elevation_factors para consistência.
        """
        try:
            self._validate_measurements(measurements)

            T_max = measurements["T2M_MAX"]
            T_min = measurements["T2M_MIN"]
            T_mean = measurements["T2M"]
            RH_mean = measurements["RH2M"]
            u2 = measurements["WS2M"]
            Rs = measurements["ALLSKY_SFC_SW_DWN"]
            z = measurements["elevation_m"]
            lat = measurements["latitude"]
            date_str = str(measurements["date"])

            # Usar gamma dos fatores pré-calculados ou calcular
            if elevation_factors and "gamma" in elevation_factors:
                gamma = float(elevation_factors["gamma"])
            else:
                # Fallback: calcular via ElevationUtils
                gamma = ElevationUtils.calculate_psychrometric_constant(z)
                logger.debug(
                    f"elevation_factors não fornecido, "
                    f"calculando gamma={gamma:.5f}"
                )

            # Cálculos FAO-56
            es = (
                self._saturation_vapor_pressure(T_max)
                + self._saturation_vapor_pressure(T_min)
            ) / 2
            ea = (RH_mean / 100.0) * es
            Vpd = es - ea
            slope = self._vapor_pressure_slope(T_mean)
            N = (
                datetime.strptime(date_str[:10], "%Y-%m-%d")
                .timetuple()
                .tm_yday
            )
            delta = self._solar_declination(N)
            Ra = self._extraterrestrial_radiation(lat, N, delta)

            Rn = (1 - self.ALBEDO) * Rs - 0.23 * Rs  # Aproximação simples
            G = 0

            numerator = (
                0.408 * slope * (Rn - G)
                + gamma * (900 / (T_mean + 273)) * u2 * Vpd
            )
            denominator = slope + gamma * (1 + 0.34 * u2)

            ET0 = max(0, numerator / denominator) if denominator != 0 else 0

            quality = "high" if 0.1 <= ET0 <= 15 else "low"

            return {
                "et0_mm_day": round(ET0, 2),
                "quality": quality,
                "method": "pm_fao56",
                "components": {
                    "Ra": round(Ra, 2),
                    "Rn": round(Rn, 2),
                    "slope": round(slope, 4),
                    "gamma": round(gamma, 4),
                },
            }

        except Exception as e:
            logger.error(f"Erro no cálculo ETo: {e}")
            return {"et0_mm_day": 0.0, "quality": "low", "error": str(e)}

    # Métodos auxiliares (mantidos iguais)
    def _saturation_vapor_pressure(self, T):
        return 0.6108 * math.exp((17.27 * T) / (T + 237.3))

    def _vapor_pressure_slope(self, T):
        return (4098 * 0.6108 * math.exp((17.27 * T) / (T + 237.3))) / (
            (T + 237.3) ** 2
        )

    def _solar_declination(self, N):
        return 0.409 * math.sin(2 * math.pi * (N - 81) / 365 - 1.39)

    def _extraterrestrial_radiation(self, lat, N, delta):
        phi = math.radians(lat)
        dr = 1 + 0.033 * math.cos(2 * math.pi * N / 365)
        omega_s = math.acos(-math.tan(phi) * math.tan(delta))
        Ra = (
            (24 * 60 / math.pi)
            * 0.0820
            * dr
            * (
                omega_s * math.sin(phi) * math.sin(delta)
                + math.cos(phi) * math.cos(delta) * math.sin(omega_s)
            )
        )
        return max(0, Ra)


class EToProcessingService:
    def __init__(self):
        self.et0_calc = EToCalculationService()
        self.ensemble = ClimateKalmanEnsemble()  # ← Orquestrador modular
        self.logger = logger

    async def process_location(
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
        sources: List[str],
        elevation: Optional[float] = None,
        use_precise_elevation: bool = True,
        enable_fusion: bool = False,  # 🔀 Controla fusão Kalman explicitamente
    ) -> Dict[str, Any]:
        warnings = []

        try:
            # 1. Elevação precisa
            final_elevation, elev_info = await self._get_best_elevation(
                latitude, longitude, elevation, use_precise_elevation
            )
            elevation_factors = ElevationUtils.get_elevation_correction_factor(
                final_elevation
            )

            # 2. Download de múltiplas fontes
            from backend.api.services.data_download import (
                download_weather_data,
            )

            multi_source_df, download_warnings = await download_weather_data(
                data_source=sources,
                data_inicial=start_date,
                data_final=end_date,
                latitude=latitude,
                longitude=longitude,
            )
            warnings.extend(download_warnings)

            if multi_source_df.empty:
                raise ValueError("Nenhuma fonte retornou dados")

            # 3. Pré-processamento (harmonização de colunas, unidades, etc.)
            from backend.core.data_processing.data_preprocessing import (
                preprocessing,
            )

            df_clean, prep_warnings = preprocessing(multi_source_df, latitude)
            warnings.extend(prep_warnings)

            # 4. DECISÃO: Fusão Kalman SOMENTE se enable_fusion=True
            if enable_fusion:
                # 🔀 SMART FUSION: usuário escolheu explicitamente
                logger.info(
                    f"🔀 Smart Fusion ativada pelo usuário: "
                    f"aplicando Kalman em {len(sources)} fonte(s)"
                )
                fused_df = self.ensemble.process(
                    df_multi_source=df_clean, lat=latitude, lon=longitude
                )
            else:
                # 🔵 FONTE ÚNICA OU DESABILITADA: usar dados originais
                sources_str = ", ".join(sources)
                logger.info(
                    f"🔵 Fusão desabilitada: usando dados originais "
                    f"de {sources_str} (sem fusão Kalman)"
                )
                fused_df = df_clean.copy()

                # Adicionar informação de fusão
                fused_df["fusion_mode"] = "single_source"
                fused_df["fusion_description"] = (
                    f"Dados originais de {sources_str} (sem fusão)"
                )
                fused_df["fusion_sources"] = sources_str

            if fused_df.empty:
                raise ValueError("Fusão resultou em DataFrame vazio")

            # Garantir que a coluna 'date' existe a partir do index
            logger.info(
                f"🔍 Verificando coluna 'date'. Index type: "
                f"{type(fused_df.index).__name__}, "
                f"Index name: {fused_df.index.name}, "
                f"Has 'date' column: {'date' in fused_df.columns}"
            )

            if "date" not in fused_df.columns:
                logger.warning("⚠️ Coluna 'date' não encontrada!")
                # Se o index é DatetimeIndex, criar coluna date a partir dele
                if isinstance(fused_df.index, pd.DatetimeIndex):
                    fused_df["date"] = fused_df.index
                    logger.info(
                        f"✅ Coluna 'date' criada a partir do index. "
                        f"Shape: {fused_df.shape}, primeiros valores: "
                        f"{fused_df['date'].head().tolist()}"
                    )
                else:
                    # Reset index e renomear se necessário
                    logger.info("🔄 Executando reset_index...")
                    fused_df.reset_index(inplace=True)
                    logger.info(
                        f"Colunas após reset_index: {list(fused_df.columns)}"
                    )

                    if "date" not in fused_df.columns:
                        # Tentar encontrar coluna temporal
                        for col in fused_df.columns:
                            if col in ["index", "time", "datetime"]:
                                fused_df.rename(
                                    columns={col: "date"}, inplace=True
                                )
                                logger.info(
                                    f"✅ Coluna '{col}' renomeada para 'date'"
                                )
                                break

                # Verificação final
                if "date" not in fused_df.columns:
                    raise ValueError(
                        f"Impossível criar coluna 'date'. "
                        f"Colunas disponíveis: {list(fused_df.columns)}"
                    )
            else:
                logger.info("✅ Coluna 'date' já existe!")

            # 5. Garantir et0_mm (caso não tenha sido calculado antes)
            if "et0_mm" not in fused_df.columns:
                fused_df = self._calculate_raw_eto(
                    fused_df,
                    latitude,
                    longitude,
                    final_elevation,
                    elevation_factors,
                )

            # 6. O ensemble já aplica Kalman em precipitação e ETo
            # eto_final e eto_evaonline já existem
            if "eto_final" not in fused_df.columns:
                fused_df["eto_final"] = fused_df["et0_mm"]
            if "eto_evaonline" not in fused_df.columns:
                fused_df["eto_evaonline"] = fused_df["eto_final"]

            # 7. Filtrar período solicitado
            fused_df["date"] = pd.to_datetime(fused_df["date"])
            mask = (fused_df["date"] >= start_date) & (
                fused_df["date"] <= end_date
            )
            result_df = fused_df[mask].copy()

            if result_df.empty:
                raise ValueError(
                    "Nenhum dado no período solicitado após fusão"
                )

            result_df["date"] = result_df["date"].dt.strftime("%Y-%m-%d")

            # 8. Montar resposta final
            cols = [
                "date",
                "T2M_MAX",
                "T2M_MIN",
                "T2M",
                "RH2M",
                "WS2M",
                "ALLSKY_SFC_SW_DWN",
                "PRECTOTCORR",
            ]
            if "eto_evaonline" in result_df.columns:
                cols.append("eto_evaonline")
            if "eto_openmeteo" in result_df.columns:
                cols.append("eto_openmeteo")

            final_series = result_df[cols].round(3)

            rename_map = {
                "T2M_MAX": "tmax_c",
                "T2M_MIN": "tmin_c",
                "T2M": "tmed_c",
                "RH2M": "humidity_pct",
                "WS2M": "wind_ms",
                "ALLSKY_SFC_SW_DWN": "radiation_mj_m2",
                "PRECTOTCORR": "precip_mm",
                "eto_evaonline": "et0_mm_day",
            }
            final_series = final_series.rename(columns=rename_map)

            logger.info(
                f"📊 Série final montada: {len(final_series)} registros. "
                f"Colunas: {list(final_series.columns)}"
            )

            # Modo de fusão
            mode = result_df["fusion_mode"].iloc[0]
            mode_text = (
                "Alta precisão (normais locais 1991-2020)"
                if mode == "high_precision"
                else "Cobertura global robusta"
            )

            return {
                "location": {
                    "lat": round(latitude, 4),
                    "lon": round(longitude, 4),
                },
                "elevation": elev_info,
                "period": {"start": start_date, "end": end_date},
                "sources_used": sources,
                "fusion_mode": mode,
                "fusion_description": mode_text,
                "et0_series": final_series.to_dict(orient="records"),
                "summary": self._summarize(final_series),
                "recommendations": self._generate_recommendations(
                    final_series
                ),
                "warnings": warnings,
                "message": (
                    f"ETo calculado com sucesso para "
                    f"{len(final_series)} dias"
                ),
            }

        except Exception as e:
            logger.error(f"Erro fatal no processamento ETo: {e}")
            import traceback

            traceback.print_exc()
            return {
                "error": str(e),
                "warnings": warnings,
            }

    async def _get_best_elevation(self, lat, lon, user_elev, use_precise):
        if user_elev is not None:
            return user_elev, {
                "value": user_elev,
                "source": "usuário",
                "no_data": False,
            }

        if use_precise:
            try:
                client = OpenTopoClient()
                result = await client.get_elevation(lat, lon)
                await client.close()
                if result and result.elevation is not None:
                    return result.elevation, {
                        "value": result.elevation,
                        "source": "OpenTopo",
                        "no_data": False,
                    }
            except Exception as e:
                logger.warning(f"Falha OpenTopo: {e}")

        # Fallback: SRTM/ASTER retornaram null → possível oceano/corpo d'água
        logger.warning(
            f"⚠️ Sem dados de elevação para ({lat}, {lon}) - "
            f"possível oceano ou corpo d'água"
        )
        return 0.0, {"value": 0.0, "source": "padrão", "no_data": True}

    def _calculate_raw_eto(self, df, lat, lon, elevation, factors):
        """Calcula ETo linha por linha usando FAO-56"""
        df["elevation_m"] = elevation
        et0_values = []

        # Garantir que temos a coluna date
        if "date" not in df.columns:
            if isinstance(df.index, pd.DatetimeIndex):
                df["date"] = df.index
            else:
                raise ValueError(
                    "DataFrame sem coluna 'date' e sem DatetimeIndex"
                )

        for _, row in df.iterrows():
            meas = row.to_dict()

            # Converter date para string no formato correto
            date_value = row.get("date", "")
            if pd.isna(date_value) or date_value == "":
                logger.warning(f"Linha sem data válida: {row}")
                et0_values.append(np.nan)
                continue

            # Garantir formato YYYY-MM-DD
            if isinstance(date_value, pd.Timestamp):
                date_str = date_value.strftime("%Y-%m-%d")
            else:
                date_str = str(date_value)[:10]

            meas.update(
                {
                    "latitude": lat,
                    "longitude": lon,
                    "date": date_str,
                    "elevation_m": elevation,
                }
            )

            try:
                result = self.et0_calc.calculate_et0(
                    meas, elevation_factors=factors
                )
                et0_values.append(result["et0_mm_day"])
            except Exception as e:
                logger.error(f"Erro ao calcular ETo para {date_str}: {e}")
                et0_values.append(np.nan)

        df["et0_mm"] = et0_values
        return df

    def _summarize(self, df):
        et0 = df["et0_mm_day"]
        return {
            "total_days": len(et0),
            "et0_total_mm": round(et0.sum(), 1),
            "et0_mean_mm_day": round(et0.mean(), 2),
            "et0_max_mm_day": round(et0.max(), 2),
            "et0_min_mm_day": round(et0.min(), 2),
        }

    def _generate_recommendations(self, df):
        total = df["et0_mm_day"].sum()
        mean = df["et0_mm_day"].mean()
        recs = [f"Irrigação estimada: {round(total * 1.1, 1)} mm"]
        if mean > 6:
            recs.append("ETo alta → aumentar irrigação")
        elif mean < 3:
            recs.append("ETo baixa → reduzir irrigação")
        return recs

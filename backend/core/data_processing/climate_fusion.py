# backend/core/data_processing/climate_fusion.py
# Fusão pura de dados climáticos — sem Kalman, sem loader de referência

import numpy as np
import pandas as pd
from loguru import logger
from typing import Dict

from backend.core.data_processing.climate_limits import get_fusion_limits
from backend.core.utils import detect_geographic_region


class ClimateFusion:
    """
    Responsável apenas pela fusão inteligente de múltiplas fontes climáticas.
    Não aplica Kalman. Não busca referência local.
    """

    WEIGHTS = {
        "T2M_MAX": 0.42,
        "T2M_MIN": 0.38,
        "T2M": 0.40,
        "RH2M": 0.28,
        "WS2M": 0.15,
        "ALLSKY_SFC_SW_DWN": 0.78,
        "PRECTOTCORR": 0.30,
    }

    GLOBAL_LIMITS = get_fusion_limits()

    def __init__(self):
        self.quality_metrics = {}
        self.source_health = {}

    def _validate_climate_data(self, df: pd.DataFrame, source_name: str):
        for var, (min_val, max_val) in self.GLOBAL_LIMITS.items():
            if var in df.columns:
                invalid = (df[var] < min_val) | (df[var] > max_val)
                if invalid.any():
                    logger.warning(
                        f"{source_name}: {invalid.sum()} valores de {var} fora dos limites físicos"
                    )

    def _track_data_quality(self, df: pd.DataFrame, source_name: str):
        if source_name not in self.quality_metrics:
            self.quality_metrics[source_name] = {
                "total_records": 0,
                "quality_scores": {},
            }

        metrics = self.quality_metrics[source_name]
        metrics["total_records"] = len(df)

        for var in self.WEIGHTS:
            if var not in df.columns:
                continue
            completeness = df[var].notna().mean()
            outliers = 0
            if var in self.GLOBAL_LIMITS:
                min_val, max_val = self.GLOBAL_LIMITS[var]
                outliers = ((df[var] < min_val) | (df[var] > max_val)).mean()
            score = completeness * (1 - outliers)
            metrics["quality_scores"][var] = round(score * 100, 2)

    def _check_source_health(self, source_name: str) -> bool:
        if source_name not in self.quality_metrics:
            return True
        scores = self.quality_metrics[source_name]["quality_scores"]
        if not scores:
            return True
        avg_quality = np.mean(list(scores.values()))
        is_healthy = avg_quality >= 60.0
        if not is_healthy:
            logger.warning(
                f"Circuit Breaker: {source_name} degradada (qualidade: {avg_quality:.1f}%)"
            )
        return is_healthy

    def _detect_region_with_priority(self, lat: float, lon: float) -> Dict:
        region = detect_geographic_region(lat, lon)
        if region == "usa":
            return {
                "name": "USA",
                "weights": {
                    "nws_forecast": 0.50,
                    "openmeteo_forecast": 0.30,
                    "met_norway": 0.20,
                },
                "order": ["nws_forecast", "openmeteo_forecast", "met_norway"],
            }
        elif region == "europe" and 55 <= lat <= 72 and -10 <= lon <= 40:
            return {
                "name": "NORDIC",
                "weights": {"met_norway": 0.80, "openmeteo_forecast": 0.20},
                "order": ["met_norway", "openmeteo_forecast"],
            }
        else:
            return {
                "name": "GLOBAL",
                "weights": {"openmeteo_forecast": 0.70, "met_norway": 0.30},
                "order": ["openmeteo_forecast", "met_norway"],
            }

    def _prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        if "source" in df.columns:
            for src in df["source"].unique():
                sub = df[df["source"] == src]
                self._validate_climate_data(sub, src)
                self._track_data_quality(sub, src)
        else:
            self._validate_climate_data(df, "unknown_source")
            self._track_data_quality(df, "unknown_source")

        if "date" not in df.columns:
            if isinstance(df.index, pd.DatetimeIndex):
                df = df.reset_index()
            else:
                logger.error("Coluna 'date' ausente e índice não é datetime")
                return df

        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")

        # Remove duplicatas mantendo fonte prioritária
        if df.index.duplicated().any():
            priority = {
                "nws_forecast": 1,
                "met_norway": 2,
                "openmeteo_forecast": 3,
            }

            def keep_best(g):
                if "source" in g.columns:
                    g = g.copy()
                    g["rank"] = g["source"].map(priority.get)
                    return g.sort_values("rank").head(1)
                return g.head(1)

            df = df.groupby(level=0).apply(keep_best).droplevel(0)

        return df

    def _interpolate_safe(self, series: pd.Series) -> pd.Series:
        interpolated = series.interpolate(
            method="linear", limit=3, limit_direction="both"
        )
        if series.name in self.GLOBAL_LIMITS:
            min_val, max_val = self.GLOBAL_LIMITS[series.name]
            interpolated = interpolated.clip(min_val, max_val)
        return interpolated

    def fuse_multi_source(
        self, df: pd.DataFrame, lat: float, lon: float
    ) -> pd.DataFrame:
        if df.empty:
            logger.warning("DataFrame vazio na fusão")
            return pd.DataFrame(columns=["date"] + list(self.WEIGHTS.keys()))

        df = self._prepare_data(df)
        region = self._detect_region_with_priority(lat, lon)

        # Circuit Breaker
        healthy_sources = [
            s for s in region["order"] if self._check_source_health(s)
        ]
        if not healthy_sources:
            logger.error(
                "Todas as fontes com problemas → usando fallback simples"
            )
            dates = pd.date_range(
                start=pd.Timestamp.now().date(), periods=7, freq="D"
            )
            return pd.DataFrame(
                {
                    "date": dates,
                    "T2M": 20.0,
                    "T2M_MAX": 28.0,
                    "T2M_MIN": 15.0,
                    "RH2M": 70.0,
                    "WS2M": 3.0,
                    "ALLSKY_SFC_SW_DWN": 20.0,
                    "PRECTOTCORR": 2.0,
                    "fusion_mode": "emergency_fallback",
                }
            ).set_index("date")

        weights = {s: region["weights"][s] for s in healthy_sources}
        total = sum(weights.values())
        weights = {k: v / total for k, v in weights.items()}

        # Fusão por dia
        result_rows = []
        for date, group in df.groupby(df.index):
            row = {"date": date}
            if "source" in group.columns:
                sources = {src: sub for src, sub in group.groupby("source")}
            else:
                sources = {"default": group}

            for var in self.WEIGHTS:
                values = {}
                for src, sub in sources.items():
                    if var in sub.columns and pd.notna(sub[var].iloc[0]):
                        values[src] = sub[var].iloc[0]

                if not values:
                    row[var] = np.nan
                    continue

                # Fusão ponderada pelas fontes saudáveis
                weighted = 0.0
                total_w = 0.0
                for src, val in values.items():
                    w = weights.get(src, 0.1)
                    weighted += w * val
                    total_w += w
                row[var] = (
                    weighted / total_w
                    if total_w > 0
                    else list(values.values())[0]
                )

            result_rows.append(row)

        result_df = pd.DataFrame(result_rows).set_index("date")

        # Clip final e interpolação
        for col in result_df.columns:
            if col in self.GLOBAL_LIMITS:
                min_val, max_val = self.GLOBAL_LIMITS[col]
                result_df[col] = result_df[col].clip(min_val, max_val)
            result_df[col] = self._interpolate_safe(result_df[col])

        result_df = result_df.dropna(thresh=4)  # pelo menos 3 vars + date
        result_df = result_df.reset_index()

        logger.success(
            f"Fusão concluída: {len(result_df)} dias | Região: {region['name']}"
        )
        return result_df

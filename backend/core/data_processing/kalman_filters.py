# backend/core/data_processing/kalman_filters.py
# Apenas os filtros Kalman — vetorizados e reutilizáveis
# No momento, aplicado somente em precipitação e ETo final calculada

import numpy as np
import pandas as pd
from typing import Dict, Optional


class AdaptiveKalmanFilter:
    def __init__(
        self,
        normal: float = 5.0,
        std: float = 1.0,
        p01: Optional[float] = None,
        p99: Optional[float] = None,
    ):
        self.normal = float(normal)
        self.std = max(float(std), 0.4)
        self.p01 = p01 if p01 is not None else normal - 3.5 * self.std
        self.p99 = p99 if p99 is not None else normal + 3.5 * self.std
        self.R_base = 0.55**2
        self.Q = self.std**2 * 0.08
        self.last_error = 0.0
        self.estimate = normal
        self.error = self.std**2

    def update(self, z: float) -> float:
        if np.isnan(z):
            return round(self.estimate, 3)

        if z < self.p01 * 0.8 or z > self.p99 * 1.25:
            R = self.R_base * 500
        elif z < self.p01 or z > self.p99:
            R = self.R_base * 50
        else:
            R = self.R_base

        current_error = abs(z - self.estimate)
        if current_error > self.last_error * 1.5:
            self.Q = min(self.Q * 1.8, self.std**2 * 0.5)
        self.last_error = current_error

        priori = self.estimate
        priori_err = self.error + self.Q
        K = priori_err / (priori_err + R)
        self.estimate = priori + K * (z - priori)
        self.error = (1 - K) * priori_err
        return round(self.estimate, 3)

    def update_batch(self, values: np.ndarray) -> np.ndarray:
        result = np.full_like(values, np.nan)
        for i, v in enumerate(values):
            if not np.isnan(v):
                result[i] = self.update(v)
        return result


class SimpleKalmanFilter:
    def __init__(self, initial_value: float = 5.0):
        self.estimate = initial_value
        self.error = 1.0
        self.Q = 0.05
        self.R = 0.8

    def update(self, z: float) -> float:
        if np.isnan(z):
            return round(self.estimate, 3)
        priori = self.estimate
        priori_err = self.error + self.Q
        K = priori_err / (priori_err + self.R)
        self.estimate = priori + K * (z - priori)
        self.error = (1 - K) * priori_err
        return round(self.estimate, 3)

    def update_batch(self, values: np.ndarray) -> np.ndarray:
        result = np.full_like(values, np.nan)
        for i, v in enumerate(values):
            if not np.isnan(v):
                result[i] = self.update(v)
        return result


class KalmanApplier:
    @staticmethod
    def apply_precipitation_filter(
        df: pd.DataFrame, ref: Optional[Dict] = None
    ) -> pd.DataFrame:
        if "PRECTOTCORR" not in df.columns:
            return df
        if ref:
            dates = pd.to_datetime(df["date"])
            months = dates.dt.month
            result = np.full(len(df), np.nan)
            for m in months.unique():
                mask = months == m
                values = df.loc[mask, "PRECTOTCORR"].values
                kalman = AdaptiveKalmanFilter(
                    normal=ref["precip_normals"].get(m, 100.0),
                    std=ref["precip_stds"].get(m, 10.0),
                    p01=ref["precip_p01"].get(m),
                    p99=ref["precip_p99"].get(m),
                )
                result[mask.values] = kalman.update_batch(values)
            df["PRECTOTCORR"] = np.round(result, 3)
        else:
            df["PRECTOTCORR"] = df["PRECTOTCORR"].clip(0, 1800).round(3)
        return df

    @staticmethod
    def apply_eto_filter(
        df: pd.DataFrame, ref: Optional[Dict] = None, lat: float = None
    ) -> pd.DataFrame:
        if "et0_mm" not in df.columns:
            return df

        dates = pd.to_datetime(df["date"])
        months = dates.dt.month
        result = np.full(len(df), np.nan)
        anomaly = np.full(len(df), np.nan)

        if ref:
            for m in months.unique():
                mask = months == m
                values = df.loc[mask, "et0_mm"].values
                kalman = AdaptiveKalmanFilter(
                    normal=ref["eto_normals"].get(m, 5.0),
                    std=ref["eto_stds"].get(m, 1.0),
                    p01=ref["eto_p01"].get(m),
                    p99=ref["eto_p99"].get(m),
                )
                filtered = kalman.update_batch(values)
                result[mask.values] = filtered
                anomaly[mask.values] = filtered - ref["eto_normals"].get(
                    m, 5.0
                )
        else:
            kalman = SimpleKalmanFilter(initial_value=5.0)
            result = kalman.update_batch(df["et0_mm"].values)

        df["eto_final"] = np.round(result, 3)
        df["anomaly_eto_mm"] = np.round(anomaly, 3) if ref else np.nan
        df["eto_evaonline"] = df["eto_final"]
        return df

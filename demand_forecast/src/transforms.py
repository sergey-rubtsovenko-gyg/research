from copy import deepcopy
from typing import Optional

import numpy as np
import pandas as pd
from etna.transforms import ReversiblePerSegmentWrapper
from etna.transforms.base import OneSegmentTransform


class _OneSegmentLogTrendTransform(OneSegmentTransform):
    """Fits a·log(t) + b trend per segment and removes it."""

    def __init__(self, in_column: str = "target"):
        self.in_column = in_column
        self._a: Optional[float] = None
        self._b: Optional[float] = None
        self._t0: Optional[float] = None

    def _get_t(self, df: pd.DataFrame) -> np.ndarray:
        idx = df.index
        if pd.api.types.is_integer_dtype(idx):
            t = idx.astype(float).values
        else:
            t = np.array([ts.timestamp() for ts in idx])
        return t

    def fit(self, df: pd.DataFrame) -> "_OneSegmentLogTrendTransform":
        col = df[self.in_column].dropna()
        t = self._get_t(df.loc[col.index])
        self._t0 = t[0]
        log_t = np.log1p(t - self._t0)  # log(1 + Δt), safe for t==t0
        # OLS: [log_t, 1] @ [a, b]
        X = np.column_stack([log_t, np.ones_like(log_t)])
        coeffs, *_ = np.linalg.lstsq(X, col.values, rcond=None)
        self._a, self._b = coeffs
        return self

    def _predict_trend(self, df: pd.DataFrame) -> np.ndarray:
        t = self._get_t(df)
        log_t = np.log1p(t - self._t0)
        return self._a * log_t + self._b

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        trend = self._predict_trend(df)
        df[self.in_column] = df[self.in_column] - trend
        return df

    def inverse_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        trend = self._predict_trend(df)
        df[self.in_column] = df[self.in_column] + trend
        return df

    def get_regressors_info(self) -> list[str]:
        return []


class LogTrendTransform(ReversiblePerSegmentWrapper):
    """Removes a logarithmic trend (a·log(t) + b) from each segment."""

    def __init__(self, in_column: str = "target"):
        self.in_column = in_column
        super().__init__(
            transform=_OneSegmentLogTrendTransform(in_column=in_column),
            required_features=[in_column],
        )

    def get_regressors_info(self) -> list[str]:
        return []

import numpy as np
import pandas as pd


def add_ema(df: pd.DataFrame, short_span: int = 13, long_span: int = 26) -> pd.DataFrame:
    """Add EMA 13 and EMA 26 to the dataframe."""
    out = df.copy()
    out["ema_13"] = out["Close"].ewm(span=short_span, adjust=False).mean()
    out["ema_26"] = out["Close"].ewm(span=long_span, adjust=False).mean()
    return out


def add_ichimoku(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add Ichimoku Cloud components to the dataframe.

    Components:
    - tenkan_sen  : (9-period high + 9-period low) / 2
    - kijun_sen   : (26-period high + 26-period low) / 2
    - cloud_top   : max(Senkou Span A raw, Senkou Span B raw) — used in signals without look-ahead
    - cloud_bottom: min(Senkou Span A raw, Senkou Span B raw) — same
    - senkou_a_plot: Senkou Span A shifted forward 26 bars (for charting only)
    - senkou_b_plot: Senkou Span B shifted forward 26 bars (for charting only)
    - chikou_span : Close shifted back 26 bars (for charting only)
    - vol_ma20    : 20-day rolling average volume
    """
    out = df.copy()

    high_9 = out["High"].rolling(9).max()
    low_9 = out["Low"].rolling(9).min()
    out["tenkan_sen"] = (high_9 + low_9) / 2

    high_26 = out["High"].rolling(26).max()
    low_26 = out["Low"].rolling(26).min()
    out["kijun_sen"] = (high_26 + low_26) / 2

    span_a_raw = (out["tenkan_sen"] + out["kijun_sen"]) / 2
    high_52 = out["High"].rolling(52).max()
    low_52 = out["Low"].rolling(52).min()
    span_b_raw = (high_52 + low_52) / 2

    # For signal use — unshifted (no look-ahead bias)
    out["cloud_top"] = np.maximum(span_a_raw, span_b_raw)
    out["cloud_bottom"] = np.minimum(span_a_raw, span_b_raw)

    # For chart plotting only — shift forward 26 bars
    out["senkou_a_plot"] = span_a_raw.shift(26)
    out["senkou_b_plot"] = span_b_raw.shift(26)

    out["chikou_span"] = out["Close"].shift(-26)
    out["vol_ma20"] = out["Volume"].rolling(20).mean()
    return out


def build_features(df):
    out = add_ema(df)
    out = add_ichimoku(out)
    return out.dropna(subset=["ema_13", "ema_26", "cloud_top", "tenkan_sen", "kijun_sen"]).copy()
import pandas as pd
import yfinance as yf
from pathlib import Path


def download_data(tickers: list, start: str = "2018-01-01", end: str = None) -> dict:
    """
    Download daily OHLCV data from Yahoo Finance for a list of .JK tickers.
    Returns a dict of {ticker: DataFrame}.
    """
    frames = {}
    for ticker in tickers:
        df = yf.download(
            ticker,
            start=start,
            end=end,
            auto_adjust=True,
            progress=False,
        )
        if df.empty:
            print(f"[WARNING] No data returned for {ticker}")
            continue
        df.columns = df.columns.get_level_values(0)
        df = df.rename(columns=str.title)
        cols = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c in df.columns]
        df = df[cols].dropna()
        frames[ticker] = df
        print(f"[OK] {ticker}: {len(df)} rows from {df.index[0].date()} to {df.index[-1].date()}")
    return frames


def save_raw_data(frames: dict, data_dir: str = "data") -> None:
    """Save each ticker dataframe as CSV in data_dir."""
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    for ticker, df in frames.items():
        filename = data_dir / f"{ticker.replace('.JK', '')}.csv"
        df.to_csv(filename)
        print(f"[SAVED] {filename}")
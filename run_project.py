import os
import sys
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

from src.data_loader import download_data, save_raw_data
from src.backtest import run_universe

TICKERS = ["PTBA.JK", "ANTM.JK", "BRPT.JK", "MDKA.JK", "PGAS.JK"]
START_DATE = "2018-01-01"
COMMISSION = 0.0025
USE_VOLUME_FILTER = False

DATA_DIR = os.path.join(BASE_DIR, "data")
CHART_DIR = os.path.join(BASE_DIR, "output", "charts")
TABLE_DIR = os.path.join(BASE_DIR, "output", "tables")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CHART_DIR, exist_ok=True)
os.makedirs(TABLE_DIR, exist_ok=True)

print("=" * 50)
print("Downloading data...")
print("=" * 50)
frames = download_data(TICKERS, start=START_DATE)
save_raw_data(frames, DATA_DIR)

print("\\n" + "=" * 50)
print("Running backtests...")
print("=" * 50)
results, summary = run_universe(frames, commission=COMMISSION, use_volume_filter=USE_VOLUME_FILTER)
summary.to_csv(os.path.join(TABLE_DIR, "summary_metrics.csv"), index=False)

print("\\n" + "=" * 50)
print("SUMMARY RESULTS")
print("=" * 50)
print(summary.to_string(index=False))

print("\\nGenerating equity curve charts...")
for ticker, df in results.items():
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={"height_ratios": [3, 1]})

    axes[0].plot(df.index, df["equity_strategy"], label="Ichimoku + EMA Strategy", color="#2196F3", linewidth=1.5)
    axes[0].plot(df.index, df["equity_buy_hold"], label="Buy & Hold", color="#FF9800", linewidth=1.5, alpha=0.85)
    axes[0].set_title(f"{ticker} — Equity Curve (Long-Only, Commission 0.25%)", fontsize=13)
    axes[0].set_ylabel("Portfolio Value (normalized)")
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    dd = df["equity_strategy"] / df["equity_strategy"].cummax() - 1
    axes[1].fill_between(df.index, dd, 0, color="#F44336", alpha=0.5, label="Drawdown")
    axes[1].set_ylabel("Drawdown")
    axes[1].set_xlabel("Date")
    axes[1].legend()
    axes[1].grid(alpha=0.3)

    fig.tight_layout()
    out_path = os.path.join(CHART_DIR, f"{ticker.replace('.JK', '')}_equity_curve.png")
    fig.savefig(out_path, dpi=160)
    plt.close(fig)
    print(f"[CHART] Saved: {out_path}")

print("\\nAll done. Check output/charts/ and output/tables/.")
import numpy as np
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.indicators import build_features


def generate_signals(df: pd.DataFrame, use_volume_filter: bool = False) -> pd.DataFrame:
    """
    Generate long-only entry and exit signals.

    Entry: Close > cloud_top AND tenkan_sen > kijun_sen AND ema_13 > ema_26
    Optional: volume > vol_ma20

    Exit (any one):
    - Close falls into or below cloud_top
    - ema_13 crosses below ema_26
    - tenkan_sen crosses below kijun_sen
    """
    x = build_features(df)

    x["entry_signal"] = (
        (x["Close"] > x["cloud_top"]) &
        (x["tenkan_sen"] > x["kijun_sen"]) &
        (x["ema_13"] > x["ema_26"])
    )
    if use_volume_filter:
        x["entry_signal"] = x["entry_signal"] & (x["Volume"] > x["vol_ma20"])

    x["exit_signal"] = (
        (x["Close"] <= x["cloud_top"]) |
        (x["ema_13"] < x["ema_26"]) |
        (x["tenkan_sen"] < x["kijun_sen"])
    )
    return x


def run_long_only_backtest(
    df: pd.DataFrame,
    commission: float = 0.0025,
    use_volume_filter: bool = False
) -> tuple:
    """
    Run a long-only daily backtest with commission cost.

    - No short selling (IDX retail constraint)
    - Commission applied on both entry and exit
    - Returns: (equity DataFrame, stats dict)
    """
    x = generate_signals(df, use_volume_filter=use_volume_filter).copy()
    x["ret"] = x["Close"].pct_change().fillna(0)

    position = 0
    positions = []
    trades = 0

    for _, row in x.iterrows():
        if position == 0 and row["entry_signal"]:
            position = 1
            trades += 1
        elif position == 1 and row["exit_signal"]:
            position = 0
        positions.append(position)

    x["position"] = positions
    x["position_prev"] = x["position"].shift(1).fillna(0)
    x["trade_flag"] = x["position"].diff().abs().fillna(0)

    x["strategy_ret_gross"] = x["position_prev"] * x["ret"]
    x["strategy_ret_net"] = x["strategy_ret_gross"] - (x["trade_flag"] * commission)
    x["buy_hold_ret"] = x["ret"]

    x["equity_strategy"] = (1 + x["strategy_ret_net"]).cumprod()
    x["equity_buy_hold"] = (1 + x["buy_hold_ret"]).cumprod()

    return x, _summarize(x, trades)


def _summarize(x: pd.DataFrame, trades: int) -> dict:
    """Compute annualized performance metrics."""
    ann = 252
    n = len(x)
    total_ret = x["equity_strategy"].iloc[-1] - 1
    bh_ret = x["equity_buy_hold"].iloc[-1] - 1
    ann_ret = (x["equity_strategy"].iloc[-1] ** (ann / n) - 1) if n > 0 else np.nan
    ann_vol = x["strategy_ret_net"].std() * np.sqrt(ann)
    sharpe = ann_ret / ann_vol if ann_vol > 0 else np.nan
    max_dd = (x["equity_strategy"] / x["equity_strategy"].cummax() - 1).min()

    in_pos = x["position"].sum()
    win_trades = (x[x["trade_flag"] == 1]["strategy_ret_net"] > 0).sum() if trades > 0 else 0

    return {
        "total_return_pct": round(total_ret * 100, 2),
        "buy_hold_return_pct": round(bh_ret * 100, 2),
        "annualized_return_pct": round(ann_ret * 100, 2),
        "annualized_volatility_pct": round(ann_vol * 100, 2),
        "sharpe_ratio": round(sharpe, 3),
        "max_drawdown_pct": round(max_dd * 100, 2),
        "total_trades": trades,
        "days_in_market": int(in_pos),
        "pct_days_in_market": round(in_pos / n * 100, 1),
        "total_days": n,
    }


def run_universe(
    frames: dict,
    commission: float = 0.0025,
    use_volume_filter: bool = False
) -> tuple:
    """Run backtest for all tickers and return (results dict, summary DataFrame)."""
    results = {}
    rows = []
    for ticker, df in frames.items():
        eq_df, stats = run_long_only_backtest(df, commission=commission, use_volume_filter=use_volume_filter)
        results[ticker] = eq_df
        rows.append({"ticker": ticker, **stats})
        print(f"[DONE] {ticker} | Sharpe: {stats['sharpe_ratio']:.3f} | Total Return: {stats['total_return_pct']:.1f}%")
    summary = pd.DataFrame(rows).sort_values("sharpe_ratio", ascending=False).reset_index(drop=True)
    return results, summary
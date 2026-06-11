# Execution-Aware Ichimoku + EMA Backtest on Indonesian Commodity Stocks

This project evaluates a long-only daily trend-following strategy on five Indonesian commodity and energy stocks:

- PTBA.JK
- ANTM.JK
- BRPT.JK
- MDKA.JK
- PGAS.JK

The strategy combines Ichimoku Cloud trend confirmation, EMA 13/26 filtering, and commission-adjusted backtesting to test whether a simple rules-based system can survive realistic execution costs in the Indonesian market.

## Why this project exists

The goal of this project is not to build a perfect trading system. The goal is to study whether a disciplined technical strategy can produce usable results on liquid Indonesian stocks while staying honest about transaction costs, drawdowns, and stock-specific behavior.

The first version of the project showed that the strategy is not universally strong across the whole basket. That result is actually useful because it reveals where the strategy works, where it fails, and why additional filtering may be needed.

## Strategy rules
<img width="1341" height="593" alt="schematic_diagram" src="https://github.com/user-attachments/assets/3689a01f-1fcc-47b3-b7a8-950041bca5e5" />

### Entry
A long position is opened only when all of the following are true:

- Close price is above the Ichimoku cloud.
- Tenkan-sen is above Kijun-sen.
- EMA 13 is above EMA 26.
- Optional: volume is above its 20-day moving average.

### Exit
The position is closed when any of the following happens:

- Close price falls into or below the cloud.
- EMA 13 falls below EMA 26.
- Tenkan-sen falls below Kijun-sen.

## Market assumptions

- Long only.
- No short selling.
- Daily timeframe.
- Commission included in performance calculations.
- Buy-and-hold used as the benchmark.

## Results summary

The first run produced mixed outcomes across the five stocks.

### Key observations

- **BRPT.JK** was the strongest performer in the basket, with the best total return and the strongest Sharpe ratio.
- **ANTM.JK** was positive on the strategy side, but still lagged its buy-and-hold benchmark.
- **PGAS.JK** and **PTBA.JK** were only mildly positive and did not clearly beat passive holding.
- **MDKA.JK** was the weakest result, ending negative on total return and Sharpe ratio.
- Drawdowns were still large on several names, which means the strategy needs refinement before it can be considered robust.

## What the results mean

The main lesson is that this strategy is selective, not universal. It seems to work much better on some Indonesian commodity names than others, which suggests that stock selection, regime conditions, and exit design matter a lot.

That is a useful quant finding rather than a failure. A good research project does not need every result to be positive. It needs to show that you can test a hypothesis, measure the outcome, and explain what it means.

## Project structure

```text
idx-ichimoku-ema-backtest/
├── data/
├── output/
│   ├── charts/
│   └── tables/
├── src/
│   ├── data_loader.py
│   ├── indicators.py
│   └── backtest.py
├── run_project.py
├── requirements.txt
├── project_documentation.pdf
└── README.md
```

## Files

### `src/data_loader.py`
Downloads and saves daily OHLCV data from Yahoo Finance for the selected `.JK` tickers.

### `src/indicators.py`
Computes EMA 13, EMA 26, and Ichimoku Cloud features.

### `src/backtest.py`
Generates signals, runs the long-only backtest, and summarizes performance metrics.

### `run_project.py`
Runs the full pipeline for all tickers and exports summary tables and charts.

## Outputs

After running the project, the following files are created:

- `output/tables/summary_metrics.csv`
- `output/charts/PTBA_equity_curve.png`
- `output/charts/ANTM_equity_curve.png`
- `output/charts/BRPT_equity_curve.png`
- `output/charts/MDKA_equity_curve.png`
- `output/charts/PGAS_equity_curve.png`

## How to run

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the project:

```bash
python run_project.py
```

## Performance metrics

The summary table reports:

- Total return.
- Buy-and-hold return.
- Annualized return.
- Annualized volatility.
- Sharpe ratio.
- Maximum drawdown.
- Total trades.
- Days in market.

## Limitations

This project is intentionally simple and research-focused.

- It does not use short selling.
- It does not include leverage.
- It does not model market impact in depth.
- It does not optimize parameters automatically.
- It does not guarantee that the strategy will generalize to all market regimes.

## Next improvements

Possible future upgrades include:

- Adding a volume confirmation filter.
- Testing a weekly trend filter on top of the daily signals.
- Adding ATR-based stop loss or trailing stop logic.
- Comparing the strategy across more Indonesian sectors.
- Testing whether the BRPT behavior can be explained by volatility regime changes or stronger trend persistence.

## Conclusion

This repository shows a practical first step into systematic trading research on Indonesian stocks. The current results are mixed, but that is exactly what makes the project honest and useful. It demonstrates technical analysis implementation, backtesting discipline, and the ability to evaluate a strategy with realistic constraints.

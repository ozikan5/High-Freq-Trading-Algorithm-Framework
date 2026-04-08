"""
Run a market-making backtest on historical daily data.

Usage:
    python scripts/run_backtest.py
    python scripts/run_backtest.py --symbol MSFT --days 365 --cash 10000
"""

import argparse
import sys
import os

# allow imports from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import yfinance as yf

from src.backtester import Backtester
from src.strategy import MarketMakerStrategy


def main():
    parser = argparse.ArgumentParser(description="Run a market-making backtest")
    parser.add_argument("--symbol", default="AAPL", help="Ticker symbol (default: AAPL)")
    parser.add_argument("--days",   default=365, type=int, help="Number of calendar days of history")
    parser.add_argument("--cash",   default=10_000, type=float, help="Starting cash (default: 10000)")
    parser.add_argument("--spread", default=0.01, type=float, help="Spread pct on each side (default: 0.01 = 1%%)")
    parser.add_argument("--qty",    default=10, type=int, help="Shares per order (default: 10)")
    args = parser.parse_args()

    print(f"Downloading {args.symbol} data ({args.days} days)...")
    bars = yf.download(args.symbol, period=f"{args.days}d", auto_adjust=True, progress=False)
    # yfinance may return MultiIndex columns like ("Close", "AAPL") — flatten to just the field name
    if isinstance(bars.columns, pd.MultiIndex):
        bars.columns = [c[0].lower() for c in bars.columns]
    else:
        bars.columns = [c.lower() for c in bars.columns]

    if bars.empty:
        print("No data returned. Check your symbol and internet connection.")
        sys.exit(1)

    print(f"  {len(bars)} bars loaded  ({bars.index[0].date()} → {bars.index[-1].date()})\n")

    strategy = MarketMakerStrategy(quantity=args.qty, spread_pct=args.spread)
    bt = Backtester(symbol=args.symbol, initial_cash=args.cash, strategy=strategy)

    results = bt.run(bars)

    # ── Summary ──────────────────────────────────────────────────────────────
    final_equity  = results["equity"].iloc[-1]
    final_pnl     = results["pnl"].iloc[-1]
    max_drawdown  = (results["equity"] - results["equity"].cummax()).min()
    pnl_pct       = (final_pnl / args.cash) * 100

    print("=" * 45)
    print(f"  Symbol         : {args.symbol}")
    print(f"  Period         : {bars.index[0].date()} → {bars.index[-1].date()}")
    print(f"  Starting cash  : ${args.cash:,.2f}")
    print(f"  Final equity   : ${final_equity:,.2f}")
    print(f"  PnL            : ${final_pnl:+,.2f}  ({pnl_pct:+.2f}%)")
    print(f"  Max drawdown   : ${max_drawdown:,.2f}")
    print(f"  Final position : {bt.position.shares} shares")
    print("=" * 45)

    print("\nLast 5 rows of equity curve:")
    print(results[["equity", "pnl", "shares"]].tail().to_string())


if __name__ == "__main__":
    main()

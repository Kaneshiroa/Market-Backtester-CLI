import argparse
from data.fetcher import get_historical_data
from engine.backtester import Backtester
from engine.indicators import add_sma_indicators


def main():
  # Set up standard command-line flags
  parser = argparse.ArgumentParser(description="Stock Backtester CLI")
  parser.add_argument(
      "--ticker",
      "-t",
      type=str,
      default="AAPL",
      help="Stock ticker (e.g. AAPL)",
  )
  # SMA meaning Simple Moving Average, 20 for 1 month and 50 for 2.5 months of trading days
  parser.add_argument(
      "--fast", type=int, default=20, help="Fast SMA days (default: 20)"
  )
  parser.add_argument(
      "--slow", type=int, default=50, help="Slow SMA days (default: 50)"
  )
  parser.add_argument(
      "--start",
      "-s",
      type=str,
      default="2023-01-01",
      help="Start date YYYY-MM-DD",
  )
  parser.add_argument(
      "--cash",
      "-c",
      type=float,
      default=10000.0,
      help="Starting capital (default: 10000)",
  )
  # Execution friction flags: flat dollar commission and decimal slippage
  parser.add_argument(
      "--commission",
      type=float,
      default=1.0,
      help="Flat commission fee per trade in USD (default: 1.0)",
  )
  parser.add_argument(
      "--slippage",
      type=float,
      default=0.0005,
      help="Slippage percentage per trade in decimal (default: 0.0005 for 0.05%)",
  )

  args = parser.parse_args()

  # Fetch data
  print(f"Fetching data for {args.ticker.upper()} starting {args.start}...")
  df = get_historical_data(ticker=args.ticker, start=args.start)

  # Calculate indicators
  print(f"Calculating SMA {args.fast}/{args.slow}...")
  data = add_sma_indicators(df, fast=args.fast, slow=args.slow)

  # Run the simulation
  print("Simulating trades...")
  engine = Backtester(
      data=data,
      initial_cash=args.cash,
      commission=args.commission,
      slippage_pct=args.slippage,
  )
  res = engine.run()

  # Print results cleanly with standard Python prints
  print("\n" + "=" * 45)
  print(
      f"  BACKTEST: {args.ticker.upper()} (SMA {args.fast} / {args.slow})"
  )
  print("=" * 45)
  print(f"Starting Capital:        ${res.starting_capital:,.2f}")
  print(f"Final Portfolio Value:   ${res.final_portfolio_value:,.2f}")
  print(f"Strategy Return:         {res.total_strategy_return * 100:+.2f}%")
  print(f"Buy & Hold Return:       {res.total_market_return * 100:+.2f}%")
  print(f"Sharpe Ratio:            {res.sharpe_ratio:.2f}")
  print(f"Max Drawdown:            {res.max_drawdown * 100:.2f}%")
  print(f"Total Trades:            {res.total_trades}")
  print(f"Est. Friction Drag:     -${res.total_friction_cost:,.2f}")
  print("=" * 45 + "\n")


if __name__ == "__main__":
  main()
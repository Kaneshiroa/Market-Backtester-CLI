import pandas as pd
import yfinance as yf
from data.database import init_db, load_cached_data, save_to_cache

# Initialize database schema if not present
init_db()


def get_historical_data(
    ticker: str, start: str, end: str | None = None
) -> pd.DataFrame:
  # Check local Supabase cache first
  cached_df = load_cached_data(ticker, start)
  if not cached_df.empty:
    print(f"Loaded {len(cached_df)} bars for {ticker.upper()} from Supabase.")
    return cached_df

  # If not found, download from Yahoo Finance
  print(f"Cache miss for {ticker.upper()}. Fetching from Yahoo Finance...")
  df = yf.download(ticker, start=start, end=end, progress=False)

  if df.empty:
    raise ValueError(
        f"No data found for symbol '{ticker}'. Check symbol or dates."
    )

  if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

  df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
  df.index = pd.to_datetime(df.index)
  df.sort_index(inplace=True)

  # Store into Supabase for next time
  save_to_cache(ticker, df)
  print(f"Cached {len(df)} bars to Supabase.")

  return df
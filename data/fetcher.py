import pandas as pd
import yfinance as yf


def get_historical_data(
    ticker: str, start: str, end: str | None = None
) -> pd.DataFrame:
  """Downloads historical OHLCV data and returns a cleaned Pandas DataFrame."""
  df = yf.download(ticker, start=start, end=end, progress=False)

  if df.empty:
    raise ValueError(
        f"No data found for symbol '{ticker}'. Check symbol or dates."
    )

  # Flatten multi-index columns if yfinance returns them
  if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

  # Standardize column casing
  df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
  df.index = pd.to_datetime(df.index)
  df.sort_index(inplace=True)
  return df
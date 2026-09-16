import pandas as pd


def add_sma_indicators(
    df: pd.DataFrame, fast: int = 20, slow: int = 50
) -> pd.DataFrame:
  """Calculates fast and slow SMAs and sets a signal column:

  1 = Bullish (Fast > Slow), 0 = Neutral/Cash.
  """
  data = df.copy()
  data[f"SMA_{fast}"] = data["Close"].rolling(window=fast).mean()
  data[f"SMA_{slow}"] = data["Close"].rolling(window=slow).mean()

  # Signal: 1 when fast SMA is strictly above slow SMA
  data["Signal"] = 0
  data.loc[data[f"SMA_{fast}"] > data[f"SMA_{slow}"], "Signal"] = 1

  # Shift signal by 1 bar to prevent lookahead bias (trade executes next open)
  data["Position"] = data["Signal"].shift(1).fillna(0)

  # Calculate strategy daily percentage returns
  data["Market_Return"] = data["Close"].pct_change().fillna(0)
  data["Strategy_Return"] = data["Market_Return"] * data["Position"]

  return data
from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass
class BacktestResults:
  starting_capital: float
  final_portfolio_value: float
  total_strategy_return: float
  total_market_return: float
  sharpe_ratio: float
  max_drawdown: float
  total_trades: int
  equity_curve: pd.Series


class Backtester:

  def __init__(
      self,
      data: pd.DataFrame,
      initial_cash: float = 10000.0,
      risk_free_rate: float = 0.0,
  ):
    """Expects a DataFrame containing 'Close', 'Position', and 'Strategy_Return' columns."""
    self.data = data.copy()
    self.initial_cash = initial_cash
    self.risk_free_rate = risk_free_rate

  def run(self) -> BacktestResults:
    # 1. Generate equity curves
    self.data["Strategy_Cumulative"] = (
        1 + self.data["Strategy_Return"]
    ).cumprod()
    self.data["Market_Cumulative"] = (1 + self.data["Market_Return"]).cumprod()

    self.data["Portfolio_Value"] = (
        self.initial_cash * self.data["Strategy_Cumulative"]
    )

    # 2. Count trade executions (where position changes state)
    trade_signals = self.data["Position"].diff().abs()
    total_trades = int((trade_signals > 0).sum())

    # 3. Calculate Annualized Sharpe Ratio (252 trading days)
    daily_returns = self.data["Strategy_Return"]
    excess_returns = daily_returns - (self.risk_free_rate / 252)
    std = daily_returns.std()
    sharpe_ratio = (
        float(np.sqrt(252) * (excess_returns.mean() / std)) if std > 0 else 0.0
    )

    # 4. Calculate Maximum Drawdown (Peak to Trough)
    rolling_max = self.data["Portfolio_Value"].cummax()
    drawdown = (self.data["Portfolio_Value"] - rolling_max) / rolling_max
    max_drawdown = float(drawdown.min())

    final_val = float(self.data["Portfolio_Value"].iloc[-1])
    total_strat_return = float(self.data["Strategy_Cumulative"].iloc[-1] - 1)
    total_mkt_return = float(self.data["Market_Cumulative"].iloc[-1] - 1)

    return BacktestResults(
        starting_capital=self.initial_cash,
        final_portfolio_value=final_val,
        total_strategy_return=total_strat_return,
        total_market_return=total_mkt_return,
        sharpe_ratio=sharpe_ratio,
        max_drawdown=max_drawdown,
        total_trades=total_trades,
        equity_curve=self.data["Portfolio_Value"],
    )
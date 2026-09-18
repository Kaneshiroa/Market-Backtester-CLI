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
  total_friction_cost: float
  equity_curve: pd.Series


class Backtester:

  def __init__(
      self,
      data: pd.DataFrame,
      initial_cash: float = 10000.0,
      risk_free_rate: float = 0.0,
      commission: float = 1.0,
      slippage_pct: float = 0.0005,
  ):
    """Expects a DataFrame containing 'Close', 'Position', 'Market_Return', and 'Strategy_Return' columns."""
    self.data = data.copy()
    self.initial_cash = initial_cash
    self.risk_free_rate = risk_free_rate
    self.commission = commission
    self.slippage_pct = slippage_pct

  def run(self) -> BacktestResults:
    # 1. Detect trade executions (where position changes state)
    trade_signals = self.data["Position"].diff().abs().fillna(0)
    total_trades = int((trade_signals > 0).sum())

    # 2. Compute execution friction drag (slippage bps + flat commission)
    slippage_drag = trade_signals * self.slippage_pct
    commission_drag = (trade_signals * self.commission) / self.initial_cash
    total_drag = slippage_drag + commission_drag
    self.data["Net_Strategy_Return"] = (
        self.data["Strategy_Return"] - total_drag
    )

    # 3. Generate equity curves using net returns
    self.data["Strategy_Cumulative"] = (
        1 + self.data["Net_Strategy_Return"]
    ).cumprod()
    self.data["Market_Cumulative"] = (1 + self.data["Market_Return"]).cumprod()

    self.data["Portfolio_Value"] = (
        self.initial_cash * self.data["Strategy_Cumulative"]
    )

    # 4. Calculate Annualized Sharpe Ratio (252 trading days)
    daily_returns = self.data["Net_Strategy_Return"]
    excess_returns = daily_returns - (self.risk_free_rate / 252)
    std = daily_returns.std()
    sharpe_ratio = (
        float(np.sqrt(252) * (excess_returns.mean() / std)) if std > 0 else 0.0
    )

    # 5. Calculate Maximum Drawdown (Peak to Trough)
    rolling_max = self.data["Portfolio_Value"].cummax()
    drawdown = (self.data["Portfolio_Value"] - rolling_max) / rolling_max
    max_drawdown = float(drawdown.min())

    final_val = float(self.data["Portfolio_Value"].iloc[-1])
    total_strat_return = float(self.data["Strategy_Cumulative"].iloc[-1] - 1)
    total_mkt_return = float(self.data["Market_Cumulative"].iloc[-1] - 1)
    total_friction = float((total_drag * self.initial_cash).sum())

    return BacktestResults(
        starting_capital=self.initial_cash,
        final_portfolio_value=final_val,
        total_strategy_return=total_strat_return,
        total_market_return=total_mkt_return,
        sharpe_ratio=sharpe_ratio,
        max_drawdown=max_drawdown,
        total_trades=total_trades,
        total_friction_cost=total_friction,
        equity_curve=self.data["Portfolio_Value"],
    )
#  Stock Backtester CLI

A modular, lightweight Python command-line interface (CLI) to simulate, evaluate, and backtest algorithmic trading strategies against historical equity market data.

Built with **Python**, **Pandas**, and **NumPy**, this engine simulates dual moving average crossover strategies, tracks portfolio equity curves, and calculates standard risk/performance metrics—all while preventing lookahead bias.

---

## Table of Contents

1. [Features](#features)
2. [Project Architecture](#project-architecture)
3. [Quick Start & Setup](#quick-start--setup)
4. [Usage & CLI Options](#usage--cli-options)
5. [Sample Output](#sample-output)
6. [Roadmap](#roadmap)

---

## Features

- **Historical Data Ingestion:** Fetches clean daily OHLCV (Open, High, Low, Close, Volume) time-series data via Yahoo Finance (`yfinance`).
- **Vectorized Signal Engine:** Computes rolling Simple Moving Averages (SMA) and strategy entry/exit signals using Pandas without slow row-by-row iteration.
- **Lookahead Bias Prevention:** Shifts trade execution signals forward by one period (`shift(1)`) to ensure simulated orders execute realistically on next-day opens rather than current-day closes.
- **Quantitative Risk Analytics:** Calculates key financial performance metrics:
  - Total Cumulative Strategy Return vs. Buy-and-Hold Benchmark
  - Annualized Sharpe Ratio (assuming 252 trading days)
  - Maximum Peak-to-Trough Drawdown
  - Total Trade Executions

---

## Project Architecture

```text
stock-cli/
├── data/
│   ├── __init__.py
│   └── fetcher.py       # Pulls and standardizes OHLCV data
├── engine/
│   ├── __init__.py
│   ├── indicators.py    # Vectorized indicator math (SMA crossover)
│   └── backtester.py    # Simulation engine, equity tracking, and risk metrics
├── main.py              # CLI entry point using argparse
├── requirements.txt     # Dependency list
├── .gitignore           # Ignored files (venv, pycache)
└── README.md            # Documentation
```

---

## Quick Start & Setup

### 1. Create directory & virtual environment

```bash
mkdir stock-cli && cd stock-cli
python3 -m venv venv

# macOS / Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Usage & CLI Options

Run the CLI using standard flags:

```bash
python main.py --ticker AAPL --fast 20 --slow 50 --start 2023-01-01 --cash 10000
```

### Available Flags

| Flag | Short | Default | Description |
| :--- | :--- | :--- | :--- |
| `--ticker` | `-t` | `AAPL` | Stock ticker symbol (e.g., `AAPL`, `MSFT`, `SPY`) |
| `--fast` | | `20` | Fast SMA window (trading days) |
| `--slow` | | `50` | Slow SMA window (trading days) |
| `--start` | `-s` | `2023-01-01` | Start date for historical data (`YYYY-MM-DD`) |
| `--cash` | `-c` | `10000.0` | Initial starting capital ($) |

To see the help menu:
```bash
python main.py --help
```

---

## Sample Output

```text
Fetching data for AAPL starting 2023-01-01...
Calculating SMA 20/50...
Simulating trades...

=============================================
  BACKTEST: AAPL (SMA 20 / 50)
=============================================
Starting Capital:        $10,000.00
Final Portfolio Value:   $15,628.86
Strategy Return:         +56.29%
Buy & Hold Return:       +170.52%
Sharpe Ratio:            0.77
Max Drawdown:            -24.58%
Total Trades:            23
=============================================
```

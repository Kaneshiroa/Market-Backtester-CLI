from datetime import datetime
import os
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import (
    Column,
    Date,
    Float,
    MetaData,
    String,
    Table,
    URL,
    create_engine,
    select,
)
from sqlalchemy.dialects.postgresql import insert

# override=True ensures .env values always take precedence
load_dotenv(override=True)

# Build connection using the IPv4 Pooler host
db_url = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("DB_USER", "postgres.xniwhxycifvhosxpbblp"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "aws-0-us-east-1.pooler.supabase.com"),
    port=int(os.getenv("DB_PORT", 6543)),
    database=os.getenv("DB_NAME", "postgres"),
)

engine = create_engine(db_url)
metadata = MetaData()

ohlcv_table = Table(
    "ohlcv_cache",
    metadata,
    Column("ticker", String(10), primary_key=True),
    Column("date", Date, primary_key=True),
    Column("open", Float),
    Column("high", Float),
    Column("low", Float),
    Column("close", Float),
    Column("volume", Float),
)


def init_db():
  """Creates the table in Supabase if it doesn't exist."""
  metadata.create_all(engine)


def load_cached_data(ticker: str, start: str) -> pd.DataFrame:
  """Queries PostgreSQL for stored bars.

  Returns data only if the cache covers the requested start date.
  """
  start_dt = datetime.strptime(start, "%Y-%m-%d").date()

  # 1. Fetch all available bars from start date onwards
  query = (
      select(ohlcv_table)
      .where(ohlcv_table.c.ticker == ticker.upper())
      .where(ohlcv_table.c.date >= start_dt)
      .order_by(ohlcv_table.c.date.asc())
  )

  with engine.connect() as conn:
    df = pd.read_sql(query, conn)

  if df.empty:
    return pd.DataFrame()

  # 2. Check if the cache actually covers the beginning of the requested window
  # Allow up to 4 calendar days of wiggle room for market weekends/holidays
  earliest_cached_date = df["date"].min()
  if (earliest_cached_date - start_dt).days > 4:
    # We don't have the early history; trigger a fetch
    return pd.DataFrame()

  df["date"] = pd.to_datetime(df["date"])
  df.set_index("date", inplace=True)
  df.rename(
      columns={
          "open": "Open",
          "high": "High",
          "low": "Low",
          "close": "Close",
          "volume": "Volume",
      },
      inplace=True,
  )
  return df[["Open", "High", "Low", "Close", "Volume"]]


def save_to_cache(ticker: str, df: pd.DataFrame):
  """Saves newly fetched OHLCV bars into PostgreSQL using an upsert."""
  records = []
  for date_val, row in df.iterrows():
    records.append({
        "ticker": ticker.upper(),
        "date": date_val.date(),
        "open": float(row["Open"]),
        "high": float(row["High"]),
        "low": float(row["Low"]),
        "close": float(row["Close"]),
        "volume": float(row["Volume"]),
    })

  if not records:
    return

  stmt = insert(ohlcv_table).values(records)
  upsert_stmt = stmt.on_conflict_do_update(
      index_elements=["ticker", "date"],
      set_={
          "open": stmt.excluded.open,
          "high": stmt.excluded.high,
          "low": stmt.excluded.low,
          "close": stmt.excluded.close,
          "volume": stmt.excluded.volume,
      },
  )

  with engine.begin() as conn:
    conn.execute(upsert_stmt)
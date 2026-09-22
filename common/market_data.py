"""Framework-free mock market data generator.

Deterministic per ticker: the price history is seeded from a stable CRC32
hash of the ticker symbol (not Python's salted built-in `hash()`), so the
same ticker always produces the same synthetic data across runs.
"""
import random
import zlib
from datetime import date

CATALOG = {
    "AAPL": 190.0,
    "TSLA": 240.0,
    "GOOG": 165.0,
    "MSFT": 420.0,
    "NVDA": 130.0,
}

HISTORY_DAYS = 30


def list_known_tickers() -> list[str]:
    return sorted(CATALOG)


def is_known_ticker(ticker: str) -> bool:
    return ticker.upper() in CATALOG


def get_market_data(ticker: str) -> dict:
    ticker = ticker.upper()
    if ticker not in CATALOG:
        raise ValueError(f"unknown ticker: {ticker}")

    rng = random.Random(zlib.crc32(ticker.encode()))
    price = CATALOG[ticker]
    history = []
    for _ in range(HISTORY_DAYS):
        pct_move = rng.uniform(-0.03, 0.03)
        price = max(0.01, price * (1 + pct_move))
        history.append(round(price, 2))

    current_price = history[-1]
    previous_price = history[-2]
    day_change_pct = round((current_price - previous_price) / previous_price * 100, 2)
    volume = rng.randint(1_000_000, 50_000_000)

    return {
        "ticker": ticker,
        "current_price": current_price,
        "day_change_pct": day_change_pct,
        "volume": volume,
        "price_history": history,
        "as_of": date.today().isoformat(),
    }

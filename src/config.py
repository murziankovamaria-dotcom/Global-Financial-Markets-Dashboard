"""
Project-wide configuration.

Single source of truth for the asset universe and for every file path, so the
pipeline works no matter which directory it is started from (project root for
``main.py``, ``notebooks/`` for the notebooks).
"""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_CSV = PROJECT_ROOT / "data" / "raw" / "market_data_raw.csv"
PROCESSED_CSV = PROJECT_ROOT / "data" / "processed" / "market_data.csv"
VOLATILITY_CSV = PROJECT_ROOT / "data" / "processed" / "volatility.csv"
DATABASE_PATH = PROJECT_ROOT / "data" / "database" / "market_data.db"

# Length of the history downloaded from Yahoo Finance. It is relative to the
# day the pipeline runs, so every run covers a slightly different window.
PERIOD = "1y"

# ticker -> (asset name, asset class)
ASSETS = {
    "AAPL": ("Apple", "Stock"),
    "MSFT": ("Microsoft", "Stock"),
    "NVDA": ("NVIDIA", "Stock"),
    "^GSPC": ("S&P 500", "Index"),
    "^IXIC": ("NASDAQ Composite", "Index"),
    "BTC-USD": ("Bitcoin", "Cryptocurrency"),
    "ETH-USD": ("Ethereum", "Cryptocurrency"),
    "GC=F": ("Gold", "Commodity"),
    "CL=F": ("Crude Oil", "Commodity"),
    "EURUSD=X": ("EUR/USD", "Forex"),
}

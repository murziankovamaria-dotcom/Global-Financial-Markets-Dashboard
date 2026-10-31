import pandas as pd

from src.config import ASSETS
from src.utils.logger import logger

REQUIRED_COLUMNS = ["Date", "Open", "High", "Low", "Close", "Volume", "Ticker"]


class DataTransformer:
    """
    Cleans, validates, and enriches financial market data.
    This class prepares raw market data for storage,
    analysis, and visualization in Tableau.
    """

    def clean_data(self, data):
        """
        Clean the raw market data.

        Expects the output of ``DataExtractor.download_data`` (a Date index
        and a 'Ticker' column). Removes unnecessary columns and duplicate
        (Date, Ticker) rows, moves the date index into a 'Date' column and
        sorts the rows by date.
        """
        data = data.drop(columns=["Adj Close"], errors="ignore")
        data = data.reset_index()
        data = data.rename(columns={data.columns[0]: "Date"})
        # Duplicates are identified by (Date, Ticker). Comparing only the price
        # columns would also drop legitimate rows from different days that
        # happen to share identical values (e.g. flat FX or zero-volume days).
        data = data.drop_duplicates(subset=["Date", "Ticker"])
        data = data.sort_values(["Date", "Ticker"]).reset_index(drop=True)
        return data

    def validate_data(self, data):
        """
        Validate the processed data.
        Checks for:
        - empty datasets
        - required columns
        - missing values
        - duplicate (Date, Ticker) rows
        - non-positive prices and High < Low

        Raises
        ------
        ValueError
            If the dataset fails validation.
        """
        if data.empty:
            raise ValueError("DataFrame is empty.")
        missing_columns = [c for c in REQUIRED_COLUMNS if c not in data.columns]
        if missing_columns:
            raise ValueError(f"Data is missing required columns: {missing_columns}")
        if data[REQUIRED_COLUMNS].isnull().values.any():
            raise ValueError("Data contains missing values.")
        if data.duplicated(subset=["Date", "Ticker"]).any():
            raise ValueError("Data contains duplicate (Date, Ticker) rows.")
        if (data[["Open", "High", "Low", "Close"]] <= 0).any().any():
            raise ValueError("Data contains non-positive prices.")
        if (data["High"] < data["Low"]).any():
            raise ValueError("Data contains rows where High < Low.")

        # Yahoo occasionally reports a Close a hair outside [Low, High],
        # mostly for EUR/USD. Worth knowing about, not worth stopping for.
        outside = ((data["Close"] > data["High"]) | (data["Close"] < data["Low"])).sum()
        if outside:
            logger.warning("%d rows have a Close outside the [Low, High] range.", outside)

        logger.info(
            "Validated %d rows for %d tickers.", len(data), data["Ticker"].nunique()
        )
        return True

    def calculate_daily_returns(self, data):
        """
        Add two columns for each asset:

        - 'Daily Change': intraday move, Close - Open (in price units).
        - 'Daily Return': close-to-close percentage change versus the previous
          row of the same ticker, as a fraction (0.01 = 1%). The first row of
          every ticker is NaN because there is no previous close.
        """
        data = data.copy()
        data["Daily Change"] = data["Close"] - data["Open"]
        data["Daily Return"] = data.groupby("Ticker")["Close"].pct_change()
        return data

    def normalize_prices(self, data):
        """
        Normalize the closing prices of each asset to a base value of 100
        (its first available close). This allows for easier comparison of
        price movements across different assets.
        """
        data = data.copy()
        first_close = data.groupby("Ticker")["Close"].transform("first")
        data["Normalized Price"] = data["Close"] / first_close * 100
        return data

    def _map_ticker(self, data, column, position):
        """Map each ticker to its name (position 0) or class (position 1)."""
        mapping = {ticker: info[position] for ticker, info in ASSETS.items()}
        data = data.copy()
        data[column] = data["Ticker"].map(mapping)
        unmapped = data.loc[data[column].isna(), "Ticker"].unique()
        if len(unmapped):
            raise ValueError(f"Tickers missing from src/config.py ASSETS: {list(unmapped)}")
        return data

    def add_asset_class(self, data):
        """
        Add an 'Asset Class' column to the market data.
        This column categorizes each financial asset into its respective class,
        such as Stock, Index, Cryptocurrency, Commodity, or Forex.
        """
        return self._map_ticker(data, "Asset Class", 1)

    def add_asset_name(self, data):
        """
        Add an 'Asset Name' column to the market data.
        This column provides a human-readable name for each financial asset.
        """
        return self._map_ticker(data, "Asset Name", 0)

    def calculate_volatility(self, data):
        """
        Volatility of each asset, measured as the standard deviation of its
        daily returns (a fraction, not annualised). Feeds the second Tableau
        data source (volatility.csv).
        """
        return (
            data.groupby(["Asset Name", "Asset Class"])["Daily Return"]
            .std()
            .reset_index()
            .rename(columns={"Daily Return": "Volatility"})
        )

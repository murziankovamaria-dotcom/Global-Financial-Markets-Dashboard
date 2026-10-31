import pandas as pd
import yfinance as yf

from src.config import ASSETS, PERIOD
from src.utils.logger import logger


class DataExtractor:
    """
    Downloads historical financial market data from Yahoo Finance.
    The class retrieves daily market data for a predefined list of
    financial assets, including stocks, stock indices,
    cryptocurrencies, commodities, and exchange rates.
    """

    def __init__(self) -> None:
        """
        Initialize the list of financial assets to download.
        """
        self.tickers = list(ASSETS)

    def download_data(self) -> pd.DataFrame:
        """
        Download the configured period of historical market data
        (see ``PERIOD`` in ``src/config.py``) for all assets.

        Returns
        -------
        pandas.DataFrame
            Combined historical price data for all assets, indexed by
            ``Date``, with an additional 'Ticker' column identifying each asset.

        Raises
        ------
        ValueError
            If Yahoo Finance returns no data for one of the tickers.
        """
        all_data = []

        for ticker in self.tickers:
            data = yf.download(
                ticker,
                period=PERIOD,
                auto_adjust=False,
                progress=False
            )
            if data.empty:
                raise ValueError(f"No data returned by Yahoo Finance for {ticker}.")

            # yfinance returns (Price, Ticker) column levels; keep only Price.
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            data.columns.name = None
            data.index.name = "Date"

            data["Ticker"] = ticker
            all_data.append(data)
            logger.info("Downloaded %s (%d rows)", ticker, len(data))

        return pd.concat(all_data)

import yfinance as yf
import pandas as pd

class DataExtractor:
    """
    Downloads historical financial market data from Yahoo Finance.
    The class retrieves daily market data for a predefined list of
    financial assets, including stocks, stock indices,
    cryptocurrencies, commodities, and exchange rates.
    """
    def __init__(self)-> None:
        """
        Initialize the list of financial assets to download.
        """
        self.tickers = [
            "AAPL",
            "MSFT",
            "NVDA",
            "^GSPC",
            "^IXIC",
            "BTC-USD",
            "ETH-USD",
            "GC=F",
            "CL=F",
            "EURUSD=X"
        ]



    def download_data(self)-> pd.DataFrame:
        """
        Download one year of historical market data for all configured assets.
        Returns
        -------
        pandas.DataFrame
            Combined historical price data for all assets with an
            additional 'Ticker' column identifying each asset.
        """
        all_data = []

        for ticker in self.tickers:
            data = yf.download(
                ticker,
                period="1y",
                auto_adjust=False
            )
            data.columns = data.columns.get_level_values(0)
            data["Ticker"] = ticker
            all_data.append(data)
        return pd.concat(all_data)
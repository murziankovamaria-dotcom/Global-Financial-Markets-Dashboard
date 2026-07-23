import yfinance as yf
import pandas as pd


class DataExtractor:
    def __init__(self):
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

    def download_data(self):
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
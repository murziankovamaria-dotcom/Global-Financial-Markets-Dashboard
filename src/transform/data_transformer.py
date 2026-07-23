class DataTransformer:

    def clean_data(self, data):
        if "Adj Close" in data.columns:
            data = data.drop(columns=["Adj Close"])
        data = data.drop_duplicates()
        data = data.sort_index()
        data = data.reset_index()
        data.rename(columns={data.columns[0]: "Date"}, inplace=True)
        return data
 
    def validate_data(self,data):
        if data.isnull().values.any():
            raise ValueError("Data contains missing values.")
        if not all(col in data.columns for col in ["Open", "Close", "Ticker"]):
            raise ValueError("Data is missing required columns.")
        if data.duplicated().any():
            raise ValueError("Data contains duplicate rows.")
        if data.empty:
            raise ValueError("DataFrame is empty.")
        print("Rows:", len(data))
        print("Tickers:", data["Ticker"].nunique())
        print(data.dtypes)
        return True

    def calculate_daily_returns(self,data):
        data["Daily Change"] = data["Close"] - data["Open"]
        data["Daily Return"] = (data.groupby("Ticker")["Close"].pct_change())

        return data

    def normalize_prices(self,data, tickers):
        data["Normalized Price"] = 0.0
        for ticker in tickers:
            asset = data["Ticker"] == ticker
            first_price = data.loc[asset, "Close"].iloc[0]
            data.loc[asset, "Normalized Price"] = (
                data.loc[asset, "Close"] / first_price) * 100
        return data

    def add_asset_class(self,data):
        asset_class = {
            "AAPL": "Stock",
            "MSFT": "Stock",
            "NVDA": "Stock",
            "^GSPC": "Index",
            "^IXIC": "Index",
            "BTC-USD": "Cryptocurrency",
            "ETH-USD": "Cryptocurrency",
            "GC=F": "Commodity",
            "CL=F": "Commodity",
            "EURUSD=X": "Forex"
        }
        data["Asset Class"] = data["Ticker"].map(asset_class)
        return data
    
    def add_asset_name(self,data):
        asset_name = {
            "AAPL": "Apple",
            "MSFT": "Microsoft",
            "NVDA": "NVIDIA",
            "^GSPC": "S&P 500",
            "^IXIC": "NASDAQ Composite",
            "BTC-USD": "Bitcoin",
            "ETH-USD": "Ethereum",
            "GC=F": "Gold",
            "CL=F": "Crude Oil",
            "EURUSD=X": "EUR/USD"
        }
        data["Asset Name"] = data["Ticker"].map(asset_name)
        return data
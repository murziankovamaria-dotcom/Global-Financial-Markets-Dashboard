import sqlite3

class DataLoader:
    def save_to_csv(self, data, filepath):
        data.to_csv(filepath, index=False)
        print(f"Data saved to {filepath}")

    def save_to_sqlite(self, data):
        connection = sqlite3.connect("../data/database/market_data.db")
        data.to_sql( "market_data",connection,if_exists="replace",index=False)
        connection.close()
        print("Data saved to SQLite.")
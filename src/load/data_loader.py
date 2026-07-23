import sqlite3
class DataLoader:
    """
    Saves processed market data to different storage formats.
    This class supports saving data as CSV files and into
    a SQLite database for later analysis.
    """

    def save_to_csv(self, data, filepath):
        """
        Save a pandas DataFrame as a CSV file.
        Parameters
        ----------
        data
            The processed market data.
        filepath
            Location where the CSV file will be saved.
        """

        data.to_csv(filepath, index=False)
        print(f"Data saved to {filepath}")

    def save_to_sqlite(self, data):
        """
        Save a pandas DataFrame to the SQLite database.
        The existing table is replaced each time the
        function is executed.
        """
        connection = sqlite3.connect("../data/database/market_data.db")
        data.to_sql("market_data", connection, if_exists="replace", index=False)
        connection.close()
        print("Data saved to SQLite.")
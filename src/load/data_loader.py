import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd

from src.config import DATABASE_PATH
from src.utils.logger import logger


class DataLoader:
    """
    Saves processed market data to different storage formats.
    This class supports saving data as CSV files and into
    a SQLite database for later analysis.
    """

    def save_to_csv(self, data, filepath, index=False):
        """
        Save a pandas DataFrame as a CSV file.

        Parameters
        ----------
        data
            The market data.
        filepath
            Location where the CSV file will be saved. Missing folders are created.
        index
            Whether to write the DataFrame index. Use ``True`` for the raw
            download, where the index *is* the Date.
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        data.to_csv(filepath, index=index)
        logger.info("Data saved to %s", filepath)

    def save_to_sqlite(self, data, db_path=DATABASE_PATH, table="market_data"):
        """
        Save a pandas DataFrame to the SQLite database.
        The existing table is replaced each time the
        function is executed. The path is absolute (built from the project
        root), so it works from ``main.py`` and from the notebooks alike.
        """
        db_path = Path(db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        data = data.copy()
        if pd.api.types.is_datetime64_any_dtype(data["Date"]):
            # Store plain ISO dates ('2026-01-02') instead of '2026-01-02 00:00:00'.
            data["Date"] = data["Date"].dt.strftime("%Y-%m-%d")

        with closing(sqlite3.connect(db_path)) as connection:
            data.to_sql(table, connection, if_exists="replace", index=False)
            connection.execute(
                f"CREATE INDEX IF NOT EXISTS idx_{table}_ticker_date "
                f"ON {table} (Ticker, Date)"
            )
            connection.commit()
        logger.info("Data saved to SQLite (%s).", db_path)

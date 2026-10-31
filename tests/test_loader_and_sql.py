"""Tests for the loader and for sql/analysis_queries.sql (no network needed)."""
import sqlite3
from pathlib import Path

import pandas as pd

from src.config import PROJECT_ROOT
from src.load.data_loader import DataLoader

SQL_FILE = PROJECT_ROOT / "sql" / "analysis_queries.sql"


def sample_frame():
    return pd.DataFrame(
        {
            "Date": pd.to_datetime(["2026-01-02", "2026-01-03", "2026-01-02", "2026-01-03"]),
            "Ticker": ["AAPL", "AAPL", "MSFT", "MSFT"],
            "Close": [100.0, 110.0, 50.0, 45.0],
            "Volume": [10, 20, 30, 40],
            "Daily Return": [float("nan"), 0.10, float("nan"), -0.10],
        }
    )


# --------------------------------------------------------------------- loader

def test_save_to_csv_creates_missing_folders(tmp_path):
    target = tmp_path / "a" / "b" / "out.csv"
    DataLoader().save_to_csv(sample_frame(), target)
    assert target.exists()
    assert "Date" in pd.read_csv(target).columns


def test_save_to_csv_can_keep_the_index(tmp_path):
    # The raw download is indexed by Date; saving it with index=False loses the dates.
    raw = sample_frame().set_index("Date")
    target = tmp_path / "raw.csv"
    DataLoader().save_to_csv(raw, target, index=True)
    assert pd.read_csv(target).columns[0] == "Date"


def test_save_to_sqlite_creates_folder_table_and_iso_dates(tmp_path):
    db = tmp_path / "nested" / "market.db"
    DataLoader().save_to_sqlite(sample_frame(), db_path=db)
    with sqlite3.connect(db) as con:
        assert con.execute("SELECT COUNT(*) FROM market_data").fetchone()[0] == 4
        assert con.execute("SELECT MIN(Date) FROM market_data").fetchone()[0] == "2026-01-02"


def test_save_to_sqlite_replaces_the_table(tmp_path):
    db = tmp_path / "market.db"
    DataLoader().save_to_sqlite(sample_frame(), db_path=db)
    DataLoader().save_to_sqlite(sample_frame().iloc[:2], db_path=db)
    with sqlite3.connect(db) as con:
        assert con.execute("SELECT COUNT(*) FROM market_data").fetchone()[0] == 2


# ------------------------------------------------------------------------ SQL

def run_statements(con):
    """Execute every statement of the SQL file, yielding (sql, rows)."""
    text = "\n".join(
        line for line in SQL_FILE.read_text().splitlines() if not line.strip().startswith("--")
    )
    for statement in filter(str.strip, text.split(";")):
        yield statement, con.execute(statement).fetchall()


def test_every_query_in_the_sql_file_runs(tmp_path):
    db = tmp_path / "market.db"
    DataLoader().save_to_sqlite(sample_frame(), db_path=db)
    with sqlite3.connect(db) as con:
        statements = list(run_statements(con))
    assert len(statements) == 10


def test_worst_and_best_day_rankings_ignore_null_returns(tmp_path):
    # Regression: SQLite sorts NULLs first in ASC order, so the first day of each
    # ticker (no previous close, Daily Return NULL) used to fill the "worst days" list.
    db = tmp_path / "market.db"
    DataLoader().save_to_sqlite(sample_frame(), db_path=db)
    with sqlite3.connect(db) as con:
        results = {sql: rows for sql, rows in run_statements(con)}
    ranking = [rows for sql, rows in results.items() if "Worst Daily Return" in sql]
    best = [rows for sql, rows in results.items() if "Best Daily Return" in sql]
    assert ranking and best
    assert all(row[2] is not None for row in ranking[0] + best[0])
    assert ranking[0][0][2] == -0.10

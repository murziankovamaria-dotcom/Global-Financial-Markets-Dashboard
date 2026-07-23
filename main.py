"""
Global Financial Markets Dashboard
----------------------------------

Main entry point for the ETL pipeline.

This script:
1. Extracts financial market data
2. Cleans and validates the data
3. Calculates daily returns
4. Normalizes prices
5. Adds asset metadata
6. Saves the processed data as CSV and SQLite
"""
import sqlite3
from src.extract.data_extractor import DataExtractor
from src.transform.data_transformer import DataTransformer
from src.load.data_loader import DataLoader


def main():
    """Run the complete ETL pipeline."""

    print("=" * 50)
    print("Global Financial Markets Dashboard")
    print("Starting ETL pipeline...")
    print("=" * 50)

    # --------------------------------------------------
    # Initialize classes
    # --------------------------------------------------

    extractor = DataExtractor()
    transformer = DataTransformer()
    loader = DataLoader()

    # --------------------------------------------------
    # Extract
    # --------------------------------------------------

    print("\nDownloading market data...")

    data = extractor.download_data()

    print("✓ Market data downloaded.")

    # --------------------------------------------------
    # Transform
    # --------------------------------------------------

    print("\nCleaning data...")

    data = transformer.clean_data(data)

    print("✓ Data cleaned.")

    print("\nValidating data...")

    transformer.validate_data(data)

    print("✓ Data validated.")

    print("\nCalculating daily returns...")

    data = transformer.calculate_daily_returns(data)

    print("✓ Daily returns calculated.")

    print("\nNormalizing prices...")

    data = transformer.normalize_prices(
        data,
        extractor.tickers
    )

    print("✓ Prices normalized.")

    print("\nAdding asset classes...")

    data = transformer.add_asset_class(data)

    print("✓ Asset classes added.")

    print("\nAdding asset names...")

    data = transformer.add_asset_name(data)

    print("✓ Asset names added.")

    # --------------------------------------------------
    # Load
    # --------------------------------------------------

    print("\nSaving processed data...")

    loader.save_to_csv(
    data,
    "data/processed/market_data.csv"
    )

    connection = sqlite3.connect("data/database/market_data.db")

    print("✓ Data successfully saved.")

    print("\n" + "=" * 50)
    print("ETL pipeline completed successfully!")
    print("=" * 50)


if __name__ == "__main__":
    main()
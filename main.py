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
from src.utils.logger import logger


def main():
    """Run the complete ETL pipeline."""

    print("=" * 50)
    print("Global Financial Markets Dashboard")
    logger.info("Starting ETL pipeline...")
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

    logger.info("Downloading market data...")

    data = extractor.download_data()

    logger.info("✓ Market data downloaded.")

    # --------------------------------------------------
    # Transform
    # --------------------------------------------------

    logger.info("Cleaning data...")

    data = transformer.clean_data(data)

    logger.info("✓ Data cleaned.")

    logger.info("Validating data...")

    transformer.validate_data(data)

    logger.info("✓ Data validated.")

    logger.info("Calculating daily returns...")

    data = transformer.calculate_daily_returns(data)

    logger.info("✓ Daily returns calculated.")

    logger.info("Normalizing prices...")

    data = transformer.normalize_prices(
        data,
        extractor.tickers
    )

    logger.info("✓ Prices normalized.")

    logger.info("Adding asset classes...")

    data = transformer.add_asset_class(data)

    logger.info("✓ Asset classes added.")

    logger.info("Adding asset names...")

    data = transformer.add_asset_name(data)

    logger.info("✓ Asset names added.")

    # --------------------------------------------------
    # Load
    # --------------------------------------------------

    logger.info("Saving processed data...")

    loader.save_to_csv(
    data,
    "data/processed/market_data.csv"
    )

    connection = sqlite3.connect("data/database/market_data.db")

    logger.info("✓ Data successfully saved.")

    print("\n" + "=" * 50)
    print("ETL pipeline completed successfully!")
    print("=" * 50)


if __name__ == "__main__":
    main()
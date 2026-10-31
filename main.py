"""
Global Financial Markets Dashboard
----------------------------------

Main entry point for the ETL pipeline.

This script:
1. Extracts financial market data (and keeps the raw download)
2. Cleans and validates the data
3. Calculates daily returns
4. Normalizes prices
5. Adds asset metadata and volatility
6. Saves the processed data as CSV and SQLite
"""
from src.config import PROCESSED_CSV, RAW_CSV, VOLATILITY_CSV
from src.extract.data_extractor import DataExtractor
from src.transform.data_transformer import DataTransformer
from src.load.data_loader import DataLoader
from src.utils.logger import logger


def main():
    """Run the complete ETL pipeline."""

    print("=" * 50)
    print("Global Financial Markets Dashboard")
    print("=" * 50)
    logger.info("Starting ETL pipeline...")

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

    raw_data = extractor.download_data()

    # The raw download is indexed by Date, so the index must be written too.
    loader.save_to_csv(raw_data, RAW_CSV, index=True)

    logger.info("✓ Market data downloaded.")

    # --------------------------------------------------
    # Transform
    # --------------------------------------------------

    logger.info("Cleaning and validating data...")

    data = transformer.clean_data(raw_data)
    transformer.validate_data(data)

    logger.info("✓ Data cleaned and validated.")

    logger.info("Calculating returns, normalizing prices, adding metadata...")

    data = transformer.calculate_daily_returns(data)
    data = transformer.normalize_prices(data)
    data = transformer.add_asset_class(data)
    data = transformer.add_asset_name(data)
    volatility = transformer.calculate_volatility(data)

    logger.info("✓ Data transformed.")

    # --------------------------------------------------
    # Load
    # --------------------------------------------------

    logger.info("Saving processed data...")

    loader.save_to_csv(data, PROCESSED_CSV)
    loader.save_to_csv(volatility, VOLATILITY_CSV)
    loader.save_to_sqlite(data)

    logger.info("✓ Data successfully saved.")

    print("\n" + "=" * 50)
    print("ETL pipeline completed successfully!")
    print("=" * 50)


if __name__ == "__main__":
    main()

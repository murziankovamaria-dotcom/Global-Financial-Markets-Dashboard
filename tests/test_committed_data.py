"""Consistency checks on the CSV files that feed Tableau.

They catch the kind of drift found in the audit: market_data.csv and
volatility.csv coming from two different downloads.
"""
import pandas as pd
import pytest

from src.config import ASSETS, PROCESSED_CSV, VOLATILITY_CSV


@pytest.fixture(scope="module")
def market():
    return pd.read_csv(PROCESSED_CSV)


@pytest.fixture(scope="module")
def volatility():
    return pd.read_csv(VOLATILITY_CSV)


def test_every_configured_asset_is_present(market):
    assert set(market["Ticker"]) == set(ASSETS)


def test_no_duplicate_date_ticker_rows(market):
    assert not market.duplicated(["Date", "Ticker"]).any()


def test_only_first_day_of_each_ticker_has_no_return(market):
    missing = market[market["Daily Return"].isna()]
    assert len(missing) == market["Ticker"].nunique()
    first_days = market.groupby("Ticker")["Date"].min().sort_index()
    missing_days = missing.set_index("Ticker")["Date"].sort_index()
    pd.testing.assert_series_equal(missing_days, first_days, check_names=False)


def test_normalized_price_is_100_on_the_first_day(market):
    first = market.sort_values("Date").groupby("Ticker")["Normalized Price"].first()
    assert first.round(6).eq(100).all()


def test_all_assets_cover_the_same_period(market):
    span = market.groupby("Ticker")["Date"].agg(["min", "max"])
    assert span["min"].nunique() == 1 and span["max"].nunique() == 1


def test_volatility_csv_matches_market_data_csv(market, volatility):
    expected = (
        market.groupby("Asset Name")["Daily Return"].std().rename("expected").reset_index()
    )
    merged = volatility.merge(expected, on="Asset Name")
    assert len(merged) == len(ASSETS)
    assert (merged["Volatility"] - merged["expected"]).abs().max() < 1e-9

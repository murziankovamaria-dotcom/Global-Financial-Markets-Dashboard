"""Unit tests for src/transform/data_transformer.py (no network needed)."""
import numpy as np
import pandas as pd
import pytest

from src.config import ASSETS
from src.transform.data_transformer import DataTransformer


def make_raw(rows):
    """Build a DataFrame shaped like DataExtractor.download_data() output.

    rows: list of (date, ticker, open, high, low, close, volume)
    """
    df = pd.DataFrame(
        rows, columns=["Date", "Ticker", "Open", "High", "Low", "Close", "Volume"]
    )
    df["Adj Close"] = df["Close"]
    df["Date"] = pd.to_datetime(df["Date"])
    return df.set_index("Date")


def make_clean(rows):
    return DataTransformer().clean_data(make_raw(rows))


# ------------------------------------------------------------------ clean_data

def test_clean_data_moves_date_to_column_and_drops_adj_close():
    data = make_clean([("2026-01-02", "AAPL", 10, 11, 9, 10.5, 100)])
    assert "Date" in data.columns
    assert "Adj Close" not in data.columns


def test_clean_data_removes_true_duplicates():
    row = ("2026-01-02", "AAPL", 10, 11, 9, 10.5, 100)
    assert len(make_clean([row, row])) == 1


def test_clean_data_keeps_different_days_with_identical_prices():
    # Regression: drop_duplicates() used to ignore the date and delete the
    # second row (typical for flat EUR/USD or zero-volume days).
    same = (10, 10, 10, 10, 0)
    data = make_clean(
        [("2026-01-02", "EURUSD=X", *same), ("2026-01-03", "EURUSD=X", *same)]
    )
    assert len(data) == 2


def test_clean_data_sorts_by_date_whatever_the_input_order():
    data = make_clean(
        [
            ("2026-01-03", "AAPL", 1, 1, 1, 1, 1),
            ("2026-01-02", "AAPL", 1, 1, 1, 1, 1),
        ]
    )
    assert data["Date"].is_monotonic_increasing


# --------------------------------------------------------------- validate_data

def valid_frame():
    return make_clean(
        [
            ("2026-01-02", "AAPL", 10, 11, 9, 10.5, 100),
            ("2026-01-03", "AAPL", 10.5, 12, 10, 11, 120),
        ]
    )


def test_validate_accepts_good_data():
    assert DataTransformer().validate_data(valid_frame()) is True


def test_validate_rejects_empty_frame():
    with pytest.raises(ValueError, match="empty"):
        DataTransformer().validate_data(valid_frame().iloc[0:0])


def test_validate_rejects_missing_columns():
    with pytest.raises(ValueError, match="required columns"):
        DataTransformer().validate_data(valid_frame().drop(columns=["Close"]))


def test_validate_rejects_missing_values():
    data = valid_frame()
    data.loc[0, "Close"] = np.nan
    with pytest.raises(ValueError, match="missing values"):
        DataTransformer().validate_data(data)


def test_validate_rejects_duplicate_date_ticker():
    data = pd.concat([valid_frame(), valid_frame().iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="duplicate"):
        DataTransformer().validate_data(data)


def test_validate_rejects_non_positive_prices():
    data = valid_frame()
    data.loc[0, "Open"] = 0
    with pytest.raises(ValueError, match="non-positive"):
        DataTransformer().validate_data(data)


def test_validate_rejects_high_below_low():
    data = valid_frame()
    data.loc[0, ["High", "Low"]] = [5, 9]
    with pytest.raises(ValueError, match="High < Low"):
        DataTransformer().validate_data(data)


# ----------------------------------------------------------- daily returns etc.

def two_asset_frame():
    # Interleaved on purpose: returns must be computed per ticker, not across rows.
    return make_clean(
        [
            ("2026-01-02", "AAPL", 100, 100, 100, 100, 1),
            ("2026-01-02", "MSFT", 50, 50, 50, 50, 1),
            ("2026-01-03", "AAPL", 100, 110, 100, 110, 1),
            ("2026-01-03", "MSFT", 50, 50, 40, 45, 1),
        ]
    )


def test_daily_return_is_close_to_close_per_ticker():
    data = DataTransformer().calculate_daily_returns(two_asset_frame())
    ret = data.set_index(["Ticker", "Date"])["Daily Return"]
    assert ret[("AAPL", pd.Timestamp("2026-01-03"))] == pytest.approx(0.10)
    assert ret[("MSFT", pd.Timestamp("2026-01-03"))] == pytest.approx(-0.10)


def test_first_day_of_each_ticker_has_no_return():
    data = DataTransformer().calculate_daily_returns(two_asset_frame())
    assert data.groupby("Ticker")["Daily Return"].apply(lambda s: s.isna().sum()).eq(1).all()


def test_daily_change_is_close_minus_open():
    data = DataTransformer().calculate_daily_returns(two_asset_frame())
    assert (data["Daily Change"] == data["Close"] - data["Open"]).all()


def test_normalized_price_starts_at_100_for_every_ticker():
    data = DataTransformer().normalize_prices(two_asset_frame())
    first = data.sort_values("Date").groupby("Ticker")["Normalized Price"].first()
    assert (first == 100).all()
    aapl_last = data[(data.Ticker == "AAPL")].sort_values("Date")["Normalized Price"].iloc[-1]
    assert aapl_last == pytest.approx(110)


def test_transformations_do_not_modify_their_input():
    original = two_asset_frame()
    snapshot = original.copy()
    DataTransformer().calculate_daily_returns(original)
    DataTransformer().normalize_prices(original)
    pd.testing.assert_frame_equal(original, snapshot)


# ---------------------------------------------------------------- enrichment

def test_asset_class_and_name_cover_every_configured_ticker():
    t = DataTransformer()
    data = pd.DataFrame({"Ticker": list(ASSETS)})
    data = t.add_asset_name(t.add_asset_class(data))
    assert data["Asset Class"].notna().all() and data["Asset Name"].notna().all()
    assert data.set_index("Ticker").loc["^GSPC", "Asset Name"] == "S&P 500"
    assert data.set_index("Ticker").loc["BTC-USD", "Asset Class"] == "Cryptocurrency"


def test_unknown_ticker_raises_instead_of_producing_nan():
    with pytest.raises(ValueError, match="XYZ"):
        DataTransformer().add_asset_class(pd.DataFrame({"Ticker": ["XYZ"]}))


def test_volatility_is_standard_deviation_of_daily_returns():
    t = DataTransformer()
    data = t.add_asset_name(t.add_asset_class(t.calculate_daily_returns(two_asset_frame())))
    vol = t.calculate_volatility(data).set_index("Asset Name")["Volatility"]
    assert set(vol.index) == {"Apple", "Microsoft"}
    # one return per asset -> std of a single value is NaN, so use a longer series
    long = make_clean([(f"2026-01-{d:02d}", "AAPL", 1, 1, 1, c, 1) for d, c in enumerate([100, 101, 99, 103], 2)])
    long = t.add_asset_name(t.add_asset_class(t.calculate_daily_returns(long)))
    expected = long["Close"].pct_change().std()
    assert t.calculate_volatility(long)["Volatility"].iloc[0] == pytest.approx(expected)

# Global Financial Markets Dashboard

An end-to-end Data Analytics project that automatically collects, processes, stores, analyzes, and visualizes global financial market data.

The project demonstrates a complete ETL (Extract, Transform, Load) pipeline built with Python, SQLite, SQL, and Tableau, following industry best practices for data analytics projects.

---
## 📊 Live Dashboard

**View the interactive dashboard on Tableau Public:**
[Open the Interactive Tableau Dashboard](https://public.tableau.com/views/GlobalFinancialMarkets_17847565599980/GlobalFinancialMarketsDashboard?:language=it-IT&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link)

# Dashboard Preview
![Dashboard](assets/figures/dashboard.png)

---

# Project Overview

This project automatically downloads daily financial market data from Yahoo Finance, cleans and transforms the data, stores it in a SQLite database, performs SQL analysis, and visualizes key market insights using Tableau.

The dashboard allows users to compare the performance of major financial assets including:

- Stock Market Indices
- Technology Stocks
- Cryptocurrencies
- Commodities
- Foreign Exchange

Assets included:

- S&P 500
- NASDAQ Composite
- Apple
- Microsoft
- NVIDIA
- Bitcoin
- Ethereum
- Gold
- Crude Oil
- EUR/USD

---

# Project Architecture

```
               Yahoo Finance API
                      │
                      ▼
             Data Extraction (Python)
                      │
                      ▼
             Data Cleaning & Validation (pandas)
                      │
                      ▼
             SQLite Database Storage
                      │
                      ▼
                SQL Analysis
                      │
                      ▼
            Tableau Dashboard
```

---

# Technologies Used

| Category | Technologies |
|----------|--------------|
| Programming | Python |
| Data Processing | Pandas |
| Financial Data | Yahoo Finance (yfinance) |
| Database | SQLite |
| Query Language | SQL |
| Visualization | Tableau Public |
| IDE | VS Code |
| Version Control | Git & GitHub |

---

# Project Structure

```text
Global-Financial-Markets-Dashboard/
│
├── assets/
│   └── figures/              # charts exported by notebook 02 + dashboard preview
│
├── data/
│   ├── raw/                  # raw Yahoo Finance download (market_data_raw.csv)
│   ├── processed/            # market_data.csv, volatility.csv (Tableau data sources)
│   └── database/             # market_data.db (generated, not tracked by Git)
│
├── notebooks/
│   ├── 01_ETL_Pipeline.ipynb
│   └── 02_SQL_Analysis.ipynb
│
├── sql/
│   └── analysis_queries.sql
│
├── src/
│   ├── config.py             # asset universe, download period, file paths
│   ├── extract/
│   │   └── data_extractor.py
│   ├── transform/
│   │   └── data_transformer.py
│   ├── load/
│   │   └── data_loader.py
│   └── utils/
│       └── logger.py
│
├── tableau/
│   └── Global Financial Markets.twb
│
├── LICENSE
├── README.md
├── requirements.txt
└── main.py
```

---

# Getting Started

```bash
# 1. Clone the repository and enter it
git clone https://github.com/murziankovamaria-dotcom/Global-Financial-Markets-Dashboard.git
cd Global-Financial-Markets-Dashboard

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install the dependencies
pip install -r requirements.txt

# 4. Run the ETL pipeline (needs an internet connection)
python main.py
```

`main.py` downloads the data, saves the raw and processed CSV files, recomputes `volatility.csv` and creates the SQLite database `data/database/market_data.db`. Afterwards, open `notebooks/02_SQL_Analysis.ipynb` to run the SQL analysis. `notebooks/01_ETL_Pipeline.ipynb` runs the same pipeline step by step.

The Tableau workbook in `tableau/` reads `data/processed/market_data.csv` and `data/processed/volatility.csv`. After refreshing the data, open the workbook and re-link both files if Tableau asks for them.

> **Note:** the pipeline downloads the *last 1 year* up to the day it is run (`PERIOD` in `src/config.py`), so each run covers a slightly different window. The CSV files committed to this repository cover 23 July 2025 – 23 July 2026.

---

# Data Dictionary

Columns of `data/processed/market_data.csv` (one row per asset and trading day):

| Column | Description |
|--------|-------------|
| Date | Trading day |
| Open / High / Low / Close | Daily prices as reported by Yahoo Finance (not adjusted for dividends or splits) |
| Volume | Traded volume as reported by Yahoo Finance. The unit differs by asset class (shares for stocks, USD for cryptocurrencies, none for EUR/USD) |
| Ticker | Yahoo Finance symbol |
| Daily Change | Intraday move, `Close - Open`, in price units |
| Daily Return | Close-to-close return versus the previous trading day of the same asset, as a fraction (0.01 = 1%). Empty on the first day of each asset |
| Normalized Price | Close rebased to 100 on the first day |
| Asset Class | Stock, Index, Cryptocurrency, Commodity or Forex |
| Asset Name | Human-readable asset name |

`data/processed/volatility.csv` contains the standard deviation of the daily returns per asset (daily, not annualised).

---

# Limitations

- **Volume is not comparable across asset classes** (see the data dictionary), so volume rankings only make sense within a class.
- Cryptocurrencies trade every day, while stocks, indices and commodities follow exchange calendars, so assets have a different number of observations.
- Returns are based on unadjusted closing prices.
- Yahoo Finance occasionally reports a Close slightly outside the daily High–Low range (mostly EUR/USD). The pipeline logs a warning for these rows and keeps them.
- All assets are quoted in US dollars (indices in points, EUR/USD as dollars per euro), so returns are USD returns and are not converted to other currencies.

---

# Tests

```bash
pip install -r requirements-dev.txt
pytest
```

The tests run offline (they never call Yahoo Finance) and cover the transformations, the loader, every query in `sql/analysis_queries.sql`, and the consistency of the CSV files that feed Tableau. They also run automatically on every push through GitHub Actions (`.github/workflows/ci.yml`).

---

# ETL Pipeline

## Extract

- Downloads historical market data
- Retrieves data for multiple asset classes
- Uses Yahoo Finance API

## Transform

The transformation stage performs:

- Data cleaning
- Duplicate removal
- Missing value validation
- Daily return calculation
- Price normalization
- Asset classification
- Asset name mapping
- Volatility calculation

## Load

The pipeline writes:

- Raw download (CSV)
- Processed data (CSV)
- Volatility per asset (CSV)
- SQLite Database

---

# SQL Analysis

The project includes SQL queries for:

- Best performing assets
- Worst performing assets
- Highest trading volume
- Average daily returns
- Asset class comparison
- Market statistics

---

# Tableau Dashboard

The interactive dashboard provides:

- Asset performance comparison
- Normalized price trends
- Daily returns
- Asset class distribution
- Interactive filters
- KPI cards

---

# Results

The project successfully demonstrates:

- Automated ETL pipeline
- Financial data processing
- Feature engineering
- SQL database management
- Data analysis using SQL
- Interactive business intelligence dashboard

---

# Future Improvements

- Automated daily data refresh
- Environment-based configuration (.env)
- Unit testing
- Docker containerization
- Cloud database support
- GitHub Actions automation
- Additional financial indicators
- Portfolio optimization metrics
- Risk analysis

---

# Author

**Maria Murziankova**

Economics & Finance Student | Data Analytics | Business Intelligence

[![GitHub](https://img.shields.io/badge/GitHub-murziankovamaria--dotcom-181717?style=for-the-badge&logo=github)](https://github.com/murziankovamaria-dotcom)

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Maria%20Murziankova-0077B5?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/maria-murziankova-004522327/)

[![Tableau Public](https://img.shields.io/badge/Tableau-Public-E97627?style=for-the-badge&logo=tableau)](https://public.tableau.com/app/profile/maria.murziankova/vizzes)

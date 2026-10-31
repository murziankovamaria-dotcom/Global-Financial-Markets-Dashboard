-- ==========================================
-- Global Financial Markets Dashboard
-- SQLite Analysis Queries
-- ==========================================

-- 1. Trading days for each asset
SELECT
    Ticker,
    COUNT(*) AS [Trading Days]
FROM market_data
GROUP BY Ticker;


-- 2. Highest and lowest closing prices
SELECT
    Ticker,
    MAX(Close) AS [Highest Closing Price],
    MIN(Close) AS [Lowest Closing Price]
FROM market_data
GROUP BY Ticker
ORDER BY MAX(Close) DESC;


-- 3. Average closing price
SELECT
    Ticker,
    AVG(Close) AS [Average Closing Price]
FROM market_data
GROUP BY Ticker
ORDER BY AVG(Close) DESC;


-- 4. Highest and lowest daily returns
SELECT
    Ticker,
    MAX([Daily Return]) AS [Highest Daily Return],
    MIN([Daily Return]) AS [Lowest Daily Return]
FROM market_data
GROUP BY Ticker
ORDER BY MAX([Daily Return]) DESC;


-- 5. Average daily return
SELECT
    Ticker,
    AVG([Daily Return]) AS [Average Daily Return]
FROM market_data
GROUP BY Ticker
ORDER BY AVG([Daily Return]) DESC;


-- 6. Average trading volume
SELECT
    Ticker,
    AVG(Volume) AS [Average Trading Volume]
FROM market_data
GROUP BY Ticker
ORDER BY AVG(Volume) DESC;


-- 7. Highest trading volume
SELECT
    Ticker,
    MAX(Volume) AS [Highest Trading Volume]
FROM market_data
GROUP BY Ticker
ORDER BY MAX(Volume) DESC;


-- 8. Top 10 best trading days
SELECT
    Ticker,
    Date,
    [Daily Return] AS [Best Daily Return]
FROM market_data
WHERE [Daily Return] IS NOT NULL
ORDER BY [Daily Return] DESC
LIMIT 10;


-- 9. Top 10 worst trading days
-- NULLs (the first day of each ticker has no previous close) sort FIRST in
-- SQLite's ASC order, so they must be filtered out explicitly.
SELECT
    Ticker,
    Date,
    [Daily Return] AS [Worst Daily Return]
FROM market_data
WHERE [Daily Return] IS NOT NULL
ORDER BY [Daily Return] ASC
LIMIT 10;


-- 10. Best and worst trading day for each asset
SELECT
    Ticker,
    Date,
    [Daily Return],
    'Best' AS Return_Type
FROM market_data
WHERE (Ticker, [Daily Return]) IN (
    SELECT
        Ticker,
        MAX([Daily Return])
    FROM market_data
    GROUP BY Ticker
)

UNION ALL

SELECT
    Ticker,
    Date,
    [Daily Return],
    'Worst' AS Return_Type
FROM market_data
WHERE (Ticker, [Daily Return]) IN (
    SELECT
        Ticker,
        MIN([Daily Return])
    FROM market_data
    GROUP BY Ticker
)

ORDER BY Ticker, Return_Type;
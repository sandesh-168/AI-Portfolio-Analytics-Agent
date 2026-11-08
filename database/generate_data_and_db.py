"""
Institutional Portfolio Dataset Generator & Database Seeder
Generates realistic, mathematically consistent portfolio analytics data across:
- Sectors, Securities (Equities & Fixed Income)
- Benchmarks, Portfolios (Active & Inactive across Risk Levels)
- Holdings (with verified Cost Basis and Normalized Weights)
- Transactions, Historical Prices, Performance Returns, and Risk Metrics

Exports to CSV files under data/ and initializes portfolio_database.db.
"""

import os
import csv
import sqlite3
import datetime
from typing import Dict, List, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(BASE_DIR, "portfolio_database.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "database_schema.sql")

os.makedirs(DATA_DIR, exist_ok=True)

def generate_and_seed():
    print("Generating institutional portfolio dataset...")

    # 1. Sectors
    sectors = [
        (1, "Technology", "Software, semiconductors, hardware and IT services", "Information Technology"),
        (2, "Healthcare", "Pharmaceuticals, biotechnology, healthcare equipment and managed care", "Healthcare"),
        (3, "Financial Services", "Diversified banks, asset management, investment banking and insurance", "Financials"),
        (4, "Consumer Cyclical", "Retail, automotive, apparel, leisure and luxury goods", "Consumer Discretionary"),
        (5, "Industrials", "Aerospace, defense, machinery, transportation and industrial conglomerates", "Industrials"),
        (6, "Energy", "Oil & gas exploration, refining, midstream and renewable energy", "Energy"),
        (7, "Communication Services", "Telecommunications, interactive media, entertainment and publishers", "Communications"),
        (8, "Utilities", "Electric, water, gas utilities and independent power producers", "Utilities"),
        (9, "Fixed Income", "Sovereign, corporate, and municipal debt instruments", "Fixed Income")
    ]

    # 2. Securities (30 Equities + 6 Fixed Income Bonds)
    securities = [
        # Tech (sector_id: 1)
        (1, "AAPL", "Apple Inc.", "Stock", 1, 3200000.0, 224.50, "USD", "NASDAQ", "USA", "1980-12-12", None, None),
        (2, "MSFT", "Microsoft Corporation", "Stock", 1, 3100000.0, 415.80, "USD", "NASDAQ", "USA", "1986-03-13", None, None),
        (3, "NVDA", "NVIDIA Corporation", "Stock", 1, 2800000.0, 118.20, "USD", "NASDAQ", "USA", "1999-01-22", None, None),
        (4, "GOOGL", "Alphabet Inc.", "Stock", 1, 2100000.0, 168.40, "USD", "NASDAQ", "USA", "2004-08-19", None, None),
        (5, "ASML", "ASML Holding N.V.", "Stock", 1, 340000.0, 842.10, "USD", "NASDAQ", "Netherlands", "1995-03-15", None, None),
        (6, "TSM", "Taiwan Semiconductor Mfg Co", "Stock", 1, 750000.0, 164.50, "USD", "NYSE", "Taiwan", "1997-10-08", None, None),
        (7, "CRM", "Salesforce Inc.", "Stock", 1, 240000.0, 252.30, "USD", "NYSE", "USA", "2004-06-23", None, None),

        # Healthcare (sector_id: 2)
        (8, "LLY", "Eli Lilly and Company", "Stock", 2, 780000.0, 825.60, "USD", "NYSE", "USA", "1952-02-01", None, None),
        (9, "UNH", "UnitedHealth Group Inc.", "Stock", 2, 510000.0, 562.40, "USD", "NYSE", "USA", "1984-10-17", None, None),
        (10, "JNJ", "Johnson & Johnson", "Stock", 2, 380000.0, 161.20, "USD", "NYSE", "USA", "1944-09-25", None, None),
        (11, "NVO", "Novo Nordisk A/S", "Stock", 2, 520000.0, 114.70, "USD", "NYSE", "Denmark", "1981-04-30", None, None),
        (12, "AZN", "AstraZeneca PLC", "Stock", 2, 240000.0, 78.50, "USD", "NASDAQ", "UK", "1993-05-12", None, None),

        # Financial Services (sector_id: 3)
        (13, "JPM", "JPMorgan Chase & Co.", "Stock", 3, 620000.0, 216.70, "USD", "NYSE", "USA", "1969-03-05", None, None),
        (14, "BAC", "Bank of America Corp.", "Stock", 3, 310000.0, 39.80, "USD", "NYSE", "USA", "1978-08-21", None, None),
        (15, "GS", "Goldman Sachs Group Inc.", "Stock", 3, 165000.0, 485.10, "USD", "NYSE", "USA", "1999-05-04", None, None),
        (16, "HSBC", "HSBC Holdings plc", "Stock", 3, 155000.0, 42.60, "USD", "NYSE", "UK", "1999-07-16", None, None),
        (17, "V", "Visa Inc.", "Stock", 3, 540000.0, 274.90, "USD", "NYSE", "USA", "2008-03-19", None, None),

        # Consumer Cyclical (sector_id: 4)
        (18, "AMZN", "Amazon.com Inc.", "Stock", 4, 1950000.0, 186.50, "USD", "NASDAQ", "USA", "1997-05-15", None, None),
        (19, "TSLA", "Tesla Inc.", "Stock", 4, 780000.0, 245.20, "USD", "NASDAQ", "USA", "2010-06-29", None, None),
        (20, "BABA", "Alibaba Group Holding Ltd", "Stock", 4, 210000.0, 84.30, "USD", "NYSE", "China", "2014-09-19", None, None),
        (21, "NKE", "Nike Inc.", "Stock", 4, 125000.0, 82.40, "USD", "NYSE", "USA", "1980-12-02", None, None),

        # Industrials (sector_id: 5)
        (22, "CAT", "Caterpillar Inc.", "Stock", 5, 170000.0, 355.80, "USD", "NYSE", "USA", "1929-12-02", None, None),
        (23, "GE", "GE Aerospace", "Stock", 5, 190000.0, 178.60, "USD", "NYSE", "USA", "1896-01-02", None, None),
        (24, "UNP", "Union Pacific Corporation", "Stock", 5, 145000.0, 238.40, "USD", "NYSE", "USA", "1969-02-03", None, None),

        # Energy (sector_id: 6)
        (25, "XOM", "Exxon Mobil Corporation", "Stock", 6, 460000.0, 115.20, "USD", "NYSE", "USA", "1928-10-01", None, None),
        (26, "CVX", "Chevron Corporation", "Stock", 6, 275000.0, 148.90, "USD", "NYSE", "USA", "1921-06-20", None, None),
        (27, "SHEL", "Shell plc", "Stock", 6, 215000.0, 68.30, "USD", "NYSE", "UK", "2005-07-20", None, None),

        # Communication Services (sector_id: 7)
        (28, "META", "Meta Platforms Inc.", "Stock", 7, 1420000.0, 560.20, "USD", "NASDAQ", "USA", "2012-05-18", None, None),
        (29, "NFLX", "Netflix Inc.", "Stock", 7, 290000.0, 680.40, "USD", "NASDAQ", "USA", "2002-05-23", None, None),

        # Utilities (sector_id: 8)
        (30, "NEE", "NextEra Energy Inc.", "Stock", 8, 160000.0, 78.90, "USD", "NYSE", "USA", "1950-02-15", None, None),

        # Fixed Income (Bonds - asset_type: 'Bond', sector_id: 9)
        (31, "UST_10Y_2034", "US Treasury Note 10Y 4.125%", "Bond", 9, 10000000.0, 99.45, "USD", "OTC", "USA", "2024-02-15", "2034-02-15", 4.125),
        (32, "UST_05Y_2029", "US Treasury Note 5Y 3.875%", "Bond", 9, 8000000.0, 98.80, "USD", "OTC", "USA", "2024-05-15", "2029-05-15", 3.875),
        (33, "CORP_AAPL_2032", "Apple Inc. Senior Notes 3.95%", "Bond", 9, 2500.0, 96.50, "USD", "OTC", "USA", "2022-08-08", "2032-08-08", 3.950),
        (34, "CORP_JPM_2030", "JPMorgan Chase Co Float/Fix 4.60%", "Bond", 9, 3000.0, 100.20, "USD", "OTC", "USA", "2020-04-22", "2030-04-22", 4.600),
        (35, "MUNI_NYC_2031", "New York City GO Bonds 4.00%", "Bond", 9, 1500.0, 101.10, "USD", "OTC", "USA", "2021-03-01", "2031-03-01", 4.000),
        (36, "BUND_10Y_2034", "German Federal Bund 2.60%", "Bond", 9, 5000000.0, 97.20, "USD", "OTC", "Germany", "2024-01-10", "2034-01-10", 2.600)
    ]

    # 3. Benchmarks
    benchmarks = [
        (1, "S&P 500 Index", "SPX", "Equity", "Large Cap US Equities market-cap weighted benchmark", "1957-03-04"),
        (2, "Nasdaq 100 Index", "NDX", "Equity", "Top 100 non-financial tech and growth US securities", "1985-01-31"),
        (3, "MSCI ACWI Index", "MSCI_ACWI", "Global Equity", "Global developed and emerging markets equity benchmark", "1988-05-31"),
        (4, "Bloomberg US Aggregate Bond Index", "AGG", "Fixed Income", "Investment grade US bond market benchmark", "1986-12-31")
    ]

    # 4. Portfolios
    # Note: Target risk levels: 'High', 'Moderate', 'Low'
    # Question 4 computes: SUM(total_aum) WHERE target_risk_level = 'High'
    # Question 8 tests portfolios with > 5 stock sectors (Global Diversified Fund)
    portfolios = [
        (1, "Growth Equity Fund", "2021-01-15", "High", 125000000.0, "Active Equity Growth", "S&P 500 Index", "Active"),
        (2, "Tech Innovation Fund", "2021-04-01", "High", 85000000.0, "Thematic Technology", "Nasdaq 100 Index", "Active"),
        (3, "International Equity Fund", "2021-06-10", "Moderate", 95000000.0, "Global Core Equity", "MSCI ACWI Index", "Active"),
        (4, "Global Diversified Fund", "2020-09-01", "Moderate", 140000000.0, "Multi-Asset Global", "MSCI ACWI Index", "Active"),
        (5, "Balanced Allocation Fund", "2019-11-15", "Moderate", 75000000.0, "60/40 Asset Allocation", "S&P 500 Index", "Active"),
        (6, "High Yield Income Fund", "2022-02-20", "Low", 50000000.0, "Fixed Income & Dividends", "Bloomberg US Aggregate Bond Index", "Active"),
        (7, "Dynamic Alpha Fund", "2023-01-10", "High", 60000000.0, "Long/Short Opportunistic", "S&P 500 Index", "Active"),
        (8, "Legacy Wealth Preservation Fund", "2018-05-01", "Low", 30000000.0, "Capital Preservation", "Bloomberg US Aggregate Bond Index", "Closed")
    ]

    # 5. Holdings
    # We construct specific holdings for each portfolio to strictly meet the requirements:
    # Portfolio 1: Growth Equity Fund (Has >= 7 holdings with distinct cost basis so top 5 is deterministic)
    # Portfolio 2: Tech Innovation Fund (Tech stocks + 1 Bond to verify equity filtering)
    # Portfolio 3: International Equity Fund (Equities across Global Sectors + Bonds)
    # Portfolio 4: Global Diversified Fund (Stocks across 6 distinct sectors > 5 to satisfy Question 8)
    # Portfolio 5: Balanced Allocation Fund
    # Portfolio 6: High Yield Income Fund
    # Portfolio 7: Dynamic Alpha Fund

    holdings_spec = [
        # Growth Equity Fund (portfolio_id: 1)
        # Cost basis = quantity * purchase_price
        (1, 1, 1, 75000, 180.00, "2023-01-15", 0.22, 75000 * 180.00),      # AAPL: $13.5M
        (2, 1, 2, 35000, 360.00, "2023-02-10", 0.19, 35000 * 360.00),      # MSFT: $12.6M
        (3, 1, 3, 90000, 95.00,  "2023-03-20", 0.14, 90000 * 95.00),       # NVDA: $8.55M
        (4, 1, 18, 50000, 150.00, "2023-04-12", 0.12, 50000 * 150.00),     # AMZN: $7.5M
        (5, 1, 28, 18000, 420.00, "2023-05-18", 0.13, 18000 * 420.00),     # META: $7.56M
        (6, 1, 8, 8000, 680.00,  "2023-06-22", 0.08, 8000 * 680.00),       # LLY:  $5.44M
        (7, 1, 13, 20000, 175.00, "2023-07-05", 0.06, 20000 * 175.00),     # JPM:  $3.5M
        (8, 1, 22, 10000, 280.00, "2023-08-14", 0.04, 10000 * 280.00),     # CAT:  $2.8M
        (9, 1, 31, 30000, 98.00,  "2023-09-01", 0.02, 30000 * 98.00),       # Bond UST_10Y (fixed income)

        # Tech Innovation Fund (portfolio_id: 2)
        # 6 Tech equities + 1 Communication (META) + 1 Bond UST_05Y
        (10, 2, 1, 60000, 190.00, "2023-02-15", 0.22, 60000 * 190.00),     # AAPL (Tech)
        (11, 2, 2, 30000, 370.00, "2023-03-10", 0.20, 30000 * 370.00),     # MSFT (Tech)
        (12, 2, 3, 120000, 85.00, "2023-04-05", 0.23, 120000 * 85.00),     # NVDA (Tech)
        (13, 2, 4, 45000, 140.00, "2023-05-12", 0.12, 45000 * 140.00),     # GOOGL (Tech)
        (14, 2, 7, 25000, 220.00, "2023-06-18", 0.10, 25000 * 220.00),     # CRM (Tech)
        (15, 2, 28, 12000, 450.00, "2023-07-20", 0.08, 12000 * 450.00),    # META (Comm Services)
        (16, 2, 32, 40000, 97.50, "2023-08-15", 0.05, 40000 * 97.50),      # Bond UST_05Y (Bond to ignore in exposure)

        # International Equity Fund (portfolio_id: 3)
        # Multi-region stocks + Bond
        (17, 3, 5, 20000, 750.00, "2023-01-20", 0.25, 20000 * 750.00),     # ASML (Tech, Netherlands)
        (18, 3, 6, 80000, 130.00, "2023-02-15", 0.19, 80000 * 130.00),     # TSM (Tech, Taiwan)
        (19, 3, 11, 70000, 95.00,  "2023-03-12", 0.12, 70000 * 95.00),      # NVO (Healthcare, Denmark)
        (20, 3, 12, 85000, 68.00,  "2023-04-18", 0.10, 85000 * 68.00),      # AZN (Healthcare, UK)
        (21, 3, 16, 120000, 38.00, "2023-05-22", 0.08, 120000 * 38.00),    # HSBC (Financials, UK)
        (22, 3, 20, 75000, 78.00,  "2023-06-10", 0.09, 75000 * 78.00),      # BABA (Consumer, China)
        (23, 3, 27, 80000, 62.00,  "2023-07-15", 0.08, 80000 * 62.00),      # SHEL (Energy, UK)
        (24, 3, 36, 60000, 96.00,  "2023-08-20", 0.09, 60000 * 96.00),      # BUND (Bond to ignore)

        # Global Diversified Fund (portfolio_id: 4)
        # MUST HAVE > 5 distinct STOCK sectors to satisfy Question 8!
        # Sectors: 1(Tech), 2(Healthcare), 3(Financials), 4(Consumer), 5(Industrials), 6(Energy), 7(Comm) = 7 sectors!
        (25, 4, 1, 30000, 195.00, "2023-01-10", 0.14, 30000 * 195.00),     # Tech (AAPL)
        (26, 4, 9, 15000, 490.00, "2023-02-14", 0.17, 15000 * 490.00),     # Healthcare (UNH)
        (27, 4, 13, 35000, 180.00, "2023-03-15", 0.15, 35000 * 180.00),    # Financials (JPM)
        (28, 4, 18, 35000, 155.00, "2023-04-20", 0.13, 35000 * 155.00),    # Consumer (AMZN)
        (29, 4, 22, 20000, 310.00, "2023-05-10", 0.14, 20000 * 310.00),    # Industrials (CAT)
        (30, 4, 25, 45000, 105.00, "2023-06-05", 0.10, 45000 * 105.00),    # Energy (XOM)
        (31, 4, 28, 12000, 480.00, "2023-07-12", 0.13, 12000 * 480.00),    # Comm (META)
        (32, 4, 30, 30000, 72.00,  "2023-08-15", 0.04, 30000 * 72.00),     # Utilities (NEE)

        # Balanced Allocation Fund (portfolio_id: 5)
        (33, 5, 2, 20000, 380.00, "2023-01-10", 0.18, 20000 * 380.00),     # MSFT
        (34, 5, 10, 30000, 155.00, "2023-02-12", 0.10, 30000 * 155.00),    # JNJ
        (35, 5, 17, 25000, 250.00, "2023-03-15", 0.15, 25000 * 250.00),    # V
        (36, 5, 26, 30000, 140.00, "2023-04-20", 0.10, 30000 * 140.00),    # CVX
        (37, 5, 31, 150000, 98.50, "2023-05-15", 0.32, 150000 * 98.50),   # UST_10Y Bond
        (38, 5, 34, 80000, 99.50,  "2023-06-18", 0.15, 80000 * 99.50),    # CORP_JPM Bond

        # High Yield Income Fund (portfolio_id: 6)
        (39, 6, 25, 80000, 110.00, "2023-01-20", 0.24, 80000 * 110.00),    # XOM
        (40, 6, 14, 150000, 36.00, "2023-02-15", 0.16, 150000 * 36.00),   # BAC
        (41, 6, 30, 90000, 74.00,  "2023-03-22", 0.18, 90000 * 74.00),     # NEE
        (42, 6, 31, 120000, 98.20, "2023-04-18", 0.30, 120000 * 98.20),   # UST_10Y
        (43, 6, 35, 45000, 100.80, "2023-05-25", 0.12, 45000 * 100.80),   # MUNI_NYC

        # Dynamic Alpha Fund (portfolio_id: 7)
        (44, 7, 3, 150000, 90.00, "2023-02-10", 0.35, 150000 * 90.00),     # NVDA
        (45, 7, 19, 60000, 210.00, "2023-03-15", 0.30, 60000 * 210.00),    # TSLA
        (46, 7, 29, 25000, 620.00, "2023-04-20", 0.35, 25000 * 620.00)     # NFLX
    ]

    # 6. Transactions (Realistic Buy/Sell history)
    transactions = [
        (1, 1, 1, "BUY", 50000, 175.00, "2023-01-15", 150.0, "2023-01-17", "Initial position build"),
        (2, 1, 1, "BUY", 25000, 190.00, "2023-06-20", 75.0, "2023-06-22", "Add on technical pullback"),
        (3, 1, 2, "BUY", 35000, 360.00, "2023-02-10", 120.0, "2023-02-12", "Core AI infra allocation"),
        (4, 1, 3, "BUY", 90000, 95.00, "2023-03-20", 250.0, "2023-03-22", "GPU accelerator thesis"),
        (5, 2, 1, "BUY", 60000, 190.00, "2023-02-15", 180.0, "2023-02-17", "Tech fund allocation"),
        (6, 2, 3, "BUY", 120000, 85.00, "2023-04-05", 300.0, "2023-04-07", "Overweight semiconductor exposure"),
        (7, 3, 5, "BUY", 20000, 750.00, "2023-01-20", 200.0, "2023-01-22", "European lithography leader"),
        (8, 4, 1, "BUY", 30000, 195.00, "2023-01-10", 90.0, "2023-01-12", "Global diversified allocation")
    ]

    # 7. Historical Prices (Sample 5-day series for key assets)
    historical_prices = [
        (1, 1, "2024-03-25", 220.10, 222.50, 219.40, 221.80, 48200000, 221.80),
        (2, 1, "2024-03-26", 222.00, 225.10, 221.30, 224.50, 52100000, 224.50),
        (3, 2, "2024-03-25", 410.20, 414.00, 408.80, 412.30, 21400000, 412.30),
        (4, 2, "2024-03-26", 413.50, 417.20, 412.00, 415.80, 24100000, 415.80),
        (5, 3, "2024-03-25", 114.50, 117.80, 113.20, 116.40, 95000000, 116.40),
        (6, 3, "2024-03-26", 117.00, 119.50, 116.10, 118.20, 89000000, 118.20),
        (7, 13, "2024-03-25", 212.00, 215.30, 211.20, 214.60, 12500000, 214.60),
        (8, 13, "2024-03-26", 215.00, 217.40, 214.00, 216.70, 11800000, 216.70),
        (9, 25, "2024-03-25", 113.80, 115.60, 113.10, 114.70, 16200000, 114.70),
        (10, 25, "2024-03-26", 114.50, 116.00, 114.00, 115.20, 15400000, 115.20)
    ]

    # 8. Portfolio Performance
    portfolio_performance = [
        (1, 1, "2024-03-31", 125.40, 3.25, 8.40, 15.60, 28.40, 0.162, 1.85, -0.094),
        (2, 2, "2024-03-31", 142.10, 4.80, 12.10, 22.30, 39.50, 0.224, 1.95, -0.142),
        (3, 3, "2024-03-31", 112.50, 2.10, 5.80, 11.20, 18.20, 0.145, 1.42, -0.081),
        (4, 4, "2024-03-31", 118.90, 1.95, 6.20, 12.80, 21.10, 0.138, 1.58, -0.076),
        (5, 5, "2024-03-31", 108.20, 1.15, 3.90, 7.40, 12.60, 0.092, 1.48, -0.052),
        (6, 6, "2024-03-31", 103.80, 0.85, 2.40, 4.90, 8.10, 0.064, 1.35, -0.038),
        (7, 7, "2024-03-31", 136.70, 5.40, 14.80, 26.50, 44.20, 0.265, 1.72, -0.185)
    ]

    # 9. Risk Metrics
    risk_metrics = [
        (1, 1, "2024-03-31", -0.021, -0.034, -0.041, 1.12, 0.94, 0.032, 1.15, 2.45),
        (2, 2, "2024-03-31", -0.029, -0.046, -0.056, 1.38, 0.88, 0.058, 1.28, 2.60),
        (3, 3, "2024-03-31", -0.019, -0.031, -0.038, 0.98, 0.86, 0.041, 0.85, 1.82),
        (4, 4, "2024-03-31", -0.018, -0.029, -0.035, 0.94, 0.92, 0.026, 1.05, 2.10),
        (5, 5, "2024-03-31", -0.012, -0.019, -0.023, 0.62, 0.81, 0.022, 0.95, 2.15),
        (6, 6, "2024-03-31", -0.008, -0.014, -0.017, 0.35, 0.54, 0.035, 0.72, 1.95),
        (7, 7, "2024-03-31", -0.035, -0.054, -0.068, 1.55, 0.82, 0.078, 1.22, 2.18)
    ]

    # Write CSV files
    tables = [
        ("sectors", ["sector_id", "sector_name", "sector_description", "industry_group"], sectors),
        ("securities", ["security_id", "symbol", "company_name", "asset_type", "sector_id", "market_cap", "current_price", "currency", "exchange", "country", "listing_date", "maturity_date", "coupon_rate"], securities),
        ("benchmarks", ["benchmark_id", "benchmark_name", "benchmark_symbol", "benchmark_type", "description", "inception_date"], benchmarks),
        ("portfolios", ["portfolio_id", "portfolio_name", "creation_date", "target_risk_level", "total_aum", "strategy_type", "benchmark_index", "status"], portfolios),
        ("holdings", ["holding_id", "portfolio_id", "security_id", "quantity", "purchase_price", "purchase_date", "current_weight", "cost_basis"], holdings_spec),
        ("transactions", ["transaction_id", "portfolio_id", "security_id", "transaction_type", "quantity", "price", "transaction_date", "fees", "settlement_date", "notes"], transactions),
        ("historical_prices", ["price_id", "security_id", "price_date", "open_price", "high_price", "low_price", "close_price", "volume", "adjusted_close"], historical_prices),
        ("portfolio_performance", ["performance_id", "portfolio_id", "performance_date", "nav", "total_return_1m", "total_return_3m", "total_return_6m", "total_return_1y", "volatility", "sharpe_ratio", "max_drawdown"], portfolio_performance),
        ("risk_metrics", ["risk_id", "portfolio_id", "calculation_date", "var_95", "var_99", "cvar_95", "beta", "correlation_sp500", "tracking_error", "information_ratio", "sortino_ratio"], risk_metrics)
    ]

    for table_name, headers, rows in tables:
        csv_path = os.path.join(DATA_DIR, f"{table_name}.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        print(f"Created {csv_path} ({len(rows)} rows)")

    # Seed SQLite Database
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except Exception:
            pass

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Execute schema
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    cur.executescript(schema_sql)

    # Insert data
    for table_name, headers, rows in tables:
        placeholders = ",".join(["?"] * len(headers))
        query = f"INSERT INTO {table_name} ({','.join(headers)}) VALUES ({placeholders})"
        cur.executemany(query, rows)

    conn.commit()
    conn.close()
    print(f"Successfully initialized and seeded SQLite database at {DB_PATH}")

if __name__ == "__main__":
    generate_and_seed()

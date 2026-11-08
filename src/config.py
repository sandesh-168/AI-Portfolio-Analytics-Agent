"""
Portfolio Analytics Agent Configuration
Centralized settings for database connections, LLM parameters, and safety thresholds.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = BASE_DIR / "portfolio_database.db"
SCHEMA_PATH = BASE_DIR / "database_schema.sql"
GROUND_TRUTH_PATH = BASE_DIR / "ground_truth_dataset.json"

# Gemini API configuration
# Priority: GEMINI_API_KEY environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", os.getenv("GOOGLE_API_KEY", ""))
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
LLM_TEMPERATURE = 0.0  # Zero temperature for deterministic quantitative generation
MAX_RETRIES = 2

# SQL Execution Guardrails
MAX_QUERY_TIMEOUT_SECONDS = 5.0
MAX_ROW_LIMIT = 500
DISALLOWED_SQL_KEYWORDS = {
    "DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "TRUNCATE",
    "REPLACE", "CREATE", "ATTACH", "DETACH", "PRAGMA", "VACUUM"
}

# Quant Analytics Defaults
DEFAULT_RISK_FREE_RATE = 0.0425  # 4.25% annualized 10Y US Treasury yield
DEFAULT_CONFIDENCE_LEVEL = 0.95

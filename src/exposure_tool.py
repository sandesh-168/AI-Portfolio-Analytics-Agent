"""
Equity Sector Exposure Calculator
Quantitatively decomposes portfolio holdings into sector weights.
Strictly isolates equity instruments from fixed-income debt, computing normalized equity factor allocations.
"""

import sqlite3
import difflib
from typing import Dict, List, Any, Optional, Tuple

from src.config import DATABASE_PATH


class ExposureCalculatorTool:
    """Calculates sector exposure breakdowns for institutional portfolios."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = str(db_path) if db_path else str(DATABASE_PATH)

    def resolve_portfolio(self, identifier: Any) -> Optional[Tuple[int, str]]:
        """
        Resolves portfolio ID and canonical name from an ID or fuzzy natural language name.
        Example: 'international equity' -> (3, 'International Equity Fund')
        """
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT portfolio_id, portfolio_name FROM portfolios;")
        portfolios = cur.fetchall()
        conn.close()

        if not portfolios:
            return None

        # Check exact integer ID match
        try:
            p_id = int(identifier)
            for pid, name in portfolios:
                if pid == p_id:
                    return (pid, name)
        except (ValueError, TypeError):
            pass

        # String matching
        target = str(identifier).strip().lower()

        # 1. Exact case-insensitive match
        for pid, name in portfolios:
            if name.lower() == target:
                return (pid, name)

        # 2. Substring match
        for pid, name in portfolios:
            if target in name.lower() or name.lower() in target:
                return (pid, name)

        # 3. Fuzzy ratio match
        names = [p[1] for p in portfolios]
        matches = difflib.get_close_matches(str(identifier), names, n=1, cutoff=0.5)
        if matches:
            matched_name = matches[0]
            for pid, name in portfolios:
                if name == matched_name:
                    return (pid, name)

        return None

    def calculate_sector_exposure(self, portfolio_identifier: Any) -> Dict[str, Any]:
        """
        Executes quantitative exposure analysis for the specified portfolio.
        Excludes fixed income securities (asset_type == 'Bond') as mandated by equity attribution models.
        """
        resolved = self.resolve_portfolio(portfolio_identifier)
        if not resolved:
            return {
                "success": False,
                "error": f"Portfolio '{portfolio_identifier}' could not be resolved in the database.",
                "portfolio_name": str(portfolio_identifier),
                "sector_exposures": {}
            }

        portfolio_id, canonical_name = resolved

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        query = """
        SELECT 
            h.holding_id,
            s.security_id,
            s.symbol,
            s.company_name,
            s.asset_type,
            COALESCE(sec.sector_name, 'Unclassified') as sector_name,
            h.quantity,
            s.current_price,
            (h.quantity * s.current_price) as market_value,
            h.current_weight,
            h.cost_basis
        FROM holdings h
        JOIN securities s ON h.security_id = s.security_id
        LEFT JOIN sectors sec ON s.sector_id = sec.sector_id
        WHERE h.portfolio_id = ?;
        """

        cur.execute(query, (portfolio_id,))
        holdings = cur.fetchall()
        conn.close()

        if not holdings:
            return {
                "success": True,
                "portfolio_id": portfolio_id,
                "portfolio_name": canonical_name,
                "total_portfolio_value": 0.0,
                "total_equity_value": 0.0,
                "total_fixed_income_value": 0.0,
                "sector_exposures": {},
                "sector_breakdown": [],
                "excluded_fixed_income": [],
                "hhi_concentration": 0.0,
                "effective_n_sectors": 0.0,
                "message": "Portfolio currently holds no active positions."
            }

        equity_holdings = []
        fixed_income_holdings = []

        total_portfolio_mv = 0.0
        total_equity_mv = 0.0
        total_fi_mv = 0.0

        for h in holdings:
            mv = float(h["market_value"])
            total_portfolio_mv += mv
            if h["asset_type"] == "Stock":
                equity_holdings.append(h)
                total_equity_mv += mv
            else:
                fixed_income_holdings.append(h)
                total_fi_mv += mv

        if total_equity_mv <= 0.0:
            return {
                "success": True,
                "portfolio_id": portfolio_id,
                "portfolio_name": canonical_name,
                "total_portfolio_value": round(total_portfolio_mv, 2),
                "total_equity_value": 0.0,
                "total_fixed_income_value": round(total_fi_mv, 2),
                "sector_exposures": {},
                "sector_breakdown": [],
                "excluded_fixed_income": [f"{h['symbol']} (${h['market_value']:,.2f})" for h in fixed_income_holdings],
                "hhi_concentration": 0.0,
                "effective_n_sectors": 0.0,
                "message": "Portfolio holds no equity positions (100% fixed income/cash)."
            }

        # Aggregate by sector
        sector_agg: Dict[str, Dict[str, Any]] = {}
        for h in equity_holdings:
            sector = h["sector_name"]
            mv = float(h["market_value"])
            if sector not in sector_agg:
                sector_agg[sector] = {
                    "sector_name": sector,
                    "market_value": 0.0,
                    "holdings_count": 0,
                    "constituents": []
                }
            sector_agg[sector]["market_value"] += mv
            sector_agg[sector]["holdings_count"] += 1
            sector_agg[sector]["constituents"].append({
                "symbol": h["symbol"],
                "company_name": h["company_name"],
                "market_value": round(mv, 2)
            })

        # Calculate normalized percentage weights and concentration indices
        sector_exposures: Dict[str, float] = {}
        sector_breakdown: List[Dict[str, Any]] = []
        sum_sq_weights = 0.0

        for sector, data in sector_agg.items():
            pct_weight = round((data["market_value"] / total_equity_mv) * 100.0, 2)
            sector_exposures[sector] = pct_weight
            sum_sq_weights += (pct_weight / 100.0) ** 2

            # Sort constituents by market value descending
            top_holdings = sorted(data["constituents"], key=lambda x: x["market_value"], reverse=True)
            sector_breakdown.append({
                "sector": sector,
                "weight_pct": pct_weight,
                "market_value_usd": round(data["market_value"], 2),
                "holding_count": data["holdings_count"],
                "top_constituent": top_holdings[0]["symbol"] if top_holdings else None
            })

        # Sort breakdown by weight descending
        sector_breakdown.sort(key=lambda x: x["weight_pct"], reverse=True)

        # Concentration metrics: Herfindahl-Hirschman Index (scale 0 - 10,000) & Effective N
        hhi = round(sum_sq_weights * 10000.0, 1)
        effective_n = round(1.0 / sum_sq_weights, 2) if sum_sq_weights > 0 else 0.0

        excluded_bonds = [
            {
                "symbol": h["symbol"],
                "description": h["company_name"],
                "market_value": round(float(h["market_value"]), 2),
                "asset_type": h["asset_type"]
            }
            for h in fixed_income_holdings
        ]

        equity_ratio = round((total_equity_mv / total_portfolio_mv) * 100.0, 2) if total_portfolio_mv > 0 else 100.0

        return {
            "success": True,
            "portfolio_id": portfolio_id,
            "portfolio_name": canonical_name,
            "total_portfolio_value": round(total_portfolio_mv, 2),
            "total_equity_value": round(total_equity_mv, 2),
            "total_fixed_income_value": round(total_fi_mv, 2),
            "equity_ratio_pct": equity_ratio,
            "sector_exposures": sector_exposures,
            "sector_breakdown": sector_breakdown,
            "excluded_fixed_income": excluded_bonds,
            "hhi_concentration": hhi,
            "effective_n_sectors": effective_n,
            "diversification_rating": (
                "Highly Diversified" if effective_n >= 5.0 else
                "Moderately Diversified" if effective_n >= 3.0 else
                "Concentrated Factor Risk"
            )
        }

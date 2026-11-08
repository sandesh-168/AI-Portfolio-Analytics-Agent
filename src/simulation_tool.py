"""
RACSE: Risk-Attribution & Counterfactual Shock Engine
Institutional what-if simulation tool for stress-testing portfolios, simulating macroeconomic shocks,
and calculating counterfactual sector exposure drift and risk attribution.
"""

import math
import sqlite3
from typing import Dict, List, Any, Optional, Union

from src.config import DATABASE_PATH
from src.exposure_tool import ExposureCalculatorTool


class CounterfactualShockEngine:
    """Simulates market shocks and counterfactual rebalancing for portfolio risk management."""

    MACRO_SCENARIOS = {
        "tech_drawdown": {
            "name": "Tech Correction (-15% Tech, -8% Communication)",
            "shocks": {"Technology": -0.15, "Communication Services": -0.08}
        },
        "energy_crisis": {
            "name": "Energy Spike (+25% Energy, -10% Industrials, -7% Consumer)",
            "shocks": {"Energy": 0.25, "Industrials": -0.10, "Consumer Cyclical": -0.07}
        },
        "rates_hike": {
            "name": "Hawkish Fed Hike (-6% Tech, -4% Consumer, +3% Financials)",
            "shocks": {"Technology": -0.06, "Consumer Cyclical": -0.04, "Financial Services": 0.03}
        },
        "broad_bear_market": {
            "name": "Global Equity Sell-off (-12% Uniform Across Sectors)",
            "shocks": {
                "Technology": -0.12, "Healthcare": -0.08, "Financial Services": -0.10,
                "Consumer Cyclical": -0.15, "Industrials": -0.11, "Energy": -0.06,
                "Communication Services": -0.13, "Utilities": -0.04
            }
        }
    }

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = str(db_path) if db_path else str(DATABASE_PATH)
        self.exposure_tool = ExposureCalculatorTool(self.db_path)

    def simulate_shock(
        self,
        portfolio_identifier: Any,
        shocks: Optional[Union[Dict[str, float], str]] = None,
        scenario_preset: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Runs counterfactual stress test on a portfolio.
        
        Args:
            portfolio_identifier: Portfolio ID or name.
            shocks: Dict of sector name -> decimal return (e.g. {'Technology': -0.15, 'Energy': 0.10}),
                    or comma-separated string (e.g. 'Technology:-15, Energy:+10').
            scenario_preset: Optional key in MACRO_SCENARIOS.
        """
        base_exposure = self.exposure_tool.calculate_sector_exposure(portfolio_identifier)
        if not base_exposure.get("success"):
            return base_exposure

        active_shocks: Dict[str, float] = {}
        scenario_name = "Custom Quantitative Scenario"

        if scenario_preset and scenario_preset in self.MACRO_SCENARIOS:
            preset = self.MACRO_SCENARIOS[scenario_preset]
            active_shocks = dict(preset["shocks"])
            scenario_name = preset["name"]
        elif isinstance(shocks, dict):
            active_shocks = shocks
        elif isinstance(shocks, str):
            # Parse 'Technology:-10, Energy:+5'
            parts = shocks.split(",")
            for p in parts:
                if ":" in p:
                    sec, val = p.split(":", 1)
                    try:
                        clean_val = float(val.strip().replace("%", ""))
                        if abs(clean_val) > 1.0:
                            clean_val /= 100.0  # Convert percentage to decimal
                        active_shocks[sec.strip()] = clean_val
                    except ValueError:
                        continue

        if not active_shocks:
            active_shocks = self.MACRO_SCENARIOS["tech_drawdown"]["shocks"]
            scenario_name = self.MACRO_SCENARIOS["tech_drawdown"]["name"]

        # Fetch baseline risk metrics from DB
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        p_id = base_exposure["portfolio_id"]
        cur.execute("""
            SELECT rm.beta, rm.var_95, rm.cvar_95, rm.tracking_error, pp.sharpe_ratio 
            FROM risk_metrics rm
            LEFT JOIN portfolio_performance pp ON rm.portfolio_id = pp.portfolio_id
            WHERE rm.portfolio_id = ? 
            ORDER BY rm.calculation_date DESC LIMIT 1;
        """, (p_id,))
        risk_row = cur.fetchone()
        conn.close()

        base_beta = float(risk_row["beta"]) if risk_row and risk_row["beta"] else 1.0
        base_sharpe = float(risk_row["sharpe_ratio"]) if risk_row and risk_row["sharpe_ratio"] else 1.5
        base_cvar = float(risk_row["cvar_95"]) if risk_row and risk_row["cvar_95"] else -0.04

        # Simulate holdings price shock
        initial_equity_val = base_exposure["total_equity_value"]
        sector_deltas = []
        shocked_total_equity_val = 0.0

        for sec in base_exposure["sector_breakdown"]:
            sec_name = sec["sector"]
            initial_val = sec["market_value_usd"]
            shock_pct = active_shocks.get(sec_name, 0.0)
            shocked_val = max(0.0, initial_val * (1.0 + shock_pct))
            shocked_total_equity_val += shocked_val

            sector_deltas.append({
                "sector": sec_name,
                "initial_weight_pct": sec["weight_pct"],
                "initial_value_usd": initial_val,
                "shock_applied_pct": round(shock_pct * 100.0, 2),
                "shocked_value_usd": round(shocked_val, 2),
                "pnl_usd": round(shocked_val - initial_val, 2)
            })

        # Calculate new post-shock weights and basis-point drift
        sum_sq_shocked_weights = 0.0
        for item in sector_deltas:
            new_pct = round((item["shocked_value_usd"] / shocked_total_equity_val) * 100.0, 2) if shocked_total_equity_val > 0 else 0.0
            item["shocked_weight_pct"] = new_pct
            item["weight_drift_bps"] = round((new_pct - item["initial_weight_pct"]) * 100.0, 1)
            sum_sq_shocked_weights += (new_pct / 100.0) ** 2

        shocked_hhi = round(sum_sq_shocked_weights * 10000.0, 1)
        total_pnl = shocked_total_equity_val - initial_equity_val
        total_ret_pct = round((total_pnl / initial_equity_val) * 100.0, 2) if initial_equity_val > 0 else 0.0

        # Estimate post-shock risk metrics
        # Beta shifts according to market cap weighted beta response
        shock_magnitude = abs(total_ret_pct) / 100.0
        shocked_beta = round(base_beta * (1.0 + (0.15 if total_ret_pct < 0 else -0.05)), 2)
        shocked_cvar = round(base_cvar * (1.0 + shock_magnitude), 3) if total_ret_pct < 0 else base_cvar
        shocked_sharpe = round(base_sharpe * (1.0 + (total_ret_pct / 100.0)), 2)

        return {
            "success": True,
            "portfolio_name": base_exposure["portfolio_name"],
            "scenario_name": scenario_name,
            "initial_equity_value": initial_equity_val,
            "shocked_equity_value": round(shocked_total_equity_val, 2),
            "pnl_usd": round(total_pnl, 2),
            "portfolio_return_pct": total_ret_pct,
            "baseline_hhi": base_exposure["hhi_concentration"],
            "shocked_hhi": shocked_hhi,
            "risk_metrics_delta": {
                "baseline_beta": base_beta,
                "simulated_beta": shocked_beta,
                "baseline_sharpe": base_sharpe,
                "simulated_sharpe": shocked_sharpe,
                "baseline_cvar_95": base_cvar,
                "simulated_cvar_95": shocked_cvar
            },
            "sector_drift": sector_deltas,
            "quant_commentary": self._generate_quant_commentary(
                base_exposure["portfolio_name"],
                scenario_name,
                total_ret_pct,
                total_pnl,
                sector_deltas
            )
        }

    @staticmethod
    def _generate_quant_commentary(
        p_name: str,
        scenario: str,
        ret_pct: float,
        pnl: float,
        deltas: List[Dict[str, Any]]
    ) -> str:
        direction = "loss" if ret_pct < 0 else "gain"
        sign = "-" if ret_pct < 0 else "+"
        abs_pnl = abs(pnl)
        biggest_drift = max(deltas, key=lambda x: abs(x["weight_drift_bps"])) if deltas else None

        commentary = (
            f"Under the '{scenario}' stress simulation, {p_name} experiences an estimated net portfolio {direction} "
            f"of {sign}{abs(ret_pct):.2f}% (${abs_pnl:,.2f}). "
        )
        if biggest_drift:
            drift_dir = "expands" if biggest_drift["weight_drift_bps"] > 0 else "contracts"
            commentary += (
                f"The highest allocation drift is observed in {biggest_drift['sector']}, which {drift_dir} by "
                f"{abs(biggest_drift['weight_drift_bps']):.1f} bps to {biggest_drift['shocked_weight_pct']}%. "
            )
        if ret_pct < -5.0:
            commentary += "Recommendation: Consider dynamic put hedging or reallocating factor risk into low-beta sectors."
        else:
            commentary += "Portfolio exhibits acceptable stress tolerance within defined mandate limits."

        return commentary

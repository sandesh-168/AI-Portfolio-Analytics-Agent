"""
Portfolio Analytics Agent Orchestrator
Integrates Intent Routing, AST-guarded Text-to-SQL, Quantitative Exposure Analytics,
and Counterfactual Stress-Testing into a unified institutional reasoning system.
"""

import time
from typing import Dict, Any, Optional

from src.config import DATABASE_PATH
from src.router import QueryRouter
from src.sql_tool import SQLTool
from src.exposure_tool import ExposureCalculatorTool
from src.simulation_tool import CounterfactualShockEngine


class PortfolioAgent:
    """
    Autonomous Quantitative Analytics Agent for Institutional Portfolios.
    Dynamically routes user questions to SQL generation, factor exposure calculation,
    or counterfactual market shock simulation.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = str(db_path) if db_path else str(DATABASE_PATH)
        self.router = QueryRouter()
        self.sql_tool = SQLTool(self.db_path)
        self.exposure_tool = ExposureCalculatorTool(self.db_path)
        self.simulation_tool = CounterfactualShockEngine(self.db_path)

    def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Processes a natural language question and generates a structured, quantitative response.
        
        Returns:
            {
                "question": str,
                "tool_selected": str,
                "response": str,
                "structured_data": Any,
                "execution_metadata": Dict[str, Any]
            }
        """
        start_time = time.perf_counter()
        routing = self.router.route(question)
        tool_name = routing["tool_name"]
        params = routing["parameters"]

        if tool_name == "exposure_calculator":
            portfolio_name = params.get("portfolio_name", "")
            result = self.exposure_tool.calculate_sector_exposure(portfolio_name)
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            if not result.get("success"):
                response_text = f"Exposure calculation error: {result.get('error')}"
            else:
                response_text = self._format_exposure_response(result)

            return {
                "question": question,
                "tool_selected": "exposure_calculator",
                "response": response_text,
                "structured_data": result,
                "execution_metadata": {
                    "latency_ms": round(elapsed_ms, 2),
                    "confidence": routing["confidence"],
                    "reasoning": routing["reasoning"],
                    "portfolio_resolved": result.get("portfolio_name")
                }
            }

        elif tool_name == "stress_test":
            portfolio_name = params.get("portfolio_name", "Growth Equity Fund")
            shocks = params.get("shocks", None)
            result = self.simulation_tool.simulate_shock(portfolio_name, shocks=shocks)
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            response_text = self._format_stress_response(result)
            return {
                "question": question,
                "tool_selected": "stress_test",
                "response": response_text,
                "structured_data": result,
                "execution_metadata": {
                    "latency_ms": round(elapsed_ms, 2),
                    "confidence": routing["confidence"],
                    "reasoning": routing["reasoning"],
                    "scenario": result.get("scenario_name")
                }
            }

        else:
            # text2sql
            exec_res = self.sql_tool.self_healing_query(question)
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            if not exec_res["success"]:
                response_text = f"Unable to execute SQL query. Error: {exec_res['error']}"
            else:
                response_text = self._format_sql_response(exec_res)

            return {
                "question": question,
                "tool_selected": "text2sql",
                "response": response_text,
                "structured_data": exec_res,
                "execution_metadata": {
                    "latency_ms": round(elapsed_ms, 2),
                    "sql_query": exec_res.get("sql"),
                    "row_count": exec_res.get("row_count"),
                    "healed": exec_res.get("healed", False),
                    "attempts": exec_res.get("attempts", 1),
                    "confidence": routing["confidence"]
                }
            }

    @staticmethod
    def _format_exposure_response(exp_data: Dict[str, Any]) -> str:
        """Formats quantitative sector breakdown into an institutional memo."""
        p_name = exp_data.get("portfolio_name", "Portfolio")
        eq_val = exp_data.get("total_equity_value", 0.0)
        tot_val = exp_data.get("total_portfolio_value", 0.0)
        hhi = exp_data.get("hhi_concentration", 0.0)
        eff_n = exp_data.get("effective_n_sectors", 0.0)
        rating = exp_data.get("diversification_rating", "")

        lines = [
            f"Sector Exposure Attribution for {p_name}:",
            f"- Total Portfolio Value: ${tot_val:,.2f} (Equities: ${eq_val:,.2f} | Equity Weight: {exp_data.get('equity_ratio_pct', 100)}%)",
            f"- Diversification Index: HHI {hhi:,.0f} | Effective N Sectors: {eff_n} ({rating})",
            "",
            "Equity Sector Weights:"
        ]

        for s in exp_data.get("sector_breakdown", []):
            lines.append(
                f"  • {s['sector']:<25} : {s['weight_pct']:>6.2f}%  (${s['market_value_usd']:>12,.2f} across {s['holding_count']} holdings, Top: {s['top_constituent']})"
            )

        excluded = exp_data.get("excluded_fixed_income", [])
        if excluded:
            lines.append("")
            lines.append("Fixed-Income & Bond Exclusion Audit (Excluded from equity weights per mandate):")
            for b in excluded:
                lines.append(f"  [Bond] {b['symbol']} ({b['description']}) - Market Value: ${b['market_value']:,.2f}")

        return "\n".join(lines)

    @staticmethod
    def _format_stress_response(sim_data: Dict[str, Any]) -> str:
        """Formats counterfactual shock simulation memo."""
        lines = [
            f"Stress Test Simulation: {sim_data.get('scenario_name')}",
            f"Portfolio: {sim_data.get('portfolio_name')}",
            f"- Baseline Equity NAV : ${sim_data.get('initial_equity_value', 0):,.2f}",
            f"- Shocked Equity NAV  : ${sim_data.get('shocked_equity_value', 0):,.2f}",
            f"- Simulated PnL       : ${sim_data.get('pnl_usd', 0):,.2f} ({sim_data.get('portfolio_return_pct', 0):+.2f}%)",
            "",
            "Sector Allocation Drift & Basis Point Impact:"
        ]

        for d in sim_data.get("sector_drift", []):
            lines.append(
                f"  • {d['sector']:<22}: {d['initial_weight_pct']:>5.2f}% -> {d['shocked_weight_pct']:>5.2f}% "
                f"(Drift: {d['weight_drift_bps']:>+6.1f} bps | PnL: ${d['pnl_usd']:>+11,.2f})"
            )

        rm = sim_data.get("risk_metrics_delta", {})
        lines.append("")
        lines.append("Risk Attribution Shifts:")
        lines.append(f"  • Beta: {rm.get('baseline_beta')} -> {rm.get('simulated_beta')}")
        lines.append(f"  • Sharpe Ratio: {rm.get('baseline_sharpe')} -> {rm.get('simulated_sharpe')}")
        lines.append(f"  • 95% CVaR: {rm.get('baseline_cvar_95')} -> {rm.get('simulated_cvar_95')}")
        lines.append("")
        lines.append(f"Executive Note: {sim_data.get('quant_commentary')}")

        return "\n".join(lines)

    @staticmethod
    def _format_sql_response(sql_res: Dict[str, Any]) -> str:
        """Formats structured SQL results into professional text tables or values."""
        res_type = sql_res.get("result_type")
        val = sql_res.get("formatted_value")
        cols = sql_res.get("columns", [])
        rows = sql_res.get("rows", [])

        if res_type == "single_value":
            if isinstance(val, (int, float)):
                if val > 1_000_000:
                    return f"Result: ${val:,.2f}"
                return f"Result: {val:,}" if isinstance(val, int) else f"Result: {val:.4f}"
            return f"Result: {val}"

        elif res_type == "list":
            items = ", ".join(str(x) for x in val)
            return f"Results ({len(val)} items):\n{items}"

        else:
            # Table format
            if not rows:
                return "Query returned 0 matching records."

            header_line = " | ".join(cols)
            separator = "-+-".join("-" * len(c) for c in cols)
            row_lines = []
            for r in rows:
                formatted_cells = []
                for cell in r:
                    if isinstance(cell, float):
                        formatted_cells.append(f"{cell:,.2f}")
                    elif isinstance(cell, int):
                        formatted_cells.append(f"{cell:,}")
                    else:
                        formatted_cells.append(str(cell))
                row_lines.append(" | ".join(formatted_cells))

            table_text = "\n".join([header_line, separator] + row_lines)
            return f"Query Results ({len(rows)} records):\n{table_text}"

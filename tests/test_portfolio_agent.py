"""
Comprehensive Unit and Regression Test Suite for Portfolio Analytics Agent.
Tests AST security validation, equity factor decomposition, counterfactual simulation,
and ground-truth benchmark accuracy.
"""

import sys
import os
import unittest

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.sql_tool import SQLTool, SQLSafetyError
from src.exposure_tool import ExposureCalculatorTool
from src.simulation_tool import CounterfactualShockEngine
from src.router import QueryRouter
from src.agent import PortfolioAgent
from agent_evaluator import AgentEvaluator


class TestSQLSafetyAndExecution(unittest.TestCase):
    def setUp(self):
        self.sql_tool = SQLTool()

    def test_safe_select_allowed(self):
        query = "SELECT COUNT(*) FROM portfolios;"
        res = self.sql_tool.execute_query(query)
        self.assertTrue(res["success"])
        self.assertEqual(res["result_type"], "single_value")
        self.assertEqual(res["formatted_value"], 8)

    def test_prohibited_drop_rejected(self):
        with self.assertRaises(SQLSafetyError):
            self.sql_tool.validate_sql("DROP TABLE portfolios;")

    def test_prohibited_delete_rejected(self):
        with self.assertRaises(SQLSafetyError):
            self.sql_tool.validate_sql("DELETE FROM holdings WHERE holding_id = 1;")

    def test_prohibited_insert_rejected(self):
        with self.assertRaises(SQLSafetyError):
            self.sql_tool.validate_sql("INSERT INTO sectors (sector_name) VALUES ('Crypto');")

    def test_multi_statement_rejected(self):
        with self.assertRaises(SQLSafetyError):
            self.sql_tool.validate_sql("SELECT * FROM sectors; DROP TABLE sectors;")


class TestExposureCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = ExposureCalculatorTool()

    def test_tech_innovation_fund_exposure(self):
        res = self.calc.calculate_sector_exposure("Tech Innovation Fund")
        self.assertTrue(res["success"])
        self.assertEqual(res["portfolio_name"], "Tech Innovation Fund")

        # Verify weights sum to 100%
        exposures = res["sector_exposures"]
        self.assertAlmostEqual(sum(exposures.values()), 100.0, delta=0.5)

        # Verify bonds were segregated
        excluded = res["excluded_fixed_income"]
        self.assertGreaterEqual(len(excluded), 1)
        self.assertEqual(excluded[0]["symbol"], "UST_05Y_2029")

    def test_international_equity_fund_exposure(self):
        res = self.calc.calculate_sector_exposure("international equity")
        self.assertTrue(res["success"])
        self.assertEqual(res["portfolio_name"], "International Equity Fund")

        exposures = res["sector_exposures"]
        self.assertAlmostEqual(sum(exposures.values()), 100.0, delta=0.5)
        self.assertIn("Technology", exposures)
        self.assertIn("Healthcare", exposures)


class TestCounterfactualShockSimulator(unittest.TestCase):
    def setUp(self):
        self.engine = CounterfactualShockEngine()

    def test_macro_shock_simulation(self):
        res = self.engine.simulate_shock("Growth Equity Fund", scenario_preset="tech_drawdown")
        self.assertTrue(res["success"])
        self.assertIn("initial_equity_value", res)
        self.assertIn("shocked_equity_value", res)
        self.assertIn("pnl_usd", res)
        self.assertIn("sector_drift", res)

        # Net return should be negative under tech drawdown
        self.assertLess(res["portfolio_return_pct"], 0.0)

        # Drift basis points should sum approximately to zero
        drifts = [d["weight_drift_bps"] for d in res["sector_drift"]]
        self.assertAlmostEqual(sum(drifts), 0.0, delta=2.0)


class TestQueryRouter(unittest.TestCase):
    def setUp(self):
        self.router = QueryRouter()

    def test_route_counts_to_sql(self):
        res = self.router.route("How many portfolios do we have in total?")
        self.assertEqual(res["tool_name"], "text2sql")

    def test_route_exposure(self):
        res = self.router.route("What are the sector exposures for the Tech Innovation Fund?")
        self.assertEqual(res["tool_name"], "exposure_calculator")
        self.assertEqual(res["parameters"]["portfolio_name"], "Tech Innovation Fund")

    def test_route_stress_test(self):
        res = self.router.route("Simulate a 15% shock on Tech Innovation Fund")
        self.assertEqual(res["tool_name"], "stress_test")


class TestAgentEvaluatorSuite(unittest.TestCase):
    def test_benchmark_full_pass(self):
        evaluator = AgentEvaluator()
        summary = evaluator.run_evaluation(verbose=False)
        self.assertEqual(summary["accuracy_pct"], 100.0)
        self.assertEqual(summary["passed"], 10)


if __name__ == "__main__":
    unittest.main()

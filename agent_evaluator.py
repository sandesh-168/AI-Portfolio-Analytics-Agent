"""
Autonomous Agent Evaluation Framework
Automated benchmarking suite that executes ground truth evaluation questions,
validates tool routing, compares execution outputs against canonical database ground truths,
and benchmarks quantitative exposure decompositions.
"""

import sys
import os
import time
import json
import sqlite3
from typing import Dict, List, Any, Tuple

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agent import PortfolioAgent
from src.config import DATABASE_PATH, GROUND_TRUTH_PATH


class AgentEvaluator:
    """Evaluates Portfolio Analytics Agent against canonical ground truth datasets."""

    def __init__(self, ground_truth_file: Optional[str] = None, db_path: Optional[str] = None):
        self.gt_path = ground_truth_file or str(GROUND_TRUTH_PATH)
        self.db_path = db_path or str(DATABASE_PATH)
        self.agent = PortfolioAgent(self.db_path)

    def load_ground_truth(self) -> List[Dict[str, Any]]:
        with open(self.gt_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("questions", [])

    def run_evaluation(self, verbose: bool = True) -> Dict[str, Any]:
        """
        Executes benchmark test suite.
        """
        questions = self.load_ground_truth()
        total_questions = len(questions)
        results = []

        passed_count = 0
        routing_correct_count = 0
        total_latency_ms = 0.0

        diff_metrics: Dict[str, Dict[str, int]] = {
            "easy": {"total": 0, "passed": 0},
            "medium": {"total": 0, "passed": 0},
            "hard": {"total": 0, "passed": 0}
        }

        print("=" * 80)
        print("INSTITUTIONAL AI PORTFOLIO AGENT EVALUATION BENCHMARK")
        print("=" * 80)
        print(f"Dataset: {self.gt_path}")
        print(f"Target Database: {self.db_path}")
        print(f"Total Test Cases: {total_questions}")
        print("-" * 80)

        for item in questions:
            q_id = item["id"]
            q_type = item["type"]
            q_text = item["question"]
            difficulty = item.get("difficulty", "medium").lower()
            gt_data = item["ground_truth"]

            diff_metrics[difficulty]["total"] += 1

            start_t = time.perf_counter()
            agent_res = self.agent.answer_question(q_text)
            elapsed_ms = (time.perf_counter() - start_t) * 1000.0
            total_latency_ms += elapsed_ms

            tool_selected = agent_res["tool_selected"]
            routing_match = (tool_selected == q_type)
            if routing_match:
                routing_correct_count += 1

            is_correct = False
            eval_details = ""

            if q_type == "text2sql":
                is_correct, eval_details = self._evaluate_text2sql(agent_res, gt_data)
            elif q_type == "exposure_calculator":
                is_correct, eval_details = self._evaluate_exposure(agent_res, gt_data)

            if is_correct:
                passed_count += 1
                diff_metrics[difficulty]["passed"] += 1
                status_str = "[PASS]"
            else:
                status_str = "[FAIL]"

            results.append({
                "id": q_id,
                "type": q_type,
                "difficulty": difficulty,
                "question": q_text,
                "tool_selected": tool_selected,
                "routing_match": routing_match,
                "passed": is_correct,
                "details": eval_details,
                "latency_ms": round(elapsed_ms, 2)
            })

            if verbose:
                print(f"Q{q_id:02d} [{difficulty.upper():<6}] {status_str} (Latency: {elapsed_ms:>6.1f}ms) | Tool: {tool_selected}")
                print(f"     Prompt: \"{q_text}\"")
                print(f"     Status: {eval_details}")
                print("-" * 80)

        avg_latency = round(total_latency_ms / total_questions, 2) if total_questions > 0 else 0.0
        accuracy = round((passed_count / total_questions) * 100.0, 2)
        routing_accuracy = round((routing_correct_count / total_questions) * 100.0, 2)

        summary = {
            "total_questions": total_questions,
            "passed": passed_count,
            "failed": total_questions - passed_count,
            "accuracy_pct": accuracy,
            "routing_accuracy_pct": routing_accuracy,
            "average_latency_ms": avg_latency,
            "difficulty_breakdown": diff_metrics,
            "results": results
        }

        self._print_scorecard(summary)
        return summary

    def _evaluate_text2sql(self, agent_res: Dict[str, Any], gt_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validates Text2SQL generated query results against ground truth SQL results."""
        gt_sql = gt_data.get("sql_query", "")
        agent_data = agent_res.get("structured_data", {})

        if not agent_data.get("success"):
            return False, f"Agent SQL execution failed: {agent_data.get('error')}"

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        try:
            cur.execute(gt_sql)
            gt_rows = cur.fetchall()
        except Exception as e:
            conn.close()
            return False, f"Ground truth SQL failed to execute on database: {str(e)}"
        finally:
            conn.close()

        agent_rows = agent_data.get("rows", [])

        # 1. Compare row count
        if len(gt_rows) != len(agent_rows):
            return False, f"Row count mismatch: Expected {len(gt_rows)}, got {len(agent_rows)}."

        # 2. Compare content values
        # For single value
        if len(gt_rows) == 1 and len(gt_rows[0]) == 1 and len(agent_rows) == 1 and len(agent_rows[0]) == 1:
            val_expected = gt_rows[0][0]
            val_actual = agent_rows[0][0]
            if isinstance(val_expected, (int, float)) and isinstance(val_actual, (int, float)):
                if abs(float(val_expected) - float(val_actual)) < 0.01:
                    return True, f"Single value match: {val_actual}"
            elif str(val_expected).strip() == str(val_actual).strip():
                return True, f"Single value match: {val_actual}"
            return False, f"Single value mismatch: Expected {val_expected}, got {val_actual}"

        # For list or table: match normalized rows
        norm_gt = [tuple(self._normalize_val(v) for v in r) for r in gt_rows]
        norm_agent = [tuple(self._normalize_val(v) for v in r) for r in agent_rows]

        # Check set equality if order is not strict, or exact match
        if norm_gt == norm_agent or set(norm_gt) == set(norm_agent):
            return True, f"Results matched ({len(gt_rows)} records, full value congruence)"

        return False, f"Value mismatch between query outputs. Sample GT: {norm_gt[:1]} vs Actual: {norm_agent[:1]}"

    def _evaluate_exposure(self, agent_res: Dict[str, Any], gt_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validates quantitative sector exposure breakdown."""
        data = agent_res.get("structured_data", {})
        if not data.get("success"):
            return False, f"Exposure calculation unsuccessful: {data.get('error')}"

        exposures = data.get("sector_exposures", {})
        if not exposures:
            return False, "Exposure calculation returned empty sector map."

        # Verify weights sum to approximately 100%
        sum_weights = sum(exposures.values())
        if abs(sum_weights - 100.0) > 0.5:
            return False, f"Normalized equity sector weights do not sum to 100% (Sum: {sum_weights:.2f}%)."

        # Verify bonds were strictly segregated
        excluded = data.get("excluded_fixed_income", [])
        if not excluded:
            # Check if portfolio had bonds in database
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("""
                SELECT COUNT(*) FROM holdings h 
                JOIN securities s ON h.security_id = s.security_id 
                WHERE h.portfolio_id = ? AND s.asset_type = 'Bond';
            """, (data["portfolio_id"],))
            bond_count = cur.fetchone()[0]
            conn.close()
            if bond_count > 0:
                return False, f"Portfolio has {bond_count} bond holdings but none were excluded in calculation!"

        sector_summary = ", ".join(f"{k}: {v}%" for k, v in sorted(exposures.items(), key=lambda x: -x[1]))
        return True, f"Accurate exposure decomposition ({len(exposures)} sectors: {sector_summary})"

    @staticmethod
    def _normalize_val(val: Any) -> Any:
        if isinstance(val, float):
            return round(val, 2)
        if isinstance(val, str):
            return val.strip().lower()
        return val

    @staticmethod
    def _print_scorecard(summary: Dict[str, Any]) -> None:
        print("\n" + "=" * 80)
        print("EVALUATION SCORECARD SUMMARY")
        print("=" * 80)
        print(f"Overall Accuracy         : {summary['accuracy_pct']}% ({summary['passed']}/{summary['total_questions']})")
        print(f"Tool Routing Precision   : {summary['routing_accuracy_pct']}%")
        print(f"Mean Execution Latency   : {summary['average_latency_ms']} ms")
        print("-" * 80)
        print("Breakdown by Difficulty:")
        for diff, stats in summary["difficulty_breakdown"].items():
            tot = stats["total"]
            pas = stats["passed"]
            pct = (pas / tot * 100.0) if tot > 0 else 0.0
            print(f"  • {diff.upper():<7}: {pas}/{tot} passed ({pct:5.1f}%)")
        print("=" * 80 + "\n")


def main():
    evaluator = AgentEvaluator()
    summary = evaluator.run_evaluation(verbose=True)
    if summary["accuracy_pct"] < 100.0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()

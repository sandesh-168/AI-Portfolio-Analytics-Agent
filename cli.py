"""
Portfolio Analytics Agent CLI
Command-line interface for natural language quantitative queries,
interactive portfolio analysis, and counterfactual stress testing.
"""

import sys
import os
import argparse

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agent import PortfolioAgent
from agent_evaluator import AgentEvaluator


def print_banner():
    banner = """
================================================================================
   INSTITUTIONAL AI PORTFOLIO ANALYTICS AGENT (RACSE ENGINE)
   Safe Text-to-SQL  |  Equity Factor Decomposition  |  Shock Simulator
================================================================================
"""
    print(banner)


def run_interactive(agent: PortfolioAgent):
    print_banner()
    print("Interactive Mode Active.")
    print("Type your questions below, or 'exit' / 'quit' to terminate.\n")
    print("Example Queries:")
    print("  1. How many portfolios do we have in total?")
    print("  2. What are the sector exposures for the Tech Innovation Fund?")
    print("  3. Show me the top 5 holdings by cost basis in the Growth Equity Fund")
    print("  4. Stress test Growth Equity Fund with Technology:-15%, Healthcare:+5%\n")

    while True:
        try:
            user_input = input("portfolio-agent> ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("Exiting Portfolio Analytics Agent session.")
                break

            print("\nProcessing quantitative query...")
            result = agent.answer_question(user_input)

            meta = result["execution_metadata"]
            print(f"\n[Tool Selected: {result['tool_selected']} | Latency: {meta.get('latency_ms')}ms]")
            if result['tool_selected'] == 'text2sql' and meta.get('sql_query'):
                print(f"[Executed SQL]: {meta['sql_query']}")

            print("-" * 75)
            print(result["response"])
            print("-" * 75 + "\n")

        except KeyboardInterrupt:
            print("\nSession terminated.")
            break
        except Exception as e:
            print(f"Error processing query: {str(e)}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Autonomous AI Portfolio Analytics Agent CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-q", "--question", type=str, help="Single natural language portfolio question to answer")
    parser.add_argument("-i", "--interactive", action="store_true", help="Launch interactive terminal session")
    parser.add_argument("-e", "--eval", action="store_true", help="Run the automated ground truth evaluation suite")
    parser.add_argument("--stress-test", type=str, help="Portfolio name to simulate counterfactual shock on")
    parser.add_argument("--shock", type=str, help="Comma-separated sector shocks (e.g. 'Technology:-10,Energy:+5')")

    args = parser.parse_args()
    agent = PortfolioAgent()

    if args.eval:
        evaluator = AgentEvaluator()
        summary = evaluator.run_evaluation(verbose=True)
        sys.exit(0 if summary["accuracy_pct"] >= 100.0 else 1)

    elif args.stress_test:
        print_banner()
        print(f"Simulating counterfactual market shock on '{args.stress_test}'...")
        query = f"Simulate market shock on {args.stress_test}"
        if args.shock:
            query += f" with {args.shock}"
        res = agent.answer_question(query)
        print("-" * 75)
        print(res["response"])
        print("-" * 75)

    elif args.question:
        res = agent.answer_question(args.question)
        meta = res["execution_metadata"]
        print(f"[Tool: {res['tool_selected']} | Latency: {meta.get('latency_ms')}ms]")
        if res['tool_selected'] == 'text2sql' and meta.get('sql_query'):
            print(f"[SQL]: {meta['sql_query']}")
        print("-" * 75)
        print(res["response"])
        print("-" * 75)

    else:
        run_interactive(agent)


if __name__ == "__main__":
    main()

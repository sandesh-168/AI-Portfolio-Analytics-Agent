"""
Intent Classifier & Dynamic Tool Router
Analyzes natural language queries and routes them to the appropriate quant tool:
- 'exposure_calculator': Equity factor & sector breakdown
- 'stress_test': What-if shock simulation & counterfactual risk analysis
- 'text2sql': Relational database queries
"""

import re
from typing import Dict, Any, Tuple

class QueryRouter:
    """Classifies user inquiries and extracts canonical execution parameters."""

    EXPOSURE_PATTERNS = [
        r"sector\s+exposure",
        r"sector\s+breakdown",
        r"exposure\s+breakdown",
        r"sector\s+allocation",
        r"exposure\s+for",
        r"breakdown\s+for",
        r"sector\s+weights"
    ]

    STRESS_PATTERNS = [
        r"stress\s*test",
        r"what\s*if",
        r"simulate",
        r"shock",
        r"scenario",
        r"market\s+drawdown",
        r"rebalance"
    ]

    PORTFOLIO_NAMES = [
        "Tech Innovation Fund",
        "Growth Equity Fund",
        "International Equity Fund",
        "Global Diversified Fund",
        "Balanced Allocation Fund",
        "High Yield Income Fund",
        "Dynamic Alpha Fund",
        "Legacy Wealth Preservation Fund"
    ]

    def route(self, question: str) -> Dict[str, Any]:
        """
        Determines the designated tool and extracts parameters.
        Returns:
            {
                "tool_name": "exposure_calculator" | "stress_test" | "text2sql",
                "parameters": {...},
                "confidence": float,
                "reasoning": str
            }
        """
        q_lower = question.lower().strip()

        # Check for stress test / simulation
        for pattern in self.STRESS_PATTERNS:
            if re.search(pattern, q_lower):
                portfolio_name = self._extract_portfolio_name(question)
                return {
                    "tool_name": "stress_test",
                    "parameters": {
                        "portfolio_name": portfolio_name or "Growth Equity Fund",
                        "raw_query": question
                    },
                    "confidence": 0.95,
                    "reasoning": "Query requests counterfactual stress testing or shock simulation."
                }

        # Check for exposure calculator
        # Explicit check: If question asks for sector exposure / breakdown of a specific portfolio
        is_exposure = any(re.search(pat, q_lower) for pat in self.EXPOSURE_PATTERNS)
        
        # Guard: If query is asking "average current price in each sector" or "holdings in > 5 sectors" or "value of tech sector", that is Text2SQL!
        if "average" in q_lower or "avg" in q_lower or "which securities" in q_lower or "more than 5" in q_lower or "for each portfolio" in q_lower:
            is_exposure = False

        if is_exposure:
            portfolio_name = self._extract_portfolio_name(question)
            return {
                "tool_name": "exposure_calculator",
                "parameters": {
                    "portfolio_name": portfolio_name or "Tech Innovation Fund"
                },
                "confidence": 0.95,
                "reasoning": "Query requests portfolio sector exposure breakdown excluding fixed income."
            }

        # Default route to text2sql
        return {
            "tool_name": "text2sql",
            "parameters": {
                "question": question
            },
            "confidence": 0.90,
            "reasoning": "Query requires relational SQL database aggregation, filtering, or join."
        }

    def _extract_portfolio_name(self, text: str) -> str:
        """Extracts portfolio name matching canonical portfolios or fuzzy substrings."""
        text_lower = text.lower()
        for name in self.PORTFOLIO_NAMES:
            if name.lower() in text_lower:
                return name

        # Partial tokens
        if "tech innovation" in text_lower:
            return "Tech Innovation Fund"
        if "international equity" in text_lower:
            return "International Equity Fund"
        if "growth equity" in text_lower:
            return "Growth Equity Fund"
        if "global diversified" in text_lower:
            return "Global Diversified Fund"
        if "balanced" in text_lower:
            return "Balanced Allocation Fund"
        if "income" in text_lower or "high yield" in text_lower:
            return "High Yield Income Fund"
        if "dynamic alpha" in text_lower:
            return "Dynamic Alpha Fund"

        return ""

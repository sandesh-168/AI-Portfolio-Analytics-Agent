"""
Production-Ready Portfolio Analytics REST API
FastAPI service exposing Natural Language Agent query endpoints,
sector exposure decomposition, and counterfactual stress simulation.
"""

import sys
import os
import sqlite3
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import DATABASE_PATH, GROUND_TRUTH_PATH
from src.agent import PortfolioAgent
from src.exposure_tool import ExposureCalculatorTool
from src.simulation_tool import CounterfactualShockEngine
from agent_evaluator import AgentEvaluator

app = FastAPI(
    title="Portfolio Analytics Agent API",
    description="Institutional AI Quantitative Analytics and Counterfactual Shock Simulation API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = PortfolioAgent(str(DATABASE_PATH))
exposure_tool = ExposureCalculatorTool(str(DATABASE_PATH))
simulation_tool = CounterfactualShockEngine(str(DATABASE_PATH))


class QueryRequest(BaseModel):
    question: str = Field(..., description="Natural language question regarding portfolio analytics")


class StressTestRequest(BaseModel):
    portfolio_name: str = Field(..., description="Portfolio identifier or name")
    shocks: Optional[Dict[str, float]] = Field(None, description="Mapping of sector name to decimal shock (e.g. {'Technology': -0.15})")
    scenario_preset: Optional[str] = Field(None, description="Preset scenario (e.g. 'tech_drawdown', 'energy_crisis')")


@app.get("/health")
def health_check():
    """Health check endpoint validating SQLite connection."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM portfolios;")
        count = cur.fetchone()[0]
        conn.close()
        return {"status": "healthy", "database": "connected", "portfolios_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")


@app.post("/api/v1/query")
def process_agent_query(request: QueryRequest):
    """
    Submits a natural language query to the Portfolio Analytics Agent.
    Routes to Text2SQL, Exposure Calculator, or Counterfactual Shock Simulator.
    """
    try:
        result = agent.answer_question(request.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/portfolios")
def list_portfolios(status: Optional[str] = Query(None, description="Filter by status (e.g. 'Active')")):
    """Retrieves all portfolios under management with strategy and AUM metadata."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    if status:
        cur.execute("SELECT * FROM portfolios WHERE status = ?;", (status,))
    else:
        cur.execute("SELECT * FROM portfolios;")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"portfolios": rows, "count": len(rows)}


@app.get("/api/v1/exposure/{portfolio_name}")
def get_sector_exposure(portfolio_name: str):
    """
    Calculates equity sector exposure breakdown for the specified portfolio.
    Excludes bond/fixed-income holdings per equity attribution mandate.
    """
    result = exposure_tool.calculate_sector_exposure(portfolio_name)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Portfolio not found"))
    return result


@app.post("/api/v1/stress-test")
def simulate_portfolio_shock(request: StressTestRequest):
    """
    Executes counterfactual stress testing on a portfolio.
    Calculates post-shock NAV, basis-point allocation drift, and simulated risk shifts.
    """
    result = simulation_tool.simulate_shock(
        request.portfolio_name,
        shocks=request.shocks,
        scenario_preset=request.scenario_preset
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Simulation error"))
    return result


@app.get("/api/v1/evaluate")
def run_evaluation_benchmark():
    """Executes full automated evaluation against the ground truth dataset."""
    evaluator = AgentEvaluator(str(GROUND_TRUTH_PATH), str(DATABASE_PATH))
    summary = evaluator.run_evaluation(verbose=False)
    return summary


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)

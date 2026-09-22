"""Risk-analysis pipeline built with LangGraph.

compute_volatility and compute_drawdown are plain arithmetic - no model
involved, ever. classify_risk is the one judgment call: it uses a real
TypeSafe Jev decision (Choice + Score primitives) when TYPESAFE_API_KEY is
set, and a deterministic formula otherwise - the same real-or-simulated
pattern used by single-prompt-agent, just for a classification step instead
of free text. Either way, LangGraph is the workflow library wiring the
steps together, independent of which classify_risk path runs.
"""
import os
import statistics
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class RiskState(TypedDict, total=False):
    price_history: list[float]
    volatility_pct: float
    max_drawdown_pct: float
    risk_score: int
    risk_rating: str
    risk_source: str
    risk_confidence: float


def compute_volatility(state: RiskState) -> dict:
    prices = state["price_history"]
    returns = [
        (prices[i] - prices[i - 1]) / prices[i - 1] for i in range(1, len(prices))
    ]
    volatility_pct = round(statistics.pstdev(returns) * 100, 2) if returns else 0.0
    return {"volatility_pct": volatility_pct}


def compute_drawdown(state: RiskState) -> dict:
    prices = state["price_history"]
    peak = prices[0] if prices else 0.0
    max_dd = 0.0
    for price in prices:
        peak = max(peak, price)
        if peak > 0:
            max_dd = max(max_dd, (peak - price) / peak)
    return {"max_drawdown_pct": round(max_dd * 100, 2)}


def _classify_deterministic(volatility_pct: float, max_drawdown_pct: float) -> dict:
    score = round(volatility_pct * 12 + max_drawdown_pct * 2)
    score = max(0, min(100, score))
    if score < 35:
        rating = "Low"
    elif score < 70:
        rating = "Medium"
    else:
        rating = "High"
    return {"risk_score": score, "risk_rating": rating, "risk_source": "deterministic"}


async def classify_risk(state: RiskState) -> dict:
    volatility_pct = state["volatility_pct"]
    max_drawdown_pct = state["max_drawdown_pct"]

    if os.environ.get("TYPESAFE_API_KEY") or os.environ.get("AI_GATEWAY_API_KEY"):
        try:
            from .typesafe_jev import classify_with_jev

            return await classify_with_jev(volatility_pct, max_drawdown_pct)
        except Exception:
            pass  # fall through to the deterministic path on any error

    return _classify_deterministic(volatility_pct, max_drawdown_pct)


def build_risk_graph():
    graph = StateGraph(RiskState)
    graph.add_node("compute_volatility", compute_volatility)
    graph.add_node("compute_drawdown", compute_drawdown)
    graph.add_node("classify_risk", classify_risk)
    graph.add_edge(START, "compute_volatility")
    graph.add_edge("compute_volatility", "compute_drawdown")
    graph.add_edge("compute_drawdown", "classify_risk")
    graph.add_edge("classify_risk", END)
    return graph.compile()


async def analyze_risk(price_history: list[float]) -> dict:
    graph = build_risk_graph()
    result = await graph.ainvoke({"price_history": price_history})
    return {
        "volatility_pct": result["volatility_pct"],
        "max_drawdown_pct": result["max_drawdown_pct"],
        "risk_score": result["risk_score"],
        "risk_rating": result["risk_rating"],
        "risk_source": result.get("risk_source", "deterministic"),
        "risk_confidence": result.get("risk_confidence"),
    }

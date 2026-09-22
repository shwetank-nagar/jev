"""Deterministic risk-analysis pipeline built with LangGraph.

No LLM node is used anywhere in this graph — every node is a plain Python
function. This showcases LangGraph purely as a state-graph/workflow library,
independent of any model calls, which keeps the demo runnable with no API
keys.
"""
import statistics
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class RiskState(TypedDict, total=False):
    price_history: list[float]
    volatility_pct: float
    max_drawdown_pct: float
    risk_score: int
    risk_rating: str


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


def classify_risk(state: RiskState) -> dict:
    score = round(state["volatility_pct"] * 12 + state["max_drawdown_pct"] * 2)
    score = max(0, min(100, score))
    if score < 35:
        rating = "Low"
    elif score < 70:
        rating = "Medium"
    else:
        rating = "High"
    return {"risk_score": score, "risk_rating": rating}


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


def analyze_risk(price_history: list[float]) -> dict:
    graph = build_risk_graph()
    result = graph.invoke({"price_history": price_history})
    return {
        "volatility_pct": result["volatility_pct"],
        "max_drawdown_pct": result["max_drawdown_pct"],
        "risk_score": result["risk_score"],
        "risk_rating": result["risk_rating"],
    }

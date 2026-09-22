"""Entry point: runs the risk-analysis agent as a standalone A2A server."""
from a2a.types.a2a_pb2 import (
    AgentCapabilities,
    AgentCard,
    AgentInterface,
    AgentSkill,
)

from common.registry import AGENTS, url_for
from common.server import run_agent_server

from .agent_executor import RiskAnalysisAgentExecutor


def build_agent_card() -> AgentCard:
    return AgentCard(
        name="risk-analysis-agent",
        description=(
            "LangGraph-based agent computing deterministic volatility, "
            "max drawdown, and a 0-100 risk score/rating from a price history."
        ),
        version="0.1.0",
        supported_interfaces=[
            AgentInterface(
                url=url_for("risk_analysis"),
                protocol_binding="JSONRPC",
                protocol_version="1.0",
            ),
        ],
        capabilities=AgentCapabilities(streaming=False),
        default_input_modes=["application/json"],
        default_output_modes=["application/json"],
        skills=[
            AgentSkill(
                id="analyze-risk",
                name="Analyze Risk",
                description=(
                    "Given a price_history list, returns volatility_pct, "
                    "max_drawdown_pct, risk_score, and risk_rating."
                ),
                tags=["finance", "risk", "langgraph"],
                examples=['{"price_history": [100.0, 101.5, 99.0, 103.2]}'],
            ),
        ],
    )


def main() -> None:
    run_agent_server(
        build_agent_card(),
        RiskAnalysisAgentExecutor(),
        port=AGENTS["risk_analysis"]["port"],
    )


if __name__ == "__main__":
    main()

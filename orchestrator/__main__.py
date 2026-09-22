"""Entry point: runs jev itself as an A2A server on its own port."""
from a2a.types.a2a_pb2 import (
    AgentCapabilities,
    AgentCard,
    AgentInterface,
    AgentSkill,
)

from common.registry import AGENTS, url_for
from common.server import run_agent_server

from .jev_executor import JevExecutor


def build_agent_card() -> AgentCard:
    return AgentCard(
        name="jev",
        description=(
            "Investment research orchestrator. Given a stock ticker, delegates "
            "to a market-data agent, a risk-analysis agent, and a report-writer "
            "agent (each built with a different library) over real A2A calls, "
            "then returns a synthesized recommendation."
        ),
        version="0.1.0",
        supported_interfaces=[
            AgentInterface(
                url=url_for("jev"),
                protocol_binding="JSONRPC",
                protocol_version="1.0",
            ),
        ],
        capabilities=AgentCapabilities(streaming=False),
        default_input_modes=["text/plain"],
        default_output_modes=["application/json"],
        skills=[
            AgentSkill(
                id="investment-research",
                name="Investment Research",
                description=(
                    "Given a stock ticker symbol as plain text, returns a "
                    "synthesized investment research report."
                ),
                tags=["finance", "orchestrator", "a2a"],
                examples=["AAPL", "TSLA"],
            ),
        ],
    )


def main() -> None:
    run_agent_server(build_agent_card(), JevExecutor(), port=AGENTS["jev"]["port"])


if __name__ == "__main__":
    main()

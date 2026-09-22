"""Entry point: runs the market-data agent as a standalone A2A server."""
from a2a.types.a2a_pb2 import (
    AgentCapabilities,
    AgentCard,
    AgentInterface,
    AgentSkill,
)

from common.registry import AGENTS, url_for
from common.server import run_agent_server

from .agent_executor import MarketDataAgentExecutor


def build_agent_card() -> AgentCard:
    return AgentCard(
        name="market-data-agent",
        description=(
            "Framework-free agent providing mock stock price history for a "
            "small ticker catalog."
        ),
        version="0.1.0",
        supported_interfaces=[
            AgentInterface(
                url=url_for("market_data"),
                protocol_binding="JSONRPC",
                protocol_version="1.0",
            ),
        ],
        capabilities=AgentCapabilities(streaming=False),
        default_input_modes=["application/json"],
        default_output_modes=["application/json"],
        skills=[
            AgentSkill(
                id="get-market-data",
                name="Get Market Data",
                description=(
                    "Given a ticker symbol, returns current price, 30-day "
                    "price history, day change %, and volume."
                ),
                tags=["finance", "market-data"],
                examples=['{"ticker": "AAPL"}'],
            ),
        ],
    )


def main() -> None:
    run_agent_server(
        build_agent_card(),
        MarketDataAgentExecutor(),
        port=AGENTS["market_data"]["port"],
    )


if __name__ == "__main__":
    main()

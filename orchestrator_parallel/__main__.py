"""Entry point: runs jev-parallel as a standalone A2A server."""
from a2a.types.a2a_pb2 import (
    AgentCapabilities,
    AgentCard,
    AgentInterface,
    AgentSkill,
)

from common.registry import AGENTS, url_for
from common.server import run_agent_server

from .parallel_executor import ParallelJevExecutor


def build_agent_card() -> AgentCard:
    return AgentCard(
        name="jev-parallel",
        description=(
            "Parallel counterpart to jev. Given a stock ticker, calls "
            "market-data-agent and risk-analysis-agent concurrently (instead "
            "of chaining them), then report-writer-agent. Used to compare "
            "orchestration latency against jev's sequential chain."
        ),
        version="0.1.0",
        supported_interfaces=[
            AgentInterface(
                url=url_for("jev_parallel"),
                protocol_binding="JSONRPC",
                protocol_version="1.0",
            ),
        ],
        capabilities=AgentCapabilities(streaming=False),
        default_input_modes=["text/plain"],
        default_output_modes=["application/json"],
        skills=[
            AgentSkill(
                id="investment-research-parallel",
                name="Investment Research (Parallel)",
                description=(
                    "Given a stock ticker symbol as plain text, returns a "
                    "synthesized investment research report, fetching market "
                    "data and risk analysis concurrently."
                ),
                tags=["finance", "orchestrator", "a2a", "parallel"],
                examples=["AAPL", "TSLA"],
            ),
        ],
    )


def main() -> None:
    run_agent_server(
        build_agent_card(),
        ParallelJevExecutor(),
        port=AGENTS["jev_parallel"]["port"],
    )


if __name__ == "__main__":
    main()

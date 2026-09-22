"""Entry point: runs the single-prompt baseline as a standalone A2A server."""
from a2a.types.a2a_pb2 import (
    AgentCapabilities,
    AgentCard,
    AgentInterface,
    AgentSkill,
)

from common.registry import AGENTS, url_for
from common.server import run_agent_server

from .agent_executor import SinglePromptAgentExecutor


def build_agent_card() -> AgentCard:
    return AgentCard(
        name="single-prompt-agent",
        description=(
            "Baseline comparison agent: does market analysis, risk assessment, "
            "and report writing in a single model completion (or a simulated "
            "equivalent without an API key), instead of jev's pipeline of fast "
            "specialized agents. Used to show the latency cost of a monolithic "
            "prompt versus agentic decomposition."
        ),
        version="0.1.0",
        supported_interfaces=[
            AgentInterface(
                url=url_for("single_prompt"),
                protocol_binding="JSONRPC",
                protocol_version="1.0",
            ),
        ],
        capabilities=AgentCapabilities(streaming=False),
        default_input_modes=["text/plain"],
        default_output_modes=["application/json"],
        skills=[
            AgentSkill(
                id="single-prompt-research",
                name="Single-Prompt Investment Research",
                description=(
                    "Given a stock ticker symbol as plain text, returns an "
                    "investment research note produced by a single model "
                    "completion (real if ANTHROPIC_API_KEY is set, else "
                    "simulated)."
                ),
                tags=["finance", "baseline", "llm"],
                examples=["AAPL", "TSLA"],
            ),
        ],
    )


def main() -> None:
    run_agent_server(
        build_agent_card(),
        SinglePromptAgentExecutor(),
        port=AGENTS["single_prompt"]["port"],
    )


if __name__ == "__main__":
    main()

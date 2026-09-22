"""Entry point: runs the report-writer agent as a standalone A2A server."""
from a2a.types.a2a_pb2 import (
    AgentCapabilities,
    AgentCard,
    AgentInterface,
    AgentSkill,
)

from common.registry import AGENTS, url_for
from common.server import run_agent_server

from .agent_executor import ReportWriterAgentExecutor


def build_agent_card() -> AgentCard:
    return AgentCard(
        name="report-writer-agent",
        description=(
            "Jinja2-templating agent that synthesizes market data and risk "
            "analysis into a narrative investment note with a recommendation."
        ),
        version="0.1.0",
        supported_interfaces=[
            AgentInterface(
                url=url_for("report_writer"),
                protocol_binding="JSONRPC",
                protocol_version="1.0",
            ),
        ],
        capabilities=AgentCapabilities(streaming=False),
        default_input_modes=["application/json"],
        default_output_modes=["application/json"],
        skills=[
            AgentSkill(
                id="write-report",
                name="Write Report",
                description=(
                    "Given market_data and risk_data objects, returns a "
                    "rendered narrative report with a recommendation."
                ),
                tags=["finance", "reporting", "jinja2"],
                examples=['{"market_data": {...}, "risk_data": {...}}'],
            ),
        ],
    )


def main() -> None:
    run_agent_server(
        build_agent_card(),
        ReportWriterAgentExecutor(),
        port=AGENTS["report_writer"]["port"],
    )


if __name__ == "__main__":
    main()

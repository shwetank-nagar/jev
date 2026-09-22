"""Shared helper to run an AgentExecutor as a standalone A2A HTTP server."""
import uvicorn
from fastapi import FastAPI

from a2a.server.agent_execution import AgentExecutor
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import (
    add_a2a_routes_to_fastapi,
    create_agent_card_routes,
    create_jsonrpc_routes,
    create_rest_routes,
)
from a2a.server.tasks import InMemoryTaskStore
from a2a.types.a2a_pb2 import AgentCard


def run_agent_server(agent_card: AgentCard, executor: AgentExecutor, port: int) -> None:
    """Wire up an AgentExecutor behind the A2A protocol routes and serve it."""
    handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
        agent_card=agent_card,
    )
    app = FastAPI(title=agent_card.name)
    add_a2a_routes_to_fastapi(
        app,
        agent_card_routes=create_agent_card_routes(agent_card),
        jsonrpc_routes=create_jsonrpc_routes(handler, rpc_url="/"),
        rest_routes=create_rest_routes(handler),
    )
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

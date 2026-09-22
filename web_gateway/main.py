"""FastAPI gateway for the React UI.

The browser only ever talks plain REST/JSON to this service. This service
is what actually speaks A2A (via a2a_bridge / registry_store) to jev,
jev-parallel, and any registered agent - so the protocol demonstration stays
real end to end, while the frontend stays simple.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from common.market_data import list_known_tickers
from common.registry import GATEWAY_PORT, url_for

from . import registry_store
from .a2a_bridge import ask_agent


@asynccontextmanager
async def lifespan(app: FastAPI):
    registry_store.seed_registry()
    await registry_store.refresh_all()
    yield


app = FastAPI(title="jev web gateway", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/tickers")
async def get_tickers():
    return {"tickers": list_known_tickers()}


@app.get("/api/agents")
async def get_agents():
    return {"agents": registry_store.list_agents()}


class RegisterRequest(BaseModel):
    url: str
    label: str | None = None


@app.post("/api/agents")
async def post_agent(req: RegisterRequest):
    try:
        return await registry_store.register(req.url, req.label)
    except Exception as exc:  # noqa: BLE001 - surfaced to the UI as an error
        raise HTTPException(
            status_code=400, detail=f"could not fetch agent card from {req.url!r}: {exc}"
        ) from exc


@app.delete("/api/agents")
async def delete_agent(url: str):
    if not registry_store.unregister(url):
        raise HTTPException(status_code=404, detail="agent not registered")
    return {"ok": True}


_MODE_TO_AGENT_KEY = {
    "sequential": "jev",
    "parallel": "jev_parallel",
    "single_prompt": "single_prompt",
}


class AskRequest(BaseModel):
    ticker: str
    mode: str = "sequential"  # "sequential" (jev) | "parallel" (jev-parallel) | "single_prompt"


@app.post("/api/ask")
async def post_ask(req: AskRequest):
    agent_key = _MODE_TO_AGENT_KEY.get(req.mode)
    if agent_key is None:
        raise HTTPException(status_code=400, detail=f"unknown mode: {req.mode!r}")
    try:
        result, elapsed_ms = await ask_agent(url_for(agent_key), req.ticker)
    except Exception as exc:  # noqa: BLE001 - surfaced to the UI as an error
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {
        "mode": req.mode,
        "ticker": req.ticker.upper(),
        "result": result,
        "elapsed_ms": round(elapsed_ms, 1),
    }


class CompareRequest(BaseModel):
    ticker: str


@app.post("/api/compare")
async def post_compare(req: CompareRequest):
    try:
        seq_result, seq_ms = await ask_agent(url_for("jev"), req.ticker)
        par_result, par_ms = await ask_agent(url_for("jev_parallel"), req.ticker)
        sp_result, sp_ms = await ask_agent(url_for("single_prompt"), req.ticker)
    except Exception as exc:  # noqa: BLE001 - surfaced to the UI as an error
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {
        "ticker": req.ticker.upper(),
        "sequential": {"result": seq_result, "elapsed_ms": round(seq_ms, 1)},
        "parallel": {"result": par_result, "elapsed_ms": round(par_ms, 1)},
        "single_prompt": {"result": sp_result, "elapsed_ms": round(sp_ms, 1)},
    }


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=GATEWAY_PORT, log_level="info")


if __name__ == "__main__":
    main()

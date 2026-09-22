"""Central registry of local agent endpoints for the jev demo."""

AGENTS = {
    "market_data": {"host": "localhost", "port": 9001},
    "risk_analysis": {"host": "localhost", "port": 9002},
    "report_writer": {"host": "localhost", "port": 9003},
    "jev": {"host": "localhost", "port": 9000},
    "jev_parallel": {"host": "localhost", "port": 9010},
    "single_prompt": {"host": "localhost", "port": 9011},
}

GATEWAY_PORT = 9020


def url_for(name: str) -> str:
    entry = AGENTS[name]
    return f"http://{entry['host']}:{entry['port']}/"

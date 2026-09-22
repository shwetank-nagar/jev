"""Convenience launcher for the jev demo.

Starts every backend A2A agent (including jev-parallel) plus the web
gateway, waits until each is reachable, then leaves them running. Use the
web UI (see README - `cd web && npm run dev`) or `python -m orchestrator.cli`
in another terminal to interact. Ctrl+C stops every backend service started
here.
"""
import subprocess
import sys
import time
import urllib.error
import urllib.request

from common.registry import AGENTS, GATEWAY_PORT, url_for

SERVERS = [
    ("market_data", [sys.executable, "-m", "agents.market_data_agent"]),
    ("risk_analysis", [sys.executable, "-m", "agents.risk_analysis_agent"]),
    ("report_writer", [sys.executable, "-m", "agents.report_writer_agent"]),
    ("single_prompt", [sys.executable, "-m", "agents.single_prompt_agent"]),
    ("jev", [sys.executable, "-m", "orchestrator"]),
    ("jev_parallel", [sys.executable, "-m", "orchestrator_parallel"]),
]

READY_TIMEOUT_SECONDS = 30


def wait_until_url_ready(url: str, label: str) -> None:
    deadline = time.time() + READY_TIMEOUT_SECONDS
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as resp:
                if resp.status == 200:
                    return
        except (urllib.error.URLError, ConnectionError, TimeoutError):
            pass
        time.sleep(0.2)
    raise RuntimeError(f"{label} did not become ready at {url}")


def main() -> None:
    processes: list[subprocess.Popen] = []
    try:
        for name, cmd in SERVERS:
            port = AGENTS[name]["port"]
            print(f"Starting {name} agent on port {port} ...", flush=True)
            processes.append(subprocess.Popen(cmd))

        for name, _ in SERVERS:
            wait_until_url_ready(url_for(name) + ".well-known/agent-card.json", name)

        print(f"Starting web gateway on port {GATEWAY_PORT} ...", flush=True)
        processes.append(subprocess.Popen([sys.executable, "-m", "web_gateway"]))
        wait_until_url_ready(f"http://localhost:{GATEWAY_PORT}/api/tickers", "web gateway")

        print("\nAll backend services are up:", flush=True)
        for name, _ in SERVERS:
            print(f"  {name:15s} {url_for(name)}", flush=True)
        print(f"  {'gateway':15s} http://localhost:{GATEWAY_PORT}/", flush=True)
        print(
            "\nWeb UI: in another terminal run `cd web && npm run dev`, "
            "then open http://localhost:5173",
            flush=True,
        )
        print(
            "Terminal chat instead: `python -m orchestrator.cli` in another terminal",
            flush=True,
        )
        print("\nPress Ctrl+C to stop all backend services.", flush=True)

        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        pass
    finally:
        print("\nShutting down agents...", flush=True)
        for proc in processes:
            proc.terminate()
        for proc in processes:
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()


if __name__ == "__main__":
    main()

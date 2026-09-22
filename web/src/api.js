const GATEWAY_URL = "http://localhost:9020";

async function request(path, options) {
  const res = await fetch(`${GATEWAY_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `${res.status} ${res.statusText}`);
  }
  return res.json();
}

export function getTickers() {
  return request("/api/tickers");
}

export function getAgents() {
  return request("/api/agents");
}

export function registerAgent(url, label) {
  return request("/api/agents", {
    method: "POST",
    body: JSON.stringify({ url, label: label || null }),
  });
}

export function unregisterAgent(url) {
  return request(`/api/agents?url=${encodeURIComponent(url)}`, {
    method: "DELETE",
  });
}

export function ask(ticker, mode) {
  return request("/api/ask", {
    method: "POST",
    body: JSON.stringify({ ticker, mode }),
  });
}

export function compare(ticker) {
  return request("/api/compare", {
    method: "POST",
    body: JSON.stringify({ ticker }),
  });
}

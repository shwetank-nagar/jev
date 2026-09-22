import { useEffect, useState } from "react";
import { getAgents, registerAgent, unregisterAgent } from "../api.js";

export default function RegisterTab({ onRegistered }) {
  const [url, setUrl] = useState("");
  const [label, setLabel] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [lastRegistered, setLastRegistered] = useState(null);
  const [agents, setAgents] = useState([]);

  async function loadAgents() {
    try {
      const data = await getAgents();
      setAgents(data.agents);
    } catch {
      // best-effort list, errors surface via the register action itself
    }
  }

  useEffect(() => {
    loadAgents();
  }, []);

  async function handleRegister() {
    const u = url.trim();
    if (!u || busy) return;
    setBusy(true);
    setError(null);
    try {
      const res = await registerAgent(u, label.trim());
      setLastRegistered(res);
      setUrl("");
      setLabel("");
      await loadAgents();
      onRegistered?.();
    } catch (err) {
      setError(err.message);
      setLastRegistered(null);
    } finally {
      setBusy(false);
    }
  }

  async function handleRemove(agentUrl) {
    try {
      await unregisterAgent(agentUrl);
      await loadAgents();
      onRegistered?.();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div>
      <p style={styles.intro}>
        Register any A2A-compliant agent by its base URL - the gateway fetches{" "}
        <code>&lt;url&gt;/.well-known/agent-card.json</code> to validate it, then
        it shows up in the Agent Cards tab. Try re-registering one of the demo
        agents below under a new label, or point it at any other A2A server you
        have running.
      </p>

      <div style={styles.form}>
        <label style={styles.label}>
          Agent URL
          <input
            data-testid="register-url"
            style={styles.input}
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="http://localhost:9001/"
          />
        </label>
        <label style={styles.label}>
          Label (optional)
          <input
            data-testid="register-label"
            style={styles.input}
            value={label}
            onChange={(e) => setLabel(e.target.value)}
            placeholder="defaults to the card's name"
          />
        </label>
        <button
          data-testid="register-submit"
          style={styles.button}
          onClick={handleRegister}
          disabled={busy}
        >
          {busy ? "Registering…" : "Register agent"}
        </button>
      </div>

      {error && <div style={styles.error}>Could not register: {error}</div>}

      {lastRegistered && (
        <div style={styles.success}>
          Registered <strong>{lastRegistered.card.name}</strong> ({lastRegistered.url}
          ) - see the Agent Cards tab for the full card.
        </div>
      )}

      <h3 style={styles.subheading}>Currently registered</h3>
      <div style={styles.list}>
        {agents.map((a) => (
          <div key={a.url} style={styles.row}>
            <div>
              <div style={styles.rowLabel}>{a.label}</div>
              <div style={styles.rowUrl}>{a.url}</div>
            </div>
            <button style={styles.removeButton} onClick={() => handleRemove(a.url)}>
              Remove
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

const styles = {
  intro: { fontSize: 13, lineHeight: 1.6, color: "var(--text-secondary)", marginBottom: 20 },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: 12,
    background: "var(--surface-1)",
    border: "1px solid var(--border)",
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    maxWidth: 480,
  },
  label: {
    display: "flex",
    flexDirection: "column",
    gap: 4,
    fontSize: 12,
    color: "var(--text-secondary)",
  },
  input: {
    padding: "9px 10px",
    borderRadius: 8,
    border: "1px solid var(--border)",
    background: "var(--surface-2)",
    color: "var(--text-primary)",
    fontSize: 13,
  },
  button: {
    alignSelf: "flex-start",
    padding: "9px 16px",
    borderRadius: 8,
    border: "none",
    background: "var(--series-1)",
    color: "#fff",
    fontSize: 13,
    fontWeight: 600,
  },
  error: { color: "var(--status-critical)", fontSize: 13, marginBottom: 16 },
  success: {
    color: "var(--status-good)",
    fontSize: 13,
    marginBottom: 16,
    background: "var(--surface-1)",
    border: "1px solid var(--border)",
    borderRadius: 8,
    padding: "10px 12px",
  },
  subheading: { fontSize: 13, color: "var(--text-secondary)", marginBottom: 8 },
  list: { display: "flex", flexDirection: "column", gap: 6 },
  row: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    background: "var(--surface-1)",
    border: "1px solid var(--border)",
    borderRadius: 8,
    padding: "8px 12px",
  },
  rowLabel: { fontSize: 13, fontWeight: 600 },
  rowUrl: { fontSize: 11, color: "var(--text-muted)" },
  removeButton: {
    border: "1px solid var(--border)",
    background: "transparent",
    color: "var(--status-critical)",
    borderRadius: 6,
    padding: "4px 10px",
    fontSize: 12,
  },
};

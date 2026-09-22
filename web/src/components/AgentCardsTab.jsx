import { useEffect, useState } from "react";
import { getAgents } from "../api.js";

export default function AgentCardsTab({ refreshKey }) {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await getAgents();
      setAgents(data.agents);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [refreshKey]);

  return (
    <div>
      <div style={styles.headerRow}>
        <p style={styles.intro}>
          Agent Cards are the A2A discovery document each agent publishes at{" "}
          <code>/.well-known/agent-card.json</code>, listing its skills, I/O
          modes, and capabilities. These are fetched live from each agent by
          the gateway.
        </p>
        <button style={styles.refreshButton} onClick={load} disabled={loading}>
          {loading ? "Refreshing…" : "Refresh"}
        </button>
      </div>

      {error && <div style={styles.error}>{error}</div>}

      <div style={styles.grid}>
        {agents.map((a) => (
          <div key={a.url} style={styles.card}>
            <div style={styles.cardHeader}>
              <span style={styles.cardName}>{a.card?.name || a.label}</span>
              {a.card?.version && <span style={styles.version}>v{a.card.version}</span>}
            </div>
            <div style={styles.url}>{a.url}</div>

            {a.error && <div style={styles.cardError}>Unreachable: {a.error}</div>}

            {a.card && (
              <>
                <p style={styles.description}>{a.card.description}</p>

                <div style={styles.badgeRow}>
                  <span style={styles.badge}>
                    streaming: {String(a.card.capabilities?.streaming ?? false)}
                  </span>
                  {a.card.supportedInterfaces?.map((iface, i) => (
                    <span key={i} style={styles.badge}>
                      {iface.protocolBinding} {iface.protocolVersion}
                    </span>
                  ))}
                </div>

                <div style={styles.skillsTitle}>Skills</div>
                {a.card.skills?.map((s) => (
                  <div key={s.id} style={styles.skill}>
                    <div style={styles.skillName}>{s.name}</div>
                    <div style={styles.skillDesc}>{s.description}</div>
                    {s.tags?.length > 0 && (
                      <div style={styles.tagRow}>
                        {s.tags.map((t) => (
                          <span key={t} style={styles.tag}>
                            {t}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

const styles = {
  headerRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    gap: 16,
    marginBottom: 16,
  },
  intro: { fontSize: 13, lineHeight: 1.6, color: "var(--text-secondary)", margin: 0 },
  refreshButton: {
    flexShrink: 0,
    padding: "8px 14px",
    borderRadius: 8,
    border: "1px solid var(--border)",
    background: "var(--surface-1)",
    color: "var(--text-primary)",
    fontSize: 13,
  },
  error: { color: "var(--status-critical)", fontSize: 13, marginBottom: 12 },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
    gap: 14,
  },
  card: {
    background: "var(--surface-1)",
    border: "1px solid var(--border)",
    borderRadius: 12,
    padding: 16,
  },
  cardHeader: { display: "flex", justifyContent: "space-between", alignItems: "baseline" },
  cardName: { fontSize: 15, fontWeight: 700 },
  version: { fontSize: 11, color: "var(--text-muted)" },
  url: { fontSize: 11, color: "var(--text-muted)", marginBottom: 8, wordBreak: "break-all" },
  cardError: { color: "var(--status-critical)", fontSize: 12 },
  description: { fontSize: 12, color: "var(--text-secondary)", lineHeight: 1.5 },
  badgeRow: { display: "flex", flexWrap: "wrap", gap: 6, margin: "8px 0" },
  badge: {
    fontSize: 10,
    padding: "2px 8px",
    borderRadius: 999,
    background: "var(--surface-2)",
    border: "1px solid var(--border)",
    color: "var(--text-secondary)",
  },
  skillsTitle: {
    fontSize: 11,
    fontWeight: 700,
    color: "var(--text-muted)",
    textTransform: "uppercase",
    letterSpacing: 0.4,
    marginTop: 10,
    marginBottom: 4,
  },
  skill: {
    borderTop: "1px solid var(--gridline)",
    padding: "8px 0",
  },
  skillName: { fontSize: 12, fontWeight: 600 },
  skillDesc: { fontSize: 12, color: "var(--text-secondary)", marginTop: 2 },
  tagRow: { display: "flex", flexWrap: "wrap", gap: 4, marginTop: 6 },
  tag: {
    fontSize: 10,
    color: "var(--text-muted)",
    background: "var(--surface-2)",
    borderRadius: 4,
    padding: "1px 6px",
  },
};

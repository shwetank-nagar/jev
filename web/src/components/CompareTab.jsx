import { useState } from "react";
import { compare } from "../api.js";

const SERIES = [
  { key: "sequential", label: "jev (sequential)", color: "var(--series-1)" },
  { key: "parallel", label: "jev-parallel (concurrent)", color: "var(--series-2)" },
  { key: "single_prompt", label: "single-prompt baseline", color: "var(--series-3)" },
];

export default function CompareTab() {
  const [ticker, setTicker] = useState("AAPL");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);
  const [hover, setHover] = useState(null);
  const [showTable, setShowTable] = useState(false);

  async function handleCompare() {
    const t = ticker.trim();
    if (!t || busy) return;
    setBusy(true);
    setError(null);
    try {
      const res = await compare(t);
      setData(res);
    } catch (err) {
      setError(err.message);
      setData(null);
    } finally {
      setBusy(false);
    }
  }

  const values = data
    ? {
        sequential: data.sequential.elapsed_ms,
        parallel: data.parallel.elapsed_ms,
        single_prompt: data.single_prompt.elapsed_ms,
      }
    : null;
  const maxVal = values ? Math.max(...Object.values(values)) : 0;
  const scaleMax = maxVal > 0 ? maxVal * 1.2 : 1;
  const ticks = scaleMax > 0 ? [0, 0.25, 0.5, 0.75, 1].map((f) => f * scaleMax) : [];

  // Headline stat: jev (agentic, decomposed) vs a single monolithic prompt.
  const speedupVsSinglePrompt =
    values && values.sequential > 0
      ? values.single_prompt / values.sequential
      : null;

  return (
    <div>
      <p style={styles.intro}>
        The headline comparison: <strong>jev</strong> delegates to three fast
        specialized agents (market-data, risk-analysis, report-writer) versus a{" "}
        <strong>single-prompt baseline</strong> that asks one model to do the
        whole job in one shot - the point jev is meant to prove is that agentic
        decomposition beats a monolithic prompt, even against a fast model.
        <strong> jev-parallel</strong> is included too, showing the same three
        specialized agents fanned out concurrently instead of chained. All three
        are timed as real A2A calls between separate processes - this is actual
        wall-clock latency, not a simulated delay (the single-prompt baseline
        itself uses a real Anthropic call if <code>ANTHROPIC_API_KEY</code> is
        set, otherwise a labeled simulated stand-in).
      </p>

      <div style={styles.formRow}>
        <input
          data-testid="compare-input"
          style={styles.input}
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleCompare()}
          placeholder="e.g. AAPL"
        />
        <button
          data-testid="compare-submit"
          style={styles.button}
          onClick={handleCompare}
          disabled={busy}
        >
          {busy ? "Comparing…" : "Compare"}
        </button>
      </div>

      {error && <div style={styles.error}>{error}</div>}

      {data && (
        <>
          <div className="viz-root" style={styles.chartCard}>
            <div style={styles.chartHeader}>
              <span style={styles.chartTitle}>
                Latency for {data.ticker} - lower is faster
              </span>
              <div style={styles.legend}>
                {SERIES.map((s) => (
                  <span key={s.key} style={styles.legendItem}>
                    <span
                      style={{ ...styles.legendSwatch, background: s.color }}
                    />
                    {s.label}
                  </span>
                ))}
              </div>
            </div>

            <div style={styles.chartBody}>
              <div style={styles.gridlines}>
                {ticks.map((t, i) => (
                  <div
                    key={i}
                    style={{ ...styles.gridline, left: `${(t / scaleMax) * 100}%` }}
                  >
                    <span style={styles.gridlineLabel}>{Math.round(t)}</span>
                  </div>
                ))}
              </div>

              {SERIES.map((s) => {
                const val = values[s.key];
                const pct = (val / scaleMax) * 100;
                return (
                  <div key={s.key} style={styles.barRow}>
                    <span style={styles.barLabel}>{s.label}</span>
                    <div style={styles.barTrack}>
                      <div
                        style={{
                          ...styles.bar,
                          width: `${pct}%`,
                          background: s.color,
                        }}
                        onMouseEnter={() => setHover(s.key)}
                        onMouseLeave={() => setHover(null)}
                      />
                      <span style={{ ...styles.barValue, left: `calc(${pct}% + 8px)` }}>
                        {val.toFixed(0)} ms
                      </span>
                      {hover === s.key && (
                        <div
                          style={{ ...styles.tooltip, left: `calc(${pct}% + 8px)` }}
                        >
                          {s.label}: {val.toFixed(1)} ms
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            {speedupVsSinglePrompt !== null && (
              <div style={styles.speedup}>
                jev was{" "}
                <strong style={{ color: "var(--status-good)" }}>
                  {speedupVsSinglePrompt.toFixed(1)}x faster
                </strong>{" "}
                than the single-prompt baseline for this run
                {data.single_prompt.result.used_real_llm === false
                  ? " (baseline simulated - set ANTHROPIC_API_KEY for a real one-shot completion)"
                  : ""}
                .
              </div>
            )}

            <button
              data-testid="compare-table-toggle"
              style={styles.tableToggle}
              onClick={() => setShowTable((v) => !v)}
            >
              {showTable ? "Hide" : "Show"} as table
            </button>
            {showTable && (
              <table style={styles.table}>
                <thead>
                  <tr>
                    <th style={styles.th}>Mode</th>
                    <th style={styles.th}>Elapsed (ms)</th>
                  </tr>
                </thead>
                <tbody>
                  {SERIES.map((s) => (
                    <tr key={s.key}>
                      <td style={styles.td}>{s.label}</td>
                      <td style={styles.td}>{values[s.key].toFixed(1)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          <div style={styles.reportsGrid}>
            <ReportCard title="jev (sequential)" report={data.sequential.result} />
            <ReportCard title="jev-parallel" report={data.parallel.result} />
            <ReportCard
              title="single-prompt baseline"
              report={data.single_prompt.result}
              badge={
                data.single_prompt.result.used_real_llm
                  ? "real LLM call"
                  : "simulated"
              }
            />
          </div>
        </>
      )}
    </div>
  );
}

function ReportCard({ title, report, badge }) {
  return (
    <div style={styles.reportCard}>
      <div style={styles.reportTitleRow}>
        <div style={styles.reportTitle}>{title}</div>
        {badge && <span style={styles.reportBadge}>{badge}</span>}
      </div>
      <pre style={styles.reportBody}>
        {report.report || JSON.stringify(report, null, 2)}
      </pre>
    </div>
  );
}

const styles = {
  intro: {
    fontSize: 13,
    lineHeight: 1.6,
    color: "var(--text-secondary)",
    marginBottom: 16,
  },
  formRow: { display: "flex", gap: 8, marginBottom: 16 },
  input: {
    flex: 1,
    padding: "10px 12px",
    borderRadius: 8,
    border: "1px solid var(--border)",
    background: "var(--surface-1)",
    color: "var(--text-primary)",
    fontSize: 14,
  },
  button: {
    padding: "10px 18px",
    borderRadius: 8,
    border: "none",
    background: "var(--series-1)",
    color: "#fff",
    fontSize: 14,
    fontWeight: 600,
  },
  error: {
    color: "var(--status-critical)",
    fontSize: 13,
    marginBottom: 12,
  },
  chartCard: {
    background: "var(--surface-1)",
    border: "1px solid var(--border)",
    borderRadius: 12,
    padding: 20,
    marginBottom: 20,
  },
  chartHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    flexWrap: "wrap",
    gap: 10,
    marginBottom: 20,
  },
  chartTitle: { fontSize: 14, fontWeight: 600, color: "var(--text-primary)" },
  legend: { display: "flex", gap: 14 },
  legendItem: {
    display: "flex",
    alignItems: "center",
    gap: 6,
    fontSize: 12,
    color: "var(--text-secondary)",
  },
  legendSwatch: { width: 10, height: 10, borderRadius: 3, display: "inline-block" },
  chartBody: { position: "relative", paddingTop: 8 },
  gridlines: {
    position: "absolute",
    inset: 0,
    top: 0,
    bottom: 24,
  },
  gridline: {
    position: "absolute",
    top: 0,
    bottom: 0,
    width: 1,
    background: "var(--gridline)",
  },
  gridlineLabel: {
    position: "absolute",
    bottom: -20,
    left: -10,
    fontSize: 10,
    color: "var(--text-muted)",
  },
  barRow: {
    display: "grid",
    gridTemplateColumns: "170px 1fr",
    alignItems: "center",
    gap: 12,
    marginBottom: 34,
    position: "relative",
  },
  barLabel: { fontSize: 12, color: "var(--text-secondary)" },
  barTrack: {
    position: "relative",
    height: 24,
    borderBottom: "1px solid var(--baseline)",
  },
  bar: {
    height: 20,
    borderRadius: "0 4px 4px 0",
    minWidth: 2,
  },
  barValue: {
    position: "absolute",
    top: 2,
    fontSize: 12,
    fontWeight: 600,
    color: "var(--text-primary)",
    whiteSpace: "nowrap",
  },
  tooltip: {
    position: "absolute",
    top: -30,
    background: "var(--text-primary)",
    color: "var(--surface-1)",
    padding: "4px 8px",
    borderRadius: 6,
    fontSize: 11,
    whiteSpace: "nowrap",
  },
  speedup: {
    marginTop: 28,
    fontSize: 13,
    color: "var(--text-secondary)",
  },
  tableToggle: {
    marginTop: 12,
    border: "none",
    background: "transparent",
    color: "var(--text-secondary)",
    fontSize: 12,
    textDecoration: "underline",
    padding: 0,
  },
  table: {
    marginTop: 10,
    width: "100%",
    borderCollapse: "collapse",
    fontSize: 12,
  },
  th: {
    textAlign: "left",
    padding: "6px 8px",
    borderBottom: "1px solid var(--border)",
    color: "var(--text-secondary)",
  },
  td: {
    padding: "6px 8px",
    borderBottom: "1px solid var(--gridline)",
    fontVariantNumeric: "tabular-nums",
  },
  reportsGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
    gap: 16,
  },
  reportCard: {
    background: "var(--surface-1)",
    border: "1px solid var(--border)",
    borderRadius: 10,
    padding: 14,
  },
  reportTitleRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8,
  },
  reportTitle: {
    fontSize: 12,
    fontWeight: 700,
    color: "var(--text-secondary)",
    textTransform: "uppercase",
    letterSpacing: 0.4,
  },
  reportBadge: {
    fontSize: 10,
    color: "var(--text-muted)",
    background: "var(--surface-2)",
    border: "1px solid var(--border)",
    borderRadius: 999,
    padding: "1px 8px",
  },
  reportBody: {
    fontSize: 12,
    whiteSpace: "pre-wrap",
    wordBreak: "break-word",
    margin: 0,
    color: "var(--text-primary)",
  },
};

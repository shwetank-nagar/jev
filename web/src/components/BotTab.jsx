import { useEffect, useRef, useState } from "react";
import { ask, getTickers } from "../api.js";

const MODE_NAMES = {
  sequential: "jev",
  parallel: "jev-parallel",
  single_prompt: "single-prompt",
};

export default function BotTab() {
  const [tickers, setTickers] = useState([]);
  const [mode, setMode] = useState("sequential");
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: "bot",
      kind: "info",
      text:
        "Hi, I'm jev. Type a stock ticker and I'll delegate to my market-data, " +
        "risk-analysis, and report-writer agents to put together a research note.",
    },
  ]);
  const [helpOpen, setHelpOpen] = useState(true);
  const logEndRef = useRef(null);

  useEffect(() => {
    getTickers()
      .then((data) => setTickers(data.tickers))
      .catch(() => setTickers([]));
  }, []);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSend() {
    const ticker = input.trim();
    if (!ticker || busy) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", text: ticker }]);
    setBusy(true);
    try {
      const res = await ask(ticker, mode);
      if (res.result.report) {
        setMessages((m) => [
          ...m,
          {
            role: "bot",
            kind: "report",
            text: res.result.report,
            elapsedMs: res.elapsed_ms,
            mode,
          },
        ]);
      } else if (res.result.error) {
        setMessages((m) => [
          ...m,
          {
            role: "bot",
            kind: "error",
            text: res.result.error,
            knownTickers: res.result.known_tickers,
          },
        ]);
      } else {
        setMessages((m) => [
          ...m,
          { role: "bot", kind: "error", text: "Unexpected response from jev." },
        ]);
      }
    } catch (err) {
      setMessages((m) => [
        ...m,
        { role: "bot", kind: "error", text: `Request failed: ${err.message}` },
      ]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <section style={styles.help}>
        <button style={styles.helpToggle} onClick={() => setHelpOpen((v) => !v)}>
          {helpOpen ? "▾" : "▸"} How to try it
        </button>
        {helpOpen && (
          <div style={styles.helpBody}>
            <p style={styles.helpP}>
              Type a stock ticker below and press Enter (or click Send). jev will
              call three agents behind the scenes over real A2A requests -
              market-data, risk-analysis, and report-writer - and return a
              synthesized recommendation. Everything is deterministic mock data,
              so the same ticker always gives the same answer - no API keys
              involved.
            </p>
            <p style={styles.helpP}>
              Known tickers:{" "}
              {tickers.length ? (
                <span>
                  {tickers.map((t) => (
                    <code key={t} style={styles.tickerChip}>
                      {t}
                    </code>
                  ))}
                </span>
              ) : (
                "loading..."
              )}
              . Anything else returns a graceful "unknown ticker" message.
            </p>
            <p style={styles.helpP}>
              Use the mode switch to talk to <strong>jev</strong> (sequential
              chain), <strong>jev-parallel</strong> (concurrent fan-out), or the{" "}
              <strong>single-prompt baseline</strong> (one model call doing
              everything at once) - see the Compare tab for a side-by-side
              timing chart of all three.
            </p>
          </div>
        )}
      </section>

      <section style={styles.modeRow}>
        <span style={styles.modeLabel}>Talking to:</span>
        <div style={styles.modeToggle}>
          <button
            data-testid="mode-sequential"
            onClick={() => setMode("sequential")}
            style={{
              ...styles.modeButton,
              ...(mode === "sequential" ? styles.modeButtonActive : {}),
            }}
          >
            jev (sequential)
          </button>
          <button
            data-testid="mode-parallel"
            onClick={() => setMode("parallel")}
            style={{
              ...styles.modeButton,
              ...(mode === "parallel" ? styles.modeButtonActive : {}),
            }}
          >
            jev-parallel
          </button>
          <button
            data-testid="mode-single_prompt"
            onClick={() => setMode("single_prompt")}
            style={{
              ...styles.modeButton,
              ...(mode === "single_prompt" ? styles.modeButtonActive : {}),
            }}
          >
            single-prompt
          </button>
        </div>
      </section>

      <section style={styles.log}>
        {messages.map((m, i) => (
          <div
            key={i}
            style={{
              ...styles.bubbleRow,
              justifyContent: m.role === "user" ? "flex-end" : "flex-start",
            }}
          >
            <div
              style={{
                ...styles.bubble,
                ...(m.role === "user" ? styles.bubbleUser : styles.bubbleBot),
                ...(m.kind === "error" ? styles.bubbleError : {}),
              }}
            >
              <pre style={styles.pre}>{m.text}</pre>
              {m.kind === "error" && m.knownTickers && (
                <div style={styles.errorHint}>
                  Known tickers: {m.knownTickers.join(", ")}
                </div>
              )}
              {m.kind === "report" && (
                <div style={styles.meta}>
                  {MODE_NAMES[m.mode] || m.mode} · {m.elapsedMs.toFixed(0)} ms
                </div>
              )}
            </div>
          </div>
        ))}
        {busy && (
          <div style={{ ...styles.bubbleRow, justifyContent: "flex-start" }}>
            <div style={{ ...styles.bubble, ...styles.bubbleBot }}>Thinking…</div>
          </div>
        )}
        <div ref={logEndRef} />
      </section>

      <section style={styles.inputRow}>
        <input
          data-testid="bot-input"
          style={styles.input}
          value={input}
          placeholder="e.g. AAPL"
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          disabled={busy}
        />
        <button
          data-testid="bot-send"
          style={styles.sendButton}
          onClick={handleSend}
          disabled={busy}
        >
          Send
        </button>
      </section>
    </div>
  );
}

const styles = {
  help: {
    border: "1px solid var(--border)",
    borderRadius: 10,
    background: "var(--surface-1)",
    marginBottom: 16,
    overflow: "hidden",
  },
  helpToggle: {
    width: "100%",
    textAlign: "left",
    padding: "10px 14px",
    background: "transparent",
    border: "none",
    fontSize: 14,
    fontWeight: 600,
    color: "var(--text-primary)",
  },
  helpBody: {
    padding: "0 14px 14px",
  },
  helpP: {
    fontSize: 13,
    lineHeight: 1.6,
    color: "var(--text-secondary)",
    margin: "6px 0",
  },
  tickerChip: {
    display: "inline-block",
    background: "var(--surface-2)",
    border: "1px solid var(--border)",
    borderRadius: 6,
    padding: "1px 6px",
    marginRight: 4,
    fontSize: 12,
  },
  modeRow: {
    display: "flex",
    alignItems: "center",
    gap: 10,
    marginBottom: 12,
  },
  modeLabel: {
    fontSize: 13,
    color: "var(--text-secondary)",
  },
  modeToggle: {
    display: "flex",
    gap: 4,
    background: "var(--surface-1)",
    border: "1px solid var(--border)",
    borderRadius: 8,
    padding: 3,
  },
  modeButton: {
    border: "none",
    background: "transparent",
    padding: "5px 10px",
    borderRadius: 6,
    fontSize: 12,
    color: "var(--text-secondary)",
  },
  modeButtonActive: {
    background: "var(--surface-2)",
    color: "var(--text-primary)",
    fontWeight: 600,
  },
  log: {
    display: "flex",
    flexDirection: "column",
    gap: 10,
    minHeight: 280,
    maxHeight: 480,
    overflowY: "auto",
    padding: "8px 4px",
    marginBottom: 12,
  },
  bubbleRow: {
    display: "flex",
  },
  bubble: {
    maxWidth: "80%",
    padding: "10px 14px",
    borderRadius: 12,
    fontSize: 14,
  },
  bubbleUser: {
    background: "var(--series-1)",
    color: "#ffffff",
  },
  bubbleBot: {
    background: "var(--surface-1)",
    border: "1px solid var(--border)",
    color: "var(--text-primary)",
  },
  bubbleError: {
    borderColor: "var(--status-critical)",
  },
  pre: {
    margin: 0,
    fontFamily: "inherit",
    whiteSpace: "pre-wrap",
    wordBreak: "break-word",
  },
  errorHint: {
    marginTop: 6,
    fontSize: 12,
    color: "var(--text-secondary)",
  },
  meta: {
    marginTop: 8,
    fontSize: 11,
    color: "var(--text-muted)",
  },
  inputRow: {
    display: "flex",
    gap: 8,
  },
  input: {
    flex: 1,
    padding: "10px 12px",
    borderRadius: 8,
    border: "1px solid var(--border)",
    background: "var(--surface-1)",
    color: "var(--text-primary)",
    fontSize: 14,
  },
  sendButton: {
    padding: "10px 18px",
    borderRadius: 8,
    border: "none",
    background: "var(--series-1)",
    color: "#ffffff",
    fontSize: 14,
    fontWeight: 600,
  },
};

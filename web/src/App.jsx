import { useState } from "react";
import BotTab from "./components/BotTab.jsx";
import CompareTab from "./components/CompareTab.jsx";
import AgentCardsTab from "./components/AgentCardsTab.jsx";
import RegisterTab from "./components/RegisterTab.jsx";

const TABS = [
  { id: "bot", label: "Bot" },
  { id: "compare", label: "Compare" },
  { id: "cards", label: "Agent Cards" },
  { id: "register", label: "Register Agent" },
];

export default function App() {
  const [tab, setTab] = useState("bot");
  // bumped whenever the registry changes, so AgentCardsTab knows to refetch
  const [registryVersion, setRegistryVersion] = useState(0);

  return (
    <div style={styles.root}>
      <header style={styles.header}>
        <div style={styles.brand}>
          <span style={styles.brandMark}>jev</span>
          <span style={styles.brandSub}>A2A multi-agent showcase</span>
        </div>
        <nav style={styles.nav}>
          {TABS.map((t) => (
            <button
              key={t.id}
              data-testid={`nav-${t.id}`}
              onClick={() => setTab(t.id)}
              style={{
                ...styles.navButton,
                ...(tab === t.id ? styles.navButtonActive : {}),
              }}
            >
              {t.label}
            </button>
          ))}
        </nav>
      </header>

      <main style={styles.main}>
        {tab === "bot" && <BotTab />}
        {tab === "compare" && <CompareTab />}
        {tab === "cards" && <AgentCardsTab refreshKey={registryVersion} />}
        {tab === "register" && (
          <RegisterTab onRegistered={() => setRegistryVersion((v) => v + 1)} />
        )}
      </main>
    </div>
  );
}

const styles = {
  root: {
    minHeight: "100%",
    display: "flex",
    flexDirection: "column",
  },
  header: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    flexWrap: "wrap",
    gap: 12,
    padding: "16px 24px",
    background: "var(--surface-1)",
    borderBottom: "1px solid var(--border)",
  },
  brand: {
    display: "flex",
    alignItems: "baseline",
    gap: 10,
  },
  brandMark: {
    fontSize: 22,
    fontWeight: 700,
  },
  brandSub: {
    fontSize: 13,
    color: "var(--text-secondary)",
  },
  nav: {
    display: "flex",
    gap: 4,
    background: "var(--surface-2)",
    padding: 4,
    borderRadius: 10,
    border: "1px solid var(--border)",
  },
  navButton: {
    border: "none",
    background: "transparent",
    color: "var(--text-secondary)",
    padding: "8px 14px",
    borderRadius: 8,
    fontSize: 14,
    fontWeight: 500,
  },
  navButtonActive: {
    background: "var(--surface-1)",
    color: "var(--text-primary)",
    boxShadow: "0 1px 2px var(--border)",
  },
  main: {
    flex: 1,
    width: "100%",
    maxWidth: 960,
    margin: "0 auto",
    padding: "24px 20px 48px",
  },
};

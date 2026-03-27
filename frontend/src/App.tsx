import { useEffect, useState } from "react";
import { fetchScenario, fetchScenarios } from "./api";
import type { Scenario, ScenarioSummary } from "./types";
import { LangProvider, useLang } from "./i18n/context";
import { ScenarioPlayer } from "./components/ScenarioPlayer";
import { OverviewPage } from "./components/OverviewPage";
import "./styles.css";

function AppContent() {
  const { lang, setLang, t } = useLang();
  const [scenarios, setScenarios] = useState<ScenarioSummary[]>([]);
  const [current, setCurrent] = useState<Scenario | null>(null);
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  useEffect(() => {
    fetchScenarios(lang).then(setScenarios);
  }, [lang]);

  useEffect(() => {
    if (selectedId) {
      setLoading(true);
      fetchScenario(selectedId, lang).then((s) => {
        setCurrent(s);
        setLoading(false);
      });
    }
  }, [lang, selectedId]);

  const loadScenario = (id: string) => {
    setActiveStep(0);
    setSelectedId(id);
  };

  const toggleLang = () => setLang(lang === "en" ? "zh" : "en");

  const step = current?.steps[activeStep] ?? null;
  const infraState = step?.post_state ?? step?.pre_state ?? current?.initial_state ?? null;

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-left">
          <div className="logo-icon">FV</div>
          <div>
            <h1>{t("header.title")}</h1>
            <p className="subtitle">{t("header.subtitle")}</p>
          </div>
        </div>
        <div className="header-right">
          <span className="badge">{t("header.badge.demo")}</span>
          <span className="badge badge-tla">{t("header.badge.tla")}</span>
          <button className="lang-toggle" onClick={toggleLang}>
            {t("lang.switch")}
          </button>
        </div>
      </header>

      <div className="main-layout">
        <aside className="sidebar">
          <h2 className="sidebar-title">{t("sidebar.title")}</h2>
          {scenarios.map((s) => (
            <button
              key={s.id}
              className={`scenario-card ${current?.id === s.id ? "active" : ""}`}
              onClick={() => loadScenario(s.id)}
            >
              <span className="scenario-card-title">{s.title}</span>
              <span className="scenario-card-subtitle">{s.subtitle}</span>
            </button>
          ))}
        </aside>

        <main className="content">
          {!current && !loading && (
            <OverviewPage onSelectScenario={loadScenario} />
          )}

          {loading && (
            <div className="empty-state">
              <div className="spinner" />
              <p>{t("loading")}</p>
            </div>
          )}

          {current && !loading && (
            <>
              <button className="back-to-overview" onClick={() => { setCurrent(null); setSelectedId(null); }}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M15 18l-6-6 6-6" />
                </svg>
                {t("nav.backToOverview")}
              </button>
              <div className="scenario-header">
                <h2>{current.title}</h2>
                <p className="scenario-subtitle-text">{current.subtitle}</p>
              </div>

              <ScenarioPlayer
                steps={current.steps}
                activeStep={activeStep}
                onStepChange={setActiveStep}
                scenarioPhase={current.phase}
                infraState={infraState}
                scenario={current}
              />
            </>
          )}
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <LangProvider>
      <AppContent />
    </LangProvider>
  );
}

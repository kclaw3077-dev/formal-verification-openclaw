import { useLang } from "../i18n/context";

const PIPELINE_STEPS = [
  { key: "step1", color: "#94a3b8" },
  { key: "step2", color: "#818cf8" },
  { key: "step3", color: "#f59e0b" },
  { key: "step4", color: "#6366f1" },
  { key: "step5", color: "#10b981" },
];

const MODES = [
  {
    key: "single",
    scenarios: ["scenario-1", "scenario-2", "scenario-5"],
  },
  {
    key: "plan",
    scenarios: ["scenario-3"],
  },
  {
    key: "concurrent",
    scenarios: ["scenario-4"],
  },
];

interface Props {
  onSelectScenario: (id: string) => void;
}

export function OverviewPage({ onSelectScenario }: Props) {
  const { t } = useLang();

  return (
    <div className="overview-page">
      {/* Header */}
      <div className="overview-header">
        <h2>{t("overview.title")}</h2>
        <p>{t("overview.subtitle")}</p>
      </div>

      {/* Architecture Pipeline */}
      <div className="pipeline">
        {PIPELINE_STEPS.map((step, i) => {
          const isHighlight = step.key === "step4";
          const example = t(`overview.pipeline.${step.key}.example`);
          return (
            <div key={step.key} className="pipeline-row">
              {/* Step node */}
              <div className={`pipeline-step ${isHighlight ? "pipeline-highlight" : ""}`}>
                <div className="pipeline-num" style={{ background: step.color }}>
                  {i + 1}
                </div>
                <div className="pipeline-body">
                  <div className="pipeline-title">
                    {t(`overview.pipeline.${step.key}.title`)}
                  </div>
                  <div className="pipeline-desc">
                    {t(`overview.pipeline.${step.key}.desc`)}
                  </div>
                  {example && (
                    <code className="pipeline-example">{example}</code>
                  )}
                </div>
              </div>
              {/* Arrow */}
              {i < PIPELINE_STEPS.length - 1 && (
                <div className="pipeline-arrow">
                  <div className="pipeline-arrow-line" />
                  <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
                    <path d="M6 9l4-4H2z" />
                  </svg>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Verification Modes */}
      <div className="overview-modes-section">
        <h3 className="overview-modes-title">{t("overview.modes.title")}</h3>
        <div className="overview-modes">
          {MODES.map((mode) => (
            <div key={mode.key} className="mode-card">
              <h4>{t(`overview.mode.${mode.key}.title`)}</h4>
              <p>{t(`overview.mode.${mode.key}.description`)}</p>
              <div className="mode-scenarios">
                {mode.scenarios.map((sid) => (
                  <button
                    key={sid}
                    className="scenario-chip"
                    onClick={() => onSelectScenario(sid)}
                  >
                    {t(`overview.mode.${mode.key}.scenario.${sid}`)}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

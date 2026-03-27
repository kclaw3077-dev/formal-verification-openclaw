import { useLang } from "../i18n/context";

const PIPELINE_STEPS = [
  { key: "step1", color: "#2e7d32" },
  { key: "step2", color: "#1565c0" },
  { key: "step3", color: "#e65100" },
  { key: "step4", color: "#c62828" },
];

const PHASES = [
  { key: "realizability", scenarios: ["scenario-1"] },
  { key: "synthesis", scenarios: ["scenario-2"] },
  { key: "bmc", scenarios: ["scenario-3", "scenario-4"] },
  { key: "feedback", scenarios: ["scenario-5"] },
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
          const example = t(`overview.pipeline.${step.key}.example`);
          return (
            <div key={step.key} className="pipeline-row">
              {/* Step node */}
              <div className="pipeline-step">
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

      {/* Lifecycle Phases */}
      <div className="overview-modes-section">
        <h3 className="overview-modes-title">{t("overview.phases.title")}</h3>
        <div className="overview-modes">
          {PHASES.map((phase) => (
            <div key={phase.key} className="mode-card">
              <h4>{t(`overview.phase.${phase.key}.title`)}</h4>
              <p>{t(`overview.phase.${phase.key}.description`)}</p>
              <div className="mode-scenarios">
                {phase.scenarios.map((sid) => (
                  <button
                    key={sid}
                    className="scenario-chip"
                    onClick={() => onSelectScenario(sid)}
                  >
                    {t(`overview.phase.${phase.key}.scenario.${sid}`)}
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

import type { ScenarioStep } from "../types";
import { useLang } from "../i18n/context";

interface Props {
  steps: ScenarioStep[];
  activeStep: number;
  onStepChange: (idx: number) => void;
}

export function ScenarioPlayer({ steps, activeStep, onStepChange }: Props) {
  const { t } = useLang();
  const step = steps[activeStep];

  return (
    <div className="scenario-player">
      <div className="step-nav">
        {steps.map((s, i) => {
          const result = s.verification?.result;
          const statusClass =
            result === "UNSAFE" || result === "UNREALIZABLE"
              ? "step-unsafe"
              : result === "SAFE" || result === "REALIZABLE"
              ? "step-safe"
              : "";
          return (
            <button
              key={s.step_id}
              className={`step-btn ${i === activeStep ? "active" : ""} ${statusClass}`}
              onClick={() => onStepChange(i)}
            >
              <span className="step-num">{t("step.label")} {s.step_id}</span>
              <span className="step-label">{s.title}</span>
            </button>
          );
        })}
      </div>

      <div className="step-detail">
        <div className="step-header">
          <h3>{step.title}</h3>
          {step.verification && (
            <span
              className={`result-badge ${
                step.verification.result === "SAFE" || step.verification.result === "REALIZABLE"
                  ? "result-safe"
                  : "result-unsafe"
              }`}
            >
              {step.verification.result === "SAFE" || step.verification.result === "REALIZABLE" ? "\u2713 " : "\u2717 "}
              {step.verification.result === "REALIZABLE"
                ? t("verification.realizable")
                : step.verification.result === "UNREALIZABLE"
                ? t("verification.unrealizable")
                : step.verification.result === "SAFE"
                ? t("verification.safe")
                : t("verification.unsafe")}
            </span>
          )}
        </div>
        <p className="step-description">{step.description}</p>
        <div className="agent-action">
          <span className="agent-label">{t("step.agentAction")}</span>
          <code>{step.agent_action}</code>
        </div>
        {step.verification && (
          <div className="verification-meta">
            <span>{t("step.statesExplored")} <strong>{step.verification.states_explored.toLocaleString()}</strong></span>
            <span>{t("step.propertiesChecked")} <strong>{step.verification.properties_checked.length}</strong></span>
            <span>{t("step.spec")} <strong>{step.verification.tla_spec_refs?.length
              ? t("tla.specFilesChecked", { count: step.verification.tla_spec_refs.length })
              : step.verification.tla_spec_used}</strong></span>
          </div>
        )}
      </div>
    </div>
  );
}

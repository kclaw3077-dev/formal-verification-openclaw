import { useState } from "react";
import type { Scenario, ScenarioStep, InfrastructureState } from "../types";
import { useLang } from "../i18n/context";
import { TopologyGraph } from "./TopologyGraph";
import { VerificationPanel } from "./VerificationPanel";
import { TraceViewer } from "./TraceViewer";
import { TlaSpecViewer } from "./TlaSpecViewer";
import { ConstraintsPanel } from "./ConstraintsPanel";

interface Props {
  steps: ScenarioStep[];
  activeStep: number;
  onStepChange: (idx: number) => void;
  scenarioPhase?: string;
  infraState: InfrastructureState | null;
  scenario: Scenario;
}

function phaseToBadge(phase: string | undefined): string {
  if (!phase) return "";
  if (phase.includes("\u2460") || phase.toLowerCase().includes("slo") || phase.includes("\u5b9a\u4e49"))
    return "realizability";
  if (phase.includes("\u2461") || phase.toLowerCase().includes("strateg") || phase.includes("\u7b56\u7565"))
    return "synthesis";
  if (phase.includes("\u2463") || phase.toLowerCase().includes("post") || phase.includes("\u590d\u76d8"))
    return "bmc_reverse";
  return "bmc";
}

export function ScenarioPlayer({ steps, activeStep, onStepChange, scenarioPhase, infraState, scenario }: Props) {
  const { t } = useLang();
  const step = steps[activeStep];
  const [detailOpen, setDetailOpen] = useState(false);

  const hasSreNarrative = !!(step.sre_context && step.key_question && step.guarantee);
  const isPositive =
    step.verification?.result === "SAFE" ||
    step.verification?.result === "REALIZABLE";
  const badgeKey = phaseToBadge(scenarioPhase);

  return (
    <div className="scenario-player">
      {/* Step navigation */}
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
              onClick={() => { onStepChange(i); setDetailOpen(false); }}
            >
              <span className="step-num">{t("step.label")} {s.step_id}</span>
              <span className="step-label">{s.title}</span>
            </button>
          );
        })}
      </div>

      <div className="step-detail">
        {hasSreNarrative ? (
          <>
            {/* Layer 1: SRE Context + Topology side by side */}
            <div className="sre-context-row">
              <div className="sre-card sre-context-card">
                <div className="sre-card-header">
                  <span className="sre-card-label">{t("sre.context")}</span>
                </div>
                <p className="sre-card-body">{step.sre_context}</p>
              </div>
              {infraState && (
                <div className="sre-topology">
                  <TopologyGraph state={infraState} />
                </div>
              )}
            </div>

            {/* Layer 2: Key Question */}
            <div className="sre-card sre-question-card">
              <div className="sre-card-header">
                <span className="sre-card-label">{t("sre.keyQuestion")}</span>
                {badgeKey && (
                  <span className="fm-badge">{t(`sre.fmBadge.${badgeKey}`)}</span>
                )}
              </div>
              <p className="sre-card-body sre-question-text">{step.key_question}</p>
            </div>

            {/* Layer 3: Guarantee Result */}
            <div className={`sre-card sre-guarantee-card ${isPositive ? "guarantee-positive" : "guarantee-negative"}`}>
              <div className="sre-card-header">
                <span className="sre-card-label">{t("sre.guarantee")}</span>
                {step.verification && (
                  <span className={`result-badge ${isPositive ? "result-safe" : "result-unsafe"}`}>
                    {isPositive ? "\u2713" : "\u2717"}{" "}
                    {step.verification.result === "REALIZABLE"
                      ? t("verification.realizable")
                      : step.verification.result === "UNREALIZABLE"
                      ? t("verification.unrealizable")
                      : isPositive
                      ? t("verification.safe")
                      : t("verification.unsafe")}
                  </span>
                )}
              </div>
              <p className="sre-card-body">{step.guarantee}</p>
            </div>

            {/* Collapsible: all technical details */}
            <button
              className="detail-toggle"
              onClick={() => setDetailOpen(!detailOpen)}
            >
              {detailOpen ? t("sre.detailToggleClose") : t("sre.detailToggle")}
              <span className={`toggle-arrow ${detailOpen ? "open" : ""}`}>&#9662;</span>
            </button>

            {detailOpen && (
              <div className="detail-section">
                {/* Agent action */}
                <div className="agent-action">
                  <span className="agent-label">{t("step.agentAction")}</span>
                  <code>{step.agent_action}</code>
                </div>

                {/* Verification meta */}
                {step.verification && (
                  <div className="verification-meta">
                    <span>{t("step.statesExplored")} <strong>{step.verification.states_explored.toLocaleString()}</strong></span>
                    <span>{t("step.propertiesChecked")} <strong>{step.verification.properties_checked.length}</strong></span>
                  </div>
                )}

                {/* Constraints */}
                {scenario.constraints.length > 0 && (
                  <ConstraintsPanel constraints={scenario.constraints} />
                )}

                {/* Verification panel */}
                {step.verification && (
                  <div className="detail-panel">
                    <h4 className="detail-panel-title">{t("panel.verification")}</h4>
                    <VerificationPanel report={step.verification} />
                  </div>
                )}

                {/* Trace */}
                {step.verification && (step.verification.counterexample_trace.length > 0 || (step.verification.violations[0]?.trace ?? []).length > 0) && (
                  <div className="detail-panel">
                    <h4 className="detail-panel-title">{t("panel.trace")}</h4>
                    <TraceViewer
                      trace={
                        step.verification.counterexample_trace.length > 0
                          ? step.verification.counterexample_trace
                          : step.verification.violations[0]?.trace ?? []
                      }
                    />
                  </div>
                )}

                {/* TLA+ spec */}
                <div className="detail-panel">
                  <h4 className="detail-panel-title">{t("panel.tlaSpec")}</h4>
                  <TlaSpecViewer
                    spec={scenario.tla_spec}
                    specRefs={step.verification?.tla_spec_refs ?? []}
                  />
                </div>
              </div>
            )}
          </>
        ) : (
          /* Fallback for steps without SRE narrative */
          <>
            <div className="step-header">
              <h3>{step.title}</h3>
            </div>
            <p className="step-description">{step.description}</p>
            <div className="agent-action">
              <span className="agent-label">{t("step.agentAction")}</span>
              <code>{step.agent_action}</code>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

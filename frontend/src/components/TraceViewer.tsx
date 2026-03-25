import type { TraceStep } from "../types";
import { useLang } from "../i18n/context";

export function TraceViewer({ trace }: { trace: TraceStep[] }) {
  const { t } = useLang();

  if (trace.length === 0) {
    return <div className="trace-empty">{t("trace.empty")}</div>;
  }

  return (
    <div className="trace-viewer">
      <div className="trace-timeline">
        {trace.map((step, i) => {
          const isViolation = !!step.violated_property;
          return (
            <div
              key={i}
              className={`trace-step ${isViolation ? "trace-violation" : ""}`}
            >
              <div className="trace-connector">
                <div className={`trace-dot ${isViolation ? "dot-violation" : "dot-normal"}`}>
                  {step.step}
                </div>
                {i < trace.length - 1 && <div className="trace-line" />}
              </div>
              <div className="trace-content">
                <div className="trace-desc">{step.description}</div>
                <div className="trace-state">
                  {Object.entries(step.state_snapshot).map(([k, v]) => (
                    <span key={k} className="state-chip">
                      {k}: <strong>{String(v)}</strong>
                    </span>
                  ))}
                </div>
                {isViolation && (
                  <div className="trace-violation-badge">
                    {t("trace.violates")} {step.violated_property}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

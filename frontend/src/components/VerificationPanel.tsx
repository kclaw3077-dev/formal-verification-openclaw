import type { VerificationReport } from "../types";
import { useLang } from "../i18n/context";

export function VerificationPanel({ report }: { report: VerificationReport }) {
  const { t } = useLang();
  const result = report.result;
  const isPositive = result === "SAFE" || result === "REALIZABLE";
  const isRealizable = result === "REALIZABLE";
  const isUnrealizable = result === "UNREALIZABLE";

  const panelClass = isRealizable
    ? "vp-realizable"
    : isUnrealizable
    ? "vp-unrealizable"
    : isPositive
    ? "vp-safe"
    : "vp-unsafe";

  const iconClass = isPositive ? "icon-safe" : "icon-unsafe";

  const resultLabel = isRealizable
    ? t("verification.realizable")
    : isUnrealizable
    ? t("verification.unrealizable")
    : isPositive
    ? t("verification.safe")
    : t("verification.unsafe");

  const resultDesc = isRealizable
    ? t("verification.realizable.desc")
    : isUnrealizable
    ? t("verification.unrealizable.desc", { count: (report as any).conflict_proof?.length ?? 0 })
    : isPositive
    ? t("verification.safe.desc")
    : t("verification.unsafe.desc", { count: report.violations.length });

  return (
    <div className={`verification-panel ${panelClass}`}>
      <div className="vp-header">
        <div className={`vp-icon ${iconClass}`}>
          {isPositive ? (
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M20 6L9 17l-5-5" />
            </svg>
          ) : (
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M18 6L6 18M6 6l12 12" />
            </svg>
          )}
        </div>
        <div>
          <div className="vp-result">{resultLabel}</div>
          <div className="vp-subtitle">{resultDesc}</div>
        </div>
      </div>

      <div className="vp-section">
        <h4>{t("verification.propertiesChecked")}</h4>
        <div className="property-list">
          {report.properties_checked.map((prop) => {
            const violated = report.violations.some((v) => v.property_name === prop);
            return (
              <div key={prop} className={`property-item ${violated ? "prop-violated" : "prop-ok"}`}>
                <span className="prop-icon">{violated ? "\u2717" : "\u2713"}</span>
                <span className="prop-name">{prop}</span>
              </div>
            );
          })}
        </div>
      </div>

      {report.violations.length > 0 && (
        <div className="vp-section">
          <h4>{t("verification.violations")}</h4>
          {report.violations.map((v, i) => (
            <div key={i} className="violation-card">
              <div className="violation-header">
                <span className={`severity-badge severity-${v.severity}`}>
                  {v.severity}
                </span>
                <span className="violation-prop">{v.property_name}</span>
              </div>
              <p className="violation-desc">{v.description}</p>
            </div>
          ))}
        </div>
      )}

      {/* Conflict proof for UNREALIZABLE results */}
      {isUnrealizable && (report as any).conflict_proof?.length > 0 && (
        <div className="conflict-proof">
          <h4>{t("verification.conflictProof")}</h4>
          <ul>
            {(report as any).conflict_proof.map((constraint: string, i: number) => (
              <li key={i}>{constraint}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Synthesized controller display */}
      {(report as any).synthesized_controller && (
        <div className="synthesized-controller">
          <h4>{t("verification.synthesizedController")}</h4>
          <div className="sc-stats">
            <span className="sc-stat">
              States: <strong>{(report as any).synthesized_controller.states?.length ?? 0}</strong>
            </span>
            <span className="sc-stat">
              Transitions: <strong>{(report as any).synthesized_controller.transitions?.length ?? 0}</strong>
            </span>
          </div>
          {(report as any).synthesized_controller.guards?.length > 0 && (
            <div className="sc-guards">
              {(report as any).synthesized_controller.guards.map((guard: string, i: number) => (
                <span key={i} className="sc-guard">{guard}</span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

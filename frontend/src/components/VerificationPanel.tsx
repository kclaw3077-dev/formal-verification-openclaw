import type { VerificationReport } from "../types";
import { useLang } from "../i18n/context";

export function VerificationPanel({ report }: { report: VerificationReport }) {
  const { t } = useLang();
  const isSafe = report.result === "SAFE";

  return (
    <div className={`verification-panel ${isSafe ? "vp-safe" : "vp-unsafe"}`}>
      <div className="vp-header">
        <div className={`vp-icon ${isSafe ? "icon-safe" : "icon-unsafe"}`}>
          {isSafe ? (
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
          <div className="vp-result">{isSafe ? t("verification.safe") : t("verification.unsafe")}</div>
          <div className="vp-subtitle">
            {isSafe
              ? t("verification.safe.desc")
              : t("verification.unsafe.desc", { count: report.violations.length })}
          </div>
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
    </div>
  );
}

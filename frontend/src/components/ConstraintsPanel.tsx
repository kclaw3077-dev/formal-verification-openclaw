import type { ConstraintDef } from "../types";
import { useLang } from "../i18n/context";

export function ConstraintsPanel({ constraints }: { constraints: ConstraintDef[] }) {
  const { t } = useLang();

  if (constraints.length === 0) return null;

  return (
    <div className="constraints-panel">
      <h3 className="constraints-title">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
        </svg>
        {t("constraints.title")}
      </h3>
      <div className="constraints-grid">
        {constraints.map((c) => (
          <div key={c.name} className="constraint-card">
            <div className="constraint-header">
              <span className="constraint-name">{c.name}</span>
              <span className="constraint-threshold">{c.threshold}</span>
            </div>
            <code className="constraint-expression">{c.expression}</code>
            <p className="constraint-desc">{c.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

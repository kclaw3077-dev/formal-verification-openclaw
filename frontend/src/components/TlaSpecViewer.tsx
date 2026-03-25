import type { TlaSpecRef } from "../types";
import { useLang } from "../i18n/context";

interface Props {
  spec: string;
  specRefs?: TlaSpecRef[];
}

export function TlaSpecViewer({ spec, specRefs = [] }: Props) {
  const { t } = useLang();

  return (
    <div className="tla-viewer">
      {specRefs.length > 0 && (
        <div className="spec-refs">
          <h4 className="spec-refs-title">{t("tla.specFiles")}</h4>
          {specRefs.map((ref) => (
            <div key={ref.filename} className="spec-ref-card">
              <div className="spec-ref-header">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                  <path d="M14 2v6h6" />
                </svg>
                <span className="spec-ref-filename">{ref.filename}</span>
              </div>
              <div className="spec-ref-defines">
                <span className="spec-ref-label">{t("tla.defines")}</span>
                {ref.defines.map((d) => (
                  <span key={d} className="defines-tag">{d}</span>
                ))}
              </div>
              <div className="spec-ref-relevance">
                <span className="spec-ref-label">{t("tla.relevance")}</span>
                <span>{ref.relevant_section}</span>
              </div>
            </div>
          ))}
        </div>
      )}
      <pre className="tla-code">
        <code>{spec}</code>
      </pre>
    </div>
  );
}

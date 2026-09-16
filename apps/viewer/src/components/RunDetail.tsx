import type { ComparisonRunDetail } from "../types";
import { formatVerdict } from "../verdictLabel";
import TraceHopList from "./TraceHopList";

interface Props {
  run: ComparisonRunDetail;
}

export default function RunDetail({ run }: Props) {
  const findings = run.report.findings ?? [];

  return (
    <div>
      <div className="panel">
        <div className="run-header">
          <div className="run-header-title">
            <h2>{run.session_id}</h2>
            <p className="meta">Run {run.id}</p>
          </div>
          <span className={`badge verdict ${run.ok ? "ok" : "fail"}`} title={run.verdict}>
            {formatVerdict(run.verdict)}
          </span>
        </div>
        <div className="stats">
          <div className="stat">
            <span className="meta">Reference hops</span>
            <strong>{run.reference_action_count}</strong>
          </div>
          <div className="stat">
            <span className="meta">Evidence hops</span>
            <strong>{run.evidence_action_count}</strong>
          </div>
          <div className="stat">
            <span className="meta">Completeness claim</span>
            <strong>{run.completeness_claim}</strong>
          </div>
        </div>
        {run.report.note ? <p>{run.report.note}</p> : null}
      </div>

      <div className="grid-two" style={{ marginTop: "1rem" }}>
        <TraceHopList
          title="Reference trace"
          actions={run.reference.actions ?? []}
          findings={findings}
          mode="reference"
        />
        <TraceHopList
          title="Evidence bundle"
          actions={run.evidence.actions ?? []}
          findings={findings}
          mode="evidence"
        />
      </div>

      {findings.length > 0 ? (
        <div className="findings panel" style={{ marginTop: "1rem" }}>
          <h3>Findings</h3>
          {findings.map((finding, index) => (
            <div key={`${finding.kind}-${index}`} className="finding">
              <strong>{finding.kind}</strong>
              <div>{finding.detail}</div>
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}

import type { HopFinding, TraceAction } from "../types";

type HopKind = "ok" | "missing" | "mismatch" | "extra";

interface Props {
  title: string;
  actions: TraceAction[];
  findings: HopFinding[];
  mode: "reference" | "evidence";
}

function hopClass(index: number, toolName: string, findings: HopFinding[], mode: Props["mode"]): HopKind {
  for (const finding of findings) {
    if (finding.kind === "missing_in_evidence" && mode === "reference" && finding.reference_index === index) {
      return "missing";
    }
    if (finding.kind === "missing_in_reference" && mode === "evidence" && finding.evidence_index === index) {
      return "extra";
    }
    if (
      (finding.kind === "tool_name_mismatch" ||
        finding.kind === "action_id_mismatch" ||
        finding.kind === "arguments_digest_mismatch") &&
      ((mode === "reference" && finding.reference_index === index) ||
        (mode === "evidence" && finding.evidence_index === index))
    ) {
      return "mismatch";
    }
    if (finding.tool_name?.toLowerCase() === toolName.toLowerCase() && finding.kind === "order_mismatch") {
      return "mismatch";
    }
  }
  return "ok";
}

export default function TraceHopList({ title, actions, findings, mode }: Props) {
  return (
    <div className="panel">
      <h2>{title}</h2>
      <p className="meta">{actions.length} hop(s)</p>
      <ul className="hop-list">
        {actions.map((action) => {
          const kind = hopClass(action.index, action.tool_name, findings, mode);
          return (
            <li key={`${mode}-${action.index}`} className={`hop ${kind}`}>
              <strong>
                #{action.index} {action.tool_name}
              </strong>
              {action.action_id ? (
                <div className="meta">action_id: {action.action_id.slice(0, 12)}…</div>
              ) : null}
              {action.arguments_digest ? (
                <div className="meta">args_digest: {action.arguments_digest.slice(0, 12)}…</div>
              ) : null}
            </li>
          );
        })}
      </ul>
    </div>
  );
}

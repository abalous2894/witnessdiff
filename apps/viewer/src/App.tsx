import { useCallback, useEffect, useState } from "react";
import { fetchHealth, fetchRun, fetchRuns, seedSilentOmissionDemo } from "./api";
import RunDetail from "./components/RunDetail";
import type { ComparisonRunDetail, ComparisonRunSummary, HealthResponse } from "./types";
import { formatVerdict } from "./verdictLabel";

export default function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [runs, setRuns] = useState<ComparisonRunSummary[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [selectedRun, setSelectedRun] = useState<ComparisonRunDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshRuns = useCallback(async () => {
    const nextRuns = await fetchRuns();
    setRuns(nextRuns);
    return nextRuns;
  }, []);

  const loadRun = useCallback(async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const run = await fetchRun(id);
      setSelectedId(id);
      setSelectedRun(run);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load run");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void (async () => {
      try {
        setHealth(await fetchHealth());
        const nextRuns = await refreshRuns();
        if (nextRuns.length > 0) {
          await loadRun(nextRuns[0].id);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to connect to API");
      }
    })();
  }, [loadRun, refreshRuns]);

  async function handleDemo() {
    setLoading(true);
    setError(null);
    try {
      const run = await seedSilentOmissionDemo();
      await refreshRuns();
      setSelectedId(run.id);
      setSelectedRun(run);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load demo");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app-shell">
      <header>
        <div>
          <h1>WitnessDiff Viewer</h1>
          <p className="subtitle">
            Replay witness-integrity failures — missing hops highlighted on the reference trace.
          </p>
        </div>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <button className="secondary" onClick={() => void refreshRuns()} disabled={loading}>
            Refresh
          </button>
          <button onClick={() => void handleDemo()} disabled={loading}>
            Load silent-omission demo
          </button>
        </div>
      </header>

      {health ? (
        <p className="meta" style={{ marginBottom: "1rem" }}>
          API {health.version} · store: {health.store}
        </p>
      ) : null}

      {error ? <div className="error">{error}</div> : null}

      <div className="grid-two">
        <div className="panel">
          <h2>Recent runs</h2>
          {runs.length === 0 ? (
            <p className="meta">No runs yet. Load the demo to create one.</p>
          ) : (
            <ul className="run-list">
              {runs.map((run) => (
                <li
                  key={run.id}
                  className={`run-item ${selectedId === run.id ? "active" : ""}`}
                  onClick={() => void loadRun(run.id)}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", gap: "0.75rem" }}>
                    <strong>{run.session_id}</strong>
                    <span className={`badge verdict ${run.ok ? "ok" : "fail"}`} title={run.verdict}>
                      {formatVerdict(run.verdict)}
                    </span>
                  </div>
                  <div className="meta">
                    {run.reference_action_count} ref / {run.evidence_action_count} evidence ·{" "}
                    {run.completeness_claim}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div>{selectedRun ? <RunDetail run={selectedRun} /> : <div className="panel">Select a run</div>}</div>
      </div>
    </div>
  );
}

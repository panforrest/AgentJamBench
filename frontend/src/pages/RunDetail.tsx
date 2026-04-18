import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getRun, type RunDetailResponse } from '../api'

function errorSummary(err: unknown): string {
  if (err && typeof err === 'object' && 'message' in err) {
    const m = (err as { message?: unknown }).message
    if (typeof m === 'string') return m.length > 160 ? `${m.slice(0, 160)}…` : m
  }
  try {
    const s = JSON.stringify(err)
    return s.length > 160 ? `${s.slice(0, 160)}…` : s
  } catch {
    return 'Unknown error'
  }
}

export function RunDetail() {
  const { runId } = useParams<{ runId: string }>()
  const id = runId ? parseInt(runId, 10) : NaN
  const [data, setData] = useState<RunDetailResponse | null>(null)
  const [err, setErr] = useState<string | null>(null)

  useEffect(() => {
    if (!Number.isFinite(id)) {
      setErr('Invalid run id')
      return
    }
    let cancelled = false
    void (async () => {
      try {
        const d = await getRun(id)
        if (!cancelled) setData(d)
      } catch (e) {
        if (!cancelled)
          setErr(e instanceof Error ? e.message : String(e))
      }
    })()
    return () => {
      cancelled = true
    }
  }, [id])

  if (err) {
    return (
      <div className="page">
        <Link to="/">← Home</Link>
        <div className="banner bad">{err}</div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="page">
        <Link to="/">← Home</Link>
        <p>Loading run…</p>
      </div>
    )
  }

  const { run, summary, results } = data
  const byProv = summary?.by_provider ?? {}

  return (
    <div className="page">
      <nav className="nav">
        <Link to="/">← Home</Link>
      </nav>

      <header className="hero">
        <h1>Run #{run.id}</h1>
        <p className="muted">
          {run.suite_id} · {run.status} ·{' '}
          {new Date(run.created_at).toLocaleString()}
        </p>
      </header>

      <section className="card">
        <h2>Summary by provider</h2>
        <div className="grid">
          {Object.entries(byProv).map(([prov, s]) => (
            <div key={prov} className="stat">
              <h3>{prov}</h3>
              <ul className="stat-list">
                <li>Tasks: {s.n_tasks}</li>
                <li>
                  Avg latency:{' '}
                  {s.avg_latency_ms != null ? `${Math.round(s.avg_latency_ms)} ms` : '—'}
                </li>
                <li>
                  Sum est. cost (OpenAI only):{' '}
                  {s.sum_estimated_cost_usd != null
                    ? `$${s.sum_estimated_cost_usd.toFixed(4)}`
                    : '—'}
                </li>
                <li>
                  Avg judge (0–5):{' '}
                  {s.avg_judge_rubric_0_to_5 != null
                    ? s.avg_judge_rubric_0_to_5.toFixed(2)
                    : '—'}
                </li>
                <li>
                  Deterministic pass rate:{' '}
                  {s.deterministic_pass_rate != null
                    ? `${(s.deterministic_pass_rate * 100).toFixed(0)}%`
                    : '—'}
                </li>
              </ul>
            </div>
          ))}
        </div>
      </section>

      <section className="card">
        <h2>Task results ({results.length})</h2>
        <div className="results">
          {results.map((r) => (
            <details key={r.id} className="task">
              <summary>
                <span className="badge">{r.provider}</span> {r.task_id}{' '}
                {r.duration_ms != null ? `· ${r.duration_ms} ms` : ''}
                {r.error ? (
                  <>
                    <span className="badge bad">error</span>
                    <span className="err-inline" title={errorSummary(r.error)}>
                      {' '}
                      {errorSummary(r.error)}
                    </span>
                  </>
                ) : null}
              </summary>
              <div className="task-body">
                <p>
                  <strong>Prompt</strong>
                </p>
                <pre className="prompt">{r.prompt}</pre>
                {r.error ? (
                  <pre className="err">{JSON.stringify(r.error, null, 2)}</pre>
                ) : (
                  <>
                    <p>
                      <strong>Output</strong>
                    </p>
                    <pre className="out">{r.output_text || '(empty)'}</pre>
                  </>
                )}
                {r.deterministic &&
                typeof r.deterministic === 'object' &&
                r.deterministic !== null &&
                'applies' in r.deterministic &&
                (r.deterministic as { applies?: boolean }).applies ? (
                  <p className="muted small">
                    Deterministic:{' '}
                    {(r.deterministic as { pass?: boolean }).pass
                      ? 'pass'
                      : 'fail'}
                  </p>
                ) : null}
              </div>
            </details>
          ))}
        </div>
      </section>
    </div>
  )
}

import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  getHealth,
  getSuite,
  listRuns,
  runSuite,
  type RunListResponse,
  type SuiteInfo,
} from '../api'

export function Home() {
  const navigate = useNavigate()
  const [health, setHealth] = useState<string>('…')
  const [suite, setSuite] = useState<SuiteInfo | null>(null)
  const [runs, setRuns] = useState<RunListResponse['runs']>([])
  const [err, setErr] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const [useOpenAI, setUseOpenAI] = useState(true)
  const [useBaseten, setUseBaseten] = useState(true)
  const [useJudge, setUseJudge] = useState(false)
  const [openaiModel, setOpenaiModel] = useState('gpt-4o-mini')

  const refresh = useCallback(async () => {
    setErr(null)
    try {
      const h = await getHealth()
      setHealth(h.ok ? 'connected' : 'unexpected')
      const s = await getSuite('default')
      setSuite(s)
      const r = await listRuns(20)
      setRuns(r.runs)
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e))
      setHealth('error')
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  async function onRunSuite() {
    const providers: ('openai' | 'baseten')[] = []
    if (useOpenAI) providers.push('openai')
    if (useBaseten) providers.push('baseten')
    if (providers.length === 0) {
      setErr('Select at least one provider.')
      return
    }
    setLoading(true)
    setErr(null)
    try {
      const out = await runSuite({
        suite_id: 'default',
        providers,
        openai_model: openaiModel,
        use_judge: useJudge,
        temperature: 0.2,
        max_tokens: 1024,
      })
      await refresh()
      navigate(`/runs/${out.run_id}`)
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <header className="hero">
        <h1>AgentJamBench</h1>
        <p className="tagline">
          Same tasks, multiple models — latency, cost, judge scores.
        </p>
        <p className={`pill ${health === 'connected' ? 'ok' : health === 'error' ? 'bad' : ''}`}>
          API: {health}
        </p>
      </header>

      {err && (
        <div className="banner bad" role="alert">
          {err}
        </div>
      )}

      <section className="card">
        <h2>Scenario pack</h2>
        {suite ? (
          <>
            <p>
              <strong>{suite.title}</strong> — {suite.tasks?.length ?? 0} tasks (
              <code>{suite.id}</code>)
            </p>
            <p className="muted">{suite.description}</p>
          </>
        ) : (
          <p className="muted">Loading suite…</p>
        )}
      </section>

      <section className="card">
        <h2>Run benchmark</h2>
        <div className="row">
          <label>
            <input
              type="checkbox"
              checked={useOpenAI}
              onChange={(e) => setUseOpenAI(e.target.checked)}
            />{' '}
            OpenAI
          </label>
          <label>
            <input
              type="checkbox"
              checked={useBaseten}
              onChange={(e) => setUseBaseten(e.target.checked)}
            />{' '}
            Baseten
          </label>
          <label>
            <input
              type="checkbox"
              checked={useJudge}
              onChange={(e) => setUseJudge(e.target.checked)}
            />{' '}
            LLM judge (slower; more API calls)
          </label>
        </div>
        <div className="row">
          <label className="grow">
            OpenAI model{' '}
            <input
              value={openaiModel}
              onChange={(e) => setOpenaiModel(e.target.value)}
              className="input"
            />
          </label>
        </div>
        <button
          type="button"
          className="btn primary"
          disabled={loading}
          onClick={() => void onRunSuite()}
        >
          {loading ? 'Running…' : 'Run full suite'}
        </button>
      </section>

      <section className="card">
        <h2>Recent runs</h2>
        {runs.length === 0 ? (
          <p className="muted">No runs yet.</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Suite</th>
                <th>Status</th>
                <th>When</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {runs.map((r) => (
                <tr key={r.id}>
                  <td>{r.id}</td>
                  <td>{r.suite_id}</td>
                  <td>{r.status}</td>
                  <td className="muted">
                    {new Date(r.created_at).toLocaleString()}
                  </td>
                  <td>
                    <Link to={`/runs/${r.id}`}>View</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  )
}

/** Use same-origin /api in dev (Vite proxy → Django). */
const prefix = '/api'

async function parseJson<T>(res: Response): Promise<T> {
  const text = await res.text()
  try {
    return JSON.parse(text) as T
  } catch {
    throw new Error(text.slice(0, 200) || `HTTP ${res.status}`)
  }
}

export async function getHealth(): Promise<{ ok: boolean; service?: string }> {
  const res = await fetch(`${prefix}/health/`)
  return parseJson(res)
}

export type SuiteInfo = {
  id: string
  title: string
  description?: string
  tasks: { id: string; prompt: string; category?: string; difficulty?: string }[]
}

export async function getSuite(suiteId: string): Promise<SuiteInfo> {
  const res = await fetch(`${prefix}/suites/${suiteId}/`)
  if (!res.ok) throw new Error(`Suite ${res.status}`)
  return parseJson(res)
}

export type RunListResponse = {
  runs: {
    id: number
    created_at: string
    suite_id: string
    status: string
    meta: Record<string, unknown>
    summary: unknown
  }[]
}

export async function listRuns(limit = 30): Promise<RunListResponse> {
  const res = await fetch(`${prefix}/runs/?limit=${limit}`)
  if (!res.ok) throw new Error(`Runs ${res.status}`)
  return parseJson(res)
}

export type RunSuiteBody = {
  suite_id?: string
  providers?: ('openai' | 'baseten')[]
  openai_model?: string
  temperature?: number
  max_tokens?: number
  use_judge?: boolean
  judge_model?: string
}

export type RunSuiteResponse = {
  run_id: number
  summary: unknown
  results: unknown[]
}

export async function runSuite(body: RunSuiteBody): Promise<RunSuiteResponse> {
  const res = await fetch(`${prefix}/run/suite/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  const data = await parseJson<RunSuiteResponse & { detail?: string }>(res)
  if (!res.ok) {
    const msg =
      typeof data.detail === 'string'
        ? data.detail
        : `Request failed (${res.status})`
    throw new Error(msg)
  }
  return data
}

export type RunDetailResponse = {
  run: {
    id: number
    created_at: string
    suite_id: string
    status: string
    meta: Record<string, unknown>
  }
  summary: {
    by_provider: Record<
      string,
      {
        n_tasks: number
        avg_latency_ms: number | null
        sum_estimated_cost_usd: number | null
        avg_judge_rubric_0_to_5: number | null
        deterministic_pass_rate: number | null
      }
    >
  }
  results: {
    id: number
    task_id: string
    provider: string
    model_label: string
    prompt: string
    output_text: string
    duration_ms: number | null
    estimated_cost_usd: number | null
    error: unknown
    deterministic: unknown
    judge: unknown
  }[]
}

export async function getRun(runId: number): Promise<RunDetailResponse> {
  const res = await fetch(`${prefix}/runs/${runId}/`)
  if (!res.ok) throw new Error(`Run ${res.status}`)
  return parseJson(res)
}

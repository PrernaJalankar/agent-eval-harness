import { BrowserRouter, Routes, Route, Link, useParams } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { Activity, CheckCircle2, XCircle, Clock, ChevronRight, BarChart3 } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

const API = '/api'

function Layout({ children }) {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center gap-3">
          <Activity className="w-6 h-6 text-emerald-400" />
          <Link to="/" className="text-xl font-semibold tracking-tight hover:text-emerald-400 transition">
            Agent Eval Harness
          </Link>
          <span className="text-slate-500 text-sm ml-2">Dashboard</span>
        </div>
      </header>
      <main className="max-w-6xl mx-auto px-6 py-8">{children}</main>
    </div>
  )
}

function PassBadge({ rate }) {
  const pct = Math.round(rate * 100)
  const color = pct >= 80 ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
    : pct >= 50 ? 'bg-amber-500/20 text-amber-400 border-amber-500/30'
    : 'bg-rose-500/20 text-rose-400 border-rose-500/30'
  return (
    <span className={`px-2.5 py-1 rounded-full text-sm font-medium border ${color}`}>
      {pct}%
    </span>
  )
}

function RunsList() {
  const [runs, setRuns] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${API}/runs`)
      .then(r => r.json())
      .then(data => { setRuns(data); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  if (loading) return <p className="text-slate-400">Loading runs…</p>
  if (!runs.length) return <p className="text-slate-400">No runs yet. Run an eval first.</p>

  const chartData = [...runs].reverse().map(r => ({
    name: r.label.slice(0, 12),
    rate: Math.round(r.pass_rate * 100),
  }))

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold mb-1">Evaluation Runs</h1>
        <p className="text-slate-400 text-sm">Click a run to inspect case-level results</p>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
        <div className="flex items-center gap-2 mb-4 text-slate-300">
          <BarChart3 className="w-5 h-5 text-emerald-400" />
          <span className="font-medium">Pass rate over time</span>
        </div>
        <ResponsiveContainer width="100%" height={180}>
          <BarChart data={chartData}>
            <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 11 }} />
            <YAxis domain={[0, 100]} tick={{ fill: '#94a3b8', fontSize: 11 }} />
            <Tooltip
              contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8 }}
              labelStyle={{ color: '#e2e8f0' }}
            />
            <Bar dataKey="rate" radius={[6, 6, 0, 0]}>
              {chartData.map((e, i) => (
                <Cell key={i} fill={e.rate >= 80 ? '#34d399' : e.rate >= 50 ? '#fbbf24' : '#f87171'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid gap-3">
        {runs.map(run => (
          <Link
            key={run.id}
            to={`/runs/${run.id}`}
            className="group flex items-center justify-between bg-slate-900 border border-slate-800 hover:border-emerald-500/40 rounded-xl px-5 py-4 transition"
          >
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-lg bg-slate-800 flex items-center justify-center text-emerald-400 font-mono text-sm">
                {run.id.slice(0, 4)}
              </div>
              <div>
                <div className="font-medium group-hover:text-emerald-400 transition">{run.label}</div>
                <div className="text-sm text-slate-500">
                  {run.model} · {run.created ? new Date(run.created).toLocaleString() : '—'}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-slate-400">{run.passed}/{run.total}</span>
              <PassBadge rate={run.pass_rate} />
              <ChevronRight className="w-5 h-5 text-slate-600 group-hover:text-emerald-400 transition" />
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}

function RunDetail() {
  const { id } = useParams()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${API}/runs/${id}`)
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false) })
      .catch(() => setLoading(false))
  }, [id])

  if (loading) return <p className="text-slate-400">Loading…</p>
  if (!data) return <p className="text-rose-400">Run not found</p>

  const passed = data.results.filter(r => r.passed).length
  const total = data.results.length

  return (
    <div className="space-y-6">
      <Link to="/" className="text-sm text-slate-400 hover:text-emerald-400 transition">← All runs</Link>
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold">{data.label}</h1>
          <p className="text-slate-400 text-sm mt-1">
            {data.model} · {data.created ? new Date(data.created).toLocaleString() : '—'} · id {data.id}
          </p>
        </div>
        <PassBadge rate={total ? passed / total : 0} />
      </div>

      <div className="grid gap-3">
        {data.results.map((r, i) => (
          <div
            key={i}
            className={`rounded-xl border px-5 py-4 ${
              r.passed
                ? 'bg-emerald-500/5 border-emerald-500/20'
                : 'bg-rose-500/5 border-rose-500/20'
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                {r.passed
                  ? <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  : <XCircle className="w-5 h-5 text-rose-400" />}
                <span className="font-medium">{r.case_id}</span>
              </div>
              <div className="flex items-center gap-3 text-sm text-slate-400">
                <span className="flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5" />
                  {r.latency != null ? `${Number(r.latency).toFixed(1)}s` : '—'}
                </span>
              </div>
            </div>
            {r.answer && (
              <p className="text-sm text-slate-300 mt-2 line-clamp-3 whitespace-pre-wrap">
                {r.answer}
              </p>
            )}
            {Array.isArray(r.tool_calls) && r.tool_calls.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1.5">
                {r.tool_calls.map((t, j) => (
                  <span key={j} className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                    {typeof t === 'object' ? t.name : String(t)}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<RunsList />} />
          <Route path="/runs/:id" element={<RunDetail />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}

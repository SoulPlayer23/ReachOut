import { useEffect, useState } from 'react'
import AppLayout from '../../components/AppLayout'
import api from '../../lib/api'
import usePageTitle from '../../hooks/usePageTitle'

interface Source {
  id: number
  source_key: string
  label: string
  category: string
  enabled: boolean
  is_custom: boolean
}

export default function Sources() {
  usePageTitle('Sources')
  const [sources, setSources] = useState<Source[]>([])
  const [loading, setLoading] = useState(true)
  const [toggling, setToggling] = useState<string | null>(null)

  useEffect(() => {
    api.get<Source[]>('/sources').then(r => setSources(r.data)).finally(() => setLoading(false))
  }, [])

  async function toggle(source: Source) {
    setToggling(source.source_key)
    try {
      const r = await api.patch<Source>(`/sources/${source.source_key}`, { enabled: !source.enabled })
      setSources(prev => prev.map(s => s.source_key === source.source_key ? r.data : s))
    } finally {
      setToggling(null)
    }
  }

  const jobBoards = sources.filter(s => s.category === 'job_board')
  const recruiterSources = sources.filter(s => s.category === 'recruiter')

  return (
    <AppLayout>
      <div className="flex-1 overflow-y-auto px-6 py-6 max-w-2xl mx-auto w-full">
        <h1 className="text-lg font-semibold text-white mb-1">Sources</h1>
        <p className="text-sm text-gray-400 mb-6">Control which job boards and recruiter databases ReachOut searches.</p>

        {loading ? (
          <div className="text-gray-500 text-sm">Loading…</div>
        ) : (
          <>
            <SourceSection title="Job Boards" sources={jobBoards} toggling={toggling} onToggle={toggle} />
            <SourceSection title="Recruiter Discovery" sources={recruiterSources} toggling={toggling} onToggle={toggle} />
          </>
        )}
      </div>
    </AppLayout>
  )
}

function SourceSection({
  title,
  sources,
  toggling,
  onToggle,
}: {
  title: string
  sources: Source[]
  toggling: string | null
  onToggle: (s: Source) => void
}) {
  if (!sources.length) return null
  return (
    <div className="mb-6">
      <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">{title}</h2>
      <div className="rounded-lg border border-gray-800 divide-y divide-gray-800 overflow-hidden">
        {sources.map(source => (
          <div key={source.source_key} className="flex items-center justify-between px-4 py-3 bg-gray-900">
            <div>
              <p className="text-sm text-white font-medium">{source.label}</p>
              <p className="text-xs text-gray-500 mt-0.5 capitalize">{source.category.replace('_', ' ')}</p>
            </div>
            <button
              onClick={() => onToggle(source)}
              disabled={toggling === source.source_key}
              className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 focus:outline-none disabled:opacity-50 ${
                source.enabled ? 'bg-indigo-600' : 'bg-gray-700'
              }`}
              role="switch"
              aria-checked={source.enabled}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition duration-200 ${
                  source.enabled ? 'translate-x-4' : 'translate-x-0'
                }`}
              />
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}

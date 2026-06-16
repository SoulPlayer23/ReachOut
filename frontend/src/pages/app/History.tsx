import { useEffect, useState } from 'react'
import AppLayout from '../../components/AppLayout'
import api from '../../lib/api'
import usePageTitle from '../../hooks/usePageTitle'

interface OutreachLog {
  id: number
  company: string
  role: string
  recruiter_name: string | null
  recruiter_email: string
  email_subject: string
  email_body: string
  status: string
  sent_at: string | null
}

const STATUS_STYLES: Record<string, string> = {
  sent: 'bg-green-900/40 text-green-300 border-green-800',
  pending: 'bg-yellow-900/30 text-yellow-300 border-yellow-800',
  failed: 'bg-red-900/30 text-red-300 border-red-800',
}

export default function History() {
  usePageTitle('History')
  const [logs, setLogs] = useState<OutreachLog[]>([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [hasMore, setHasMore] = useState(true)
  const [expanded, setExpanded] = useState<number | null>(null)

  useEffect(() => {
    setLoading(true)
    api.get<OutreachLog[]>('/history', { params: { page, page_size: 20 } })
      .then(r => {
        setLogs(r.data)
        setHasMore(r.data.length === 20)
      })
      .finally(() => setLoading(false))
  }, [page])

  return (
    <AppLayout>
      <div className="flex-1 overflow-y-auto px-6 py-6 max-w-3xl mx-auto w-full">
        <h1 className="text-lg font-semibold text-white mb-1">History</h1>
        <p className="text-sm text-gray-400 mb-6">All cold emails drafted and sent through ReachOut.</p>

        {loading ? (
          <div className="text-gray-500 text-sm">Loading…</div>
        ) : logs.length === 0 ? (
          <div className="text-gray-500 text-sm text-center py-12">No outreach history yet. Start a conversation in Chat.</div>
        ) : (
          <>
            <div className="space-y-2">
              {logs.map(log => (
                <div key={log.id} className="rounded-lg border border-gray-800 bg-gray-900 overflow-hidden">
                  <button
                    onClick={() => setExpanded(expanded === log.id ? null : log.id)}
                    className="w-full px-4 py-3 flex items-start justify-between gap-3 text-left hover:bg-gray-800/50 transition-colors"
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-sm font-medium text-white">{log.company}</span>
                        <span className="text-gray-600">·</span>
                        <span className="text-sm text-gray-300">{log.role}</span>
                        <span className={`text-xs px-1.5 py-0.5 rounded border ${STATUS_STYLES[log.status] ?? 'bg-gray-700 text-gray-400 border-gray-700'}`}>
                          {log.status}
                        </span>
                      </div>
                      <p className="text-xs text-gray-500 mt-0.5 truncate">
                        To: {log.recruiter_name ? `${log.recruiter_name} ` : ''}&lt;{log.recruiter_email}&gt;
                      </p>
                    </div>
                    <span className="text-xs text-gray-600 shrink-0 mt-0.5">
                      {log.sent_at ? new Date(log.sent_at).toLocaleDateString() : '—'}
                    </span>
                  </button>

                  {expanded === log.id && (
                    <div className="px-4 pb-4 border-t border-gray-800">
                      <p className="text-xs font-medium text-gray-500 mt-3 mb-1">Subject</p>
                      <p className="text-sm text-gray-200">{log.email_subject}</p>
                      <p className="text-xs font-medium text-gray-500 mt-3 mb-1">Body</p>
                      <pre className="text-xs text-gray-300 whitespace-pre-wrap leading-relaxed font-sans">{log.email_body}</pre>
                    </div>
                  )}
                </div>
              ))}
            </div>

            <div className="flex items-center justify-between mt-4">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="text-sm text-gray-400 hover:text-white disabled:opacity-30 transition-colors"
              >
                ← Previous
              </button>
              <span className="text-xs text-gray-600">Page {page}</span>
              <button
                onClick={() => setPage(p => p + 1)}
                disabled={!hasMore}
                className="text-sm text-gray-400 hover:text-white disabled:opacity-30 transition-colors"
              >
                Next →
              </button>
            </div>
          </>
        )}
      </div>
    </AppLayout>
  )
}

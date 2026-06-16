import { useEffect, useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../../lib/api'

type KeyStatus = { serper: boolean; hunter: boolean; apollo: boolean; snov: boolean; ollama: boolean }
type GmailStatus = { connected: boolean }

export default function OnboardingConnections() {
  const navigate = useNavigate()
  const [keys, setKeys] = useState({ serper: '', hunter: '', apollo: '', snov: '', ollama: '' })
  const [status, setStatus] = useState<KeyStatus | null>(null)
  const [gmail, setGmail] = useState<GmailStatus | null>(null)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    api.get('/api-keys/status').then(r => setStatus(r.data)).catch(() => {})
    api.get('/gmail/status').then(r => setGmail(r.data)).catch(() => {})
    // Show connected feedback if redirected back from Gmail OAuth
    if (new URLSearchParams(window.location.search).get('gmail') === 'connected') {
      setGmail({ connected: true })
    }
  }, [])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setSaving(true)
    setError('')
    setSaved(false)
    try {
      const body: Record<string, string | null> = {}
      if (keys.serper) body.serper_key = keys.serper
      if (keys.hunter) body.hunter_key = keys.hunter
      if (keys.apollo) body.apollo_key = keys.apollo
      if (keys.snov) body.snov_key = keys.snov
      if (keys.ollama) body.ollama_api_key = keys.ollama
      const r = await api.post('/api-keys', body)
      setStatus(r.data)
      setSaved(true)
      setKeys({ serper: '', hunter: '', apollo: '', snov: '', ollama: '' })
    } catch {
      setError('Failed to save keys')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        <StepIndicator current={3} />

        <h1 className="text-2xl font-bold text-white mb-1">Connect your accounts</h1>
        <p className="text-gray-400 text-sm mb-8">
          ReachOut uses these services to find jobs, discover recruiter contacts, and send emails.
        </p>

        {/* Gmail */}
        <div className="border border-gray-700 rounded-lg p-4 mb-6">
          <div className="flex items-center justify-between mb-3">
            <div>
              <p className="text-white text-sm font-medium">Gmail</p>
              <p className="text-gray-500 text-xs">Required to send cold emails</p>
            </div>
            <StatusBadge ok={gmail?.connected ?? false} />
          </div>
          {!gmail?.connected && (
            <button
              type="button"
              onClick={() =>
                api.get('/gmail/connect').then(r => { window.location.href = r.data.url })
              }
              className="flex items-center justify-center gap-2 w-full border border-gray-600 hover:border-gray-500 text-gray-300 rounded-lg py-2 text-sm transition-colors"
            >
              Connect Gmail
            </button>
          )}
        </div>

        {/* API Keys */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <p className="text-gray-400 text-xs uppercase tracking-wider">API Keys</p>

          <ApiKeyField
            label="Serper.dev"
            desc="Job search — required"
            placeholder="Paste your Serper API key"
            value={keys.serper}
            onChange={v => setKeys(k => ({ ...k, serper: v }))}
            configured={status?.serper}
          />
          <ApiKeyField
            label="Apollo.io"
            desc="Recruiter contact discovery"
            placeholder="Paste your Apollo API key"
            value={keys.apollo}
            onChange={v => setKeys(k => ({ ...k, apollo: v }))}
            configured={status?.apollo}
          />
          <ApiKeyField
            label="Hunter.io"
            desc="Email finder by domain"
            placeholder="Paste your Hunter API key"
            value={keys.hunter}
            onChange={v => setKeys(k => ({ ...k, hunter: v }))}
            configured={status?.hunter}
          />
          <ApiKeyField
            label="Snov.io"
            desc="Optional — additional email finder"
            placeholder="Paste your Snov client ID"
            value={keys.snov}
            onChange={v => setKeys(k => ({ ...k, snov: v }))}
            configured={status?.snov}
          />
          <ApiKeyField
            label="Ollama API key"
            desc="Optional — for Ollama Cloud"
            placeholder="Paste your Ollama API key"
            value={keys.ollama}
            onChange={v => setKeys(k => ({ ...k, ollama: v }))}
            configured={status?.ollama}
          />

          {error && <p className="text-red-400 text-sm">{error}</p>}
          {saved && <p className="text-green-400 text-sm">Keys saved successfully</p>}

          <button
            type="submit"
            disabled={saving}
            className="w-full border border-indigo-600 hover:bg-indigo-600/20 disabled:opacity-50 text-indigo-400 font-medium rounded-lg py-2 text-sm transition-colors"
          >
            {saving ? 'Saving…' : 'Save keys'}
          </button>
        </form>

        <button
          onClick={() => navigate('/app/chat')}
          className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium rounded-lg py-2 text-sm transition-colors mt-4"
        >
          Go to chat →
        </button>
        <p className="text-gray-600 text-xs text-center mt-2">
          You can add or update keys anytime from Settings
        </p>
      </div>
    </div>
  )
}

function ApiKeyField({
  label, desc, placeholder, value, onChange, configured,
}: {
  label: string
  desc: string
  placeholder: string
  value: string
  onChange: (v: string) => void
  configured?: boolean
}) {
  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <label className="text-sm text-gray-300">{label}</label>
        {configured !== undefined && <StatusBadge ok={configured} />}
      </div>
      <p className="text-gray-500 text-xs mb-1.5">{desc}</p>
      <input
        type="password"
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder={configured ? '••••••••  (already saved)' : placeholder}
        className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500 text-sm"
      />
    </div>
  )
}

function StatusBadge({ ok }: { ok: boolean }) {
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full ${ok ? 'bg-green-900/40 text-green-400' : 'bg-gray-800 text-gray-500'}`}>
      {ok ? '✓ Connected' : 'Not set'}
    </span>
  )
}

function StepIndicator({ current }: { current: number }) {
  return (
    <div className="flex items-center gap-2 mb-8">
      {[1, 2, 3].map(n => (
        <div key={n} className={`h-1 flex-1 rounded-full ${n <= current ? 'bg-indigo-500' : 'bg-gray-700'}`} />
      ))}
    </div>
  )
}

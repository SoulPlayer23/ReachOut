import { useEffect, useState } from 'react'
import AppLayout from '../../components/AppLayout'
import api from '../../lib/api'
import usePageTitle from '../../hooks/usePageTitle'

interface Prefs {
  default_location: string | null
  target_roles: string[] | null
  tone: string
}

interface KeysStatus {
  serper: boolean
  hunter: boolean
  apollo: boolean
  snov: boolean
  ollama: boolean
}

const TONES = ['professional', 'casual', 'enthusiastic'] as const

export default function Settings() {
  usePageTitle('Settings')
  return (
    <AppLayout>
      <div className="flex-1 overflow-y-auto px-6 py-6 max-w-2xl mx-auto w-full space-y-8">
        <div>
          <h1 className="text-lg font-semibold text-white mb-1">Settings</h1>
          <p className="text-sm text-gray-400">Manage your preferences, API keys, and connected accounts.</p>
        </div>
        <ResumeSection />
        <PreferencesSection />
        <ApiKeysSection />
        <ConnectionsSection />
      </div>
    </AppLayout>
  )
}

// ── Resume ────────────────────────────────────────────────────────────────────

function ResumeSection() {
  const [found, setFound] = useState<boolean | null>(null)

  useEffect(() => {
    api.get('/onboarding/resume-check').then(r => setFound(r.data.found)).catch(() => setFound(false))
  }, [])

  return (
    <Card title="Resume">
      {found === null ? (
        <p className="text-sm text-gray-500">Checking…</p>
      ) : found ? (
        <div className="flex items-center gap-2 text-green-400 text-sm">
          <span className="text-base">✓</span> Resume found at <code className="text-xs bg-gray-800 px-1.5 py-0.5 rounded">~/.reachout/</code>
        </div>
      ) : (
        <div className="text-sm text-yellow-400 space-y-1">
          <p>No resume detected.</p>
          <p className="text-gray-400 text-xs">Place a PDF file in <code className="bg-gray-800 px-1 py-0.5 rounded">~/.reachout/</code> on your host machine and restart the container.</p>
        </div>
      )}
    </Card>
  )
}

// ── Preferences ───────────────────────────────────────────────────────────────

function PreferencesSection() {
  const [location, setLocation] = useState('')
  const [roles, setRoles] = useState<string[]>([])
  const [roleInput, setRoleInput] = useState('')
  const [tone, setTone] = useState<string>('professional')
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    api.get<Prefs>('/preferences').then(r => {
      if (!r.data) return
      setLocation(r.data.default_location ?? '')
      setRoles(r.data.target_roles ?? [])
      setTone(r.data.tone)
    }).catch(() => {})
  }, [])

  function addRole(value: string) {
    const trimmed = value.trim().replace(/,$/, '')
    if (trimmed && !roles.includes(trimmed)) setRoles(prev => [...prev, trimmed])
    setRoleInput('')
  }

  function handleRoleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter' || e.key === ',') { e.preventDefault(); addRole(roleInput) }
    if (e.key === 'Backspace' && !roleInput) setRoles(prev => prev.slice(0, -1))
  }

  async function save() {
    setSaving(true)
    try {
      await api.post('/preferences', { default_location: location || null, target_roles: roles, tone })
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Card title="Preferences">
      <div className="space-y-4">
        <div>
          <label className="block text-xs text-gray-400 mb-1">Default location</label>
          <input
            value={location}
            onChange={e => setLocation(e.target.value)}
            placeholder="e.g. Bangalore, India"
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm placeholder-gray-600 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div>
          <label className="block text-xs text-gray-400 mb-1">Target roles <span className="text-gray-600">(Enter or comma to add)</span></label>
          <div className="flex flex-wrap gap-1.5 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 focus-within:border-indigo-500 min-h-[42px]">
            {roles.map(r => (
              <span key={r} className="flex items-center gap-1 bg-indigo-900/60 text-indigo-200 text-xs px-2 py-0.5 rounded-full">
                {r}
                <button onClick={() => setRoles(prev => prev.filter(x => x !== r))} className="text-indigo-400 hover:text-white leading-none">×</button>
              </span>
            ))}
            <input
              value={roleInput}
              onChange={e => setRoleInput(e.target.value)}
              onKeyDown={handleRoleKeyDown}
              onBlur={() => { if (roleInput.trim()) addRole(roleInput) }}
              placeholder={roles.length ? '' : 'Software Engineer…'}
              className="flex-1 min-w-[120px] bg-transparent text-white text-sm placeholder-gray-600 focus:outline-none"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs text-gray-400 mb-2">Email tone</label>
          <div className="grid grid-cols-3 gap-2">
            {TONES.map(t => (
              <button
                key={t}
                onClick={() => setTone(t)}
                className={`py-2 rounded-lg border text-sm capitalize transition-colors ${
                  tone === t
                    ? 'border-indigo-500 bg-indigo-600/20 text-indigo-300'
                    : 'border-gray-700 bg-gray-800 text-gray-400 hover:border-gray-600 hover:text-white'
                }`}
              >
                {t}
              </button>
            ))}
          </div>
        </div>

        <button
          onClick={save}
          disabled={saving}
          className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
        >
          {saved ? 'Saved ✓' : saving ? 'Saving…' : 'Save preferences'}
        </button>
      </div>
    </Card>
  )
}

// ── API Keys ──────────────────────────────────────────────────────────────────

const KEY_FIELDS: { key: keyof ApiKeysFormState; label: string; placeholder: string }[] = [
  { key: 'serper_key',    label: 'Serper.dev',  placeholder: 'API key for Google search' },
  { key: 'hunter_key',   label: 'Hunter.io',   placeholder: 'API key for email lookup' },
  { key: 'apollo_key',   label: 'Apollo.io',   placeholder: 'API key for recruiter search' },
  { key: 'snov_key',     label: 'Snov.io',     placeholder: 'Client ID (optional)' },
  { key: 'ollama_api_key', label: 'Ollama Cloud', placeholder: 'API key for cloud LLM' },
]

interface ApiKeysFormState {
  serper_key: string
  hunter_key: string
  apollo_key: string
  snov_key: string
  ollama_api_key: string
}

const EMPTY_KEYS: ApiKeysFormState = { serper_key: '', hunter_key: '', apollo_key: '', snov_key: '', ollama_api_key: '' }
const STATUS_KEY_MAP: Record<keyof ApiKeysFormState, keyof KeysStatus> = {
  serper_key: 'serper', hunter_key: 'hunter', apollo_key: 'apollo', snov_key: 'snov', ollama_api_key: 'ollama',
}

function ApiKeysSection() {
  const [form, setForm] = useState<ApiKeysFormState>(EMPTY_KEYS)
  const [status, setStatus] = useState<KeysStatus | null>(null)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    api.get<KeysStatus>('/api-keys/status').then(r => setStatus(r.data)).catch(() => {})
  }, [])

  async function save() {
    const payload = Object.fromEntries(
      Object.entries(form).filter(([, v]) => v.trim() !== '')
    )
    if (!Object.keys(payload).length) return
    setSaving(true)
    try {
      await api.post<KeysStatus>('/api-keys', payload).then(r => setStatus(r.data))
      setForm(EMPTY_KEYS)
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Card title="API Keys">
      <p className="text-xs text-gray-500 mb-4">Keys are encrypted at rest. Leave a field blank to keep the existing key.</p>
      <div className="space-y-3">
        {KEY_FIELDS.map(({ key, label, placeholder }) => (
          <div key={key} className="flex items-center gap-3">
            <div className="w-28 shrink-0">
              <p className="text-xs text-gray-300 font-medium">{label}</p>
              {status && (
                <p className={`text-xs mt-0.5 ${status[STATUS_KEY_MAP[key]] ? 'text-green-400' : 'text-gray-600'}`}>
                  {status[STATUS_KEY_MAP[key]] ? '✓ Set' : 'Not set'}
                </p>
              )}
            </div>
            <input
              type="password"
              value={form[key]}
              onChange={e => setForm(prev => ({ ...prev, [key]: e.target.value }))}
              placeholder={placeholder}
              className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm placeholder-gray-600 focus:outline-none focus:border-indigo-500"
            />
          </div>
        ))}
      </div>
      <button
        onClick={save}
        disabled={saving || Object.values(form).every(v => !v.trim())}
        className="mt-4 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
      >
        {saved ? 'Saved ✓' : saving ? 'Saving…' : 'Update keys'}
      </button>
    </Card>
  )
}

// ── Connections ───────────────────────────────────────────────────────────────

function ConnectionsSection() {
  const [gmailConnected, setGmailConnected] = useState<boolean | null>(null)

  useEffect(() => {
    if (new URLSearchParams(window.location.search).get('gmail') === 'connected') {
      setGmailConnected(true)
      window.history.replaceState({}, '', '/app/settings')
      return
    }
    api.get('/gmail/status').then(r => setGmailConnected(r.data.connected)).catch(() => setGmailConnected(false))
  }, [])

  async function connectGmail() {
    const r = await api.get<{ url: string }>('/gmail/connect', { params: { return_to: '/app/settings' } })
    window.location.href = r.data.url
  }

  return (
    <Card title="Connected Accounts">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-white font-medium">Gmail</p>
          <p className="text-xs text-gray-500 mt-0.5">Used to send emails on your behalf</p>
        </div>
        {gmailConnected === null ? (
          <span className="text-xs text-gray-600">Checking…</span>
        ) : gmailConnected ? (
          <span className="text-xs bg-green-900/40 border border-green-800 text-green-300 px-2.5 py-1 rounded-full">Connected</span>
        ) : (
          <button
            onClick={connectGmail}
            className="text-sm bg-indigo-600 hover:bg-indigo-500 text-white px-3 py-1.5 rounded-lg transition-colors"
          >
            Connect Gmail
          </button>
        )}
      </div>
    </Card>
  )
}

// ── Shared ────────────────────────────────────────────────────────────────────

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">{title}</h2>
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
        {children}
      </div>
    </div>
  )
}

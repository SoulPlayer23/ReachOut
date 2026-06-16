import { useState, type FormEvent, type KeyboardEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../../lib/api'

const TONES = [
  { value: 'professional', label: 'Professional', desc: 'Formal and polished' },
  { value: 'casual', label: 'Casual', desc: 'Friendly and approachable' },
  { value: 'enthusiastic', label: 'Enthusiastic', desc: 'Energetic and passionate' },
]

export default function OnboardingPreferences() {
  const navigate = useNavigate()
  const [location, setLocation] = useState('')
  const [roles, setRoles] = useState<string[]>([])
  const [roleInput, setRoleInput] = useState('')
  const [tone, setTone] = useState('professional')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  function addRole() {
    const trimmed = roleInput.trim()
    if (trimmed && !roles.includes(trimmed)) {
      setRoles([...roles, trimmed])
    }
    setRoleInput('')
  }

  function handleRoleKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault()
      addRole()
    } else if (e.key === 'Backspace' && !roleInput && roles.length) {
      setRoles(roles.slice(0, -1))
    }
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (roleInput.trim()) addRole()
    setLoading(true)
    setError('')
    try {
      await api.post('/preferences', {
        default_location: location || null,
        target_roles: roles.length ? roles : null,
        tone,
      })
      navigate('/onboarding/connections')
    } catch {
      setError('Failed to save preferences')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <StepIndicator current={2} />

        <h1 className="text-2xl font-bold text-white mb-1">Your preferences</h1>
        <p className="text-gray-400 text-sm mb-8">
          Used to personalize your job search and email tone.
        </p>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm text-gray-300 mb-1">Default location</label>
            <input
              type="text"
              value={location}
              onChange={e => setLocation(e.target.value)}
              placeholder="e.g. Bengaluru, India"
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500 text-sm"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-300 mb-1">Target roles</label>
            <div className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 focus-within:border-indigo-500 min-h-[42px] flex flex-wrap gap-1.5 items-center">
              {roles.map(role => (
                <span key={role} className="flex items-center gap-1 bg-indigo-900/60 text-indigo-300 text-xs px-2 py-0.5 rounded">
                  {role}
                  <button type="button" onClick={() => setRoles(roles.filter(r => r !== role))} className="text-indigo-400 hover:text-white">×</button>
                </span>
              ))}
              <input
                type="text"
                value={roleInput}
                onChange={e => setRoleInput(e.target.value)}
                onKeyDown={handleRoleKeyDown}
                onBlur={addRole}
                placeholder={roles.length ? '' : 'e.g. Software Engineer — press Enter to add'}
                className="flex-1 min-w-32 bg-transparent text-white placeholder-gray-500 text-sm focus:outline-none"
              />
            </div>
            <p className="text-gray-600 text-xs mt-1">Press Enter or comma to add each role</p>
          </div>

          <div>
            <label className="block text-sm text-gray-300 mb-2">Email tone</label>
            <div className="grid grid-cols-3 gap-2">
              {TONES.map(t => (
                <button
                  key={t.value}
                  type="button"
                  onClick={() => setTone(t.value)}
                  className={`rounded-lg p-3 text-left border transition-colors ${
                    tone === t.value
                      ? 'border-indigo-500 bg-indigo-900/30'
                      : 'border-gray-700 bg-gray-800/40 hover:border-gray-600'
                  }`}
                >
                  <p className={`text-sm font-medium ${tone === t.value ? 'text-indigo-300' : 'text-gray-300'}`}>{t.label}</p>
                  <p className="text-xs text-gray-500 mt-0.5">{t.desc}</p>
                </button>
              ))}
            </div>
          </div>

          {error && <p className="text-red-400 text-sm">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium rounded-lg py-2 text-sm transition-colors"
          >
            {loading ? 'Saving…' : 'Continue'}
          </button>
        </form>
      </div>
    </div>
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

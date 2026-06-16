import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../../lib/api'

export default function OnboardingResume() {
  const navigate = useNavigate()
  const [found, setFound] = useState<boolean | null>(null)

  useEffect(() => {
    api.get('/onboarding/resume-check')
      .then(r => setFound(r.data.found))
      .catch(() => setFound(false))
  }, [])

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <StepIndicator current={1} />

        <h1 className="text-2xl font-bold text-white mb-1">Your resume</h1>
        <p className="text-gray-400 text-sm mb-8">
          ReachOut attaches your resume to every cold email automatically.
        </p>

        <div className={`rounded-lg border p-4 mb-6 ${
          found === null ? 'border-gray-700 bg-gray-800/40' :
          found ? 'border-green-700 bg-green-900/20' :
          'border-yellow-700 bg-yellow-900/20'
        }`}>
          {found === null && (
            <p className="text-gray-400 text-sm">Checking…</p>
          )}
          {found === true && (
            <div className="flex items-center gap-3">
              <span className="text-green-400 text-xl">✓</span>
              <div>
                <p className="text-green-400 text-sm font-medium">Resume found</p>
                <p className="text-gray-400 text-xs font-mono mt-0.5">~/.reachout/resume.pdf</p>
              </div>
            </div>
          )}
          {found === false && (
            <div>
              <div className="flex items-center gap-3 mb-3">
                <span className="text-yellow-400 text-xl">!</span>
                <p className="text-yellow-400 text-sm font-medium">Resume not found</p>
              </div>
              <p className="text-gray-300 text-sm mb-2">Place your resume at:</p>
              <code className="block bg-gray-900 text-indigo-300 text-xs px-3 py-2 rounded font-mono mb-3">
                ~/.reachout/resume.pdf
              </code>
              <p className="text-gray-500 text-xs">
                Create the folder if it doesn't exist:{' '}
                <code className="text-gray-400">mkdir -p ~/.reachout</code>
              </p>
            </div>
          )}
        </div>

        {found === false && (
          <button
            onClick={() => api.get('/onboarding/resume-check').then(r => setFound(r.data.found))}
            className="w-full border border-gray-600 hover:border-gray-500 text-gray-300 rounded-lg py-2 text-sm mb-3 transition-colors"
          >
            Check again
          </button>
        )}

        <button
          onClick={() => navigate('/onboarding/preferences')}
          className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium rounded-lg py-2 text-sm transition-colors"
        >
          Continue
        </button>

        {!found && found !== null && (
          <p className="text-gray-600 text-xs text-center mt-3">
            You can add your resume later from Settings
          </p>
        )}
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

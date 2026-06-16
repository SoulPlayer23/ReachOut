export interface Recruiter {
  name: string
  title: string
  email: string
  source: string
  confidence: number
}

const SOURCE_LABELS: Record<string, string> = {
  apollo: 'Apollo.io',
  hunter: 'Hunter.io',
  snov: 'Snov.io',
}

export default function RecruiterCard({
  recruiter,
  index,
  onSelect,
}: {
  recruiter: Recruiter
  index: number
  onSelect: (n: string) => void
}) {
  const confidence = recruiter.confidence
  const confidenceColor =
    confidence >= 80 ? 'text-green-400' :
    confidence >= 60 ? 'text-yellow-400' :
    'text-gray-500'

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-3 flex items-start justify-between gap-3">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-0.5">
          <span className="text-xs text-gray-500 font-mono">{index + 1}</span>
          <span className="text-xs bg-gray-700 text-gray-400 px-1.5 py-0.5 rounded">
            {SOURCE_LABELS[recruiter.source] ?? recruiter.source}
          </span>
          {confidence > 0 && (
            <span className={`text-xs ${confidenceColor}`}>{confidence}% confidence</span>
          )}
        </div>
        <p className="text-white text-sm font-medium leading-snug">
          {recruiter.name || 'Unknown'}
        </p>
        {recruiter.title && (
          <p className="text-gray-400 text-xs mt-0.5">{recruiter.title}</p>
        )}
        <p className="text-indigo-300 text-xs mt-0.5 font-mono">{recruiter.email}</p>
      </div>
      <button
        onClick={() => onSelect(String(index + 1))}
        className="shrink-0 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium px-3 py-1.5 rounded transition-colors"
      >
        Select
      </button>
    </div>
  )
}

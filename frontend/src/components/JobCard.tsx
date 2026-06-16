const SOURCE_LABELS: Record<string, string> = {
  linkedin: 'LinkedIn',
  indeed: 'Indeed',
  naukri: 'Naukri',
  google_jobs: 'Google Jobs',
  glassdoor: 'Glassdoor',
  wellfound: 'Wellfound',
}

export interface Job {
  title: string
  company: string
  location: string
  url: string
  source: string
}

export default function JobCard({
  job,
  index,
  onSelect,
}: {
  job: Job
  index: number
  onSelect: (n: string) => void
}) {
  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-3 flex items-start justify-between gap-3">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-0.5">
          <span className="text-xs text-gray-500 font-mono">{index + 1}</span>
          <span className="text-xs bg-gray-700 text-gray-400 px-1.5 py-0.5 rounded">
            {SOURCE_LABELS[job.source] ?? job.source}
          </span>
        </div>
        <p className="text-white text-sm font-medium leading-snug">{job.title}</p>
        <p className="text-gray-400 text-xs mt-0.5">{job.company} · {job.location}</p>
        {job.url && (
          <a
            href={job.url}
            target="_blank"
            rel="noreferrer"
            className="text-indigo-400 text-xs hover:underline mt-1 inline-block"
          >
            View listing ↗
          </a>
        )}
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

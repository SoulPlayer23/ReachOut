import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center px-4">
      <div className="text-center">
        <p className="text-6xl font-bold text-indigo-500 mb-4">404</p>
        <h1 className="text-white text-xl font-semibold mb-2">Page not found</h1>
        <p className="text-gray-400 text-sm mb-6">The page you're looking for doesn't exist.</p>
        <Link
          to="/app/chat"
          className="bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
        >
          Go to Chat
        </Link>
      </div>
    </div>
  )
}

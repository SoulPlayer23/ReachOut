import { useState } from 'react'

export default function EmailPreview({
  subject,
  body,
  onSend,
}: {
  subject: string
  body: string
  onSend: (text: string) => void
}) {
  const [editing, setEditing] = useState(false)
  const [editedBody, setEditedBody] = useState(body)

  function handleApprove() {
    onSend('send')
  }

  function handleSubmitEdit() {
    if (editedBody.trim()) {
      onSend(editedBody.trim())
      setEditing(false)
    }
  }

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg overflow-hidden">
      {/* Subject */}
      <div className="px-4 py-2.5 border-b border-gray-700 bg-gray-800/80">
        <p className="text-xs text-gray-500 mb-0.5">Subject</p>
        <p className="text-white text-sm font-medium">{subject}</p>
      </div>

      {/* Body */}
      <div className="px-4 py-3">
        {editing ? (
          <>
            <textarea
              value={editedBody}
              onChange={e => setEditedBody(e.target.value)}
              rows={10}
              className="w-full bg-gray-900 border border-gray-600 rounded text-sm text-white p-2 focus:outline-none focus:border-indigo-500 resize-none font-mono text-xs leading-relaxed"
            />
            <div className="flex gap-2 mt-2">
              <button
                onClick={handleSubmitEdit}
                className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium px-3 py-1.5 rounded transition-colors"
              >
                Update draft
              </button>
              <button
                onClick={() => { setEditing(false); setEditedBody(body) }}
                className="border border-gray-600 hover:border-gray-500 text-gray-400 text-xs px-3 py-1.5 rounded transition-colors"
              >
                Cancel
              </button>
            </div>
          </>
        ) : (
          <p className="text-gray-200 text-sm whitespace-pre-wrap leading-relaxed">{body}</p>
        )}
      </div>

      {/* Actions */}
      {!editing && (
        <div className="px-4 py-3 border-t border-gray-700 flex gap-2">
          <button
            onClick={handleApprove}
            className="bg-green-700 hover:bg-green-600 text-white text-sm font-medium px-4 py-1.5 rounded transition-colors"
          >
            Send email ✓
          </button>
          <button
            onClick={() => setEditing(true)}
            className="border border-gray-600 hover:border-gray-500 text-gray-300 text-sm px-4 py-1.5 rounded transition-colors"
          >
            Edit
          </button>
        </div>
      )}
    </div>
  )
}

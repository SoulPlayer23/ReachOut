import { useEffect, useRef, useState, type FormEvent } from 'react'
import Markdown from 'react-markdown'
import AppLayout from '../../components/AppLayout'
import usePageTitle from '../../hooks/usePageTitle'
import EmailPreview from '../../components/EmailPreview'
import JobCard, { type Job } from '../../components/JobCard'
import RecruiterCard, { type Recruiter } from '../../components/RecruiterCard'

// ── Message types ─────────────────────────────────────────────────────────────

type UserMsg = { id: string; from: 'user'; text: string }
type AgentMsg = { id: string; from: 'agent'; event: SSEEvent }
type Msg = UserMsg | AgentMsg

type SSEEvent =
  | { type: 'text'; content: string }
  | { type: 'jobs'; items: Job[] }
  | { type: 'recruiters'; items: Recruiter[] }
  | { type: 'email_preview'; subject: string; body: string }
  | { type: 'sent'; message_id: string }
  | { type: 'error'; message: string }

function uid() {
  return Math.random().toString(36).slice(2)
}

const MD_COMPONENTS = {
  p: ({ children }: { children?: React.ReactNode }) => <p className="mb-1.5 last:mb-0 leading-relaxed">{children}</p>,
  strong: ({ children }: { children?: React.ReactNode }) => <strong className="font-semibold text-white">{children}</strong>,
  em: ({ children }: { children?: React.ReactNode }) => <em className="italic text-gray-300">{children}</em>,
  ul: ({ children }: { children?: React.ReactNode }) => <ul className="list-disc list-inside space-y-0.5 mb-1.5">{children}</ul>,
  ol: ({ children }: { children?: React.ReactNode }) => <ol className="list-decimal list-inside space-y-0.5 mb-1.5">{children}</ol>,
  li: ({ children }: { children?: React.ReactNode }) => <li className="text-gray-200">{children}</li>,
  code: ({ children }: { children?: React.ReactNode }) => <code className="bg-gray-700 text-indigo-300 px-1 py-0.5 rounded text-xs font-mono">{children}</code>,
  h1: ({ children }: { children?: React.ReactNode }) => <h1 className="font-bold text-base text-white mb-1">{children}</h1>,
  h2: ({ children }: { children?: React.ReactNode }) => <h2 className="font-semibold text-sm text-white mb-1">{children}</h2>,
  h3: ({ children }: { children?: React.ReactNode }) => <h3 className="font-semibold text-sm text-gray-200 mb-1">{children}</h3>,
}

// ── Chat page ─────────────────────────────────────────────────────────────────

export default function Chat() {
  usePageTitle('Chat')
  const [messages, setMessages] = useState<Msg[]>([
    {
      id: 'welcome',
      from: 'agent',
      event: {
        type: 'text',
        content: "Hi! I'm ReachOut. Tell me which company and role you're targeting and I'll find job openings, discover recruiter contacts, and draft a personalized cold email for you.",
      },
    },
  ])
  const [input, setInput] = useState('')
  const [streaming, setStreaming] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function sendMessage(text: string) {
    if (!text.trim() || streaming) return

    setInput('')
    setMessages(prev => [...prev, { id: uid(), from: 'user', text }])
    setStreaming(true)

    try {
      const res = await fetch('/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({ message: text }),
      })

      if (!res.ok || !res.body) {
        setMessages(prev => [
          ...prev,
          { id: uid(), from: 'agent', event: { type: 'error', message: 'Request failed.' } },
        ])
        return
      }

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() ?? ''
        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          try {
            const event: SSEEvent = JSON.parse(line.slice(6))
            setMessages(prev => [...prev, { id: uid(), from: 'agent', event }])
          } catch {
            // skip malformed line
          }
        }
      }
    } catch {
      setMessages(prev => [
        ...prev,
        { id: uid(), from: 'agent', event: { type: 'error', message: 'Connection error.' } },
      ])
    } finally {
      setStreaming(false)
    }
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    sendMessage(input)
  }

  return (
    <AppLayout>
      <div className="flex flex-col h-full">
        {/* Message list */}
        <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3">
          {messages.map(msg =>
            msg.from === 'user' ? (
              <UserBubble key={msg.id} text={msg.text} />
            ) : (
              <AgentBubble key={msg.id} event={msg.event} onSend={sendMessage} />
            )
          )}
          {streaming && <TypingIndicator />}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <form
          onSubmit={handleSubmit}
          className="border-t border-gray-800 px-4 py-3 flex gap-2 bg-gray-900/50"
        >
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            disabled={streaming}
            placeholder={streaming ? 'ReachOut is thinking…' : 'Type a message…'}
            className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500 text-sm disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={streaming || !input.trim()}
            className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            Send
          </button>
        </form>
      </div>
    </AppLayout>
  )
}

// ── Sub-components ────────────────────────────────────────────────────────────

function UserBubble({ text }: { text: string }) {
  return (
    <div className="flex justify-end">
      <div className="bg-indigo-600 text-white text-sm px-3 py-2 rounded-2xl rounded-tr-sm max-w-xs lg:max-w-md">
        {text}
      </div>
    </div>
  )
}

function AgentBubble({ event, onSend }: { event: SSEEvent; onSend: (t: string) => void }) {
  if (event.type === 'text') {
    return (
      <div className="flex justify-start">
        <div className="bg-gray-800 text-gray-100 text-sm px-3 py-2 rounded-2xl rounded-tl-sm max-w-xs lg:max-w-lg">
          <Markdown components={MD_COMPONENTS}>{event.content}</Markdown>
        </div>
      </div>
    )
  }

  if (event.type === 'jobs') {
    return (
      <div className="space-y-2 max-w-lg">
        {event.items.map((job, i) => (
          <JobCard key={i} job={job} index={i} onSelect={onSend} />
        ))}
      </div>
    )
  }

  if (event.type === 'recruiters') {
    return (
      <div className="space-y-2 max-w-lg">
        {event.items.map((rec, i) => (
          <RecruiterCard key={i} recruiter={rec} index={i} onSelect={onSend} />
        ))}
      </div>
    )
  }

  if (event.type === 'email_preview') {
    return (
      <div className="max-w-lg">
        <EmailPreview subject={event.subject} body={event.body} onSend={onSend} />
      </div>
    )
  }

  if (event.type === 'sent') {
    return (
      <div className="flex justify-start">
        <div className="bg-green-900/40 border border-green-700 text-green-300 text-sm px-3 py-2 rounded-lg max-w-xs">
          ✓ Email sent successfully!
        </div>
      </div>
    )
  }

  if (event.type === 'error') {
    return (
      <div className="flex justify-start">
        <div className="bg-red-900/30 border border-red-800 text-red-300 text-sm px-3 py-2 rounded-lg max-w-xs">
          ⚠ {event.message}
        </div>
      </div>
    )
  }

  return null
}

function TypingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="bg-gray-800 px-3 py-2.5 rounded-2xl rounded-tl-sm flex gap-1 items-center">
        {[0, 1, 2].map(i => (
          <span
            key={i}
            className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce"
            style={{ animationDelay: `${i * 0.15}s` }}
          />
        ))}
      </div>
    </div>
  )
}

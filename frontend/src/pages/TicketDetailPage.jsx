import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import PriorityBadge from '../components/PriorityBadge.jsx'
import StatusBadge from '../components/StatusBadge.jsx'
import { getTicket, updateTicket } from '../services/api.js'

const dateTimeFormatter = new Intl.DateTimeFormat(undefined, {
  month: 'short',
  day: 'numeric',
  year: 'numeric',
  hour: 'numeric',
  minute: '2-digit',
})

function formatDateTime(value) {
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? '—' : dateTimeFormatter.format(date)
}

function TicketDetailPage() {
  const { ticketId } = useParams()
  const [ticket, setTicket] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [notFound, setNotFound] = useState(false)
  const [error, setError] = useState('')
  const [retryKey, setRetryKey] = useState(0)
  const [statusDraft, setStatusDraft] = useState('')
  const [isStatusSaving, setIsStatusSaving] = useState(false)
  const [statusFeedback, setStatusFeedback] = useState(null)
  const [noteText, setNoteText] = useState('')
  const [isNoteSaving, setIsNoteSaving] = useState(false)
  const [noteFeedback, setNoteFeedback] = useState(null)

  useEffect(() => {
    const controller = new AbortController()
    let isActive = true

    async function loadTicket() {
      setIsLoading(true)
      setNotFound(false)
      setError('')

      try {
        const data = await getTicket(ticketId, { signal: controller.signal })
        if (isActive) {
          setTicket(data)
          setStatusDraft(data.status)
        }
      } catch (requestError) {
        if (!isActive) return

        setTicket(null)
        if (requestError.response?.status === 404) {
          setNotFound(true)
        } else {
          setError('Unable to load this ticket. Check the API and try again.')
        }
      } finally {
        if (isActive) setIsLoading(false)
      }
    }

    loadTicket()
    return () => {
      isActive = false
      controller.abort()
    }
  }, [ticketId, retryKey])

  const isUpdating = isStatusSaving || isNoteSaving

  async function handleStatusSubmit(event) {
    event.preventDefault()
    if (!ticket || statusDraft === ticket.status || isUpdating) return

    setIsStatusSaving(true)
    setStatusFeedback(null)

    try {
      const response = await updateTicket(ticketId, { status: statusDraft })
      setTicket(response.ticket)
      setStatusDraft(response.ticket.status)
      setStatusFeedback({
        type: 'success',
        message: `Status updated to ${response.ticket.status}.`,
      })
    } catch {
      setStatusFeedback({
        type: 'error',
        message: 'Unable to update status. Please try again.',
      })
    } finally {
      setIsStatusSaving(false)
    }
  }

  async function handleNoteSubmit(event) {
    event.preventDefault()
    if (!ticket || isUpdating) return

    const trimmedNote = noteText.trim()
    if (!trimmedNote) {
      setNoteFeedback({
        type: 'error',
        message: 'Note cannot be blank.',
      })
      return
    }
    if (trimmedNote.length < 2) {
      setNoteFeedback({
        type: 'error',
        message: 'Note must be at least 2 characters.',
      })
      return
    }
    if (trimmedNote.length > 2000) {
      setNoteFeedback({
        type: 'error',
        message: 'Note must be 2000 characters or fewer.',
      })
      return
    }

    setIsNoteSaving(true)
    setNoteFeedback(null)

    try {
      const response = await updateTicket(ticketId, {
        note_text: trimmedNote,
      })
      setTicket(response.ticket)
      setStatusDraft(response.ticket.status)
      setNoteText('')
      setNoteFeedback({
        type: 'success',
        message: 'Note added successfully.',
      })
    } catch {
      setNoteFeedback({
        type: 'error',
        message: 'Unable to add note. Your text has been preserved.',
      })
    } finally {
      setIsNoteSaving(false)
    }
  }

  if (isLoading) {
    return <TicketDetailSkeleton />
  }

  if (notFound) {
    return (
      <DetailState
        icon="?"
        title="Ticket not found"
        description="This ticket may have been removed, or the ticket ID may be incorrect."
      />
    )
  }

  if (error) {
    return (
      <DetailState
        icon="!"
        title="Ticket could not be loaded"
        description={error}
        action={
          <button
            className="button button-dark"
            type="button"
            onClick={() => setRetryKey((value) => value + 1)}
          >
            Retry
          </button>
        }
      />
    )
  }

  if (!ticket) return null

  const priorityTone = ticket.priority.toLowerCase()
  const reasons = Array.isArray(ticket.priority_reasons)
    ? ticket.priority_reasons
    : []
  const notes = Array.isArray(ticket.notes) ? ticket.notes : []

  return (
    <article className="ticket-detail-page">
      <div className="detail-layout">
        <div className="detail-main-column">
          <header className="detail-header detail-widget">
            <Link className="back-link" to="/tickets">
              <span aria-hidden="true">←</span>
              Back to Tickets
            </Link>
            <div className="detail-id-line">
              <span className="ticket-id">{ticket.ticket_id}</span>
              <StatusBadge status={ticket.status} />
            </div>
            <h2>{ticket.subject}</h2>
            <p>Customer support request details and automatic triage context.</p>
          </header>

          <section className="detail-card description-card">
            <div className="detail-card-header">
              <span className="detail-card-index">01</span>
              <div>
                <span className="section-kicker">Customer request</span>
                <h3>Full description</h3>
              </div>
            </div>
            <p className="ticket-description">{ticket.description}</p>
          </section>

          <section className="detail-card notes-card">
            <div className="detail-card-header notes-header">
              <div className="notes-title">
                <span className="detail-card-index">02</span>
                <div>
                  <span className="section-kicker">Internal context</span>
                  <h3>Notes</h3>
                </div>
              </div>
              <span className="notes-count">
                {notes.length} {notes.length === 1 ? 'note' : 'notes'}
              </span>
            </div>

            <div
              className="notes-content-scroll"
              aria-label="Notes and add note form"
              role="region"
              tabIndex="0"
            >
              <div className="notes-scroll-area">
                {notes.length === 0 ? (
                  <div className="empty-notes">
                    <span aria-hidden="true">⌁</span>
                    <p>No notes have been added yet.</p>
                  </div>
                ) : (
                  <ol className="notes-list">
                    {notes.map((note, index) => (
                      <li key={note.id}>
                        <span className="note-number" aria-hidden="true">
                          {String(index + 1).padStart(2, '0')}
                        </span>
                        <div>
                          <p>{note.note_text}</p>
                          <time dateTime={note.created_at}>
                            {formatDateTime(note.created_at)}
                          </time>
                        </div>
                      </li>
                    ))}
                  </ol>
                )}
              </div>

              <form className="note-form" onSubmit={handleNoteSubmit} noValidate>
                <div className="note-form-heading">
                  <label htmlFor="note_text">Add an internal note</label>
                  <span>{noteText.length} / 2000</span>
                </div>
                <textarea
                  id="note_text"
                  name="note_text"
                  value={noteText}
                  onChange={(event) => {
                    setNoteText(event.target.value)
                    setNoteFeedback(null)
                  }}
                  placeholder="Add context for the next support agent..."
                  rows="4"
                  maxLength="2000"
                  disabled={isNoteSaving}
                  aria-invalid={noteFeedback?.type === 'error'}
                />
                <div className="update-form-footer">
                  <FeedbackMessage feedback={noteFeedback} />
                  <button
                    className="button button-dark compact-button"
                    type="submit"
                    disabled={isUpdating}
                  >
                    {isNoteSaving ? 'Adding note…' : 'Add Note'}
                  </button>
                </div>
              </form>
            </div>
          </section>
        </div>

        <aside className="detail-side-column">
          <section
            className={`detail-priority-card detail-priority-${priorityTone}`}
          >
            <div className="detail-priority-heading">
              <div>
                <span>Automatic triage</span>
                <h3>{ticket.category}</h3>
              </div>
              <PriorityBadge priority={ticket.priority} />
            </div>

            <div className="detail-score">
              <div>
                <span>Priority score</span>
                <strong>
                  {ticket.priority_score}
                  <small>/100</small>
                </strong>
              </div>
              <div
                className="detail-score-track"
                role="progressbar"
                aria-label="Priority score"
                aria-valuemin="0"
                aria-valuemax="100"
                aria-valuenow={ticket.priority_score}
              >
                <span style={{ width: `${ticket.priority_score}%` }} />
              </div>
            </div>

            <div className="detail-reasons">
              <span>Why this priority</span>
              {reasons.length === 0 ? (
                <p className="empty-reasons">No priority reasons available.</p>
              ) : (
                <ul>
                  {reasons.map((reason, index) => (
                    <li key={`${reason}-${index}`}>
                      <span aria-hidden="true">
                        {String(index + 1).padStart(2, '0')}
                      </span>
                      {reason}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </section>

          <section className="detail-card customer-card">
            <div className="detail-card-header">
              <span className="detail-card-index">03</span>
              <div>
                <span className="section-kicker">Requester</span>
                <h3>Customer</h3>
              </div>
            </div>
            <dl className="customer-details">
              <div>
                <dt>Name</dt>
                <dd>{ticket.customer_name}</dd>
              </div>
              <div>
                <dt>Email</dt>
                <dd>
                  <a href={`mailto:${ticket.customer_email}`}>
                    {ticket.customer_email}
                  </a>
                </dd>
              </div>
            </dl>
          </section>

          <section
            className="detail-card ticket-info-card"
            aria-label="Ticket information and status controls"
            role="region"
            tabIndex="0"
          >
            <div className="detail-card-header">
              <span className="detail-card-index">04</span>
              <div>
                <span className="section-kicker">At a glance</span>
                <h3>Ticket information</h3>
              </div>
            </div>
            <dl>
              <div>
                <dt>Status</dt>
                <dd><StatusBadge status={ticket.status} /></dd>
              </div>
              <div>
                <dt>Category</dt>
                <dd>{ticket.category}</dd>
              </div>
              <div>
                <dt>Created</dt>
                <dd>{formatDateTime(ticket.created_at)}</dd>
              </div>
              <div>
                <dt>Last updated</dt>
                <dd>{formatDateTime(ticket.updated_at)}</dd>
              </div>
            </dl>

            <form
              className="status-update-form"
              onSubmit={handleStatusSubmit}
            >
              <label htmlFor="ticket-status">Update status</label>
              <div className="status-update-controls">
                <select
                  id="ticket-status"
                  value={statusDraft}
                  onChange={(event) => {
                    setStatusDraft(event.target.value)
                    setStatusFeedback(null)
                  }}
                  disabled={isStatusSaving}
                >
                  <option value="Open">Open</option>
                  <option value="In Progress">In Progress</option>
                  <option value="Closed">Closed</option>
                </select>
                <button
                  className="button button-dark compact-button"
                  type="submit"
                  disabled={
                    statusDraft === ticket.status || isUpdating
                  }
                >
                  {isStatusSaving ? 'Saving…' : 'Save'}
                </button>
              </div>
              <FeedbackMessage feedback={statusFeedback} />
            </form>
          </section>
        </aside>
      </div>
    </article>
  )
}

function FeedbackMessage({ feedback }) {
  if (!feedback) return null

  return (
    <p
      className={`update-feedback feedback-${feedback.type}`}
      role={feedback.type === 'error' ? 'alert' : 'status'}
    >
      <span aria-hidden="true">{feedback.type === 'error' ? '!' : '✓'}</span>
      {feedback.message}
    </p>
  )
}

function DetailState({ icon, title, description, action }) {
  return (
    <section className="detail-state">
      <span className="state-icon" aria-hidden="true">{icon}</span>
      <h2>{title}</h2>
      <p>{description}</p>
      <div className="detail-state-actions">
        {action}
        <Link className="button button-ghost-on-light" to="/tickets">
          Back to Tickets
        </Link>
      </div>
    </section>
  )
}

function TicketDetailSkeleton() {
  return (
    <div className="detail-skeleton" aria-label="Loading ticket details" aria-busy="true">
      <span className="detail-skeleton-back" />
      <span className="detail-skeleton-title" />
      <span className="detail-skeleton-subtitle" />
      <div className="detail-skeleton-grid">
        <span />
        <span />
        <span />
      </div>
    </div>
  )
}

export default TicketDetailPage

import { useNavigate } from 'react-router-dom'

import PriorityBadge from './PriorityBadge.jsx'
import StatusBadge from './StatusBadge.jsx'

const dateFormatter = new Intl.DateTimeFormat(undefined, {
  month: 'short',
  day: 'numeric',
  year: 'numeric',
})

function formatDate(value) {
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? '—' : dateFormatter.format(date)
}

function TicketTable({ tickets }) {
  const navigate = useNavigate()

  function openTicket(ticketId) {
    navigate(`/tickets/${encodeURIComponent(ticketId)}`)
  }

  function handleKeyDown(event, ticketId) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      openTicket(ticketId)
    }
  }

  return (
    <>
      <div className="ticket-table-wrap">
        <table className="ticket-table">
          <thead>
            <tr>
              <th>Ticket ID</th>
              <th>Customer</th>
              <th>Subject</th>
              <th>Category</th>
              <th>Priority</th>
              <th>Status</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            {tickets.map((ticket) => (
              <tr
                key={ticket.ticket_id}
                role="link"
                tabIndex="0"
                aria-label={`Open ticket ${ticket.ticket_id}: ${ticket.subject}`}
                onClick={() => openTicket(ticket.ticket_id)}
                onKeyDown={(event) => handleKeyDown(event, ticket.ticket_id)}
              >
                <td>
                  <span className="ticket-id">{ticket.ticket_id}</span>
                </td>
                <td>
                  <div className="customer-cell">
                    <span className="customer-avatar" aria-hidden="true">
                      {ticket.customer_name.charAt(0).toUpperCase()}
                    </span>
                    <span>
                      <strong>{ticket.customer_name}</strong>
                      <small>{ticket.customer_email}</small>
                    </span>
                  </div>
                </td>
                <td>
                  <span className="ticket-subject">{ticket.subject}</span>
                </td>
                <td>
                  <span className="category-label">{ticket.category}</span>
                </td>
                <td>
                  <div className="priority-cell">
                    <PriorityBadge priority={ticket.priority} />
                    <small>{ticket.priority_score} / 100</small>
                  </div>
                </td>
                <td>
                  <StatusBadge status={ticket.status} />
                </td>
                <td>
                  <time dateTime={ticket.created_at}>{formatDate(ticket.created_at)}</time>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="ticket-card-list">
        {tickets.map((ticket) => (
          <article
            className="ticket-mobile-card"
            key={ticket.ticket_id}
            role="link"
            tabIndex="0"
            aria-label={`Open ticket ${ticket.ticket_id}: ${ticket.subject}`}
            onClick={() => openTicket(ticket.ticket_id)}
            onKeyDown={(event) => handleKeyDown(event, ticket.ticket_id)}
          >
            <div className="mobile-ticket-top">
              <span className="ticket-id">{ticket.ticket_id}</span>
              <StatusBadge status={ticket.status} />
            </div>
            <h3>{ticket.subject}</h3>
            <div className="mobile-customer">
              <strong>{ticket.customer_name}</strong>
              <small>{ticket.customer_email}</small>
            </div>
            <div className="mobile-ticket-footer">
              <div className="priority-cell">
                <PriorityBadge priority={ticket.priority} />
                <small>{ticket.priority_score} / 100</small>
              </div>
              <time dateTime={ticket.created_at}>{formatDate(ticket.created_at)}</time>
            </div>
          </article>
        ))}
      </div>
    </>
  )
}

export default TicketTable

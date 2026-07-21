import { Link } from 'react-router-dom'

function Topbar() {
  return (
    <header className="topbar">
      <div>
        <p className="eyebrow">ResolveIQ / Tickets</p>
        <h1>Support Workspace</h1>
        <p className="topbar-subtitle">Create, triage and resolve customer requests.</p>
      </div>

      <div className="topbar-actions">
        <button className="icon-button" type="button" aria-label="Search tickets">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <circle cx="11" cy="11" r="6.5" />
            <path d="m16 16 4 4" />
          </svg>
        </button>
        <Link className="button button-dark topbar-create" to="/tickets/new">
          <span aria-hidden="true">+</span> Create Ticket
        </Link>
        <div className="avatar" aria-label="Signed in as Support Agent">SA</div>
      </div>
    </header>
  )
}

export default Topbar

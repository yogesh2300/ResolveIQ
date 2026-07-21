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
        <Link className="button button-dark topbar-create" to="/tickets/new">
          <span aria-hidden="true">+</span> Create Ticket
        </Link>
      </div>
    </header>
  )
}

export default Topbar

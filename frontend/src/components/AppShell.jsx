import { useEffect, useState } from 'react'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'

import Sidebar from './Sidebar.jsx'
import Topbar from './Topbar.jsx'

function AppShell() {
  const location = useLocation()
  const navigate = useNavigate()
  const [ticketCreatedToast, setTicketCreatedToast] = useState(null)

  useEffect(() => {
    const ticketCreated = location.state?.ticketCreated
    if (!ticketCreated) return

    setTicketCreatedToast(ticketCreated)
    navigate(`${location.pathname}${location.search}${location.hash}`, {
      replace: true,
      state: null,
    })
  }, [
    location.hash,
    location.pathname,
    location.search,
    location.state,
    navigate,
  ])

  useEffect(() => {
    if (!ticketCreatedToast) return undefined

    const timeout = window.setTimeout(() => {
      setTicketCreatedToast(null)
    }, 5000)

    return () => window.clearTimeout(timeout)
  }, [ticketCreatedToast])

  return (
    <div className="app-frame">
      {ticketCreatedToast ? (
        <div className="ticket-created-toast" role="status" aria-live="polite">
          <span className="toast-success-icon" aria-hidden="true">✓</span>
          <div>
            <strong>Ticket Created Successfully</strong>
            <span>Ticket ID: {ticketCreatedToast.ticketId}</span>
            <span>Severity: {ticketCreatedToast.severity}</span>
          </div>
        </div>
      ) : null}

      <div className="app-shell">
        <Sidebar />
        <div className="app-main">
          <Topbar />
          <main className="page-content">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  )
}

export default AppShell

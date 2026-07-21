import { Link, useLocation } from 'react-router-dom'

const navItems = [
  { label: 'Workspace', icon: '▦', section: true },
  { label: 'Tickets', icon: '▦', to: '/tickets', end: true },
  { label: 'Create Ticket', icon: '+', to: '/tickets/new' },
  { label: 'Open', icon: '○', to: '/tickets/open' },
  { label: 'In Progress', icon: '◐', to: '/tickets/in-progress' },
  { label: 'Closed', icon: '●', to: '/tickets/closed' },
]

function Sidebar() {
  const { pathname } = useLocation()
  const fixedStatusPaths = new Set([
    '/tickets/open',
    '/tickets/in-progress',
    '/tickets/closed',
  ])

  return (
    <aside className="sidebar" aria-label="Primary navigation">
      <div className="brand">
        <span className="brand-mark" aria-hidden="true">R</span>
        <span>ResolveIQ</span>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => {
          if (item.section) {
            return (
              <div className="nav-section-label" key={item.label}>
                <span aria-hidden="true">{item.icon}</span>
                {item.label}
              </div>
            )
          }

          const isActive = item.to === '/tickets'
            ? pathname === '/tickets'
              || (
                pathname.startsWith('/tickets/')
                && pathname !== '/tickets/new'
                && !fixedStatusPaths.has(pathname)
              )
            : pathname === item.to

          return (
            <Link
              aria-current={isActive ? 'page' : undefined}
              className={`nav-item${isActive ? ' active' : ''}`}
              key={item.label}
              to={item.to}
            >
              <span className="nav-icon" aria-hidden="true">{item.icon}</span>
              {item.label}
            </Link>
          )
        })}
      </nav>

      <div className="sidebar-footer">
        <span className="system-dot" aria-hidden="true" />
        All systems operational
      </div>
    </aside>
  )
}

export default Sidebar

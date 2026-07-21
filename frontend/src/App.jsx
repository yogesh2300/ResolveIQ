import { Navigate, Route, Routes } from 'react-router-dom'

import AppShell from './components/AppShell.jsx'
import CreateTicketPage from './pages/CreateTicketPage.jsx'
import TicketDetailPage from './pages/TicketDetailPage.jsx'
import TicketListPage from './pages/TicketListPage.jsx'

function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<Navigate to="/tickets" replace />} />
        <Route path="tickets" element={<TicketListPage />} />
        <Route path="tickets/open" element={<TicketListPage fixedStatus="Open" />} />
        <Route
          path="tickets/in-progress"
          element={<TicketListPage fixedStatus="In Progress" />}
        />
        <Route path="tickets/closed" element={<TicketListPage fixedStatus="Closed" />} />
        <Route path="tickets/new" element={<CreateTicketPage />} />
        <Route path="tickets/:ticketId" element={<TicketDetailPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/tickets" replace />} />
    </Routes>
  )
}

export default App

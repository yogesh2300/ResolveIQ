import { useEffect, useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'

import SearchFilters from '../components/SearchFilters.jsx'
import TicketTable from '../components/TicketTable.jsx'
import { getTickets } from '../services/api.js'

function TicketListPage({ fixedStatus = null }) {
  const [searchParams, setSearchParams] = useSearchParams()
  const [tickets, setTickets] = useState([])
  const [search, setSearch] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')
  const [priorityFilter, setPriorityFilter] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [retryKey, setRetryKey] = useState(0)
  const latestRequest = useRef(0)
  const statusFilter = fixedStatus ?? searchParams.get('status') ?? ''
  const pageTitle = fixedStatus ? `${fixedStatus} Tickets` : 'Support Tickets'

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setDebouncedSearch(search.trim())
    }, 300)

    return () => window.clearTimeout(timer)
  }, [search])

  useEffect(() => {
    const requestId = latestRequest.current + 1
    latestRequest.current = requestId
    const controller = new AbortController()
    let isActive = true

    async function loadTickets() {
      setIsLoading(true)
      setError('')

      try {
        const data = await getTickets({
          search: debouncedSearch,
          status: statusFilter,
          priority: priorityFilter,
        }, {
          signal: controller.signal,
        })

        if (isActive && requestId === latestRequest.current) {
          setTickets(data)
        }
      } catch {
        if (isActive && requestId === latestRequest.current) {
          setError('Unable to load support tickets. Check the API and try again.')
        }
      } finally {
        if (isActive && requestId === latestRequest.current) {
          setIsLoading(false)
        }
      }
    }

    loadTickets()
    return () => {
      isActive = false
      controller.abort()
    }
  }, [debouncedSearch, statusFilter, priorityFilter, retryKey])

  function clearFilters() {
    setSearch('')
    setDebouncedSearch('')
    setPriorityFilter('')
    if (fixedStatus === null) {
      setSearchParams({})
    }
  }

  function handleStatusChange(status) {
    setSearchParams(status ? { status } : {})
  }

  const hasActiveFilters = Boolean(
    search.trim() || statusFilter || priorityFilter,
  )

  return (
    <section className="ticket-list-page" aria-labelledby="ticket-list-title">
      <div className="list-page-heading">
        <div>
          <span className="section-kicker">Ticket operations</span>
          <h2 id="ticket-list-title">{pageTitle}</h2>
          <p>Review, search, and prioritize customer requests.</p>
        </div>
      </div>

      <SearchFilters
        search={search}
        status={statusFilter}
        priority={priorityFilter}
        onSearchChange={setSearch}
        onStatusChange={handleStatusChange}
        onPriorityChange={setPriorityFilter}
        onClear={clearFilters}
        fixedStatus={fixedStatus}
      />

      <div className="ticket-list-card">
        <div className="list-card-header">
          <div>
            <span className="list-card-mark" aria-hidden="true">▦</span>
            <div>
              <h3>Ticket queue</h3>
              <p>
                {isLoading
                  ? 'Loading customer requests…'
                  : `${tickets.length} ${tickets.length === 1 ? 'ticket' : 'tickets'} shown`}
              </p>
            </div>
          </div>
          <span className="sort-label">Newest first</span>
        </div>

        {isLoading ? (
          <TicketListSkeleton />
        ) : error ? (
          <div className="list-state" role="alert">
            <span className="state-icon" aria-hidden="true">!</span>
            <h3>Tickets could not be loaded</h3>
            <p>{error}</p>
            <button
              className="button button-dark"
              type="button"
              onClick={() => setRetryKey((value) => value + 1)}
            >
              Retry
            </button>
          </div>
        ) : tickets.length === 0 ? (
          <div className="list-state">
            <span className="state-icon" aria-hidden="true">⌁</span>
            <h3>
              {hasActiveFilters
                ? 'No tickets match your current filters.'
                : 'No tickets have been created yet.'}
            </h3>
            <p>
              {hasActiveFilters
                ? 'Try changing your search or clearing the selected filters.'
                : 'Create the first support request to start your ticket queue.'}
            </p>
            {hasActiveFilters ? (
              <button className="button button-dark" type="button" onClick={clearFilters}>
                Clear Filters
              </button>
            ) : (
              <Link className="button button-dark" to="/tickets/new">
                Create Ticket
              </Link>
            )}
          </div>
        ) : (
          <TicketTable tickets={tickets} />
        )}
      </div>
    </section>
  )
}

function TicketListSkeleton() {
  return (
    <div className="ticket-skeleton" aria-label="Loading tickets" aria-busy="true">
      {Array.from({ length: 6 }, (_, index) => (
        <div className="skeleton-row" key={index}>
          <span />
          <span />
          <span />
          <span />
          <span />
        </div>
      ))}
    </div>
  )
}

export default TicketListPage

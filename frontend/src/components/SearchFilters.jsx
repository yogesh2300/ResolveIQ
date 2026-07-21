function SearchFilters({
  search,
  status,
  priority,
  onSearchChange,
  onStatusChange,
  onPriorityChange,
  onClear,
  fixedStatus = null,
}) {
  const showStatusFilter = fixedStatus === null
  const hasFilters = Boolean(search || (showStatusFilter && status) || priority)

  return (
    <div
      className={`search-filters${showStatusFilter ? '' : ' search-filters--fixed-status'}`}
      aria-label="Ticket filters"
    >
      <div className="ticket-search">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <circle cx="11" cy="11" r="6.5" />
          <path d="m16 16 4 4" />
        </svg>
        <label className="sr-only" htmlFor="ticket-search">
          Search tickets
        </label>
        <input
          id="ticket-search"
          type="search"
          value={search}
          onChange={(event) => onSearchChange(event.target.value)}
          placeholder="Search by ID, customer, email, subject, or description"
        />
      </div>

      {showStatusFilter ? (
        <label className="filter-select">
          <span className="sr-only">Filter by status</span>
          <select
            value={status}
            onChange={(event) => onStatusChange(event.target.value)}
          >
            <option value="">All Statuses</option>
            <option value="Open">Open</option>
            <option value="In Progress">In Progress</option>
            <option value="Closed">Closed</option>
          </select>
        </label>
      ) : null}

      <label className="filter-select">
        <span className="sr-only">Filter by priority</span>
        <select
          value={priority}
          onChange={(event) => onPriorityChange(event.target.value)}
        >
          <option value="">All Priorities</option>
          <option value="Low">Low</option>
          <option value="Medium">Medium</option>
          <option value="High">High</option>
          <option value="Critical">Critical</option>
        </select>
      </label>

      <button
        className="clear-filters"
        type="button"
        onClick={onClear}
        disabled={!hasFilters}
      >
        Clear Filters
      </button>
    </div>
  )
}

export default SearchFilters

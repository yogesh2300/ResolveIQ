function StatusBadge({ status }) {
  const tone = status?.toLowerCase().replace(/\s+/g, '-') || 'open'

  return (
    <span className={`status-badge status-${tone}`}>
      <span className="status-dot" aria-hidden="true" />
      {status}
    </span>
  )
}

export default StatusBadge

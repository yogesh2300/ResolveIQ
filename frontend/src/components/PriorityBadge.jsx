function PriorityBadge({ priority }) {
  const level = priority?.toLowerCase() || 'low'

  return (
    <span className={`priority-badge priority-${level}`}>
      <span className="priority-dot" aria-hidden="true" />
      {priority}
    </span>
  )
}

export default PriorityBadge

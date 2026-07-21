import axios from 'axios'

const baseURL = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export async function getTickets({ search, status, priority }, config = {}) {
  const params = {}
  const normalizedSearch = search?.trim()

  if (normalizedSearch) params.search = normalizedSearch
  if (status) params.status = status
  if (priority) params.priority = priority

  const response = await api.get('/api/tickets', { ...config, params })
  return response.data
}

export async function getTicket(ticketId, config = {}) {
  const response = await api.get(
    `/api/tickets/${encodeURIComponent(ticketId)}`,
    config,
  )
  return response.data
}

export async function updateTicket(ticketId, payload) {
  const cleanedPayload = {}
  const status = payload.status?.trim()
  const noteText = payload.note_text?.trim()

  if (status) cleanedPayload.status = status
  if (noteText) cleanedPayload.note_text = noteText

  const response = await api.put(
    `/api/tickets/${encodeURIComponent(ticketId)}`,
    cleanedPayload,
  )
  return response.data
}

export default api

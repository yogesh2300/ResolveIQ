import { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import api from '../services/api.js'

const initialForm = {
  customer_name: '',
  customer_email: '',
  subject: '',
  description: '',
}

const fieldLabels = {
  customer_name: 'Customer name',
  customer_email: 'Customer email',
  subject: 'Subject',
  description: 'Description',
}

function validateForm(values) {
  const errors = {}

  if (!values.customer_name) {
    errors.customer_name = 'Customer name is required.'
  } else if (values.customer_name.length < 2) {
    errors.customer_name = 'Customer name must be at least 2 characters.'
  }

  if (!values.customer_email) {
    errors.customer_email = 'Customer email is required.'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.customer_email)) {
    errors.customer_email = 'Enter a valid email address.'
  }

  if (!values.subject) {
    errors.subject = 'Subject is required.'
  } else if (values.subject.length < 3) {
    errors.subject = 'Subject must be at least 3 characters.'
  }

  if (!values.description) {
    errors.description = 'Description is required.'
  } else if (values.description.length < 10) {
    errors.description = 'Description must be at least 10 characters.'
  }

  return errors
}

function mapValidationErrors(detail) {
  if (!Array.isArray(detail)) return {}

  return detail.reduce((errors, item) => {
    const field = item.loc?.at(-1)
    if (fieldLabels[field] && !errors[field]) {
      errors[field] = item.msg || `${fieldLabels[field]} is invalid.`
    }
    return errors
  }, {})
}

function CreateTicketPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState(initialForm)
  const [errors, setErrors] = useState({})
  const [apiError, setApiError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const submissionLock = useRef(false)

  function handleChange(event) {
    const { name, value } = event.target
    setForm((current) => ({ ...current, [name]: value }))
    setErrors((current) => ({ ...current, [name]: undefined }))
    setApiError('')
  }

  async function handleSubmit(event) {
    event.preventDefault()
    if (submissionLock.current) return

    const payload = Object.fromEntries(
      Object.entries(form).map(([key, value]) => [key, value.trim()]),
    )
    const nextErrors = validateForm(payload)

    if (Object.keys(nextErrors).length > 0) {
      setErrors(nextErrors)
      return
    }

    setErrors({})
    setApiError('')
    submissionLock.current = true
    setIsSubmitting(true)

    try {
      const response = await api.post('/api/tickets', payload)
      navigate(`/tickets/${encodeURIComponent(response.data.ticket_id)}`, {
        state: {
          ticketCreated: {
            ticketId: response.data.ticket_id,
            severity: response.data.priority,
          },
        },
      })
    } catch (error) {
      submissionLock.current = false
      setIsSubmitting(false)

      if (error.response?.status === 422) {
        const validationErrors = mapValidationErrors(error.response.data?.detail)
        setErrors(validationErrors)
        setApiError(
          Object.keys(validationErrors).length
            ? 'Please review the highlighted fields.'
            : 'The submitted ticket could not be validated.',
        )
      } else if (!error.response) {
        setApiError('Unable to reach ResolveIQ. Check the API server and try again.')
      } else {
        setApiError('Unable to create the ticket right now. Please try again.')
      }
    }
  }

  return (
    <section className="create-ticket-page" aria-labelledby="create-ticket-title">
      <div className="page-heading">
        <div>
          <span className="section-kicker">New request</span>
          <h2 id="create-ticket-title">Create a support ticket</h2>
          <p>Capture the customer request. ResolveIQ handles the first triage pass.</p>
        </div>
        <span className="step-indicator">01 / Intake</span>
      </div>

      <div className="create-grid">
        <form className="form-card" onSubmit={handleSubmit} noValidate>
          <div className="card-header">
            <div>
              <span className="card-index">01</span>
              <h3>Customer request</h3>
            </div>
            <span className="required-note">All fields required</span>
          </div>

          <div className="form-fields-scroll">
            {apiError && (
              <div className="form-alert" role="alert">
                <span aria-hidden="true">!</span>
                {apiError}
              </div>
            )}

            <div className="form-row">
              <div className="field-group">
              <label htmlFor="customer_name">Customer name</label>
              <input
                id="customer_name"
                name="customer_name"
                type="text"
                value={form.customer_name}
                onChange={handleChange}
                disabled={isSubmitting}
                placeholder="e.g. Jordan Lee"
                autoComplete="name"
                aria-invalid={Boolean(errors.customer_name)}
                aria-describedby={errors.customer_name ? 'customer-name-error' : undefined}
              />
                <FieldError
                  error={errors.customer_name}
                  id="customer-name-error"
                />
              </div>

              <div className="field-group">
              <label htmlFor="customer_email">Customer email</label>
              <input
                id="customer_email"
                name="customer_email"
                type="email"
                value={form.customer_email}
                onChange={handleChange}
                disabled={isSubmitting}
                placeholder="name@company.com"
                autoComplete="email"
                aria-invalid={Boolean(errors.customer_email)}
                aria-describedby={errors.customer_email ? 'customer-email-error' : undefined}
              />
                <FieldError
                  error={errors.customer_email}
                  id="customer-email-error"
                />
              </div>
            </div>

            <div className="field-group">
              <label htmlFor="subject">Subject</label>
              <input
                id="subject"
                name="subject"
                type="text"
                value={form.subject}
                onChange={handleChange}
                disabled={isSubmitting}
                placeholder="A concise summary of the issue"
                aria-invalid={Boolean(errors.subject)}
                aria-describedby={errors.subject ? 'subject-error' : undefined}
              />
              <FieldError error={errors.subject} id="subject-error" />
            </div>

            <div className="field-group description-field">
              <div className="label-row">
                <label htmlFor="description">Description</label>
                <span>{form.description.length} / 5000</span>
              </div>
              <textarea
                id="description"
                name="description"
                value={form.description}
                onChange={handleChange}
                disabled={isSubmitting}
                placeholder="Describe what happened, when it started, and the impact on the customer..."
                rows="7"
                maxLength="5000"
                aria-invalid={Boolean(errors.description)}
                aria-describedby={errors.description ? 'description-error' : undefined}
              />
              <FieldError
                error={errors.description}
                id="description-error"
              />
            </div>
          </div>

          <div className="form-footer">
            <p>
              <span className="privacy-mark" aria-hidden="true">⌁</span>
              Customer data is used only to resolve this request.
            </p>
            <button className="button button-dark submit-button" type="submit" disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <span className="submit-spinner" aria-hidden="true" />
                  Creating Ticket...
                </>
              ) : (
                <>
                  Create &amp; Triage Ticket
                  <span aria-hidden="true">↗</span>
                </>
              )}
            </button>
          </div>
        </form>

        <aside className="triage-column" aria-live="polite">
          <WorkflowPreview />
        </aside>
      </div>
    </section>
  )
}

function FieldError({ error, id }) {
  return (
    <span
      className={`field-error${error ? '' : ' field-error-placeholder'}`}
      id={error ? id : undefined}
      aria-hidden={!error}
    >
      {error || '\u00A0'}
    </span>
  )
}

function WorkflowPreview() {
  return (
    <div className="triage-card triage-preview">
      <div className="triage-orbit" aria-hidden="true">
        <span>RI</span>
      </div>
      <span className="section-kicker section-kicker-inverse">Request processing</span>
      <h3>Resolution Workflow</h3>

      <div className="workflow-list">
        <WorkflowRow label="Severity">Pending</WorkflowRow>
        <WorkflowRow label="Support Queue">Pending</WorkflowRow>
        <WorkflowRow label="Response SLA">Pending</WorkflowRow>
        <WorkflowRow label="Ticket Status">Open</WorkflowRow>
      </div>

      <p className="workflow-description">
        ResolveIQ automatically evaluates each request after submission using internal business
        rules and explainable AI. Classification and routing occur securely in the background.
      </p>
    </div>
  )
}

function WorkflowRow({ label, children }) {
  return (
    <div className="workflow-row">
      <span>{label}</span>
      <strong>{children}</strong>
    </div>
  )
}

export default CreateTicketPage

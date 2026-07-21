# ResolveIQ Frontend

ResolveIQ is an explainable customer-support ticket triage CRM. This React
frontend provides ticket creation, searchable ticket lists, ticket details,
status updates, and internal notes.

## Setup

From the `frontend` directory:

```bash
npm install
npm run dev
```

The development server is available at `http://localhost:5173`.

Set the optional API base URL in `frontend/.env`:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Without this variable, the frontend uses `http://127.0.0.1:8000`.

## Commands

```bash
npm run lint
npm run build
npm run preview
```

## Architecture

- `src/components/` contains the application shell and reusable UI.
- `src/pages/` contains ticket creation, list, and detail screens.
- `src/services/api.js` centralizes requests to the ResolveIQ API.
- `src/index.css` contains the responsive widget-based visual system.

The frontend uses React, React Router, Axios, Vite, and plain CSS.

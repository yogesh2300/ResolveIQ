# ResolveIQ

ResolveIQ is a customer support ticket management system that automatically categorizes and prioritizes support tickets based on their content. It helps support teams organize customer requests and respond more efficiently.

## Features

- Create support tickets
- Automatic ticket categorization
- Automatic priority assignment
- Search tickets
- Filter by status and priority
- View ticket details
- Update ticket status
- Add internal notes
- Responsive dashboard UI

## Tech Stack

### Frontend
- React
- Vite
- Axios

### Backend
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic

## Project Structure

```
ResolveIQ/
│
├── frontend/
├── backend/
└── README.md
```

## Installation

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API

Backend:

```
http://localhost:8000
```

Swagger Documentation:

```
http://localhost:8000/docs
```

Frontend:

```
http://localhost:5173
```

## Screenshots

(Add project screenshots here)

## Future Improvements

- User Authentication
- Email Notifications
- Dashboard Analytics
- File Attachments
- PostgreSQL Support
- Cloud Deployment

## Author

Yogesh Salve
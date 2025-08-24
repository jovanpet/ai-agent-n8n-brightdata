# Full-Stack Application

A full-stack web application with React frontend and Flask backend.

## Project Structure

```
├── backend/           # Flask API server
│   ├── app/          # Application modules
│   │   ├── routes/   # API endpoints
│   │   ├── models/   # Database models
│   │   └── utils/    # Utility functions
│   ├── tests/        # Backend tests
│   ├── app.py        # Application entry point
│   └── requirements.txt
├── frontend/         # React application
│   ├── src/
│   │   └── services/ # API service layer
│   └── package.json
└── docs/            # Documentation
```

## Getting Started

### Prerequisites
- Node.js 16+
- Python 3.8+
- pip

### Installation

1. Install all dependencies:
```bash
npm run install:all
```

2. Set up environment variables:
```bash
# Backend
cp backend/.env.example backend/.env

# Frontend  
cp frontend/.env.example frontend/.env
```

### Development

Start both frontend and backend:
```bash
npm run dev
```

Or start them separately:
```bash
# Backend (Flask) - runs on http://localhost:5001
npm run dev:backend

# Frontend (React) - runs on http://localhost:3000
npm run dev:frontend
```

### API Endpoints

- `GET /api/health` - Health check
- `GET /api/hello` - Hello message
- `POST /api/echo` - Echo request data

## Technologies

**Frontend:**
- React with TypeScript
- Axios for API calls
- Create React App

**Backend:**
- Flask
- SQLAlchemy
- Flask-CORS
- Python-dotenv

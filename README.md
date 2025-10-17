# QR Code Reader Premium Platform

A modern full-stack application for QR code scanning, generation, analytics, and management with advanced customization features.

[![CI/CD Pipeline](https://github.com/ArmanShirzad/qrRobust-scanner/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/ArmanShirzad/qrRobust-scanner/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)

## Features

- **🔍 QR Code Scanning**: Multi-engine detection with zxing-cpp and OpenCV
- **🎨 QR Code Generation**: Custom colors, logos, backgrounds, and templates
- **📊 Analytics Dashboard**: Track scans, locations, devices, and performance
- **🔐 Authentication**: JWT-based auth with Firebase integration
- **📱 Responsive Design**: Beautiful React frontend with Tailwind CSS
- **⚡ FastAPI Backend**: High-performance Python API with async support
- **🗄️ Database Integration**: PostgreSQL with SQLAlchemy ORM
- **🚀 Real-time Features**: Live preview and WebSocket support
- **🔒 Security**: Rate limiting, CORS, and security headers
- **📈 API Access**: Comprehensive REST API with documentation

## Run Locally

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (for production)
- Redis (optional, for caching)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/ArmanShirzad/qrRobust-scanner.git
cd qrRobust-scanner
git checkout qr-designer-v2
```

2. **Set up Python environment:**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -e ".[dev]"

# Set up pre-commit hooks
pre-commit install
```

3. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Set up the database:**
```bash
# Run database migrations
alembic upgrade head
```

5. **Set up the frontend:**
```bash
cd frontend
npm install
```

6. **Start the development servers:**
```bash
# Terminal 1: Backend
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm start
```

7. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Development Commands

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html

# Format code
black app/
isort app/

# Lint code
flake8 app/
mypy app/

# Frontend tests
cd frontend && npm test

# Frontend linting
cd frontend && npm run lint

# Build frontend
cd frontend && npm run build
```

## Configuration

### Environment Variables
Create a `.env` file with:
```env
# Database
DATABASE_URL=sqlite:///./qr_reader.db

# JWT Settings
SECRET_KEY=your-secret-key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Firebase (for authentication)
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY=your-private-key
FIREBASE_CLIENT_EMAIL=your-client-email
FIREBASE_CLIENT_ID=your-client-id
```

### Firebase Setup
1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Enable Authentication → Google sign-in
3. Download service account key
4. Update environment variables
5. See [FIREBASE_SETUP.md](FIREBASE_SETUP.md) for detailed instructions

## Deploy

### Vercel + Supabase (Recommended)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/ArmanShirzad/qrRobust-scanner/tree/qr-designer-v2)

**Why Vercel + Supabase?**
- **Truly Free**: No time limits, no sleep time
- **Student-Friendly**: GitHub Student Pack benefits  
- **Better Performance**: Global CDN, edge functions
- **Modern Stack**: Serverless + PostgreSQL

**Quick Deploy:**
1. **Set up Supabase** (free PostgreSQL database)
2. **Deploy to Vercel** (one-click deployment)
3. **Configure environment variables**
4. **See [VERCEL_SUPABASE_DEPLOYMENT.md](VERCEL_SUPABASE_DEPLOYMENT.md) for detailed instructions**

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Production deployment
docker-compose -f docker-compose.prod.yml up -d
```

### Other Platforms

- **Railway**: [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/ArmanShirzad/qrRobust-scanner/tree/qr-designer-v2)
- **Render**: [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)
- **Heroku**: See [DEPLOYMENT.md](DEPLOYMENT.md)

## API Documentation

### Authentication Endpoints
- `POST /api/v1/auth/firebase-verify` - Verify Firebase token
- `POST /api/v1/auth/refresh` - Refresh JWT token

### QR Designer Endpoints
- `POST /api/v1/qr-designer/design` - Generate QR code preview
- `POST /api/v1/qr-designer/design-and-save` - Create and save QR code
- `GET /api/v1/qr-designer/qr-code/{id}/image` - Get QR code image

### QR Management Endpoints
- `GET /api/v1/qr-codes/my-codes` - Get user's QR codes
- `PUT /api/v1/qr-codes/{id}` - Update QR code
- `DELETE /api/v1/qr-codes/{id}` - Delete QR code

## Project Structure

```
├── app/                    # FastAPI backend
│   ├── api/v1/            # API routes
│   ├── core/              # Configuration
│   ├── models/            # Database models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   └── utils/             # Utilities
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── contexts/       # React contexts
│   │   └── services/       # API services
├── alembic/               # Database migrations
├── requirements.txt       # Python dependencies
└── frontend/package.json  # Node.js dependencies
```

## Technologies Used

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: Python ORM
- **Alembic**: Database migrations
- **Pydantic**: Data validation
- **Firebase Admin SDK**: Authentication
- **QRCode**: QR code generation

### Frontend
- **React**: JavaScript UI library
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client
- **Firebase SDK**: Authentication
- **React Router**: Client-side routing

### Database
- **SQLite**: Development database
- **PostgreSQL**: Production database (migratable)

## Testing

```bash
# Backend tests
python -m pytest

# Frontend tests
cd frontend
npm test
```

## Features Roadmap

- [ ] QR code analytics dashboard
- [ ] Bulk QR code generation
- [ ] Custom QR code templates
- [ ] API rate limiting
- [ ] User subscription tiers
- [ ] QR code usage tracking

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [React](https://reactjs.org/) for the frontend
- [Firebase](https://firebase.google.com/) for authentication
- [Railway](https://railway.app/) for hosting

---

**Version**: QR Designer V2  
**Status**: Ready for Deployment  
**Tech Stack**: FastAPI + React + Firebase + PostgreSQL
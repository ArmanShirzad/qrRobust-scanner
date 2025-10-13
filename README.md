# QR Code Designer V2

A modern FastAPI + React application for creating, designing, and managing QR codes with advanced customization features.

## Features

- **Advanced QR Design**: Custom colors, logos, backgrounds, and templates
- **Firebase Authentication**: Google sign-in integration
- **QR Management**: Create, edit, download, and organize QR codes
- **Responsive Design**: Beautiful React frontend with Tailwind CSS
- **FastAPI Backend**: High-performance Python API
- **Database Integration**: SQLite with PostgreSQL migration support
- **Analytics**: Track QR code usage and performance
- **Real-time Preview**: Live preview of QR code designs

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Firebase project (for authentication)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/ArmanShirzad/qrRobust-scanner.git
cd qrRobust-scanner
git checkout qr-designer-v2
```

2. **Backend Setup:**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start backend server
python -m uvicorn app.main:app --reload --port 8000
```

3. **Frontend Setup:**
```bash
cd frontend
npm install
npm start
```

4. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

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

## Deployment

### Vercel + Supabase (Recommended - Truly Free!)
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

### Railway (Alternative)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/ArmanShirzad/qrRobust-scanner/tree/qr-designer-v2)

### Render (Alternative)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### Other Platforms
- **Render**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Heroku**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Docker**: See [docker-compose.yml](docker-compose.yml)

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
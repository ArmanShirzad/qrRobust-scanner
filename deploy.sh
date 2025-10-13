#!/bin/bash
# Production deployment script

set -e

echo "🚀 Starting QR App deployment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your production settings before continuing."
    echo "   Especially: DATABASE_URL, JWT_SECRET_KEY, POSTGRES_PASSWORD"
    read -p "Press Enter when you've updated .env file..."
fi

# Create uploads directory
mkdir -p uploads

# Build and start services
echo "🔨 Building Docker images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Run database migrations
echo "📊 Running database migrations..."
docker-compose exec backend python -c "
from app.database import engine
from app.models import Base
Base.metadata.create_all(bind=engine)
print('Database tables created successfully!')
"

echo "✅ Deployment completed!"
echo "🌐 Backend API: http://localhost:8000"
echo "🌐 Frontend: http://localhost:3000"
echo "📊 API Docs: http://localhost:8000/docs"

echo ""
echo "📋 Useful commands:"
echo "  View logs: docker-compose logs -f"
echo "  Stop services: docker-compose down"
echo "  Restart: docker-compose restart"
echo "  Update: docker-compose pull && docker-compose up -d"
# Deployment Guide - QR Code Reader Premium Platform

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/qr-reader-premium.git
   cd qr-reader-premium
   ```

2. **Copy environment configuration**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Start development environment**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

4. **Run database migrations**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

5. **Access the application**
   - Frontend: http://localhost:80
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 🐳 Docker Deployment

### Production Deployment

1. **Build and start services**
   ```bash
   docker-compose up -d --build
   ```

2. **Initialize database**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

3. **Create admin user (optional)**
   ```bash
   docker-compose exec backend python -c "
   from app.database import get_db
   from app.models import User
   from app.utils.auth import get_password_hash
   from sqlalchemy.orm import Session
   
   db = next(get_db())
   admin_user = User(
       email='admin@example.com',
       hashed_password=get_password_hash('admin123'),
       is_active=True,
       is_verified=True,
       tier='enterprise'
   )
   db.add(admin_user)
   db.commit()
   print('Admin user created')
   "
   ```

### Environment Variables

Key environment variables to configure:

```bash
# Database
DATABASE_URL=postgresql://user:password@postgres:5432/qr_reader_db

# Redis
REDIS_URL=redis://redis:6379

# JWT Security
JWT_SECRET_KEY=your-super-secret-key

# Stripe (Production)
STRIPE_SECRET_KEY=sk_live_your_live_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Email
EMAIL_HOST=smtp.your-provider.com
EMAIL_USERNAME=your-email@domain.com
EMAIL_PASSWORD=your-app-password

# CORS
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
```

## ☸️ Kubernetes Deployment

### Prerequisites
- Kubernetes cluster (v1.20+)
- kubectl configured
- Helm (optional)

### Deploy to Staging

1. **Create namespace**
   ```bash
   kubectl create namespace qr-reader-staging
   ```

2. **Create secrets**
   ```bash
   kubectl create secret generic qr-reader-secrets \
     --from-literal=database-url="postgresql://user:pass@postgres:5432/db" \
     --from-literal=redis-url="redis://redis:6379" \
     --from-literal=jwt-secret-key="your-secret-key" \
     --from-literal=stripe-secret-key="sk_test_..." \
     -n qr-reader-staging
   ```

3. **Deploy application**
   ```bash
   kubectl apply -f k8s/staging/ -n qr-reader-staging
   ```

4. **Check deployment status**
   ```bash
   kubectl get pods -n qr-reader-staging
   kubectl get services -n qr-reader-staging
   ```

### Deploy to Production

1. **Create production namespace**
   ```bash
   kubectl create namespace qr-reader-production
   ```

2. **Create production secrets**
   ```bash
   kubectl create secret generic qr-reader-secrets \
     --from-literal=database-url="postgresql://user:pass@prod-postgres:5432/db" \
     --from-literal=redis-url="redis://prod-redis:6379" \
     --from-literal=jwt-secret-key="your-production-secret-key" \
     --from-literal=stripe-secret-key="sk_live_..." \
     -n qr-reader-production
   ```

3. **Deploy with production configuration**
   ```bash
   kubectl apply -f k8s/production/ -n qr-reader-production
   ```

## 🔄 CI/CD Pipeline

### GitHub Actions Setup

1. **Repository Secrets**
   Add the following secrets to your GitHub repository:
   - `DATABASE_URL`: Production database URL
   - `REDIS_URL`: Production Redis URL
   - `JWT_SECRET_KEY`: Production JWT secret
   - `STRIPE_SECRET_KEY`: Production Stripe secret key
   - `STRIPE_WEBHOOK_SECRET`: Stripe webhook secret
   - `EMAIL_USERNAME`: Email username
   - `EMAIL_PASSWORD`: Email password

2. **Environment Protection Rules**
   - Set up branch protection rules
   - Require pull request reviews
   - Require status checks to pass

3. **Deployment Environments**
   - `staging`: Auto-deploy from `develop` branch
   - `production`: Auto-deploy from `main` branch

### Pipeline Stages

1. **Code Quality**
   - Linting (flake8, black, isort)
   - Type checking (mypy)
   - Security scanning (Trivy)

2. **Testing**
   - Unit tests with coverage
   - Integration tests
   - Frontend tests

3. **Building**
   - Docker image building
   - Multi-architecture support
   - Image scanning

4. **Deployment**
   - Staging deployment
   - Production deployment
   - Database migrations

## 📊 Monitoring and Logging

### Application Monitoring

1. **Health Checks**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Metrics Endpoint**
   ```bash
   curl http://localhost:8000/metrics
   ```

3. **Database Health**
   ```bash
   docker-compose exec postgres pg_isready
   ```

4. **Redis Health**
   ```bash
   docker-compose exec redis redis-cli ping
   ```

### Logging Configuration

1. **Application Logs**
   ```bash
   docker-compose logs -f backend
   docker-compose logs -f frontend
   ```

2. **Database Logs**
   ```bash
   docker-compose logs -f postgres
   ```

3. **Redis Logs**
   ```bash
   docker-compose logs -f redis
   ```

### Performance Monitoring

1. **Resource Usage**
   ```bash
   docker stats
   ```

2. **Database Performance**
   ```bash
   docker-compose exec postgres psql -U qr_reader_user -d qr_reader_db -c "
   SELECT * FROM pg_stat_activity;
   "
   ```

## 🔧 Maintenance

### Database Maintenance

1. **Backup Database**
   ```bash
   docker-compose exec postgres pg_dump -U qr_reader_user qr_reader_db > backup.sql
   ```

2. **Restore Database**
   ```bash
   docker-compose exec -T postgres psql -U qr_reader_user qr_reader_db < backup.sql
   ```

3. **Run Migrations**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

4. **Create Migration**
   ```bash
   docker-compose exec backend alembic revision --autogenerate -m "Description"
   ```

### Application Updates

1. **Update Application**
   ```bash
   git pull origin main
   docker-compose down
   docker-compose up -d --build
   ```

2. **Rollback**
   ```bash
   git checkout previous-version
   docker-compose down
   docker-compose up -d --build
   ```

### Scaling

1. **Horizontal Scaling**
   ```bash
   docker-compose up -d --scale backend=3 --scale frontend=2
   ```

2. **Load Balancer Configuration**
   ```yaml
   # nginx.conf
   upstream backend {
       server backend_1:8000;
       server backend_2:8000;
       server backend_3:8000;
   }
   ```

## 🛡️ Security

### SSL/TLS Configuration

1. **Generate SSL Certificate**
   ```bash
   openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
   ```

2. **Update Docker Compose**
   ```yaml
   services:
     nginx:
       volumes:
         - ./cert.pem:/etc/ssl/certs/cert.pem
         - ./key.pem:/etc/ssl/private/key.pem
   ```

### Security Headers

1. **Nginx Security Headers**
   ```nginx
   add_header X-Frame-Options "SAMEORIGIN" always;
   add_header X-XSS-Protection "1; mode=block" always;
   add_header X-Content-Type-Options "nosniff" always;
   add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
   ```

### Firewall Configuration

1. **UFW Rules**
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Issues**
   ```bash
   # Check database status
   docker-compose exec postgres pg_isready
   
   # Check connection string
   echo $DATABASE_URL
   ```

2. **Redis Connection Issues**
   ```bash
   # Check Redis status
   docker-compose exec redis redis-cli ping
   
   # Check Redis logs
   docker-compose logs redis
   ```

3. **Application Startup Issues**
   ```bash
   # Check application logs
   docker-compose logs backend
   
   # Check environment variables
   docker-compose exec backend env | grep -E "(DATABASE|REDIS|JWT)"
   ```

4. **Frontend Build Issues**
   ```bash
   # Check frontend logs
   docker-compose logs frontend
   
   # Rebuild frontend
   docker-compose build frontend
   ```

### Performance Issues

1. **High Memory Usage**
   ```bash
   # Check memory usage
   docker stats
   
   # Optimize Docker images
   docker system prune -a
   ```

2. **Slow Database Queries**
   ```bash
   # Check slow queries
   docker-compose exec postgres psql -U qr_reader_user -d qr_reader_db -c "
   SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;
   "
   ```

## 📞 Support

### Getting Help

1. **Documentation**: Check the `/docs` directory
2. **Issues**: Create a GitHub issue
3. **Discussions**: Use GitHub Discussions
4. **Email**: support@qrreader-premium.com

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

**Happy Deploying! 🚀**

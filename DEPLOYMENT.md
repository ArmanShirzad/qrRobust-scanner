# QR App Deployment Guide

## **Scale-Based Deployment Strategies**

### **1. Small Scale (1-100 users) - SQLite + Single Server**
```bash
# Current setup - works fine for small scale
./deploy.sh  # Uses SQLite + Docker
```

**Pros**: Simple, no changes needed
**Cons**: Limited scalability, single point of failure
**Cost**: $5-20/month (VPS)

---

### **2. Medium Scale (100-1000 users) - PostgreSQL + Load Balancer**

#### **Option A: Docker Compose (Recommended)**
```bash
# 1. Set up PostgreSQL environment
export POSTGRES_USER=qr_user
export POSTGRES_PASSWORD=secure_password_here
export POSTGRES_DB=qr_app

# 2. Deploy with Docker Compose
docker-compose up -d

# 3. Migrate existing SQLite data
python migrate_to_postgres.py
```

#### **Option B: Cloud Database (AWS RDS, Google Cloud SQL)**
```bash
# 1. Create PostgreSQL instance on cloud
# 2. Update .env with cloud database URL
DATABASE_URL=postgresql://user:pass@your-cloud-db.amazonaws.com:5432/qr_app

# 3. Deploy application
docker-compose up -d
```

**Pros**: Better performance, concurrent users, backups
**Cons**: More complex setup
**Cost**: $20-100/month

---

### **3. Large Scale (1000+ users) - Microservices + Cloud**

#### **Architecture:**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │────│   API Gateway   │────│   QR Service    │
│   (Nginx/ALB)   │    │   (FastAPI)     │    │   (FastAPI)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Auth Service  │    │   File Service  │
                       │   (FastAPI)     │    │   (FastAPI)     │
                       └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐    ┌─────────────────┐
                       │   PostgreSQL    │    │     Redis       │
                       │   (Primary)     │    │   (Cache)       │
                       └─────────────────┘    └─────────────────┘
```

#### **Deployment Options:**

**AWS:**
```bash
# 1. ECS/EKS for containers
# 2. RDS for PostgreSQL
# 3. ElastiCache for Redis
# 4. S3 for file storage
# 5. CloudFront for CDN
```

**Google Cloud:**
```bash
# 1. Cloud Run for containers
# 2. Cloud SQL for PostgreSQL
# 3. Memorystore for Redis
# 4. Cloud Storage for files
# 5. Cloud CDN for static content
```

**DigitalOcean:**
```bash
# 1. App Platform for containers
# 2. Managed PostgreSQL
# 3. Managed Redis
# 4. Spaces for file storage
```

**Pros**: Highly scalable, fault-tolerant, auto-scaling
**Cons**: Complex architecture, higher costs
**Cost**: $100-1000+/month

---

## **Database Migration Strategy**

### **Step 1: Backup Current Data**
```bash
# Backup SQLite database
cp qr_reader.db qr_reader_backup_$(date +%Y%m%d_%H%M%S).db
```

### **Step 2: Set Up PostgreSQL**
```bash
# Local PostgreSQL
sudo apt-get install postgresql postgresql-contrib
sudo -u postgres createdb qr_app
sudo -u postgres createuser qr_user

# Or use Docker
docker run --name postgres-db -e POSTGRES_DB=qr_app -e POSTGRES_USER=qr_user -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:15
```

### **Step 3: Migrate Data**
```bash
# Run migration script
python migrate_to_postgres.py
```

### **Step 4: Update Configuration**
```bash
# Update .env file
DATABASE_URL=postgresql://qr_user:password@localhost:5432/qr_app
```

---

## **Performance Optimization**

### **Database Optimizations:**
```sql
-- Add indexes for better performance
CREATE INDEX idx_qr_codes_user_id ON qr_codes(user_id);
CREATE INDEX idx_qr_codes_created_at ON qr_codes(created_at);
CREATE INDEX idx_qr_codes_short_url ON qr_codes(short_url);
CREATE INDEX idx_users_email ON users(email);
```

### **Caching Strategy:**
```python
# Redis caching for frequently accessed data
import redis
from functools import wraps

redis_client = redis.Redis.from_url(settings.redis_url)

def cache_result(expiration=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            return result
        return wrapper
    return decorator
```

### **CDN for Static Files:**
```python
# Serve QR code images from CDN
def get_qr_image_url(qr_id: int) -> str:
    if settings.environment == "production":
        return f"https://cdn.yourdomain.com/qr-codes/{qr_id}.png"
    return f"/api/v1/qr-designer/qr-code/{qr_id}/image"
```

---

## **Security Considerations**

### **Production Security Checklist:**
- [ ] Change default JWT secret key
- [ ] Use HTTPS in production
- [ ] Set up proper CORS origins
- [ ] Enable database SSL
- [ ] Use environment variables for secrets
- [ ] Set up monitoring and logging
- [ ] Enable rate limiting
- [ ] Regular security updates

### **Environment Variables:**
```bash
# Production .env
JWT_SECRET_KEY=your-super-secure-random-key-here
DATABASE_URL=postgresql://user:pass@secure-db-host:5432/qr_app
REDIS_URL=redis://secure-redis-host:6379/0
DEBUG=False
ENVIRONMENT=production
ALLOWED_ORIGINS=https://yourdomain.com
```

---

## **Monitoring & Maintenance**

### **Health Checks:**
```python
# Add health check endpoint
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected",
        "timestamp": datetime.utcnow()
    }
```

### **Logging:**
```python
import logging
from pythonjsonlogger import jsonlogger

# Structured logging for production
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)
```

### **Backup Strategy:**
```bash
# Daily database backups
#!/bin/bash
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
aws s3 cp backup_$(date +%Y%m%d).sql s3://your-backup-bucket/
```

---

## **Cost Estimation**

| Scale | Users | Infrastructure | Monthly Cost |
|-------|-------|---------------|--------------|
| Small | 1-100 | VPS + SQLite | $5-20 |
| Medium | 100-1000 | VPS + PostgreSQL | $20-100 |
| Large | 1000+ | Cloud + Microservices | $100-1000+ |

---

## **Quick Start Commands**

```bash
# 1. Clone and setup
git clone your-repo
cd qr-app

# 2. Choose your deployment strategy
cp env.example .env
# Edit .env with your settings

# 3. Deploy
./deploy.sh

# 4. Check status
docker-compose ps
docker-compose logs -f
```

This gives you a complete deployment strategy that scales from small to enterprise level!
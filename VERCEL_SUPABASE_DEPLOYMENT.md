# Vercel + Supabase Deployment Guide

## **Why Vercel + Supabase?**

- **Truly Free**: No time limits, no sleep time
- **Student-Friendly**: GitHub Student Pack benefits
- **Better Performance**: Global CDN, edge functions
- **Modern Stack**: Serverless + PostgreSQL
- **Easy Setup**: One-click deployment

## **Prerequisites**

1. **GitHub Account** (for Vercel integration)
2. **Supabase Account** (free tier)
3. **GitHub Student Pack** (optional, but recommended)

## **Step 1: Set Up Supabase**

### 1.1 Create Supabase Project
1. **Go to [supabase.com](https://supabase.com)**
2. **Sign up/login**
3. **Click "New Project"**
4. **Configure:**
   - **Name**: `qr-designer-v2`
   - **Database Password**: Generate a strong password
   - **Region**: Choose closest to your users
5. **Click "Create new project"**
6. **Wait for setup** (2-3 minutes)

### 1.2 Get Supabase Credentials
1. **Go to Project Settings → API**
2. **Copy these values:**
   - **Project URL**: `https://your-project.supabase.co`
   - **Anon Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
   - **Service Role Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

### 1.3 Set Up Database Schema
1. **Go to SQL Editor**
2. **Run this SQL to create tables:**

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    tier VARCHAR(50) DEFAULT 'free',
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- QR Codes table
CREATE TABLE qr_codes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    destination_url TEXT NOT NULL,
    short_url VARCHAR(255),
    size INTEGER DEFAULT 300,
    border INTEGER DEFAULT 4,
    error_correction_level VARCHAR(10) DEFAULT 'M',
    foreground_color VARCHAR(7) DEFAULT '#000000',
    background_color VARCHAR(7) DEFAULT '#FFFFFF',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE qr_codes ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view own data" ON users FOR SELECT USING (auth.uid()::text = id::text);
CREATE POLICY "Users can update own data" ON users FOR UPDATE USING (auth.uid()::text = id::text);

CREATE POLICY "Users can view own QR codes" ON qr_codes FOR SELECT USING (auth.uid()::text = user_id::text);
CREATE POLICY "Users can insert own QR codes" ON qr_codes FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);
CREATE POLICY "Users can update own QR codes" ON qr_codes FOR UPDATE USING (auth.uid()::text = user_id::text);
CREATE POLICY "Users can delete own QR codes" ON qr_codes FOR DELETE USING (auth.uid()::text = user_id::text);
```

### 1.4 Enable Authentication
1. **Go to Authentication → Settings**
2. **Enable Email authentication**
3. **Enable Google OAuth** (optional)
4. **Configure redirect URLs**: `https://your-app.vercel.app`

## **Step 2: Deploy to Vercel**

### 2.1 Connect GitHub to Vercel
1. **Go to [vercel.com](https://vercel.com)**
2. **Sign up/login with GitHub**
3. **Click "New Project"**
4. **Import your repository**: `ArmanShirzad/qrRobust-scanner`
5. **Select branch**: `qr-designer-v2`

### 2.2 Configure Vercel Project
1. **Framework Preset**: Other
2. **Root Directory**: Leave empty
3. **Build Command**: `cd frontend && npm install && npm run build`
4. **Output Directory**: `frontend/build`

### 2.3 Set Environment Variables
Add these in Vercel Project Settings → Environment Variables:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key

# Database
DATABASE_URL=postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres

# JWT Settings
JWT_SECRET_KEY=your-super-secret-jwt-key-here
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Production Settings
DEBUG=false
ENVIRONMENT=production

# CORS
ALLOWED_ORIGINS=https://your-app.vercel.app

# Frontend Environment Variables
REACT_APP_API_URL=https://your-app.vercel.app/api
REACT_APP_SUPABASE_URL=https://your-project.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your-supabase-anon-key
```

### 2.4 Deploy
1. **Click "Deploy"**
2. **Wait for build** (2-3 minutes)
3. **Your app will be live at**: `https://your-app.vercel.app`

## **Step 3: Configure Backend API**

### 3.1 Create API Routes
Vercel will automatically create API routes from your FastAPI app:
- **API Base**: `https://your-app.vercel.app/api`
- **Health Check**: `https://your-app.vercel.app/api/health`
- **API Docs**: `https://your-app.vercel.app/api/docs`

### 3.2 Update Frontend API Configuration
The frontend will automatically use the Vercel API URL through environment variables.

## **Step 4: Test Your Deployment**

### 4.1 Test Frontend
1. **Visit**: `https://your-app.vercel.app`
2. **Check**: React app loads correctly
3. **Test**: Navigation works

### 4.2 Test Backend API
1. **Visit**: `https://your-app.vercel.app/api/docs`
2. **Check**: FastAPI docs load
3. **Test**: API endpoints work

### 4.3 Test Database
1. **Go to Supabase Dashboard**
2. **Check**: Tables created successfully
3. **Test**: Insert/query data

## **Step 5: Authentication Setup**

### 5.1 Supabase Auth (Recommended)
1. **Frontend**: Use Supabase client for auth
2. **Backend**: Verify Supabase JWT tokens
3. **Database**: Row Level Security policies

### 5.2 Firebase Auth (Alternative)
1. **Keep existing Firebase setup**
2. **Use Firebase for authentication**
3. **Use Supabase for database only**

## **Step 6: Monitoring & Analytics**

### 6.1 Vercel Analytics
- **Built-in**: Performance metrics
- **Real-time**: User analytics
- **Free tier**: Basic analytics

### 6.2 Supabase Dashboard
- **Database**: Query performance
- **Auth**: User management
- **Storage**: File uploads

## **Deployment URLs**

After deployment:
- **Frontend**: `https://your-app.vercel.app`
- **API**: `https://your-app.vercel.app/api`
- **API Docs**: `https://your-app.vercel.app/api/docs`
- **Health Check**: `https://your-app.vercel.app/api/health`

## **Updates & Maintenance**

### Deploying Updates:
1. **Push changes to `qr-designer-v2` branch**
2. **Vercel auto-deploys** (if enabled)
3. **Or manually trigger** from Vercel dashboard

### Database Migrations:
```bash
# Run migrations in Supabase SQL Editor
# Or use Supabase CLI
supabase db push
```

## **Cost Breakdown**

### Free Tier Limits:
- **Vercel**: Unlimited static sites, 100GB bandwidth
- **Supabase**: 500MB database, 50MB file storage
- **Total Cost**: $0/month

### When to Upgrade:
- **Vercel Pro**: $20/month (team features)
- **Supabase Pro**: $25/month (more storage)

## **Student Benefits**

### GitHub Student Pack:
- **Vercel**: Extra credits and features
- **Supabase**: Extended free tier
- **Total Savings**: $500+/month

## **Troubleshooting**

### Common Issues:

1. **Build Failures**
   - Check Vercel build logs
   - Verify environment variables
   - Check package.json dependencies

2. **Database Connection**
   - Verify DATABASE_URL format
   - Check Supabase project status
   - Verify network access

3. **Authentication Issues**
   - Check Supabase auth settings
   - Verify redirect URLs
   - Check JWT configuration

### Debug Commands:
```bash
# Check Vercel logs
vercel logs

# Test API locally
vercel dev

# Check Supabase connection
supabase status
```

## **Success!**

Your QR Designer V2 is now deployed on:
- **Vercel**: Frontend + API
- **Supabase**: Database + Auth
- **Free Forever**: No time limits!

**Your app is live and ready for users!**

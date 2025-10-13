# 🚀 Render Deployment Guide for QR Designer V2

## 📋 Prerequisites

1. **GitHub Repository**: Your code should be pushed to GitHub
2. **Firebase Project**: Set up Firebase authentication (see FIREBASE_SETUP.md)
3. **Render Account**: Sign up at [render.com](https://render.com)

## 🎯 Quick Deployment (Recommended)

### Option 1: One-Click Deploy with render.yaml

1. **Push render.yaml to your repository**
2. **Go to [render.com](https://render.com)**
3. **Click "New +" → "Blueprint"**
4. **Connect your GitHub repository**
5. **Select the `qr-designer-v2` branch**
6. **Render will automatically detect render.yaml and create all services**

### Option 2: Manual Deployment

## 🔧 Step-by-Step Manual Deployment

### 1. Create Database Service

1. **Go to Render Dashboard**
2. **Click "New +" → "PostgreSQL"**
3. **Configure:**
   - **Name**: `qr-designer-db`
   - **Plan**: Free
   - **Region**: Choose closest to your users
4. **Click "Create Database"**
5. **Note the connection string** (you'll need this later)

### 2. Deploy Backend Service

1. **Click "New +" → "Web Service"**
2. **Connect GitHub repository**
3. **Configure Backend:**
   - **Name**: `qr-designer-backend`
   - **Branch**: `qr-designer-v2`
   - **Root Directory**: Leave empty (root)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt && alembic upgrade head`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Environment Variables:**
   ```
   DATABASE_URL=<from your PostgreSQL service>
   JWT_SECRET_KEY=<generate a random secret key>
   JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
   JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
   DEBUG=false
   ENVIRONMENT=production
   ALLOWED_ORIGINS=https://qr-designer-frontend.onrender.com
   FIREBASE_PROJECT_ID=<your-firebase-project-id>
   FIREBASE_PRIVATE_KEY_ID=<your-private-key-id>
   FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n<your-private-key>\n-----END PRIVATE KEY-----\n"
   FIREBASE_CLIENT_EMAIL=<your-service-account-email>
   FIREBASE_CLIENT_ID=<your-client-id>
   ```

5. **Click "Create Web Service"**

### 3. Deploy Frontend Service

1. **Click "New +" → "Static Site"**
2. **Connect GitHub repository**
3. **Configure Frontend:**
   - **Name**: `qr-designer-frontend`
   - **Branch**: `qr-designer-v2`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `build`

4. **Environment Variables:**
   ```
   REACT_APP_API_URL=https://qr-designer-backend.onrender.com
   REACT_APP_FIREBASE_API_KEY=<your-firebase-api-key>
   REACT_APP_FIREBASE_AUTH_DOMAIN=<your-project>.firebaseapp.com
   REACT_APP_FIREBASE_PROJECT_ID=<your-firebase-project-id>
   REACT_APP_FIREBASE_STORAGE_BUCKET=<your-project>.appspot.com
   REACT_APP_FIREBASE_MESSAGING_SENDER_ID=<your-sender-id>
   REACT_APP_FIREBASE_APP_ID=<your-app-id>
   ```

5. **Click "Create Static Site"**

## 🔐 Firebase Configuration

### 1. Get Firebase Config

1. **Go to Firebase Console**
2. **Select your project**
3. **Go to Project Settings → General**
4. **Scroll down to "Your apps"**
5. **Click on your web app**
6. **Copy the config object**

### 2. Update Frontend Environment Variables

Use the Firebase config values in your frontend environment variables:

```javascript
// From Firebase config
const firebaseConfig = {
  apiKey: "your-api-key",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project-id",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "123456789",
  appId: "your-app-id"
};
```

## 🚀 Deployment URLs

After deployment, you'll get:

- **Frontend**: `https://qr-designer-frontend.onrender.com`
- **Backend API**: `https://qr-designer-backend.onrender.com`
- **API Docs**: `https://qr-designer-backend.onrender.com/docs`

## 🔧 Troubleshooting

### Common Issues:

1. **Database Connection Error**
   - Check DATABASE_URL format
   - Ensure database service is running
   - Run migrations: `alembic upgrade head`

2. **Frontend Can't Connect to Backend**
   - Update REACT_APP_API_URL with correct backend URL
   - Check CORS settings in backend
   - Verify ALLOWED_ORIGINS includes frontend URL

3. **Firebase Authentication Issues**
   - Verify all Firebase environment variables
   - Check Firebase project settings
   - Ensure Google sign-in is enabled

4. **Build Failures**
   - Check build logs in Render dashboard
   - Verify all dependencies in requirements.txt
   - Ensure Python version compatibility

### Debug Commands:

```bash
# Check backend logs
# Go to Render dashboard → Your backend service → Logs

# Check frontend build logs
# Go to Render dashboard → Your frontend service → Logs

# Test API endpoints
curl https://qr-designer-backend.onrender.com/docs
```

## 📊 Monitoring

### Render Dashboard Features:
- **Logs**: Real-time application logs
- **Metrics**: CPU, memory, and request metrics
- **Deployments**: Deployment history and status
- **Environment**: Environment variables management

### Health Checks:
- **Backend**: `GET /health` endpoint
- **Frontend**: Static file serving
- **Database**: Connection status

## 🔄 Updates and Maintenance

### Deploying Updates:
1. **Push changes to `qr-designer-v2` branch**
2. **Render auto-deploys** (if auto-deploy is enabled)
3. **Or manually trigger deployment** from dashboard

### Database Migrations:
```bash
# Run migrations after code changes
alembic upgrade head
```

## 💰 Pricing

### Free Tier Limits:
- **Web Services**: 750 hours/month
- **Database**: 1GB storage
- **Static Sites**: Unlimited
- **Bandwidth**: 100GB/month

### Upgrade When Needed:
- **Starter Plan**: $7/month per service
- **Standard Plan**: $25/month per service
- **Pro Plan**: $85/month per service

## 🎉 Success!

Once deployed, your QR Designer V2 will be live at:
**https://qr-designer-frontend.onrender.com**

Users can:
- ✅ Sign in with Google
- ✅ Create custom QR codes
- ✅ Manage their QR code library
- ✅ Download QR codes
- ✅ View analytics

---

**Need Help?** Check the logs in Render dashboard or refer to the troubleshooting section above.

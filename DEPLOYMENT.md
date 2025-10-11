# Production Deployment Configuration

This branch contains production-ready deployment configurations.

## Environment Variables for Production
```bash
SECRET_KEY=your-production-secret-key
FLASK_ENV=production
RAILWAY_STATIC_URL=https://your-app.railway.app
```

## Deployment Commands
```bash
# Deploy to Railway
railway login
railway link
railway up

# Or use GitHub integration for auto-deploy
git push origin deployer
```

## Monitoring
- Railway dashboard: https://railway.app/dashboard
- Application logs: Available in Railway dashboard
- Health checks: Configured in railway.json

## Security Notes
- Never commit production secrets to git
- Use Railway environment variables for sensitive data
- Enable HTTPS (automatic with Railway)
- Set up proper CORS policies if needed

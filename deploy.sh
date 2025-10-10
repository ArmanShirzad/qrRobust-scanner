#!/bin/bash
# Railway deployment script for QR code reader

echo "🚀 Preparing QR Code Reader for Railway deployment..."

# Install dependencies locally for testing
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Test the installation
echo "🧪 Testing installation..."
python test_installation.py

if [ $? -eq 0 ]; then
    echo "✅ Local installation test passed!"
else
    echo "❌ Installation test failed. Please check dependencies."
    exit 1
fi

echo ""
echo "🎉 Ready for Railway deployment!"
echo ""
echo "📋 Railway Deployment Steps:"
echo "1. Push your code to GitHub:"
echo "   git add ."
echo "   git commit -m 'Add Railway deployment support'"
echo "   git push origin main"
echo ""
echo "2. Deploy to Railway:"
echo "   - Go to https://railway.app"
echo "   - Sign up/login with GitHub"
echo "   - Click 'New Project' → 'Deploy from GitHub repo'"
echo "   - Select your repository"
echo "   - Railway will auto-detect Python and deploy!"
echo ""
echo "3. Your app will be live at: https://your-app-name.railway.app"
echo ""
echo "💡 Railway Features:"
echo "   - Free $5/month credit (enough for small apps)"
echo "   - Automatic HTTPS"
echo "   - Environment variables support"
echo "   - Auto-deploy on git push"
echo "   - Built-in monitoring"
echo ""
echo "🔧 Optional: Set environment variables in Railway dashboard:"
echo "   - FLASK_ENV=production (for production mode)"
echo "   - SECRET_KEY=your-secret-key (for Flask sessions)"

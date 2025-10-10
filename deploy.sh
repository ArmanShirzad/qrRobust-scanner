#!/bin/bash
# Quick deployment script for your QR code reader

echo "🚀 Deploying QR Code Reader App..."

# Install dependencies
pip install -r requirements.txt

# Create production configuration
cat > production_config.py << EOF
import os

class ProductionConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-production-secret-key'
    DEBUG = False
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 5000))
EOF

# Create Procfile for Heroku
echo "web: python app.py" > Procfile

# Create runtime.txt
echo "python-3.12" > runtime.txt

echo "✅ Ready for deployment!"
echo ""
echo "Next steps:"
echo "1. Create Heroku account: https://heroku.com"
echo "2. Install Heroku CLI"
echo "3. Run: heroku create your-qr-reader-app"
echo "4. Run: git add . && git commit -m 'Deploy QR reader'"
echo "5. Run: git push heroku main"
echo ""
echo "Your app will be live at: https://your-qr-reader-app.herokuapp.com"

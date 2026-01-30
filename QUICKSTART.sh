"""
Quick Start Guide - Get the project running in 5 minutes
"""

# BACKEND SETUP
cd backend

# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
cp .env.example .env

# 4. Run server
python app.py
# ✅ Server running on http://localhost:5000

# FRONTEND SETUP (NEW TERMINAL)
cd frontend

# 1. Install npm packages
npm install

# 2. Start React dev server
npm start
# ✅ Dashboard running on http://localhost:3000

# API TESTING (NEW TERMINAL)

# 1. Register a user
curl -X POST http://localhost:5000/api/auth/register-user \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "9876543210",
    "unit": "A101",
    "resident_type": "resident"
  }'

# 2. Issue credential
curl -X POST http://localhost:5000/api/auth/issue-credential/1 \
  -H "Content-Type: application/json" \
  -d '{
    "credential_type": "qr_code",
    "valid_for_days": 30
  }'

# 3. Check dashboard
# Open http://localhost:3000 in browser
# You should see: users = 1, access attempts = 0

# 4. Get system health
curl http://localhost:5000/api/health

# SUCCESS INDICATORS
echo "✅ Backend: http://localhost:5000"
echo "✅ Frontend: http://localhost:3000"
echo "✅ API Status: Healthy"
echo "✅ Database: Created"

# DOCKER ALTERNATIVE (if you have Docker installed)
docker-compose up -d
# Backend: http://localhost:5000
# Frontend: http://localhost:3000

# TROUBLESHOOTING
# If port 5000 is in use: Change in app.py line 'port=5000' to 'port=5001'
# If dependencies fail: pip install -r requirements.txt --upgrade
# If database error: Delete identity_spoofing.db and restart

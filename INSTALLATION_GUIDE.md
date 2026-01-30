# 🚀 Installation Guide - Identity Spoofing Detection System

## Prerequisites
- Python 3.11 (NOT 3.14 - has compatibility issues)
- Node.js 16+ and npm
- Git

---

## 📦 Backend Setup

### Step 1: Create Python Virtual Environment
```bash
cd identity-spoofing-detection/backend
python -m venv .venv
```

### Step 2: Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

**Mac/Linux:**
```bash
source .venv/bin/activate
```

### Step 3: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Start Backend Server
```bash
flask --app app run
```

Backend will run on: **http://127.0.0.1:5000**

---

## 🎨 Frontend Setup

### Step 1: Navigate to Frontend
```bash
cd identity-spoofing-detection/frontend
```

### Step 2: Install Node Dependencies
```bash
npm install
```

### Step 3: Start Development Server
```bash
npm start
```

Frontend will open at: **http://localhost:3000**

---

## 🧪 Testing the System

### Option 1: Use Demo Data
1. Open browser: http://localhost:3000
2. Go to Dashboard tab - see pre-populated statistics
3. Go to Face Test tab

### Option 2: Load Demo Data via API
```powershell
Invoke-RestMethod -Uri http://127.0.0.1:5000/api/demo/seed?fresh=true -Method POST
```

### Option 3: Test Face Detection
1. Click **Face Test** tab
2. Click **📹 Use Camera** button
3. Allow camera access
4. Capture your photo and enroll
5. Test verification with same/different faces

---

## 📚 Main Libraries Used

### Backend (Python)
- **Flask** - Web framework
- **DeepFace** - AI face recognition (uses TensorFlow)
- **TensorFlow** - Deep learning framework
- **OpenCV** - Image processing
- **SQLAlchemy** - Database ORM
- **Flask-CORS** - Cross-origin requests

### Frontend (React)
- **React 18.2.0** - UI framework
- **Axios** - HTTP requests
- **Recharts** - Data visualization
- **React Scripts** - Build tools

---

## ⚠️ Common Issues

### Issue: "No module named flask"
**Solution:** Make sure virtual environment is activated!
```bash
.\.venv\Scripts\Activate.ps1
```

### Issue: Python 3.14 build errors
**Solution:** Use Python 3.11 instead
```bash
python --version  # Should show 3.11.x
```

### Issue: Camera not working
**Solution:** 
- Use HTTPS or localhost (browser security requirement)
- Allow camera permissions when browser prompts
- Check if another app is using the camera

### Issue: Port 3000 already in use
**Solution:**
```bash
# Kill the process or use different port
set PORT=3001 && npm start
```

---

## 🎯 Quick Start (All Commands)

```bash
# Terminal 1 - Backend
cd identity-spoofing-detection/backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
flask --app app run

# Terminal 2 - Frontend
cd identity-spoofing-detection/frontend
npm install
npm start
```

---

## ✅ Verification

Backend running: http://127.0.0.1:5000/api/health should return `{"status":"healthy"}`

Frontend running: http://localhost:3000 should show the dashboard

---

## 👥 Team Development Tips

1. **Always activate virtual environment** before working on backend
2. **Pull latest code** before starting work
3. **Share this guide** with all teammates
4. **Use the same Python version** (3.11) to avoid compatibility issues
5. **Don't commit `.venv/` or `node_modules/`** folders

---

## 📞 Need Help?

Check if services are running:
```bash
# Check backend
curl http://127.0.0.1:5000/api/health

# Check frontend
# Open http://localhost:3000 in browser
```

Happy coding! 🎉

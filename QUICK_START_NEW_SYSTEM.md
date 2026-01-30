# 🚀 QUICK START - NEW ENROLLMENT SYSTEM

Get the face recognition enrollment system running in **5 minutes**!

---

## ✅ Prerequisites

- Python 3.8+ installed
- Node.js 16+ installed
- MongoDB running locally OR MongoDB Atlas account
- Git configured

---

## 📦 Step 1: Backend Setup

### 1.1 Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 1.2 Set Environment Variables
Create `.env` file in backend folder:
```
MONGODB_URI=mongodb://localhost:27017
FLASK_ENV=production
FACE_SIMILARITY_THRESHOLD=0.55
```

**OR** if using MongoDB Atlas:
```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/identity_spoofing_db?retryWrites=true&w=majority
```

### 1.3 Start Backend
```bash
python app.py
```
✅ Backend running on http://localhost:5000

---

## 🎨 Step 2: Frontend Setup

### 2.1 Install Node Modules
```bash
cd frontend
npm install
```

### 2.2 Start React App
```bash
npm start
```
✅ Frontend running on http://localhost:3000

---

## 🗄️ Step 3: MongoDB Setup

### Option A: Local MongoDB
```bash
# Install MongoDB (Windows/Mac/Linux)
# Then start MongoDB server:
mongod
```

### Option B: MongoDB Atlas (Cloud)
1. Go to https://www.mongodb.com/cloud/atlas
2. Create free account
3. Create cluster
4. Get connection string
5. Update `.env` with connection string

---

## 🎯 Step 4: Test the System

### 4.1 Visit the App
Open browser to: **http://localhost:3000**

### 4.2 Test Enrollment
1. Click **"Enroll User"** in sidebar
2. Fill in test data:
   - Name: "Test User"
   - Email: "test@example.com"
   - Phone: "123-456-7890"
   - Unit: "Apt 101"
   - Proof Type: "National ID"
3. Click **"Start Camera"**
4. Capture your face
5. Review and submit ✅

### 4.3 Test Verification
1. Click **"Verify Access"** in sidebar
2. Search for "Test User"
3. Select user
4. Click **"Start Camera"**
5. Capture face again
6. AI shows match % 
7. Click **"Grant Access"** to approve

---

## 🔧 Troubleshooting

### Frontend Won't Start
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm start
```

### Backend ImportError: No module 'deepface'
```bash
# Reinstall all dependencies
pip install --upgrade -r requirements.txt
```

### MongoDB Connection Error
```bash
# Check MongoDB is running
# Windows:
tasklist | find "mongod"

# Mac/Linux:
ps aux | grep mongod

# If not running, start it:
mongod
```

### Camera Permission Denied
- Browser will ask for camera permission
- Click "Allow"
- Try in Chrome/Edge (Firefox has issues)
- HTTPS only in production

### Face Not Detected
- Ensure good lighting
- Position face directly to camera
- Move closer to camera
- Remove glasses/masks

---

## 📊 Checking MongoDB Data

### View All Users
```bash
mongosh
use identity_spoofing_db
db.users.find()
```

### View All Verifications
```bash
db.verifications.find()
```

### View Access Logs
```bash
db.access_logs.find()
```

---

## 🌐 API Endpoints

### Enroll User
```bash
curl -X POST http://localhost:5000/api/enrollment/enroll-new-user \
  -F "name=John Doe" \
  -F "email=john@example.com" \
  -F "phone=123-456-7890" \
  -F "unit=Apt 101" \
  -F "proof_type=national_id" \
  -F "face_image=@photo.jpg"
```

### Search Users
```bash
curl http://localhost:5000/api/enrollment/search-users?query=john
```

### Verify Face
```bash
curl -X POST http://localhost:5000/api/enrollment/verify-user \
  -F "user_id=USER_ID_HERE" \
  -F "face_image=@photo.jpg"
```

---

## 🎨 System Pages

### Landing Page
- **URL**: Main page on startup
- **Features**: Two big buttons (Enroll / Verify)
- **Design**: Beautiful hero section

### Enroll User Page (Sidebar: 👤 Enroll User)
- **Step 1**: Enter personal info
- **Step 2**: Capture face with camera
- **Step 3**: Review details
- **Step 4**: Success confirmation

### Security Verification (Sidebar: 🔒 Verify Access)
- **Search**: Find users by name/email
- **Camera**: Capture verification photo
- **Match**: AI compares and shows %
- **Decision**: Approve ✅ or Deny ⛔

### Other Pages
- **Dashboard**: System overview
- **Live Verification**: Real-time stats
- **Analytics**: Charts and trends
- **Admin Panel**: User management
- **Settings**: Configuration

---

## 📋 File Structure

```
Identity-Spoofing-Detection/
├── backend/
│   ├── app.py                          # Main Flask app
│   ├── requirements.txt                # Python dependencies
│   ├── database/
│   │   └── mongodb_models.py           # MongoDB User/Verification models
│   ├── routes/
│   │   ├── enrollment_routes.py        # NEW: Enrollment API endpoints
│   │   └── ...other routes...
│   └── services/
│       ├── face_recognition_service.py # Face embedding & comparison
│       └── ...
├── frontend/
│   ├── src/
│   │   ├── App.jsx                     # Main app component
│   │   ├── NewUserEnrollment.jsx       # NEW: 4-step enrollment
│   │   ├── SecurityVerification.jsx    # NEW: Verification portal
│   │   ├── LandingPage.jsx             # NEW: Welcome page
│   │   └── ...other components...
│   └── package.json
└── HACKATHON_FINAL_REDESIGN.md         # This documentation
```

---

## 🎯 Key Features

✅ **Face Recognition**: DeepFace + FaceNet512
✅ **MongoDB Storage**: Production-ready database
✅ **Beautiful UI**: Modern gradient design
✅ **Camera Integration**: Real-time face capture
✅ **Verification Logic**: Instant face matching
✅ **Audit Logging**: Track all access
✅ **Responsive**: Works on all devices
✅ **API-First**: RESTful endpoints

---

## 📞 Common Commands

```bash
# Check if backend is running
curl http://localhost:5000/api/auth/health

# Check if frontend is running
curl http://localhost:3000

# Restart backend
pkill -f "python app.py"
cd backend && python app.py

# Restart frontend
npm start

# View backend logs
tail -f backend.log

# Test face enrollment
curl -F "name=Test" -F "email=test@test.com" ... \
  http://localhost:5000/api/enrollment/enroll-new-user
```

---

## 🏆 Success Indicators

✅ Backend running (no errors in console)
✅ Frontend loads in browser
✅ MongoDB connected
✅ Can enroll new user
✅ Can search user
✅ Can verify face
✅ Confidence score displays
✅ Grant/Deny works

---

## 🚀 Ready to Demo!

1. **Have two people ready** (one to enroll, one to verify)
2. **Start backend**: `cd backend && python app.py`
3. **Start frontend**: `cd frontend && npm start`
4. **Open browser**: http://localhost:3000
5. **First person**: Enroll their face
6. **Second person**: Search and verify access
7. **Impress judges** with beautiful UI + working AI! 🎉

---

## 💡 Pro Tips

- **Better lighting** = better face recognition
- **Dark background** = better face detection
- **Closer to camera** = better accuracy
- **Straight on** = best results
- **Remove distractions** = faster processing

---

**Status**: 🏆 Ready for judgment
**Last Updated**: 2024
**Version**: 2.0 - Hackathon Final Round

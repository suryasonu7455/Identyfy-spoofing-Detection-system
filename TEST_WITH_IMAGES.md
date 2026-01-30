# Testing with Face Images

## Quick Test (PowerShell)

### 1. Enroll a Face
```powershell
# Replace with your actual image path
$imagePath = "C:\path\to\your\photo.jpg"
$userId = 1  # User ID from database

$form = @{
    face_image = Get-Item -Path $imagePath
}

Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/auth/enroll-face/$userId" `
    -Method POST `
    -Form $form
```

### 2. Verify Access with Face
```powershell
$user = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/auth/user/1" -Method GET
$qrData = $user.credentials[0].qr_code_data

$body = @{
    user_id = 1
    credential_type = "qr_code"
    qr_data = $qrData
    live_image_path = "C:\path\to\live_photo.jpg"  # Image to verify
    entry_point = "Main Gate"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/access/verify-access" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

## What Happens

1. **Face Enrollment**: System extracts 128-dimensional face embedding using DeepFace
2. **Live Verification**: Compares live photo against enrolled embedding
3. **Match Score**: Returns confidence (0.0-1.0) - higher = better match
4. **Detection Triggers**:
   - **Low confidence (<0.6)**: Spoofing suspected
   - **Different person**: Creates security incident
   - **Multiple failures**: Flags user as high-risk

## Detection Scenarios

### ✅ Legitimate Access
- Same person's photo → High confidence (>0.85)
- Valid QR code
- Normal time/location pattern
- **Result**: Access granted

### 🚨 Spoofing Detected
- Different person's photo → Low confidence (<0.5)
- Or valid QR but wrong face
- **Result**: Access denied + incident created

### ⚠️ Suspicious Pattern
- Same person but unusual times (3 AM)
- Multiple entry points in short time
- Shared credentials (QR used by 2+ people)
- **Result**: Flagged for review

## Image Requirements

- **Format**: JPG, PNG
- **Size**: Any (system resizes)
- **Face**: Must be visible, front-facing
- **Quality**: Clear, well-lit preferred
- **Single face**: Works best with one face per image

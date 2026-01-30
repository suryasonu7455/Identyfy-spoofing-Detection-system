"""
Simple Test Script for Face Recognition
Upload a test image to see face detection in action
"""

import requests
import sys
from pathlib import Path

BASE_URL = "http://127.0.0.1:5000/api"

def test_face_enrollment(user_id, image_path):
    """Enroll a face image for a user"""
    print(f"\n🔍 Enrolling face for user {user_id}...")
    
    if not Path(image_path).exists():
        print(f"❌ Image not found: {image_path}")
        return False
    
    with open(image_path, 'rb') as img:
        files = {'face_image': img}
        response = requests.post(f"{BASE_URL}/auth/enroll-face/{user_id}", files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Face enrolled successfully!")
        print(f"   Model: {result.get('embedding_model', 'N/A')}")
        return True
    else:
        print(f"❌ Enrollment failed: {response.text}")
        return False


def test_access_verification(user_id, image_path):
    """Verify access with face image"""
    print(f"\n🚪 Testing access verification for user {user_id}...")
    
    # Get user's credential
    user_resp = requests.get(f"{BASE_URL}/auth/user/{user_id}")
    if user_resp.status_code != 200:
        print(f"❌ User {user_id} not found")
        return False
    
    user = user_resp.json()
    if not user.get('credentials'):
        print("❌ No credentials found for user")
        return False
    
    qr_data = user['credentials'][0]['qr_code_data']
    
    # Verify access
    payload = {
        "user_id": user_id,
        "credential_type": "qr_code",
        "qr_data": qr_data,
        "live_image_path": image_path,
        "entry_point": "Test Gate"
    }
    
    response = requests.post(f"{BASE_URL}/access/verify-access", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        granted = result['access_granted']
        details = result['verification_details']
        
        print(f"\n{'✅ ACCESS GRANTED' if granted else '🚫 ACCESS DENIED'}")
        print(f"   Face Match: {details.get('face_match', False)}")
        print(f"   Confidence: {details.get('face_confidence', 0):.2%}")
        print(f"   Risk Level: {details.get('risk_level', 'N/A')}")
        print(f"   Credential Valid: {details.get('credential_valid', False)}")
        
        return granted
    else:
        print(f"❌ Verification failed: {response.text}")
        return False


def demo_with_webcam():
    """Instructions for webcam testing"""
    print("\n📹 To test with webcam:")
    print("1. Take a photo using Windows Camera app")
    print("2. Save to: C:\\Users\\<you>\\Pictures\\Camera Roll\\")
    print("3. Run this script with that image path")
    print("\nExample:")
    print('  python test_face.py "C:\\Users\\gamer\\Pictures\\test.jpg"')


if __name__ == "__main__":
    print("=" * 60)
    print("🔐 Identity Spoofing Detection - Face Test")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("\nUsage: python test_face.py <path_to_image.jpg>")
        print("\nThis will:")
        print("  1. Enroll the face for User ID 1")
        print("  2. Test access verification with the same image")
        demo_with_webcam()
        sys.exit(1)
    
    image_path = sys.argv[1]
    user_id = 1  # Default to first demo user
    
    # Step 1: Enroll face
    if test_face_enrollment(user_id, image_path):
        print("\n⏳ Waiting 2 seconds...")
        import time
        time.sleep(2)
        
        # Step 2: Verify access
        test_access_verification(user_id, image_path)
    
    print("\n" + "=" * 60)
    print("💡 Tip: Try with a DIFFERENT person's photo to see spoofing detection!")
    print("=" * 60)

import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './FaceTest.css';

const API_URL = process.env.REACT_APP_API_URL || '/api';

function FaceTest() {
  const [selectedUser, setSelectedUser] = useState('1');
  const [enrollImage, setEnrollImage] = useState(null);
  const [verifyImage, setVerifyImage] = useState(null);
  const [enrollPreview, setEnrollPreview] = useState(null);
  const [verifyPreview, setVerifyPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // Camera states
  const [enrollCameraActive, setEnrollCameraActive] = useState(false);
  const [verifyCameraActive, setVerifyCameraActive] = useState(false);
  const enrollVideoRef = useRef(null);
  const verifyVideoRef = useRef(null);
  const enrollStreamRef = useRef(null);
  const verifyStreamRef = useRef(null);

  // Cleanup camera streams on unmount
  useEffect(() => {
    return () => {
      stopEnrollCamera();
      stopVerifyCamera();
    };
  }, []);

  const startEnrollCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 640, height: 480 } 
      });
      enrollStreamRef.current = stream;
      if (enrollVideoRef.current) {
        enrollVideoRef.current.srcObject = stream;
      }
      setEnrollCameraActive(true);
      setEnrollPreview(null);
    } catch (error) {
      alert('Camera access denied. Please allow camera access in your browser settings.');
      console.error('Camera error:', error);
    }
  };

  const stopEnrollCamera = () => {
    if (enrollStreamRef.current) {
      enrollStreamRef.current.getTracks().forEach(track => track.stop());
      enrollStreamRef.current = null;
    }
    setEnrollCameraActive(false);
  };

  const captureEnrollPhoto = () => {
    const video = enrollVideoRef.current;
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    
    canvas.toBlob((blob) => {
      if (blob) {
        const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' });
        setEnrollImage(file);
        setEnrollPreview(URL.createObjectURL(blob));
        stopEnrollCamera();
      }
    }, 'image/jpeg');
  };

  const startVerifyCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 640, height: 480 } 
      });
      verifyStreamRef.current = stream;
      if (verifyVideoRef.current) {
        verifyVideoRef.current.srcObject = stream;
      }
      setVerifyCameraActive(true);
      setVerifyPreview(null);
    } catch (error) {
      alert('Camera access denied. Please allow camera access in your browser settings.');
      console.error('Camera error:', error);
    }
  };

  const stopVerifyCamera = () => {
    if (verifyStreamRef.current) {
      verifyStreamRef.current.getTracks().forEach(track => track.stop());
      verifyStreamRef.current = null;
    }
    setVerifyCameraActive(false);
  };

  const captureVerifyPhoto = () => {
    const video = verifyVideoRef.current;
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    
    canvas.toBlob((blob) => {
      if (blob) {
        const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' });
        setVerifyImage(file);
        setVerifyPreview(URL.createObjectURL(blob));
        stopVerifyCamera();
      }
    }, 'image/jpeg');
  };

  const handleEnrollImageChange = (e) => {
    const file = e.target.files[0];
    if (file && file instanceof Blob) {
      setEnrollImage(file);
      setEnrollPreview(URL.createObjectURL(file));
    }
  };

  const handleVerifyImageChange = (e) => {
    const file = e.target.files[0];
    if (file && file instanceof Blob) {
      setVerifyImage(file);
      setVerifyPreview(URL.createObjectURL(file));
    }
  };

  const enrollFace = async () => {
    if (!enrollImage) {
      setResult({ error: 'Please select an image to enroll' });
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('face_image', enrollImage);

      const response = await axios.post(
        `${API_URL}/auth/enroll-face/${selectedUser}`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );

      setResult({
        success: true,
        message: '✅ Face enrolled successfully!',
        data: response.data
      });
    } catch (error) {
      setResult({
        error: true,
        message: '❌ Enrollment failed: ' + (error.response?.data?.error || error.message)
      });
    } finally {
      setLoading(false);
    }
  };

  const verifyAccess = async () => {
    if (!verifyImage) {
      setResult({ error: 'Please select an image to verify' });
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      // First get user's QR credential
      const userResp = await axios.get(`${API_URL}/auth/user/${selectedUser}`);
      const qrData = userResp.data.credentials?.[0]?.qr_code_data;

      if (!qrData) {
        setResult({ error: 'No credentials found for this user. Issue a credential first.' });
        setLoading(false);
        return;
      }

      // Upload image temporarily (for demo, we'll use a data URL)
      const reader = new FileReader();
      reader.onloadend = async () => {
        const payload = {
          user_id: parseInt(selectedUser),
          credential_type: 'qr_code',
          qr_data: qrData,
          live_image_path: reader.result, // Base64 image
          entry_point: 'Web Dashboard'
        };

        try {
          const response = await axios.post(`${API_URL}/access/verify-access`, payload);
          const { access_granted, verification_details } = response.data;

          setResult({
            success: access_granted,
            message: access_granted ? '✅ ACCESS GRANTED' : '🚫 ACCESS DENIED',
            details: {
              'Face Match': verification_details.face_match ? '✅' : '❌',
              'Confidence': `${(verification_details.face_confidence * 100).toFixed(1)}%`,
              'Risk Level': verification_details.risk_level,
              'Credential Valid': verification_details.credential_valid ? '✅' : '❌',
              'Behavioral Anomaly': verification_details.behavioral_anomaly ? '⚠️ Yes' : '✅ No'
            }
          });
        } catch (error) {
          setResult({
            error: true,
            message: '❌ Verification failed: ' + (error.response?.data?.error || error.message)
          });
        } finally {
          setLoading(false);
        }
      };
      reader.readAsDataURL(verifyImage);
    } catch (error) {
      setResult({
        error: true,
        message: '❌ Error: ' + (error.response?.data?.error || error.message)
      });
      setLoading(false);
    }
  };

  return (
    <div className="face-test-container">
      <div className="face-test-header">
        <h2>🎭 Face Detection Test</h2>
        <p>Upload images to test face enrollment and access verification</p>
      </div>

      <div className="user-selector">
        <label>Select User:</label>
        <select value={selectedUser} onChange={(e) => setSelectedUser(e.target.value)}>
          <option value="1">User 1 - Rahul Kumar</option>
          <option value="2">User 2 - Priya Singh</option>
          <option value="3">User 3 - Security Staff</option>
        </select>
      </div>

      <div className="test-sections">
        <div className="test-section">
          <h3>1️⃣ Enroll Face</h3>
          <p className="section-desc">Upload a photo to register this user's face</p>
          
          <div className="camera-controls">
            <button 
              className="camera-toggle-btn"
              onClick={enrollCameraActive ? stopEnrollCamera : startEnrollCamera}
            >
              {enrollCameraActive ? '📷 Stop Camera' : '📹 Use Camera'}
            </button>
          </div>

          {enrollCameraActive ? (
            <div className="camera-view">
              <video ref={enrollVideoRef} autoPlay playsInline />
              <button className="capture-btn" onClick={captureEnrollPhoto}>
                📸 Capture Photo
              </button>
            </div>
          ) : (
            <>
              <div className="upload-area">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleEnrollImageChange}
                  id="enroll-upload"
                />
                <label htmlFor="enroll-upload" className="upload-label">
                  {enrollPreview ? '📷 Change Photo' : '📁 Choose Photo'}
                </label>
              </div>

              {enrollPreview && (
                <div className="image-preview">
                  <img src={enrollPreview} alt="Enroll preview" />
                </div>
              )}
            </>
          )}

          <button
            className="action-btn enroll-btn"
            onClick={enrollFace}
            disabled={loading || !enrollImage}
          >
            {loading ? '⏳ Enrolling...' : '✅ Enroll Face'}
          </button>
        </div>

        <div className="test-section">
          <h3>2️⃣ Verify Access</h3>
          <p className="section-desc">Upload a photo to test identity verification</p>
          
          <div className="camera-controls">
            <button 
              className="camera-toggle-btn"
              onClick={verifyCameraActive ? stopVerifyCamera : startVerifyCamera}
            >
              {verifyCameraActive ? '📷 Stop Camera' : '📹 Use Camera'}
            </button>
          </div>

          {verifyCameraActive ? (
            <div className="camera-view">
              <video ref={verifyVideoRef} autoPlay playsInline />
              <button className="capture-btn" onClick={captureVerifyPhoto}>
                📸 Capture Photo
              </button>
            </div>
          ) : (
            <>
              <div className="upload-area">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleVerifyImageChange}
                  id="verify-upload"
                />
                <label htmlFor="verify-upload" className="upload-label">
                  {verifyPreview ? '📷 Change Photo' : '📁 Choose Photo'}
                </label>
              </div>

              {verifyPreview && (
                <div className="image-preview">
                  <img src={verifyPreview} alt="Verify preview" />
                </div>
              )}
            </>
          )}

          <button
            className="action-btn verify-btn"
            onClick={verifyAccess}
            disabled={loading || !verifyImage}
          >
            {loading ? '⏳ Verifying...' : '🔍 Verify Access'}
          </button>
        </div>
      </div>

      {result && (
        <div className={`result-box ${result.success ? 'success' : result.error ? 'error' : 'info'}`}>
          <h3>{result.message}</h3>
          {result.details && (
            <div className="result-details">
              {Object.entries(result.details).map(([key, value]) => (
                <div key={key} className="detail-row">
                  <span className="detail-label">{key}:</span>
                  <span className="detail-value">{value}</span>
                </div>
              ))}
            </div>
          )}
          {result.data && (
            <pre className="result-json">{JSON.stringify(result.data, null, 2)}</pre>
          )}
        </div>
      )}

      <div className="instructions">
        <h4>💡 How to Test:</h4>
        <ol>
          <li><strong>Enroll</strong>: Upload YOUR photo first</li>
          <li><strong>Verify with same photo</strong>: Should show ACCESS GRANTED ✅</li>
          <li><strong>Verify with different person</strong>: Should DENY + flag as spoofing 🚨</li>
        </ol>
      </div>
    </div>
  );
}

export default FaceTest;

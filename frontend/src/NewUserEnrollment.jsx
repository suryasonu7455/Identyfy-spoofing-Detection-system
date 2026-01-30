import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './NewUserEnrollment.css';

function NewUserEnrollment({ onSuccess }) {
  const [step, setStep] = useState(1); // 1: Info, 2: Camera, 3: Review
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [cameraActive, setCameraActive] = useState(false);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    unit: '',
    proofType: 'national_id'
  });

  const [capturedPhoto, setCapturedPhoto] = useState(null);
  const [photoPreview, setPhotoPreview] = useState(null);

  const proofTypes = [
    { value: 'national_id', label: '🆔 National ID' },
    { value: 'passport', label: '📕 Passport' },
    { value: 'license', label: '🚗 Driving License' },
    { value: 'voter_id', label: '🗳️ Voter ID' },
    { value: 'employee_card', label: '💼 Employee Card' }
  ];

  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError(null);
  };

  const startCamera = async () => {
    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { 
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user'
        },
        audio: false
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        // Wait for video to load
        videoRef.current.onloadedmetadata = () => {
          videoRef.current.play().catch(e => console.log('Play error:', e));
          setCameraActive(true);
        };
      }
    } catch (err) {
      setError('❌ Camera access denied. Please allow camera permissions in browser settings.');
      console.error('Camera error:', err);
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setCameraActive(false);
  };

  const capturePhoto = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (!video) {
      setError('❌ Video element not found. Please refresh and try again.');
      return;
    }

    // Wait for video to be ready
    if (video.readyState !== video.HAVE_ENOUGH_DATA) {
      setError('⏳ Camera is loading... Please wait a moment.');
      setTimeout(capturePhoto, 500);
      return;
    }

    if (!video.videoWidth || !video.videoHeight) {
      setError('❌ Camera feed not ready. Please wait and try again.');
      setTimeout(capturePhoto, 500);
      return;
    }

    try {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      
      if (!ctx) {
        setError('❌ Canvas error. Please refresh and try again.');
        return;
      }

      // Mirror the image
      ctx.translate(canvas.width, 0);
      ctx.scale(-1, 1);
      ctx.drawImage(video, 0, 0);
      ctx.translate(canvas.width, 0);
      ctx.scale(-1, 1);
      
      canvas.toBlob((blob) => {
        if (blob) {
          setCapturedPhoto(blob);
          setPhotoPreview(URL.createObjectURL(blob));
          stopCamera();
          setStep(3); // Go to review
        } else {
          setError('❌ Failed to capture photo.');
        }
      }, 'image/jpeg', 0.95);
    } catch (err) {
      setError(`❌ Capture error: ${err.message}`);
      console.error('Capture error:', err);
    }
  };

  const validateStep1 = () => {
    if (!formData.name.trim()) return '❌ Name is required';
    if (!formData.email.trim()) return '❌ Email is required';
    if (!formData.phone.trim()) return '❌ Phone is required';
    if (!formData.unit.trim()) return '❌ Unit/Address is required';
    return null;
  };

  const submitEnrollment = async () => {
    if (!capturedPhoto) {
      setError('❌ Photo capture failed. Please try again.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formDataToSend = new FormData();
      formDataToSend.append('name', formData.name);
      formDataToSend.append('email', formData.email);
      formDataToSend.append('phone', formData.phone);
      formDataToSend.append('unit', formData.unit);
      formDataToSend.append('proof_type', formData.proofType);
      formDataToSend.append('face_image', capturedPhoto);

      const response = await axios.post(
        '/api/enrollment/enroll-new-user',
        formDataToSend,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );

      if (response.data.success) {
        setStep(4); // Success screen
        if (onSuccess) {
          setTimeout(onSuccess, 2000);
        }
      } else {
        setError(`❌ ${response.data.error || 'Enrollment failed'}`);
      }
    } catch (err) {
      setError(`❌ ${err.response?.data?.error || err.message}`);
      console.error('Enrollment error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="enrollment-container">
      <div className="enrollment-header">
        <h1>🎯 New User Enrollment</h1>
        <p>Create your secure identity profile</p>
        <div className="progress-bar">
          <div className={`step ${step >= 1 ? 'active' : ''}`}>1</div>
          <div className={`step ${step >= 2 ? 'active' : ''}`}>2</div>
          <div className={`step ${step >= 3 ? 'active' : ''}`}>3</div>
          <div className={`step ${step >= 4 ? 'active' : ''}`}>✓</div>
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {/* Step 1: User Information */}
      {step === 1 && (
        <div className="enrollment-section">
          <h2>📋 Personal Information</h2>
          <div>
            <div className="form-group">
              <label>Full Name *</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                placeholder="Enter your full name"
              />
            </div>

            <div className="form-group">
              <label>Email Address *</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="your@email.com"
              />
            </div>

            <div className="form-group">
              <label>Phone Number *</label>
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleInputChange}
                placeholder="+91 98765 43210"
              />
            </div>

            <div className="form-group">
              <label>Unit / Address *</label>
              <input
                type="text"
                name="unit"
                value={formData.unit}
                onChange={handleInputChange}
                placeholder="e.g., A-101, Block 2"
              />
            </div>

            <div className="form-group">
              <label>Proof Type *</label>
              <select name="proofType" value={formData.proofType} onChange={handleInputChange}>
                {proofTypes.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            <button
              className="btn-primary"
              onClick={() => {
                const validation = validateStep1();
                if (validation) {
                  setError(validation);
                } else {
                  setStep(2);
                }
              }}
            >
              Continue to Face Capture →
            </button>
          </div>
        </div>
      )}

      {/* Step 2: Face Capture */}
      {step === 2 && (
        <div className="enrollment-section">
          <h2>📸 Capture Your Face</h2>
          <p className="instruction">Please ensure good lighting and face the camera directly</p>

          {!cameraActive ? (
            <div className="camera-starter">
              <div className="camera-icon">📷</div>
              <button className="btn-primary" onClick={startCamera}>
                Start Camera
              </button>
            </div>
          ) : (
            <div className="camera-setup">
              <div className="video-container">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
                <canvas ref={canvasRef} style={{ display: 'none' }} />
                <div className="camera-guide">
                  <div className="face-oval"></div>
                  <p>Position your face in the circle</p>
                </div>
              </div>

              <div className="camera-buttons">
                <button className="btn-capture" onClick={capturePhoto}>
                  📸 Capture Photo
                </button>
                <button className="btn-secondary" onClick={stopCamera}>
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Step 3: Review */}
      {step === 3 && (
        <div className="enrollment-section">
          <h2>✅ Review Your Enrollment</h2>

          <div className="review-grid">
            <div className="review-info">
              <h3>Personal Details</h3>
              <p><strong>Name:</strong> {formData.name}</p>
              <p><strong>Email:</strong> {formData.email}</p>
              <p><strong>Phone:</strong> {formData.phone}</p>
              <p><strong>Unit:</strong> {formData.unit}</p>
              <p><strong>Proof Type:</strong> {proofTypes.find(t => t.value === formData.proofType)?.label}</p>
            </div>

            <div className="review-photo">
              <h3>Your Face</h3>
              <img src={photoPreview} alt="Captured face" />
            </div>
          </div>

          <div className="review-buttons">
            <button className="btn-secondary" onClick={() => setStep(2)}>
              ← Retake Photo
            </button>
            <button
              className="btn-primary"
              onClick={submitEnrollment}
              disabled={loading}
            >
              {loading ? '⏳ Enrolling...' : '✅ Complete Enrollment'}
            </button>
          </div>
        </div>
      )}

      {/* Step 4: Success */}
      {step === 4 && (
        <div className="enrollment-section success-section">
          <div className="success-icon">🎉</div>
          <h2>Enrollment Successful!</h2>
          <p className="success-message">
            Welcome {formData.name}! Your identity has been securely registered.
          </p>
          <div className="success-details">
            <p>✅ Face recognized and stored</p>
            <p>✅ Profile created successfully</p>
            <p>✅ Ready for verification</p>
          </div>
          <button className="btn-primary" onClick={() => window.location.reload()}>
            Go to Home
          </button>
        </div>
      )}
    </div>
  );
}

export default NewUserEnrollment;

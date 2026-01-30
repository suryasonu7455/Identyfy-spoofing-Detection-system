import React, { useState, useRef } from 'react';
import axios from 'axios';
import './SecurityVerification.css';

function SecurityVerification() {
  const [phase, setPhase] = useState('search'); // search, verify, result
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [cameraActive, setCameraActive] = useState(false);

  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);

  const [verificationResult, setVerificationResult] = useState(null);

  const searchUsers = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      setError('❌ Please enter a name or email to search');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await axios.get(
        `/api/enrollment/search-users?query=${encodeURIComponent(searchQuery)}`
      );

      if (response.data.success) {
        setSearchResults(response.data.users);
        if (response.data.users.length === 0) {
          setError('❌ No users found. They may need to enroll first.');
        }
      } else {
        setError('❌ Search failed');
      }
    } catch (err) {
      setError(`❌ ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const selectUserForVerification = (user) => {
    setSelectedUser(user);
    setSearchResults([]);
    setSearchQuery('');
    setPhase('verify');
    setError(null);
    setSuccess(null);
  };

  const startCamera = async () => {
    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 }
        }
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setCameraActive(true);
    } catch (err) {
      setError('❌ Camera access denied. Please allow camera permissions.');
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
    }
    setCameraActive(false);
  };

  const captureAndVerify = async () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (!video || !video.videoWidth) {
      setError('❌ Camera not ready. Please wait.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0);

      canvas.toBlob(async (blob) => {
        if (!blob) {
          setError('❌ Failed to capture photo');
          setLoading(false);
          return;
        }

        try {
          const formData = new FormData();
          formData.append('face_image', blob);
          formData.append('user_id', selectedUser._id);

          const response = await axios.post(
            '/api/enrollment/verify-user',
            formData,
            { headers: { 'Content-Type': 'multipart/form-data' } }
          );

          setVerificationResult(response.data);
          setPhase('result');
          stopCamera();

          if (response.data.match) {
            setSuccess('✅ Face matched! Ready to grant/deny access.');
          } else {
            setError('❌ Face does not match. Access denied.');
          }
        } catch (err) {
          setError(`❌ ${err.response?.data?.error || err.message}`);
        } finally {
          setLoading(false);
        }
      }, 'image/jpeg', 0.95);
    } catch (err) {
      setError('❌ Verification failed');
      setLoading(false);
    }
  };

  const grantAccess = async () => {
    setLoading(true);
    try {
      const response = await axios.post('/api/enrollment/grant-access', {
        user_id: selectedUser._id,
        verification_id: verificationResult.verification_id,
        notes: 'Verified by security officer'
      });

      if (response.data.success) {
        setSuccess(`✅ Access GRANTED to ${selectedUser.name}`);
        setError(null);
        setTimeout(() => resetVerification(), 3000);
      }
    } catch (err) {
      setError(`❌ ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const denyAccess = async () => {
    setLoading(true);
    try {
      const response = await axios.post('/api/enrollment/deny-access', {
        user_id: selectedUser._id,
        verification_id: verificationResult.verification_id,
        notes: 'Denied by security officer'
      });

      if (response.data.success) {
        setError(`⛔ Access DENIED to ${selectedUser.name}`);
        setSuccess(null);
        setTimeout(() => resetVerification(), 3000);
      }
    } catch (err) {
      setError(`❌ ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const resetVerification = () => {
    setPhase('search');
    setSelectedUser(null);
    setVerificationResult(null);
    setSearchQuery('');
    setError(null);
    setSuccess(null);
  };

  return (
    <div className="verification-container">
      <div className="verification-header">
        <h1>🔒 Security Verification Portal</h1>
        <p>Verify user identity and grant/deny access</p>
      </div>

      {error && <div className="error-banner">{error}</div>}
      {success && <div className="success-banner">{success}</div>}

      {/* Phase 1: Search User */}
      {phase === 'search' && (
        <div className="verification-card">
          <h2>🔍 Search User</h2>
          <p>Find registered users to verify</p>

          <form onSubmit={searchUsers}>
            <div className="search-box">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Enter name or email..."
                className="search-input"
              />
              <button type="submit" disabled={loading} className="btn-search">
                {loading ? '🔍 Searching...' : '🔍 Search'}
              </button>
            </div>
          </form>

          {searchResults.length > 0 && (
            <div className="results-list">
              <h3>Found {searchResults.length} user(s):</h3>
              {searchResults.map((user) => (
                <div key={user._id} className="user-result">
                  <div className="result-info">
                    <h4>{user.name}</h4>
                    <p>📧 {user.email}</p>
                    <p>📱 {user.phone}</p>
                    <p>🏠 {user.unit}</p>
                    <p className="proof-type">
                      {user.proof_type === 'national_id' && '🆔 National ID'}
                      {user.proof_type === 'passport' && '📕 Passport'}
                      {user.proof_type === 'license' && '🚗 License'}
                      {user.proof_type === 'voter_id' && '🗳️ Voter ID'}
                      {user.proof_type === 'employee_card' && '💼 Employee Card'}
                    </p>
                  </div>
                  <button
                    className="btn-select"
                    onClick={() => selectUserForVerification(user)}
                  >
                    Select →
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Phase 2: Verify */}
      {phase === 'verify' && selectedUser && (
        <div className="verification-card">
          <div className="user-header">
            <h2>✅ Verifying: {selectedUser.name}</h2>
            <button className="btn-back" onClick={() => resetVerification()}>
              ← Back to Search
            </button>
          </div>

          <div className="verification-info">
            <p><strong>Email:</strong> {selectedUser.email}</p>
            <p><strong>Phone:</strong> {selectedUser.phone}</p>
            <p><strong>Unit:</strong> {selectedUser.unit}</p>
            <p><strong>Status:</strong> <span className="status-badge active">{selectedUser.status}</span></p>
          </div>

          {!cameraActive ? (
            <div className="camera-starter">
              <p className="instruction">Capture the person's face to verify</p>
              <button className="btn-primary" onClick={startCamera}>
                📷 Start Camera
              </button>
            </div>
          ) : (
            <div className="camera-verification">
              <div className="video-container">
                <video ref={videoRef} autoPlay playsInline muted />
                <canvas ref={canvasRef} style={{ display: 'none' }} />
                <div className="camera-overlay">
                  <div className="face-guide">Position face in frame</div>
                </div>
              </div>

              <div className="verification-controls">
                <button
                  className="btn-capture"
                  onClick={captureAndVerify}
                  disabled={loading}
                >
                  {loading ? '⏳ Verifying...' : '📸 Capture & Verify'}
                </button>
                <button className="btn-secondary" onClick={stopCamera}>
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Phase 3: Result */}
      {phase === 'result' && verificationResult && (
        <div className="verification-card">
          <h2>{verificationResult.match ? '✅ Match Found!' : '❌ No Match'}</h2>

          <div className="result-details">
            <div className="match-score">
              <p><strong>Similarity Score:</strong></p>
              <div className="score-bar">
                <div
                  className={`score-fill ${verificationResult.match ? 'high' : 'low'}`}
                  style={{
                    width: `${(verificationResult.confidence || 0) * 100}%`
                  }}
                ></div>
              </div>
              <p className="score-value">{((verificationResult.confidence || 0) * 100).toFixed(1)}%</p>
            </div>

            {verificationResult.match && (
              <div className="decision-section">
                <p className="decision-question">Grant access to {selectedUser.name}?</p>
                <div className="decision-buttons">
                  <button
                    className="btn-grant"
                    onClick={grantAccess}
                    disabled={loading}
                  >
                    ✅ Grant Access
                  </button>
                  <button
                    className="btn-deny"
                    onClick={denyAccess}
                    disabled={loading}
                  >
                    ⛔ Deny Access
                  </button>
                </div>
              </div>
            )}

            {!verificationResult.match && (
              <div className="deny-section">
                <p className="deny-message">⚠️ Face does not match registered user.</p>
                <button className="btn-primary" onClick={() => resetVerification()}>
                  Search Another User
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default SecurityVerification;

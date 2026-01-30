import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './LiveVerification.css';

function LiveVerification() {
  const [isStreaming, setIsStreaming] = useState(false);
  const [verificationResult, setVerificationResult] = useState(null);
  const [qrCode, setQrCode] = useState('');
  const [logs, setLogs] = useState([]);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 640, height: 480 } 
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        setIsStreaming(true);
        addLog('Camera started successfully', 'success');
      }
    } catch (error) {
      addLog('Camera access denied: ' + error.message, 'error');
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      setIsStreaming(false);
      addLog('Camera stopped', 'info');
    }
  };

  const captureAndVerify = async () => {
    if (!videoRef.current || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const video = videoRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);

    canvas.toBlob(async (blob) => {
      const formData = new FormData();
      formData.append('image', blob, 'capture.jpg');
      formData.append('qr_data', qrCode);

      addLog('Sending verification request...', 'info');

      try {
        const response = await axios.post('http://localhost:5000/api/access/verify-access', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });

        setVerificationResult(response.data);
        addLog(`Verification ${response.data.access_granted ? 'SUCCESS' : 'DENIED'}`, 
          response.data.access_granted ? 'success' : 'error');
      } catch (error) {
        addLog('Verification failed: ' + error.message, 'error');
        setVerificationResult({ 
          access_granted: false, 
          reason: 'Network error',
          error: error.message 
        });
      }
    }, 'image/jpeg');
  };

  const addLog = (message, type) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [{timestamp, message, type}, ...prev.slice(0, 19)]);
  };

  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  return (
    <div className="live-verification">
      <div className="page-header">
        <h1>Live Identity Verification</h1>
        <p>Real-time face recognition and QR code validation</p>
      </div>

      <div className="verification-layout">
        <div className="camera-section">
          <div className="camera-container">
            <video 
              ref={videoRef} 
              autoPlay 
              playsInline
              className={isStreaming ? 'active' : ''}
            />
            <canvas ref={canvasRef} style={{display: 'none'}} />
            
            {!isStreaming && (
              <div className="camera-placeholder">
                <span className="camera-icon">📹</span>
                <p>Camera is off</p>
                <button onClick={startCamera} className="btn-primary">
                  Start Camera
                </button>
              </div>
            )}

            {verificationResult && (
              <div className={`verification-overlay ${verificationResult.access_granted ? 'success' : 'denied'}`}>
                <div className="result-icon">
                  {verificationResult.access_granted ? '✓' : '✗'}
                </div>
                <h3>{verificationResult.access_granted ? 'Access Granted' : 'Access Denied'}</h3>
                <p>{verificationResult.reason || verificationResult.message}</p>
              </div>
            )}
          </div>

          <div className="camera-controls">
            {isStreaming ? (
              <>
                <button onClick={captureAndVerify} className="btn-verify">
                  🔍 Verify Identity
                </button>
                <button onClick={stopCamera} className="btn-secondary">
                  ⏹️ Stop Camera
                </button>
              </>
            ) : (
              <button onClick={startCamera} className="btn-primary">
                ▶️ Start Camera
              </button>
            )}
          </div>
        </div>

        <div className="control-panel">
          <div className="qr-input-section">
            <h3>QR Code / Credential ID</h3>
            <input 
              type="text"
              value={qrCode}
              onChange={(e) => setQrCode(e.target.value)}
              placeholder="Scan or enter QR code data"
              className="qr-input"
            />
            <button className="btn-scan">📱 Scan QR Code</button>
          </div>

          <div className="verification-stats">
            <h3>Live Statistics</h3>
            <div className="stat-grid">
              <div className="stat-item">
                <span className="stat-value">156</span>
                <span className="stat-label">Today's Verifications</span>
              </div>
              <div className="stat-item success">
                <span className="stat-value">142</span>
                <span className="stat-label">Successful</span>
              </div>
              <div className="stat-item warning">
                <span className="stat-value">14</span>
                <span className="stat-label">Denied</span>
              </div>
            </div>
          </div>

          <div className="activity-log">
            <h3>Activity Log</h3>
            <div className="log-container">
              {logs.map((log, index) => (
                <div key={index} className={`log-entry ${log.type}`}>
                  <span className="log-time">{log.timestamp}</span>
                  <span className="log-message">{log.message}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LiveVerification;

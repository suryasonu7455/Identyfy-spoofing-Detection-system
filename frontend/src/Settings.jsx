import React, { useState } from 'react';
import './Settings.css';

function Settings() {
  const [settings, setSettings] = useState({
    faceRecognitionThreshold: 0.4,
    qrExpiryHours: 24,
    anomalyDetectionEnabled: true,
    realTimeAlertsEnabled: true,
    autoBlockSuspiciousUsers: false,
    emailNotifications: true,
    smsNotifications: false,
    maxFailedAttempts: 3,
    sessionTimeout: 30,
    dataRetentionDays: 90
  });

  const handleChange = (key, value) => {
    setSettings({...settings, [key]: value});
  };

  const handleSave = () => {
    // Save settings to backend
    alert('Settings saved successfully!');
  };

  return (
    <div className="settings-page">
      <div className="page-header">
        <h1>System Settings</h1>
        <p>Configure security parameters and system behavior</p>
      </div>

      <div className="settings-container">
        <div className="settings-section">
          <h2>🔐 Security Settings</h2>
          <div className="setting-item">
            <div className="setting-info">
              <label>Face Recognition Threshold</label>
              <p>Lower values = stricter matching (0.0 - 1.0)</p>
            </div>
            <div className="setting-control">
              <input 
                type="range" 
                min="0" 
                max="1" 
                step="0.05"
                value={settings.faceRecognitionThreshold}
                onChange={(e) => handleChange('faceRecognitionThreshold', parseFloat(e.target.value))}
              />
              <span className="value-display">{settings.faceRecognitionThreshold}</span>
            </div>
          </div>

          <div className="setting-item">
            <div className="setting-info">
              <label>QR Code Expiry (Hours)</label>
              <p>How long QR codes remain valid</p>
            </div>
            <div className="setting-control">
              <input 
                type="number" 
                min="1" 
                max="168"
                value={settings.qrExpiryHours}
                onChange={(e) => handleChange('qrExpiryHours', parseInt(e.target.value))}
              />
            </div>
          </div>

          <div className="setting-item">
            <div className="setting-info">
              <label>Max Failed Attempts</label>
              <p>Block user after this many failed attempts</p>
            </div>
            <div className="setting-control">
              <input 
                type="number" 
                min="1" 
                max="10"
                value={settings.maxFailedAttempts}
                onChange={(e) => handleChange('maxFailedAttempts', parseInt(e.target.value))}
              />
            </div>
          </div>

          <div className="setting-item">
            <div className="setting-info">
              <label>Auto-Block Suspicious Users</label>
              <p>Automatically suspend flagged accounts</p>
            </div>
            <div className="setting-control">
              <label className="toggle-switch">
                <input 
                  type="checkbox"
                  checked={settings.autoBlockSuspiciousUsers}
                  onChange={(e) => handleChange('autoBlockSuspiciousUsers', e.target.checked)}
                />
                <span className="slider"></span>
              </label>
            </div>
          </div>
        </div>

        <div className="settings-section">
          <h2>🔔 Notification Settings</h2>
          
          <div className="setting-item">
            <div className="setting-info">
              <label>Real-Time Alerts</label>
              <p>Show instant security notifications</p>
            </div>
            <div className="setting-control">
              <label className="toggle-switch">
                <input 
                  type="checkbox"
                  checked={settings.realTimeAlertsEnabled}
                  onChange={(e) => handleChange('realTimeAlertsEnabled', e.target.checked)}
                />
                <span className="slider"></span>
              </label>
            </div>
          </div>

          <div className="setting-item">
            <div className="setting-info">
              <label>Email Notifications</label>
              <p>Send alerts via email</p>
            </div>
            <div className="setting-control">
              <label className="toggle-switch">
                <input 
                  type="checkbox"
                  checked={settings.emailNotifications}
                  onChange={(e) => handleChange('emailNotifications', e.target.checked)}
                />
                <span className="slider"></span>
              </label>
            </div>
          </div>

          <div className="setting-item">
            <div className="setting-info">
              <label>SMS Notifications</label>
              <p>Send alerts via SMS</p>
            </div>
            <div className="setting-control">
              <label className="toggle-switch">
                <input 
                  type="checkbox"
                  checked={settings.smsNotifications}
                  onChange={(e) => handleChange('smsNotifications', e.target.checked)}
                />
                <span className="slider"></span>
              </label>
            </div>
          </div>
        </div>

        <div className="settings-section">
          <h2>🤖 AI & Detection</h2>
          
          <div className="setting-item">
            <div className="setting-info">
              <label>Anomaly Detection</label>
              <p>Enable behavioral pattern analysis</p>
            </div>
            <div className="setting-control">
              <label className="toggle-switch">
                <input 
                  type="checkbox"
                  checked={settings.anomalyDetectionEnabled}
                  onChange={(e) => handleChange('anomalyDetectionEnabled', e.target.checked)}
                />
                <span className="slider"></span>
              </label>
            </div>
          </div>
        </div>

        <div className="settings-section">
          <h2>💾 Data Management</h2>
          
          <div className="setting-item">
            <div className="setting-info">
              <label>Session Timeout (minutes)</label>
              <p>Auto-logout after inactivity</p>
            </div>
            <div className="setting-control">
              <input 
                type="number" 
                min="5" 
                max="120"
                value={settings.sessionTimeout}
                onChange={(e) => handleChange('sessionTimeout', parseInt(e.target.value))}
              />
            </div>
          </div>

          <div className="setting-item">
            <div className="setting-info">
              <label>Data Retention (days)</label>
              <p>Keep logs for compliance</p>
            </div>
            <div className="setting-control">
              <input 
                type="number" 
                min="30" 
                max="365"
                value={settings.dataRetentionDays}
                onChange={(e) => handleChange('dataRetentionDays', parseInt(e.target.value))}
              />
            </div>
          </div>

          <div className="setting-item danger-zone">
            <div className="setting-info">
              <label>⚠️ Danger Zone</label>
              <p>Irreversible actions</p>
            </div>
            <div className="setting-control">
              <button className="btn-danger">Clear All Logs</button>
              <button className="btn-danger">Reset All Settings</button>
            </div>
          </div>
        </div>
      </div>

      <div className="settings-footer">
        <button className="btn-secondary">Cancel</button>
        <button className="btn-primary" onClick={handleSave}>💾 Save Changes</button>
      </div>
    </div>
  );
}

export default Settings;

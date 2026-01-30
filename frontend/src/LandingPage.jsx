import React from 'react';
import './LandingPage.css';

function LandingPage({ onSelectEnroll, onSelectVerify }) {
  return (
    <div className="landing-container">
      <div className="landing-background">
        <div className="gradient-blob blob-1"></div>
        <div className="gradient-blob blob-2"></div>
        <div className="gradient-blob blob-3"></div>
      </div>

      <div className="landing-content">
        <header className="landing-header">
          <div className="header-icon">🛡️</div>
          <h1>SecureGuard AI</h1>
          <p className="header-subtitle">Identity Spoofing Detection & Access Control</p>
          <p className="header-description">
            Advanced face recognition system for secure facility access management
          </p>
        </header>

        <div className="options-grid">
          {/* Enroll Option */}
          <div className="option-card enroll-card">
            <div className="option-icon">👤</div>
            <h2>Enroll New User</h2>
            <p className="option-description">
              Register a new user with face recognition. First-time users enroll here.
            </p>

            <div className="option-features">
              <div className="feature">✓ Identity Verification</div>
              <div className="feature">✓ Face Capture</div>
              <div className="feature">✓ Document Upload</div>
              <div className="feature">✓ Proof of Identity</div>
            </div>

            <div className="option-flow">
              <div className="flow-step">
                <div className="step-number">1</div>
                <div className="step-text">Enter Information</div>
              </div>
              <div className="flow-arrow">→</div>
              <div className="flow-step">
                <div className="step-number">2</div>
                <div className="step-text">Capture Face</div>
              </div>
              <div className="flow-arrow">→</div>
              <div className="flow-step">
                <div className="step-number">3</div>
                <div className="step-text">Review & Submit</div>
              </div>
            </div>

            <button className="option-button enroll-button" onClick={onSelectEnroll}>
              Start Enrollment →
            </button>
          </div>

          {/* Verify Option */}
          <div className="option-card verify-card">
            <div className="option-icon">🔒</div>
            <h2>Security Verification</h2>
            <p className="option-description">
              Verify enrolled users for access. Security staff verifies identities.
            </p>

            <div className="option-features">
              <div className="feature">✓ User Search</div>
              <div className="feature">✓ Face Verification</div>
              <div className="feature">✓ Grant/Deny Access</div>
              <div className="feature">✓ Audit Trail</div>
            </div>

            <div className="option-flow">
              <div className="flow-step">
                <div className="step-number">1</div>
                <div className="step-text">Search User</div>
              </div>
              <div className="flow-arrow">→</div>
              <div className="flow-step">
                <div className="step-number">2</div>
                <div className="step-text">Verify Face</div>
              </div>
              <div className="flow-arrow">→</div>
              <div className="flow-step">
                <div className="step-number">3</div>
                <div className="step-text">Decision</div>
              </div>
            </div>

            <button className="option-button verify-button" onClick={onSelectVerify}>
              Verify Access →
            </button>
          </div>
        </div>

        <footer className="landing-footer">
          <p>🔐 Enterprise-grade security powered by AI face recognition</p>
          <p className="footer-detail">For authorized personnel only</p>
        </footer>
      </div>
    </div>
  );
}

export default LandingPage;

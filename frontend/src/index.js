import React, { useState } from 'react';
import ReactDOM from 'react-dom/client';
import Dashboard from './Dashboard';
import FaceTest from './FaceTest';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  return (
    <div className="app-container">
      <nav className="app-nav">
        <h1>🛡️ Identity Spoofing Detection</h1>
        <div className="nav-tabs">
          <button
            className={activeTab === 'dashboard' ? 'active' : ''}
            onClick={() => setActiveTab('dashboard')}
          >
            📊 Dashboard
          </button>
          <button
            className={activeTab === 'facetest' ? 'active' : ''}
            onClick={() => setActiveTab('facetest')}
          >
            🎭 Face Test
          </button>
        </div>
      </nav>
      <div className="app-content">
        {activeTab === 'dashboard' ? <Dashboard /> : <FaceTest />}
      </div>
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

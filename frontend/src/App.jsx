import React, { useState } from 'react';
import './App.css';
import Dashboard from './Dashboard';
import LiveVerification from './LiveVerification';
import AdminPanel from './AdminPanel';
import Analytics from './Analytics';
import Settings from './Settings';

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');

  const renderPage = () => {
    switch(currentPage) {
      case 'dashboard':
        return <Dashboard />;
      case 'live':
        return <LiveVerification />;
      case 'admin':
        return <AdminPanel />;
      case 'analytics':
        return <Analytics />;
      case 'settings':
        return <Settings />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="app-container">
      <nav className="sidebar">
        <div className="logo-section">
          <div className="logo-icon">🛡️</div>
          <h2>SecureGuard AI</h2>
          <p className="tagline">Identity Protection System</p>
        </div>
        
        <div className="nav-menu">
          <button 
            className={`nav-item ${currentPage === 'dashboard' ? 'active' : ''}`}
            onClick={() => setCurrentPage('dashboard')}
          >
            <span className="nav-icon">📊</span>
            <span>Dashboard</span>
          </button>
          
          <button 
            className={`nav-item ${currentPage === 'live' ? 'active' : ''}`}
            onClick={() => setCurrentPage('live')}
          >
            <span className="nav-icon">📹</span>
            <span>Live Verification</span>
          </button>
          
          <button 
            className={`nav-item ${currentPage === 'analytics' ? 'active' : ''}`}
            onClick={() => setCurrentPage('analytics')}
          >
            <span className="nav-icon">📈</span>
            <span>Analytics</span>
          </button>
          
          <button 
            className={`nav-item ${currentPage === 'admin' ? 'active' : ''}`}
            onClick={() => setCurrentPage('admin')}
          >
            <span className="nav-icon">👥</span>
            <span>Admin Panel</span>
          </button>
          
          <button 
            className={`nav-item ${currentPage === 'settings' ? 'active' : ''}`}
            onClick={() => setCurrentPage('settings')}
          >
            <span className="nav-icon">⚙️</span>
            <span>Settings</span>
          </button>
        </div>

        <div className="sidebar-footer">
          <div className="system-status">
            <div className="status-indicator active"></div>
            <span>System Active</span>
          </div>
          <div className="user-info">
            <div className="avatar">SA</div>
            <div>
              <div className="username">Security Admin</div>
              <div className="role">Administrator</div>
            </div>
          </div>
        </div>
      </nav>

      <main className="main-content">
        {renderPage()}
      </main>
    </div>
  );
}

export default App;

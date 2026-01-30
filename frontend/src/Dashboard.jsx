import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Dashboard.css';
import StatCard from './components/StatCard';
import IncidentList from './components/IncidentList';
import ActivityChart from './components/ActivityChart';
import AccessLogsTable from './components/AccessLogsTable';

// Prefer env override, else rely on CRA proxy ("/api")
const API_URL = process.env.REACT_APP_API_URL || '/api';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [incidents, setIncidents] = useState([]);
  const [accessLogs, setAccessLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [overviewRes, incidentsRes, logsRes] = await Promise.all([
        axios.get(`${API_URL}/dashboard/overview`),
        axios.get(`${API_URL}/dashboard/incidents?limit=10`),
        axios.get(`${API_URL}/access/all-access-logs?limit=20`)
      ]);

      setStats(overviewRes.data.statistics);
      setIncidents(incidentsRes.data.incidents);
      setAccessLogs(logsRes.data.access_logs);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>🔐 Identity Spoofing Detection System</h1>
          <p>Real-time Access Control & Security Monitoring</p>
        </div>
        <div className="header-status">
          <span className="status-indicator online">●</span>
          <span>System Online</span>
        </div>
      </header>

      <nav className="dashboard-nav">
        <button 
          className={`nav-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          📊 Overview
        </button>
        <button 
          className={`nav-btn ${activeTab === 'incidents' ? 'active' : ''}`}
          onClick={() => setActiveTab('incidents')}
        >
          ⚠️ Incidents ({stats?.open_incidents || 0})
        </button>
        <button 
          className={`nav-btn ${activeTab === 'logs' ? 'active' : ''}`}
          onClick={() => setActiveTab('logs')}
        >
          📋 Access Logs
        </button>
      </nav>

      <main className="dashboard-content">
        {activeTab === 'overview' && (
          <div className="overview-section">
            <div className="stats-grid">
              <StatCard 
                title="Active Users" 
                value={stats?.total_users || 0}
                icon="👥"
              />
              <StatCard 
                title="Access Attempts (24h)" 
                value={stats?.attempts_24h || 0}
                icon="🚪"
              />
              <StatCard 
                title="Denied Access (24h)" 
                value={stats?.denied_24h || 0}
                icon="🚫"
                negative={true}
              />
              <StatCard 
                title="Open Incidents" 
                value={stats?.open_incidents || 0}
                icon="🚨"
                negative={true}
              />
            </div>

            <div className="charts-section">
              <div className="chart-card">
                <h3>24-Hour Activity</h3>
                <ActivityChart />
              </div>

              <div className="chart-card">
                <h3>Recent Access Logs</h3>
                <AccessLogsTable logs={accessLogs.slice(0, 5)} />
              </div>
            </div>
          </div>
        )}

        {activeTab === 'incidents' && (
          <div className="incidents-section">
            <h2>Security Incidents</h2>
            <IncidentList incidents={incidents} />
          </div>
        )}

        {activeTab === 'logs' && (
          <div className="logs-section">
            <h2>Access Control Logs</h2>
            <AccessLogsTable logs={accessLogs} />
          </div>
        )}
      </main>

      <footer className="dashboard-footer">
        <p>Identity Spoofing Detection System © 2024 | Last updated: {new Date().toLocaleTimeString()}</p>
      </footer>
    </div>
  );
}

export default Dashboard;

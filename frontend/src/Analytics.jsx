import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import axios from 'axios';
import './Analytics.css';

function Analytics() {
  const [timeRange, setTimeRange] = useState('7days');
  const [analyticsData, setAnalyticsData] = useState({
    accessTrends: [],
    anomalyDistribution: [],
    peakHours: [],
    userActivity: []
  });

  useEffect(() => {
    fetchAnalytics();
  }, [timeRange]);

  const fetchAnalytics = async () => {
    // Demo data - replace with actual API call
    setAnalyticsData({
      accessTrends: [
        { date: 'Mon', successful: 145, denied: 12, anomalies: 3 },
        { date: 'Tue', successful: 168, denied: 8, anomalies: 2 },
        { date: 'Wed', successful: 152, denied: 15, anomalies: 5 },
        { date: 'Thu', successful: 178, denied: 10, anomalies: 4 },
        { date: 'Fri', successful: 190, denied: 7, anomalies: 1 },
        { date: 'Sat', successful: 95, denied: 5, anomalies: 2 },
        { date: 'Sun', successful: 87, denied: 3, anomalies: 1 },
      ],
      anomalyDistribution: [
        { name: 'Face Mismatch', value: 45, color: '#ff6b6b' },
        { name: 'Invalid QR', value: 28, color: '#ffa500' },
        { name: 'Time Anomaly', value: 18, color: '#4ecdc4' },
        { name: 'Location Jump', value: 12, color: '#95e1d3' },
      ],
      peakHours: [
        { hour: '6 AM', count: 12 },
        { hour: '8 AM', count: 45 },
        { hour: '10 AM', count: 28 },
        { hour: '12 PM', count: 32 },
        { hour: '2 PM', count: 25 },
        { hour: '4 PM', count: 18 },
        { hour: '6 PM', count: 52 },
        { hour: '8 PM', count: 35 },
        { hour: '10 PM', count: 15 },
      ],
      userActivity: [
        { category: 'Regular Users', count: 856 },
        { category: 'New Users', count: 124 },
        { category: 'Flagged Users', count: 23 },
      ]
    });
  };

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  return (
    <div className="analytics-page">
      <div className="page-header">
        <h1>Advanced Analytics</h1>
        <p>Deep insights into security patterns and trends</p>
      </div>

      <div className="analytics-controls">
        <div className="time-range-selector">
          <button 
            className={timeRange === '24hours' ? 'active' : ''}
            onClick={() => setTimeRange('24hours')}
          >
            24 Hours
          </button>
          <button 
            className={timeRange === '7days' ? 'active' : ''}
            onClick={() => setTimeRange('7days')}
          >
            7 Days
          </button>
          <button 
            className={timeRange === '30days' ? 'active' : ''}
            onClick={() => setTimeRange('30days')}
          >
            30 Days
          </button>
          <button 
            className={timeRange === 'custom' ? 'active' : ''}
            onClick={() => setTimeRange('custom')}
          >
            Custom
          </button>
        </div>
        <button className="btn-export">📥 Export Report</button>
      </div>

      <div className="analytics-grid">
        <div className="chart-card full-width">
          <div className="chart-header">
            <h3>Access Trends</h3>
            <p>Daily verification patterns</p>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={analyticsData.accessTrends}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="successful" stroke="#4caf50" strokeWidth={2} />
              <Line type="monotone" dataKey="denied" stroke="#f44336" strokeWidth={2} />
              <Line type="monotone" dataKey="anomalies" stroke="#ff9800" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <div className="chart-header">
            <h3>Anomaly Distribution</h3>
            <p>Types of security incidents</p>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={analyticsData.anomalyDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({name, percent}) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {analyticsData.anomalyDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <div className="chart-header">
            <h3>Peak Access Hours</h3>
            <p>Busiest times of the day</p>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={analyticsData.peakHours}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#2196f3" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="insights-panel">
          <h3>🎯 Key Insights</h3>
          <div className="insight-list">
            <div className="insight-item">
              <span className="insight-icon success">✓</span>
              <div>
                <strong>95.2% Success Rate</strong>
                <p>Above target threshold of 90%</p>
              </div>
            </div>
            <div className="insight-item">
              <span className="insight-icon warning">⚠️</span>
              <div>
                <strong>Peak Hours: 6-8 PM</strong>
                <p>Consider additional security during this period</p>
              </div>
            </div>
            <div className="insight-item">
              <span className="insight-icon info">ℹ️</span>
              <div>
                <strong>Face Mismatch Leading Cause</strong>
                <p>44% of anomalies are face recognition failures</p>
              </div>
            </div>
            <div className="insight-item">
              <span className="insight-icon danger">⛔</span>
              <div>
                <strong>23 Flagged Users</strong>
                <p>Require immediate review and investigation</p>
              </div>
            </div>
          </div>
        </div>

        <div className="predictions-panel">
          <h3>🔮 AI Predictions</h3>
          <div className="prediction-list">
            <div className="prediction-item">
              <div className="prediction-header">
                <span className="prediction-label">Tomorrow's Traffic</span>
                <span className="prediction-confidence">92% confidence</span>
              </div>
              <div className="prediction-value">~185 verifications</div>
            </div>
            <div className="prediction-item">
              <div className="prediction-header">
                <span className="prediction-label">Risk Level</span>
                <span className="prediction-confidence">85% confidence</span>
              </div>
              <div className="prediction-value low">Low Risk</div>
            </div>
            <div className="prediction-item">
              <div className="prediction-header">
                <span className="prediction-label">Anomaly Forecast</span>
                <span className="prediction-confidence">78% confidence</span>
              </div>
              <div className="prediction-value">2-4 incidents expected</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Analytics;

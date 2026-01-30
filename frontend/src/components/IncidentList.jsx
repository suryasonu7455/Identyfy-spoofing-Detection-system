import React from 'react';

function IncidentList({ incidents }) {
  const getSeverityColor = (severity) => {
    switch(severity) {
      case 'critical': return '#e74c3c';
      case 'high': return '#e67e22';
      case 'medium': return '#f39c12';
      default: return '#3498db';
    }
  };

  return (
    <div className="incident-list">
      {incidents.length === 0 ? (
        <p className="no-data">No incidents detected</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Type</th>
              <th>Severity</th>
              <th>Detected</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {incidents.map(incident => (
              <tr key={incident.id}>
                <td>#{incident.id}</td>
                <td>{incident.incident_type.toUpperCase()}</td>
                <td>
                  <span 
                    className="severity-badge"
                    style={{ backgroundColor: getSeverityColor(incident.severity) }}
                  >
                    {incident.severity.toUpperCase()}
                  </span>
                </td>
                <td>{new Date(incident.detected_at).toLocaleString()}</td>
                <td>{incident.status}</td>
                <td>
                  <button className="action-btn">Review</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default IncidentList;

import React from 'react';

function AccessLogsTable({ logs }) {
  return (
    <div className="access-logs">
      {logs.length === 0 ? (
        <p className="no-data">No access logs</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>User</th>
              <th>Entry Point</th>
              <th>Status</th>
              <th>Face Confidence</th>
              <th>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {logs.map(log => (
              <tr key={log.id} className={log.access_status === 'granted' ? 'granted' : 'denied'}>
                <td>#{log.id}</td>
                <td>User {log.user_id}</td>
                <td>{log.entry_point}</td>
                <td>
                  <span className={`status-badge ${log.access_status}`}>
                    {log.access_status.toUpperCase()}
                  </span>
                </td>
                <td>
                  {log.face_match_confidence 
                    ? `${(log.face_match_confidence * 100).toFixed(1)}%`
                    : 'N/A'
                  }
                </td>
                <td>{new Date(log.timestamp).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default AccessLogsTable;

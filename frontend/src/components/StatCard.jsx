import React from 'react';

function StatCard({ title, value, icon, negative }) {
  const bgColor = negative ? '#fee' : '#efe';
  const textColor = negative ? '#c33' : '#3c3';
  
  return (
    <div className="stat-card" style={{ backgroundColor: bgColor }}>
      <div className="stat-icon">{icon}</div>
      <div className="stat-content">
        <div className="stat-title">{title}</div>
        <div className="stat-value" style={{ color: textColor }}>
          {value.toLocaleString()}
        </div>
      </div>
    </div>
  );
}

const statCardStyles = `
.stat-card {
  border-radius: 12px;
  padding: 20px;
  display: flex;
  gap: 15px;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  font-size: 32px;
}

.stat-content {
  flex: 1;
}

.stat-title {
  font-size: 12px;
  color: #666;
  font-weight: 600;
  text-transform: uppercase;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  margin-top: 5px;
}
`;

export default StatCard;

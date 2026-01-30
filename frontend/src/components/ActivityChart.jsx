import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function ActivityChart() {
  // Sample data - in production, fetch from API
  const data = [
    { time: '00:00', granted: 5, denied: 1 },
    { time: '04:00', granted: 3, denied: 0 },
    { time: '08:00', granted: 45, denied: 3 },
    { time: '12:00', granted: 52, denied: 5 },
    { time: '16:00', granted: 48, denied: 4 },
    { time: '20:00', granted: 35, denied: 2 },
  ];

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="time" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey="granted" fill="#2ecc71" name="Granted" />
        <Bar dataKey="denied" fill="#e74c3c" name="Denied" />
      </BarChart>
    </ResponsiveContainer>
  );
}

export default ActivityChart;

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './AdminPanel.css';

function AdminPanel() {
  const [users, setUsers] = useState([]);
  const [showAddUser, setShowAddUser] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [newUser, setNewUser] = useState({
    name: '',
    email: '',
    phone: '',
    unit: '',
    role: 'resident'
  });

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/admin/users');
      setUsers(response.data.users || []);
    } catch (error) {
      // Demo data for display
      setUsers([
        { id: 1, name: 'John Doe', email: 'john@example.com', unit: 'A101', role: 'resident', status: 'active', face_enrolled: true },
        { id: 2, name: 'Jane Smith', email: 'jane@example.com', unit: 'B205', role: 'resident', status: 'active', face_enrolled: true },
        { id: 3, name: 'Mike Johnson', email: 'mike@example.com', unit: 'C303', role: 'security', status: 'active', face_enrolled: false },
        { id: 4, name: 'Sarah Williams', email: 'sarah@example.com', unit: 'A405', role: 'resident', status: 'suspended', face_enrolled: true },
      ]);
    }
  };

  const handleAddUser = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:5000/api/auth/register-user', newUser);
      setUsers([...users, response.data.user]);
      setShowAddUser(false);
      setNewUser({ name: '', email: '', phone: '', unit: '', role: 'resident' });
    } catch (error) {
      alert('Failed to add user: ' + error.message);
    }
  };

  const enrollFace = async (userId) => {
    // This would trigger face enrollment process
    alert(`Face enrollment initiated for User ID: ${userId}`);
  };

  const toggleUserStatus = (userId) => {
    setUsers(users.map(user => 
      user.id === userId 
        ? {...user, status: user.status === 'active' ? 'suspended' : 'active'}
        : user
    ));
  };

  const filteredUsers = users.filter(user =>
    user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.unit.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="admin-panel">
      <div className="page-header">
        <h1>User Management</h1>
        <p>Manage residents, credentials, and access permissions</p>
      </div>

      <div className="admin-controls">
        <div className="search-bar">
          <span className="search-icon">🔍</span>
          <input 
            type="text"
            placeholder="Search users by name, email, or unit..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <button className="btn-primary" onClick={() => setShowAddUser(true)}>
          ➕ Add New User
        </button>
      </div>

      <div className="users-grid">
        {filteredUsers.map(user => (
          <div key={user.id} className={`user-card ${user.status}`}>
            <div className="user-card-header">
              <div className="user-avatar">
                {user.name.split(' ').map(n => n[0]).join('')}
              </div>
              <div className="user-info">
                <h3>{user.name}</h3>
                <p className="user-email">{user.email}</p>
              </div>
              <span className={`status-badge ${user.status}`}>
                {user.status}
              </span>
            </div>

            <div className="user-card-body">
              <div className="user-detail">
                <span className="label">Unit:</span>
                <span className="value">{user.unit}</span>
              </div>
              <div className="user-detail">
                <span className="label">Role:</span>
                <span className="value">{user.role}</span>
              </div>
              <div className="user-detail">
                <span className="label">Face Enrolled:</span>
                <span className={`value ${user.face_enrolled ? 'enrolled' : 'not-enrolled'}`}>
                  {user.face_enrolled ? '✓ Yes' : '✗ No'}
                </span>
              </div>
            </div>

            <div className="user-card-actions">
              <button className="btn-icon" title="View Details">
                👁️
              </button>
              {!user.face_enrolled && (
                <button className="btn-icon" onClick={() => enrollFace(user.id)} title="Enroll Face">
                  📸
                </button>
              )}
              <button 
                className="btn-icon" 
                onClick={() => toggleUserStatus(user.id)}
                title={user.status === 'active' ? 'Suspend' : 'Activate'}
              >
                {user.status === 'active' ? '⏸️' : '▶️'}
              </button>
              <button className="btn-icon danger" title="Delete">
                🗑️
              </button>
            </div>
          </div>
        ))}
      </div>

      {showAddUser && (
        <div className="modal-overlay" onClick={() => setShowAddUser(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Add New User</h2>
              <button className="close-btn" onClick={() => setShowAddUser(false)}>✕</button>
            </div>
            <form onSubmit={handleAddUser}>
              <div className="form-group">
                <label>Full Name</label>
                <input 
                  type="text"
                  value={newUser.name}
                  onChange={(e) => setNewUser({...newUser, name: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input 
                  type="email"
                  value={newUser.email}
                  onChange={(e) => setNewUser({...newUser, email: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Phone</label>
                <input 
                  type="tel"
                  value={newUser.phone}
                  onChange={(e) => setNewUser({...newUser, phone: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Unit Number</label>
                <input 
                  type="text"
                  value={newUser.unit}
                  onChange={(e) => setNewUser({...newUser, unit: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Role</label>
                <select 
                  value={newUser.role}
                  onChange={(e) => setNewUser({...newUser, role: e.target.value})}
                >
                  <option value="resident">Resident</option>
                  <option value="security">Security Staff</option>
                  <option value="admin">Administrator</option>
                  <option value="visitor">Visitor</option>
                </select>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={() => setShowAddUser(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  Add User
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default AdminPanel;

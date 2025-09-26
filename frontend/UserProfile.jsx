import React, { useState, useEffect } from 'react';
import axios from 'axios';

const UserProfile = ({ userId, onUpdate }) => {
  const [user, setUser] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({});
  
  const API_BASE = 'https://api.example.com';
  
  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await axios.get(`${API_BASE}/users/${userId}`);
        setUser(response.data);
        setFormData(response.data);
      } catch (err) {
        setError(err.message);
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchUser();
  }, [userId]);
  
  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const response = await axios.put(`${API_BASE}/users/${userId}`, formData);
      document.getElementById('success-message').style.display = 'block';
      onUpdate && onUpdate(response.data);
    } catch (error) {
      console.log('Update failed:', error);
    }
  };
  
  const containerStyle = {
    padding: '20px',
    border: '1px solid #ccc',
    margin: '10px'
  };
  
  if (loading) {
    return <div>Loading user data...</div>;
  }
  
  if (error) {
    return <div style={{color: 'red'}}>Error: {error}</div>;
  }
  
  return (
    <div style={containerStyle}>
      <h2>{user.name || 'Unknown User'}</h2>
      
      <form onSubmit={handleSubmit}>
        <div>
          <input
            type="text"
            name="name"
            value={formData.name || ''}
            onChange={handleInputChange}
            placeholder="Full Name"
          />
        </div>
        
        <div>
          <input
            type="email"
            name="email"
            value={formData.email || ''}
            onChange={handleInputChange}
            placeholder="Email Address"
          />
        </div>
        
        <div>
          <textarea
            name="bio"
            value={formData.bio || ''}
            onChange={handleInputChange}
            placeholder="Biography"
            rows="4"
          />
        </div>
        
        <button type="submit">Update Profile</button>
      </form>
      
      <div id="success-message" style={{display: 'none', color: 'green'}}>
        Profile updated successfully!
      </div>
      
      <div style={{marginTop: '20px', fontSize: '12px', color: '#666'}}>
        Debug: User ID = {userId}
      </div>
    </div>
  );
};

export default UserProfile;
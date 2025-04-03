import React, { useState } from 'react';
import './LoginForm.css';

export interface Institution {
  id: string;
  name: string;
}

export const institutions: Institution[] = [
  { id: 'uni1', name: 'University of Example' },
  { id: 'uni2', name: 'Research Institute' }
];

const LoginForm: React.FC = () => {
  const [institution, setInstitution] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username: `${username}@${institution}`,
          password: password,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        window.location.href = '/dashboard';
      } else {
        setError('Invalid credentials');
      }
    } catch (error) {
      setError('Connection error. Please try again.');
    }
  };

  return (
    <div className="login-container">
      <div className="brand-section">
        <h1 className="brand-title">
          Research Storage<br />
          ACL Manager
        </h1>
        <p className="brand-subtitle">
          Secure, efficient permission management for research data at scale
        </p>
      </div>
      
      <div className="login-section">
        <div className="login-box">
          <h2 className="login-title">Sign In</h2>
          <p className="login-subtitle">Access your research storage</p>
          
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Institution</label>
              <select 
                value={institution}
                onChange={(e) => setInstitution(e.target.value)}
                required
              >
                <option value="">Select your research institution</option>
                {institutions.map((inst) => (
                  <option key={inst.id} value={inst.id}>
                    {inst.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Username</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>

            <div className="form-group password-group">
              <label>Password</label>
              <a href="/forgot-password" className="forgot-link">
                Forgot?
              </a>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            {error && <div className="error-message">{error}</div>}

            <button type="submit" className="login-button">
              Login
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default LoginForm; 
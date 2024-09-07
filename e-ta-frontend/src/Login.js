// Login.js
import React, { useState } from 'react';
import './Login.css';

const Login = ({ onLogin, loading }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();
    onLogin(email, password);
  };

  return (
    <div className="login-container">
      <div className="left-side">
      </div>      
      <div className="login-form">
        <div className="login-intro">
          <h1 className="welcome">Welcome to E-TA System</h1>
          <p className="enhanced">Your Enhanced Teaching Assistant</p>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <span className="input-icon">
              <i className="fas fa-user"></i> {/* User icon from Font Awesome */}
            </span>
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="input-group">
            <span className="input-icon">
              <i className="fas fa-lock"></i> {/* Lock icon from Font Awesome */}
            </span>
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <h4>Please Login with Piazza Credential</h4>
          <button type="submit" className="login-button" disabled={loading}>
            {loading ? 'Loading...' : 'LOGIN'}
          </button>
          <h5>Design By Team A+</h5>
        </form>
      </div>
    </div>
  );
};

export default Login;

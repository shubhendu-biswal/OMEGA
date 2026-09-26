import React, { StrictMode, Component } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App.jsx';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("OMEGA React Error Boundary caught an error:", error, errorInfo);
    try {
      localStorage.clear();
    } catch (e) {}
  }

  handleReset = () => {
    try {
      localStorage.clear();
      sessionStorage.clear();
    } catch (e) {}
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          minHeight: '100vh',
          backgroundColor: '#000000',
          color: '#ffffff',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          fontFamily: 'sans-serif',
          padding: '20px',
          textAlign: 'center'
        }}>
          <div style={{
            padding: '24px 32px',
            backgroundColor: 'rgba(6, 11, 22, 0.95)',
            border: '1px solid #475569',
            borderRadius: '16px',
            boxShadow: '0 10px 40px rgba(0, 0, 0, 0.8)'
          }}>
            <h2 style={{ color: '#00e5ff', fontSize: '18px', fontWeight: 'bold', marginBottom: '10px', fontFamily: 'monospace' }}>
              ✦ OMEGA QUANTUM RECOVERY
            </h2>
            <p style={{ color: '#94a3b8', fontSize: '12px', marginBottom: '20px', maxWidth: '380px', lineHeight: '1.5' }}>
              Local browser storage cache mismatch detected. Click below to reset state cache and restore full interface view.
            </p>
            <button
              onClick={this.handleReset}
              style={{
                padding: '10px 24px',
                background: 'linear-gradient(135deg, rgba(0, 242, 254, 0.25) 0%, rgba(16, 185, 129, 0.2) 100%)',
                border: '1px solid #475569',
                borderRadius: '12px',
                color: '#ffffff',
                fontSize: '12px',
                fontWeight: 'bold',
                cursor: 'pointer',
                boxShadow: '0 0 16px rgba(0, 242, 254, 0.3)'
              }}
            >
              Reset State & Reload Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </StrictMode>
);

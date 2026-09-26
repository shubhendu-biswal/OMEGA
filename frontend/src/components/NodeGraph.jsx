import React from 'react';

const NODES = [
  { id: 'memory', label: 'Memory', color: '#10b981', icon: '🧠' },
  { id: 'soul', label: 'Soul', color: '#e2e8f0', icon: '🔔' },
  { id: 'skills', label: 'Skills', color: '#00f2fe', icon: '📖' },
  { id: 'settings', label: 'Settings', color: '#ef4444', icon: '⚙️' }
];

export default function NodeGraph({ activeNode, onSelectNode }) {
  return (
    <div className="node-graph-container">
      {/* Node list on left */}
      <div className="node-list">
        {NODES.map((node) => (
          <div 
            key={node.id} 
            className={`node-card ${activeNode === node.id ? 'active' : ''}`}
            onClick={() => onSelectNode && onSelectNode(node.id)}
            style={{ '--node-color': node.color }}
          >
            <div className="node-icon-badge" style={{ borderColor: node.color, color: node.color }}>
              <span>{node.icon}</span>
            </div>
            <span className="node-label">{node.label}</span>
            <span className="node-dot" style={{ backgroundColor: node.color }} />
          </div>
        ))}
      </div>

      {/* SVG Connecting Bezier Cables */}
      <div className="node-svg-wrapper">
        <svg viewBox="0 0 200 180" className="node-svg">
          <defs>
            <linearGradient id="grad-memory" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#10b981" stopOpacity="0.9" />
              <stop offset="100%" stopColor="#00f2fe" stopOpacity="0.8" />
            </linearGradient>
            <linearGradient id="grad-soul" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#94a3b8" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#00f2fe" stopOpacity="0.8" />
            </linearGradient>
            <linearGradient id="grad-skills" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#00f2fe" stopOpacity="0.9" />
              <stop offset="100%" stopColor="#00f2fe" stopOpacity="0.8" />
            </linearGradient>
            <linearGradient id="grad-settings" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#ef4444" stopOpacity="0.9" />
              <stop offset="100%" stopColor="#00f2fe" stopOpacity="0.8" />
            </linearGradient>

            <filter id="glow-line" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Node 1: Memory (top) -> Junction */}
          <path d="M 0,25 C 60,25 75,90 110,90" fill="none" stroke="url(#grad-memory)" strokeWidth="2.5" filter="url(#glow-line)" />
          {/* Node 2: Soul -> Junction */}
          <path d="M 0,68 C 50,68 70,90 110,90" fill="none" stroke="url(#grad-soul)" strokeWidth="2" filter="url(#glow-line)" />
          {/* Node 3: Skills -> Junction */}
          <path d="M 0,112 C 50,112 70,90 110,90" fill="none" stroke="url(#grad-skills)" strokeWidth="2" filter="url(#glow-line)" />
          {/* Node 4: Settings -> Junction */}
          <path d="M 0,155 C 60,155 75,90 110,90" fill="none" stroke="url(#grad-settings)" strokeWidth="2.5" filter="url(#glow-line)" />

          {/* Convergence Node Junction Point */}
          <circle cx="110" cy="90" r="5" fill="#00f2fe" filter="url(#glow-line)" />
          <circle cx="110" cy="90" r="2.5" fill="#ffffff" />

          {/* Trunk line to 3D Sphere Display */}
          <line x1="110" y1="90" x2="200" y2="90" stroke="#00f2fe" strokeWidth="2.5" strokeDasharray="4 4" className="pulse-trunk-line" filter="url(#glow-line)" />

          {/* Animated data pulses along trunk */}
          <circle cx="140" cy="90" r="3" fill="#ffffff" className="data-pulse-dot">
            <animate attributeName="cx" from="110" to="200" dur="1.8s" repeatCount="indefinite" />
          </circle>
          <circle cx="200" cy="90" r="4" fill="#00f2fe" />
        </svg>
      </div>
    </div>
  );
}

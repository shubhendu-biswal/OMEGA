import React from 'react';

/**
 * HologramSphere component rendering the highly animated futuristic central hologram.
 * @param {boolean} computing - Whether the AI is active and "thinking"
 * @param {string} agent - Currently selected AI agent key
 */
export default function HologramSphere({ computing, agent }) {
  // Determine if computing modifier should be added
  const stateClass = computing ? 'computing' : '';

  return (
    <div className="hologram-outer">
      {/* Dynamic Back-Glow */}
      <div className="hologram-glow-core"></div>

      {/* Hologram SVG */}
      <svg
        className="hologram-canvas"
        viewBox="0 0 400 400"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          {/* Radial Gradient for central core sphere */}
          <radialGradient id="coreGlow" cx="50%" cy="50%" r="50%" fx="50%" fy="50%">
            <stop offset="0%" stopColor="var(--accent)" stopOpacity="1" />
            <stop offset="35%" stopColor="var(--accent)" stopOpacity="0.85" />
            <stop offset="70%" stopColor="var(--accent)" stopOpacity="0.45" />
            <stop offset="100%" stopColor="var(--accent)" stopOpacity="0" />
          </radialGradient>

          {/* Linear gradient for orbit rings */}
          <linearGradient id="orbitGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="var(--accent)" stopOpacity="0.6" />
            <stop offset="50%" stopColor="rgba(255, 255, 255, 0.1)" stopOpacity="0.2" />
            <stop offset="100%" stopColor="var(--accent)" stopOpacity="0.8" />
          </linearGradient>

          {/* Soft blur for glowing effect */}
          <filter id="neonGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="6" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {/* Outer Orbit with dotted particles */}
        <g className={`hologram-ring-outer ${stateClass}`}>
          {/* Outer circle line */}
          <circle
            cx="200"
            cy="200"
            r="160"
            stroke="url(#orbitGrad)"
            strokeWidth="1"
            strokeDasharray="4 8 12 8"
            opacity="0.35"
          />
          {/* Outer floating nodes */}
          <circle cx="200" cy="40" r="3" fill="var(--accent)" filter="url(#neonGlow)" />
          <circle cx="360" cy="200" r="2.5" fill="var(--accent)" />
          <circle cx="200" cy="360" r="3" fill="var(--accent)" filter="url(#neonGlow)" />
          <circle cx="40" cy="200" r="2" fill="rgba(255,255,255,0.6)" />
        </g>

        {/* Middle Orbit with solid sections and spacing */}
        <g className={`hologram-ring-middle ${stateClass}`}>
          {/* Medium circle arcs */}
          <path
            d="M 200,60 A 140,140 0 0,1 340,200"
            stroke="var(--accent)"
            strokeWidth="1.5"
            strokeDasharray="40 10 5 10"
            opacity="0.5"
          />
          <path
            d="M 200,340 A 140,140 0 0,1 60,200"
            stroke="var(--accent)"
            strokeWidth="1.5"
            strokeDasharray="20 20 40 15"
            opacity="0.4"
          />
          
          {/* Orbiting nodes */}
          <circle cx="101" cy="98" r="4" fill="var(--accent)" filter="url(#neonGlow)" />
          <circle cx="299" cy="302" r="3" fill="var(--accent)" />
        </g>

        {/* Inner Orbit with dense dash styling */}
        <g className={`hologram-ring-inner ${stateClass}`}>
          <circle
            cx="200"
            cy="200"
            r="110"
            stroke="url(#orbitGrad)"
            strokeWidth="2"
            strokeDasharray="150 15 30 15"
            opacity="0.75"
          />
          
          {/* Close-orbit micro particles */}
          <circle cx="200" cy="90" r="2.5" fill="#fff" filter="url(#neonGlow)" />
          <circle cx="200" cy="310" r="2" fill="#fff" />
          <circle cx="110" cy="250" r="3" fill="var(--accent)" />
          <circle cx="290" cy="150" r="2.5" fill="var(--accent)" filter="url(#neonGlow)" />
        </g>

        {/* Dynamic Glowing Sphere Center Core */}
        <circle
          className={`hologram-globe-core ${stateClass}`}
          cx="200"
          cy="200"
          r="70"
          fill="url(#coreGlow)"
          filter="url(#neonGlow)"
        />

        {/* Central Core Outline with tiny ticks */}
        <circle
          cx="200"
          cy="200"
          r="70"
          stroke="var(--accent)"
          strokeWidth="1"
          strokeDasharray="10 5"
          opacity="0.4"
        />

        {/* Hologram horizontal scanner bar simulation */}
        <line
          x1="120"
          y1="200"
          x2="280"
          y2="200"
          stroke="rgba(255, 255, 255, 0.15)"
          strokeWidth="1"
          strokeDasharray="20 4 2 4"
        />
        
        {/* Core crosshair rings */}
        <circle cx="200" cy="200" r="15" stroke="var(--accent)" strokeWidth="0.75" opacity="0.4" />
        <circle cx="200" cy="200" r="5" fill="var(--accent)" opacity="0.7" />
      </svg>
    </div>
  );
}

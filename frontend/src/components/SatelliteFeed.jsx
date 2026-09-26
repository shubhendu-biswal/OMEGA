import React, { useState } from 'react';
import { Radio, Tv, Maximize2, RotateCw, Globe, Shield, Wifi } from 'lucide-react';

const SATELLITE_DOTS = [
  { id: 1, x: 28, y: 35, color: '#f59e0b', pulse: true, label: 'NA-EAST-1' },
  { id: 2, x: 22, y: 42, color: '#ef4444', pulse: false, label: 'NA-WEST-2' },
  { id: 3, x: 48, y: 30, color: '#10b981', pulse: true, label: 'EU-CENTRAL' },
  { id: 4, x: 52, y: 34, color: '#f59e0b', pulse: true, label: 'EU-WEST-1' },
  { id: 5, x: 74, y: 42, color: '#00f2fe', pulse: true, label: 'AP-SOUTH-1' },
  { id: 6, x: 82, y: 48, color: '#f59e0b', pulse: false, label: 'AP-SOUTHEAST' },
  { id: 7, x: 88, y: 36, color: '#10b981', pulse: true, label: 'AP-NORTHEAST' },
  { id: 8, x: 38, y: 68, color: '#00f2fe', pulse: false, label: 'SA-EAST-1' },
  { id: 9, x: 56, y: 62, color: '#f59e0b', pulse: true, label: 'AF-SOUTH-1' },
];

const HEADLINES = [
  {
    id: '01',
    text: 'Global tech summit kicks off with focus on AI ethics and regulation'
  },
  {
    id: '02',
    text: 'Historic peace treaty signed between long-standing rival nations'
  },
  {
    id: '03',
    text: 'Breakthrough in quantum computing promises to revolutionize data encryption'
  }
];

export default function SatelliteFeed() {
  const [activeDot, setActiveDot] = useState(SATELLITE_DOTS[4]);

  return (
    <div className="sat-sidebar">
      {/* 1. MEDIA LINK Card */}
      <div className="sat-card media-link-card">
        <div className="sat-card-header">
          <div className="sat-title-badge">
            <Radio size={12} className="text-cyan-400" />
            <span>Media Feed</span>
          </div>
          <div className="sat-controls">
            <span className="sat-dot-menu">• • •</span>
          </div>
        </div>

        <div className="media-offline-display">
          <span className="offline-pill">Offline</span>
          <div className="media-buttons-row">
            <button className="media-btn" title="Home Feed">
              <Tv size={14} />
            </button>
            <button className="media-btn" title="Display Options">
              <RotateCw size={14} />
            </button>
          </div>
        </div>
      </div>

      {/* 2. SAT-LINK FEED / SATELLITE STREAM Card */}
      <div className="sat-card sat-stream-card">
        <div className="sat-card-header">
          <div className="sat-title-badge">
            <Globe size={12} />
            <span>Satellite Feed</span>
          </div>
          <span className="sat-sub-signal font-mono"><Wifi size={10} className="inline mr-1 text-emerald-400" />1.2 Gbps</span>
        </div>

        <div className="sat-stream-subhead">
          <span className="stream-label">• Live Stream</span>
          <div className="sat-hud-pill">
            <span className="hud-code">SO NO</span>
            <Maximize2 size={10} className="hud-icon" />
          </div>
        </div>

        {/* Tactical Dark Grid World Map Canvas Container */}
        <div className="tactical-map-container">
          {/* Radar Scanning Line Animation Overlay */}
          <div className="radar-sweep-line" />

          {/* Grid lines background */}
          <div className="map-grid-overlay" />

          {/* SVG World Outline */}
          <svg viewBox="0 0 100 60" className="map-svg-world">
            <path d="M 12 18 Q 20 12 32 18 T 35 32 T 22 36 T 10 28 Z" fill="rgba(0, 242, 254, 0.08)" stroke="rgba(0, 242, 254, 0.3)" strokeWidth="0.5" />
            <path d="M 28 38 Q 38 40 36 54 T 26 50 Z" fill="rgba(0, 242, 254, 0.08)" stroke="rgba(0, 242, 254, 0.3)" strokeWidth="0.5" />
            <path d="M 45 15 Q 55 12 58 22 T 44 26 Z" fill="rgba(0, 242, 254, 0.08)" stroke="rgba(0, 242, 254, 0.3)" strokeWidth="0.5" />
            <path d="M 44 28 Q 58 28 56 46 T 42 42 Z" fill="rgba(0, 242, 254, 0.08)" stroke="rgba(0, 242, 254, 0.3)" strokeWidth="0.5" />
            <path d="M 58 14 Q 85 10 92 30 T 68 35 Z" fill="rgba(0, 242, 254, 0.08)" stroke="rgba(0, 242, 254, 0.3)" strokeWidth="0.5" />
            <path d="M 80 42 Q 90 42 88 52 T 78 50 Z" fill="rgba(0, 242, 254, 0.08)" stroke="rgba(0, 242, 254, 0.3)" strokeWidth="0.5" />

            <path d="M 28 35 Q 50 20 74 42" fill="none" stroke="rgba(245, 158, 11, 0.5)" strokeWidth="0.4" strokeDasharray="1 1" />
            <path d="M 48 30 Q 65 40 88 36" fill="none" stroke="rgba(0, 242, 254, 0.5)" strokeWidth="0.4" strokeDasharray="1 1" />
          </svg>

          {/* Satellite Data Nodes */}
          {SATELLITE_DOTS.map(dot => (
            <div
              key={dot.id}
              className={`sat-node-dot ${dot.pulse ? 'pulsing' : ''} ${activeDot?.id === dot.id ? 'active' : ''}`}
              style={{
                left: `${dot.x}%`,
                top: `${dot.y}%`,
                backgroundColor: dot.color,
                boxShadow: `0 0 10px ${dot.color}`
              }}
              onClick={() => setActiveDot(dot)}
              title={`${dot.label} Telemetry Node`}
            >
              <div className="sat-node-ping" style={{ borderColor: dot.color }} />
            </div>
          ))}

          {/* Bottom telemetry overlay pill */}
          <div className="map-bottom-telemetry">
            <span className="telemetry-node-name">{activeDot ? activeDot.label : 'ORBITAL-SYNC'}</span>
            <span className="telemetry-status font-mono">LAT: 28.61° N | LIVE</span>
          </div>
        </div>
      </div>

      {/* 3. TODAY HEADLINES Card */}
      <div className="sat-card headlines-card">
        <div className="sat-card-header">
          <span className="headlines-title">! Latest News</span>
          <div className="headlines-actions">
            <RotateCw size={11} className="headline-icon" />
            <Maximize2 size={11} className="headline-icon" />
          </div>
        </div>

        <div className="headlines-list">
          {HEADLINES.map(item => (
            <div key={item.id} className="headline-item">
              <span className="headline-num">{item.id}</span>
              <p className="headline-text">{item.text}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

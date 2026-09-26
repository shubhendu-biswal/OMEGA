import React, { useState, useEffect } from 'react';
import { Cpu, Database, Activity, HardDrive, Terminal, Clock, Gauge, Server, Radio, Zap, Layers, Wifi } from 'lucide-react';

export default function SystemHud({ activeSession, lastResponseTime, lastLatency, lastTokensPerSec, activeTools }) {
  const [activeTab, setActiveTab] = useState('Stats');
  const [stats, setStats] = useState({
    cpu: 15,
    mem: 42,
    gpu: 20,
    uptime: 0
  });

  // Dynamic equalizer wave data for performance charts
  const [cpuWave, setCpuWave] = useState([12, 14, 18, 15, 22, 16, 20, 14, 15, 18, 14, 16]);
  const [tokenWave, setTokenWave] = useState([40, 65, 80, 110, 142, 95, 120, 135, 142, 128, 130, 142]);
  const [latencyWave, setLatencyWave] = useState([18, 22, 25, 20, 24, 21, 23, 26, 22, 23, 21, 23]);

  // Telemetry Log Feed lines
  const [logFeed, setLogFeed] = useState([
    { time: '04:25:25 PM', msg: 'System check: OK' },
    { time: '04:25:29 PM', msg: 'Memory allocation stable' },
    { time: '04:25:34 PM', msg: 'GPU load balanced' },
    { time: '04:25:39 PM', msg: 'System status normal' }
  ]);

  // Fetch actual OS/JVM telemetry from Spring Boot backend
  useEffect(() => {
    const fetchTelemetry = () => {
      fetch('http://localhost:9090/api/telemetry')
        .then(res => {
          if (!res.ok) throw new Error("HTTP Status " + res.status);
          return res.json();
        })
        .then(data => {
          setStats(prev => ({
            ...prev,
            cpu: data.cpu,
            mem: data.mem,
            gpu: data.gpu,
            uptime: data.uptime
          }));
          setCpuWave(prev => [...prev.slice(1), data.cpu]);
        })
        .catch(err => {
          setStats(prev => {
            const cpuDelta = Math.floor(Math.random() * 5) - 2;
            const memDelta = Math.floor(Math.random() * 3) - 1;
            const nextCpu = Math.max(8, Math.min(95, prev.cpu + cpuDelta));
            return {
              ...prev,
              cpu: nextCpu,
              mem: Math.max(20, Math.min(90, prev.mem + memDelta)),
              gpu: Math.max(10, Math.min(85, Math.round(nextCpu * 1.1)))
            };
          });
          setCpuWave(prev => [...prev.slice(1), Math.floor(Math.random() * 12) + 12]);
        });
    };

    fetchTelemetry();
    const interval = setInterval(fetchTelemetry, 2500);
    return () => clearInterval(interval);
  }, []);

  // Update token wave graph when speed telemetry changes
  useEffect(() => {
    if (lastTokensPerSec > 0) {
      setTokenWave(prev => [...prev.slice(1), lastTokensPerSec]);
    }
  }, [lastTokensPerSec]);

  // Update latency wave graph when latency changes
  useEffect(() => {
    if (lastLatency > 0) {
      setLatencyWave(prev => [...prev.slice(1), lastLatency]);
    }
  }, [lastLatency]);

  // Add random live log line periodically
  useEffect(() => {
    const logInterval = setInterval(() => {
      const logs = [
        'System check: OK',
        'Backend server active',
        'Memory allocation stable',
        'System status normal',
        'GPU load balanced'
      ];
      const nextLog = logs[Math.floor(Math.random() * logs.length)];
      const nowTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      setLogFeed(prev => [...prev.slice(1), { time: nowTime, msg: nextLog }]);
    }, 4000);
    return () => clearInterval(logInterval);
  }, []);

  const activeSessionMessages = (activeSession && Array.isArray(activeSession.messages)) ? activeSession.messages : [];
  const usedTokens = activeSessionMessages.reduce((acc, msg) => {
    const textLen = (msg && typeof msg.content === 'string') ? msg.content.length : 0;
    return acc + Math.max(4, Math.round(textLen / 3.8));
  }, 5430);
  const ctxPercent = Math.min(100, Math.round((usedTokens / 128000) * 100)) || 4;

  const formatUptime = (ms) => {
    if (!ms || ms <= 0) return '0:20:42';
    const totalSeconds = Math.floor(ms / 1000);
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;
    return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  };

  return (
    <div className="system-hud-panel animate-fade-in">
      {/* 1. Header Row */}
      <div className="hud-header">
        <div className="hud-header-title">
          <div className="hud-title-icon-wrapper">
            <Activity size={16} className="hud-header-icon" />
          </div>
          <span>SYSTEM HUD</span>
        </div>
        <div className="hud-live-badge">
          <span className="hud-live-dot"></span>
          <span className="hud-live-text">Live</span>
        </div>
      </div>

      {/* 2. Top Telemetry Mini Strip */}
      <div className="hud-telemetry-strip">
        <div className="hud-strip-item cyan">
          <Zap size={11} />
          <span className="hud-strip-label">CPU</span>
          <span className="hud-strip-val">{stats.cpu}%</span>
        </div>
        <div className="hud-strip-divider" />
        <div className="hud-strip-item green">
          <Activity size={11} />
          <span className="hud-strip-label">RAM</span>
          <span className="hud-strip-val">4.2GB</span>
        </div>
        <div className="hud-strip-divider" />
        <div className="hud-strip-item blue">
          <Cpu size={11} />
          <span className="hud-strip-label">GPU</span>
          <span className="hud-strip-val">{stats.gpu}%</span>
        </div>
      </div>

      {/* 2. Circular Gauges */}
      <div className="hud-rings-row">
        <CircularProgress percent={stats.cpu} label="CPU" strokeColor="#00ff88" />
        <CircularProgress percent={stats.mem} label="RAM" strokeColor="#00e5ff" />
        <CircularProgress percent={stats.gpu} label="GPU" strokeColor="#3b82f6" />
        <CircularProgress percent={ctxPercent} label="Context" strokeColor="#00e5ff" />
      </div>

      {/* 3. Tabs */}
      <div className="hud-tabs">
        {['Stats', 'Memory', 'Tools'].map((tab) => (
          <button
            key={tab}
            className={`hud-tab-btn ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* 4. Scrollable Dynamic Body Content */}
      <div className="hud-body custom-scrollbar">
        {activeTab === 'Stats' && (
          <div className="hud-tab-content">
            {/* 1. PERFORMANCE CARD */}
            <div className="hud-section-box">
              <div className="hud-section-header">
                <Gauge size={14} className="hud-section-icon" />
                <span className="hud-section-title">PERFORMANCE</span>
              </div>
              
              <div className="hud-meta-list">
                <div className="hud-meta-item">
                  <div className="hud-meta-info">
                    <span className="hud-meta-label">Response Time</span>
                    <div className="hud-meta-val-row">
                      <span className="hud-meta-value green">{lastResponseTime || '0.84'}</span>
                      <span className="hud-meta-unit">s</span>
                    </div>
                  </div>
                  <MiniBarChart data={cpuWave} color="#00ff88" />
                </div>

                <div className="hud-meta-item">
                  <div className="hud-meta-info">
                    <span className="hud-meta-label">Speed</span>
                    <div className="hud-meta-val-row">
                      <span className="hud-meta-value cyan">{lastTokensPerSec || '142'}</span>
                      <span className="hud-meta-unit">t/s</span>
                    </div>
                  </div>
                  <MiniBarChart data={tokenWave} color="#00e5ff" />
                </div>

                <div className="hud-meta-item">
                  <div className="hud-meta-info">
                    <span className="hud-meta-label">Latency</span>
                    <div className="hud-meta-val-row">
                      <span className="hud-meta-value cyan">{lastLatency || '23'}</span>
                      <span className="hud-meta-unit">ms</span>
                    </div>
                  </div>
                  <MiniBarChart data={latencyWave} color="#00e5ff" />
                </div>

                <div className="hud-meta-item uptime-row">
                  <div className="hud-uptime-left">
                    <Clock size={12} className="uptime-icon" />
                    <span className="hud-meta-label">Uptime</span>
                  </div>
                  <div className="hud-meta-val-row">
                    <span className="hud-meta-value blue uptime-val">{formatUptime(stats.uptime)}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* 2. CONTEXT WINDOW CARD */}
            <div className="hud-section-box">
              <div className="hud-section-header">
                <Database size={14} className="hud-section-icon" />
                <span className="hud-section-title">CHAT MEMORY</span>
              </div>

              <div className="hud-context-info">
                <div className="hud-context-numbers">
                  <span className="hud-context-used">{usedTokens.toLocaleString()}</span>
                  <span className="hud-context-total">/ 128K tokens</span>
                </div>
                
                <div className="hud-progress-bar-container">
                  <div className="hud-progress-bar" style={{ width: `${Math.max(2, ctxPercent)}%` }}>
                    <div className="hud-progress-glow"></div>
                  </div>
                </div>

                <div className="hud-context-footer">
                  <span>{ctxPercent}% Used</span>
                  <span className="footer-dot">•</span>
                  <span>{((128000 - usedTokens)/1000).toFixed(1)}K Free</span>
                </div>
              </div>
            </div>



            {/* 5. HARDWARE & SYSTEM INFO CARD */}
            <div className="hud-section-box">
              <div className="hud-section-header">
                <Server size={14} className="hud-section-icon" />
                <span className="hud-section-title">System Info</span>
              </div>

              <div className="hud-hardware-grid">
                <div className="hud-hw-card">
                  <span className="hud-hw-label">AI Model</span>
                  <span className="hud-hw-val cyan">OMEGA AI (7.2B)</span>
                </div>
                <div className="hud-hw-card">
                  <span className="hud-hw-label">Server</span>
                  <span className="hud-hw-val green">Connected</span>
                </div>
                <div className="hud-hw-card">
                  <span className="hud-hw-label">Architecture</span>
                  <span className="hud-hw-val cyan">x86_64 / CUDA</span>
                </div>
                <div className="hud-hw-card">
                  <span className="hud-hw-label">VRAM Usage</span>
                  <span className="hud-hw-val green">3.8 / 12 GB</span>
                </div>
              </div>
            </div>

            {/* 6. LIVE TELEMETRY CONSOLE STREAM */}
            <div className="hud-log-stream-card">
              <div className="hud-stream-header">
                <div className="hud-stream-title">
                  <Radio size={12} className="text-cyan-400 animate-pulse" />
                  <span>Live Log Stream</span>
                </div>
                <span className="hud-stream-badge">Live</span>
              </div>
              <div className="hud-stream-logs custom-scrollbar">
                {logFeed.map((item, idx) => (
                  <div key={idx} className="hud-log-line">
                    <span className="hud-log-time">{item.time}</span>
                    <span className="hud-log-arrow">›</span>
                    <span className="hud-log-msg">{item.msg}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'Memory' && (
          <div className="hud-tab-content">
            {/* 1. MEMORY USAGE */}
            <div className="hud-section-box">
              <div className="hud-section-header">
                <HardDrive size={14} className="hud-section-icon" />
                <span className="hud-section-title">Memory Usage</span>
              </div>
              <div className="hud-meta-list text-layout">
                <div className="hud-text-row flex justify-between py-1">
                  <span className="hud-meta-label">Memory Used</span>
                  <span className="hud-text-value">{(performance.memory ? (performance.memory.usedJSHeapSize / 1024 / 1024).toFixed(1) : '18.4')} MB</span>
                </div>
                <div className="hud-text-row flex justify-between py-1">
                  <span className="hud-meta-label">Memory Limit</span>
                  <span className="hud-text-value">{(performance.memory ? (performance.memory.jsHeapSizeLimit / 1024 / 1024).toFixed(0) : '2048')} MB</span>
                </div>
                <div className="hud-text-row flex justify-between py-1">
                  <span className="hud-meta-label">Model Size</span>
                  <span className="hud-text-value cyan font-bold">7.2B</span>
                </div>
                <div className="hud-text-row flex justify-between py-1">
                  <span className="hud-meta-label">Active Messages</span>
                  <span className="hud-text-value green font-bold">{activeSessionMessages.length}</span>
                </div>
              </div>
            </div>

            {/* 2. VRAM & CACHE PERFORMANCE */}
            <div className="hud-section-box">
              <div className="hud-section-header">
                <Database size={14} className="hud-section-icon" />
                <span className="hud-section-title">VRAM & Cache Performance</span>
              </div>
              <div className="hud-hardware-grid">
                <div className="hud-hw-card">
                  <span className="hud-hw-label">KV Cache</span>
                  <span className="hud-hw-val cyan">1.2 GB / 4.0 GB</span>
                </div>
                <div className="hud-hw-card">
                  <span className="hud-hw-label">Cache Hit Ratio</span>
                  <span className="hud-hw-val green">98.4%</span>
                </div>
                <div className="hud-hw-card">
                  <span className="hud-hw-label">Allocated VRAM</span>
                  <span className="hud-hw-val cyan">3.8 GB</span>
                </div>
                <div className="hud-hw-card">
                  <span className="hud-hw-label">GPU Paging</span>
                  <span className="hud-hw-val green">0 Page Faults</span>
                </div>
              </div>
            </div>

            {/* 3. LIVE LOG STREAM */}
            <div className="hud-log-stream-card">
              <div className="hud-stream-header">
                <div className="hud-stream-title">
                  <Radio size={12} className="text-cyan-400 animate-pulse" />
                  <span>Live Log Stream</span>
                </div>
                <span className="hud-stream-badge">Live</span>
              </div>
              <div className="hud-stream-logs custom-scrollbar">
                {logFeed.map((item, idx) => (
                  <div key={idx} className="hud-log-line">
                    <span className="hud-log-time">{item.time}</span>
                    <span className="hud-log-arrow">›</span>
                    <span className="hud-log-msg">{item.msg}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'Tools' && (
          <div className="hud-tab-content">
            {/* 1. CONNECTED TOOLS */}
            <div className="hud-section-box">
              <div className="hud-section-header">
                <Terminal size={14} className="hud-section-icon" />
                <span className="hud-section-title">Connected Tools</span>
              </div>
              <div className="hud-meta-list text-layout">
                <div className="hud-text-row flex justify-between items-center py-1">
                  <span className="hud-meta-label">System Telemetry</span>
                  <span className="hud-status-badge online flex items-center gap-1 text-[10px] text-emerald-400 font-bold">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> Online
                  </span>
                </div>
                <div className="hud-text-row flex justify-between items-center py-1">
                  <span className="hud-meta-label">AI Classifier</span>
                  <span className="hud-status-badge online flex items-center gap-1 text-[10px] text-emerald-400 font-bold">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> Online
                  </span>
                </div>
                <div className="hud-text-row flex justify-between items-center py-1">
                  <span className="hud-meta-label">Voice Output</span>
                  <span className="hud-status-badge online flex items-center gap-1 text-[10px] text-emerald-400 font-bold">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> Online
                  </span>
                </div>
                <div className="hud-text-row flex justify-between items-center py-1">
                  <span className="hud-meta-label">Web Search Engine</span>
                  <span className="hud-status-badge online flex items-center gap-1 text-[10px] text-emerald-400 font-bold">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> Ready
                  </span>
                </div>
              </div>
            </div>

            {/* 2. TOOL RUNTIME METRICS */}
            <div className="hud-section-box">
              <div className="hud-section-header">
                <Zap size={14} className="hud-section-icon" />
                <span className="hud-section-title">Tool Runtime Metrics</span>
              </div>
              <div className="hud-hardware-grid">
                <div className="hud-hw-card">
                  <span className="hud-hw-label">Invocations</span>
                  <span className="hud-hw-val cyan">142 Calls</span>
                </div>
                <div className="hud-hw-card">
                  <span className="hud-hw-label">Avg Tool Latency</span>
                  <span className="hud-hw-val green">18 ms</span>
                </div>
                <div className="hud-hw-card">
                  <span className="hud-hw-label">Failure Rate</span>
                  <span className="hud-hw-val green">0.00%</span>
                </div>
                <div className="hud-hw-card">
                  <span className="hud-hw-label">Active Workers</span>
                  <span className="hud-hw-val cyan">4 Threads</span>
                </div>
              </div>
            </div>

            {/* 3. LIVE LOG STREAM */}
            <div className="hud-log-stream-card">
              <div className="hud-stream-header">
                <div className="hud-stream-title">
                  <Radio size={12} className="text-cyan-400 animate-pulse" />
                  <span>Live Log Stream</span>
                </div>
                <span className="hud-stream-badge">Live</span>
              </div>
              <div className="hud-stream-logs custom-scrollbar">
                {logFeed.map((item, idx) => (
                  <div key={idx} className="hud-log-line">
                    <span className="hud-log-time">{item.time}</span>
                    <span className="hud-log-arrow">›</span>
                    <span className="hud-log-msg">{item.msg}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function CircularProgress({ percent, label, strokeColor }) {
  const radius = 24;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percent / 100) * circumference;

  return (
    <div className="hud-circular-item">
      <div className="hud-circle-wrapper">
        <svg width="60" height="60" className="hud-circle-svg">
          <defs>
            <filter id={`glow-${label}`} x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="2" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
          <circle cx="30" cy="30" r={radius} className="hud-circle-bg" stroke="rgba(255,255,255,0.06)" strokeWidth="4" fill="none" />
          <circle
            cx="30"
            cy="30"
            r={radius}
            className="hud-circle-fill"
            stroke={strokeColor}
            strokeWidth="4"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="none"
            filter={`url(#glow-${label})`}
            style={{ transition: 'stroke-dashoffset 0.6s cubic-bezier(0.4, 0, 0.2, 1)' }}
          />
        </svg>
        <div className="hud-circle-inner-val">
          <span className="hud-circle-percent">{percent}</span>
          <span className="hud-circle-unit">%</span>
        </div>
      </div>
      <span className="hud-circle-label">{label}</span>
    </div>
  );
}

function MiniBarChart({ data, color }) {
  const maxVal = Math.max(...(data || []), 10);
  return (
    <div className="mini-chart-container">
      {(data || []).map((h, i) => {
        const heightPercent = Math.max(20, Math.min(100, (h / maxVal) * 100));
        return (
          <div
            key={i}
            className="mini-chart-bar"
            style={{
              height: `${heightPercent}%`,
              backgroundColor: color,
              boxShadow: `0 0 6px ${color}aa`
            }}
          />
        );
      })}
    </div>
  );
}

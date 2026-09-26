import React, { useState, useEffect, useRef } from 'react';
import { VideoOff, Rss, Layers, Radio, Shield, Database, User, Cpu, Play, ToggleLeft, ToggleRight } from 'lucide-react';
import HologramSphere from './HologramSphere';

export default function DashboardView({ 
  computing, 
  activeAgentKey, 
  sessions, 
  onSelectSession,
  attachment,
  activeTools,
  setActiveTools,
  activityLogs,
  setActivityLogs,
  onSelectAgent,
  telemetry
}) {
  const [dashboardTab, setDashboardTab] = useState('Overview');
  const [transmitGlow, setTransmitGlow] = useState(false);
  const [isTransmitting, setIsTransmitting] = useState(false);

  // Terminal Console CLI States
  const [consoleInput, setConsoleInput] = useState('');
  const [consoleLines, setConsoleLines] = useState([
    "Initializing OMEGA...",
    "Backend server: Connected",
    "AI predictor model: Connected",
    "System ready. Type 'help' for commands."
  ]);
  const consoleEndRef = useRef(null);

  useEffect(() => {
    if (consoleEndRef.current) {
      consoleEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [consoleLines, dashboardTab]);

  const handleTransmitClick = () => {
    if (isTransmitting) return;
    setTransmitGlow(true);
    setIsTransmitting(true);
    
    // Append packet transmission log
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    setActivityLogs(prev => [
      { type: "CORE SYNC", text: "Syncing data with system...", status: "ACTIVE", time: timeStr },
      ...prev
    ]);

    setTimeout(() => {
      setTransmitGlow(false);
      setIsTransmitting(false);
      const timeStrDone = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      setActivityLogs(prev => [
        { type: "CORE SYNC", text: "Data synced successfully.", status: "COMPLETE", time: timeStrDone },
        ...prev
      ]);
    }, 2500);
  };

  const toggleTool = (toolKey) => {
    if (!setActiveTools) return;
    setActiveTools(prev => {
      const updated = { ...prev, [toolKey]: !prev[toolKey] };
      // Append log
      const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      const toolName = toolKey.toUpperCase();
      const action = updated[toolKey] ? "ENABLED" : "DISABLED";
      setActivityLogs(oldLogs => [
        { type: "TOOL STATE", text: `Tool ${toolName} has been ${action.toLowerCase()}.`, status: updated[toolKey] ? "READY" : "OK", time: timeStr },
        ...oldLogs
      ]);
      return updated;
    });
  };

  const handleConsoleSubmit = (e) => {
    e.preventDefault();
    if (!consoleInput.trim()) return;

    const cmd = consoleInput.trim();
    const args = cmd.toLowerCase().split(' ');
    const mainCommand = args[0];

    const linesToAdd = [`$ ${cmd}`];

    if (mainCommand === 'help') {
      linesToAdd.push(
        "Available console commands:",
        "  help                 - Show available commands",
        "  status               - Show active AI agents",
        "  telemetry            - Show system performance metrics",
        "  agent <name>         - Switch active AI agent",
        "  clear                - Clear console screen"
      );
    } else if (mainCommand === 'clear') {
      setConsoleLines([]);
      setConsoleInput('');
      return;
    } else if (mainCommand === 'status') {
      linesToAdd.push(
        "Active AI Agents:",
        "  - NEXUS CORE   : General AI & planning (Active)",
        "  - CODEFORGE    : Programming assistant",
        "  - SYNAPSE      : Knowledge & search assistant",
        "  - VOICEPULSE   : Voice & speech assistant"
      );
    } else if (mainCommand === 'telemetry') {
      linesToAdd.push(
        "System Metrics:",
        `  {`,
        `    "cpu_usage": "${telemetry ? Math.round(telemetry.cpu * 10) : 12}%",`,
        `    "latency": "${telemetry ? telemetry.latency : 23}ms",`,
        `    "speed": "${telemetry ? telemetry.tokens : 142} t/s",`,
        `    "active_session": "${sessions && sessions.length > 0 ? sessions[0].title : 'None'}"`,
        `  }`
      );
    } else if (mainCommand === 'agent') {
      const agentTarget = args[1];
      if (!agentTarget) {
        linesToAdd.push("Error: Must specify agent target. Usage: agent <nexus|codeforge|synapse|voicepulse>");
      } else if (['nexus', 'codeforge', 'synapse', 'voicepulse'].includes(agentTarget)) {
        if (onSelectAgent) {
          onSelectAgent(agentTarget);
          linesToAdd.push(`Success: Operational state routed to agent [${agentTarget.toUpperCase()}].`);
        } else {
          linesToAdd.push("Error: Agent dispatcher callback binding unavailable.");
        }
      } else {
        linesToAdd.push(`Error: Unknown agent target '${agentTarget}'.`);
      }
    } else {
      linesToAdd.push(`omega: command not found: ${mainCommand}`);
    }

    setConsoleLines(prev => [...prev, ...linesToAdd]);
    setConsoleInput('');
  };

  const headlines = [
    { text: "System routing ready", time: "1m ago" },
    { text: "AI model connected", time: "5m ago" },
    { text: "Knowledge base loaded (1.2M records)", time: "12m ago" },
    { text: "System speed optimized", time: "24m ago" },
    { text: "Voice synthesis ready", time: "40m ago" }
  ];

  // If the user attached an image, prepare a local object URL for visual preview
  const [imagePreviewUrl, setImagePreviewUrl] = useState(null);
  useEffect(() => {
    if (attachment && attachment.file && attachment.file.type.startsWith('image/')) {
      const url = URL.createObjectURL(attachment.file);
      setImagePreviewUrl(url);
      
      const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      setActivityLogs(prev => [
        { type: "CAMERA LINK", text: `Camera connected: Image "${attachment.name}" loaded successfully.`, status: "COMPLETE", time: timeStr },
        ...prev
      ]);

      return () => URL.revokeObjectURL(url);
    } else {
      setImagePreviewUrl(null);
    }
  }, [attachment]);

  return (
    <div className="dashboard-container">
      {/* A. Top Navigation Bar */}
      <div className="dashboard-header">
        <div className="dash-brand-indicator">
          <Radio size={14} className="radio-pulse-icon" />
          <span>Dashboard</span>
        </div>
        <div className="dashboard-nav-tabs">
          {['Overview', 'Agents', 'Tools', 'Console'].map((tab) => (
            <button
              key={tab}
              className={`dash-tab-btn ${dashboardTab === tab ? 'active' : ''}`}
              onClick={() => setDashboardTab(tab)}
            >
              {tab}
            </button>
          ))}
        </div>
        <div className="dash-status-badge">
          <span className="dash-badge-dot"></span>
          <span>System Online</span>
        </div>
      </div>

      {dashboardTab === 'Overview' && (
        <div className="dashboard-grid animate-fade-in">
          {/* 1. Left Column */}
          <div className="dash-col left-col">
            {/* Widget 1.1: Camera Feed */}
            <div className="dash-card camera-card">
              <div className="card-corner tl"></div>
              <div className="card-corner tr"></div>
              <div className="card-corner bl"></div>
              <div className="card-corner br"></div>
              
              <div className="camera-header">
                <span className={`camera-dot ${imagePreviewUrl ? 'online-dot' : ''}`}></span>
                <span className="camera-title">{imagePreviewUrl ? 'Camera: Online' : 'Camera: Offline'}</span>
              </div>
              
              <div className="camera-body">
                {imagePreviewUrl ? (
                  <div className="camera-preview-wrapper" style={{ width: '100%', height: '100%', overflow: 'hidden', borderRadius: '8px' }}>
                    <img 
                      src={imagePreviewUrl} 
                      alt="Camera Feed Preview" 
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }} 
                    />
                  </div>
                ) : (
                  <>
                    <VideoOff size={32} className="camera-off-icon" />
                    <span className="camera-status-text">Camera Offline</span>
                  </>
                )}
              </div>
              <div className="camera-overlay-text">
                {imagePreviewUrl ? `File: ${attachment.name}` : 'Camera: Offline'}
              </div>
            </div>

            {/* Widget 1.2: Today Headlines */}
            <div className="dash-card headlines-card">
              <div className="card-header">
                <Rss size={14} className="card-icon blue" />
                <span>Latest News</span>
              </div>
              <div className="headlines-list">
                {headlines.map((hl, i) => (
                  <div key={i} className="headline-item">
                    <span className="headline-bullet"></span>
                    <div className="headline-content">
                      <p className="headline-text">{hl.text}</p>
                      <span className="headline-time">{hl.time}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* 2. Center Column */}
          <div className="dash-col center-col">
            {/* Widget 2.1: Neural Node Connector */}
            <div className="dash-card connector-card">
              <div className="connector-flex">
                {/* Left side node list */}
                <div className="connector-nodes">
                  <div 
                    className={`node-item hud-node clickable-node ${activeAgentKey === 'nexus' ? 'active-node' : ''}`}
                    onClick={() => onSelectAgent && onSelectAgent('nexus')}
                  >
                    <Shield size={14} className="node-icon" />
                    <span>Nexus</span>
                    <span className="node-status-led blue"></span>
                  </div>
                  <div 
                    className={`node-item history-node clickable-node ${activeAgentKey === 'synapse' ? 'active-node' : ''}`}
                    onClick={() => onSelectAgent && onSelectAgent('synapse')}
                  >
                    <Database size={14} className="node-icon" />
                    <span>Synapse</span>
                    <span className="node-status-led blue"></span>
                  </div>
                  <div 
                    className={`node-item user-node clickable-node ${activeAgentKey === 'codeforge' ? 'active-node' : ''}`}
                    onClick={() => onSelectAgent && onSelectAgent('codeforge')}
                  >
                    <User size={14} className="node-icon" />
                    <span>CodeForge</span>
                    <span className="node-status-led blue"></span>
                  </div>
                </div>

                {/* SVG Connecting Paths */}
                <div className="connector-svg-container">
                  <svg className="connector-svg" viewBox="0 0 100 120" fill="none">
                    <path
                      d="M 10 25 C 40 25, 45 60, 90 60"
                      stroke={activeAgentKey === 'nexus' ? 'var(--color-cyan)' : 'rgba(255, 255, 255, 0.15)'}
                      strokeWidth="1.5"
                      strokeDasharray={isTransmitting ? "2 2" : "4 4"}
                      className={`dash-svg-path path-blue ${isTransmitting ? 'path-transmitting' : ''}`}
                    />
                    <path
                      d="M 10 60 C 40 60, 45 60, 90 60"
                      stroke={activeAgentKey === 'synapse' ? 'var(--color-cyan)' : 'rgba(255, 255, 255, 0.15)'}
                      strokeWidth="1.5"
                      strokeDasharray={isTransmitting ? "2 2" : "4 4"}
                      className={`dash-svg-path path-red ${isTransmitting ? 'path-transmitting' : ''}`}
                    />
                    <path
                      d="M 10 95 C 40 95, 45 60, 90 60"
                      stroke={activeAgentKey === 'codeforge' ? 'var(--color-cyan)' : 'rgba(255, 255, 255, 0.15)'}
                      strokeWidth="1.5"
                      strokeDasharray={isTransmitting ? "2 2" : "4 4"}
                      className={`dash-svg-path path-gray ${isTransmitting ? 'path-transmitting' : ''}`}
                    />
                    <circle cx="90" cy="60" r="3" fill="var(--color-cyan)" />
                  </svg>
                </div>

                {/* Right side Hologram Sphere */}
                <div className="connector-sphere-container">
                  <HologramSphere computing={computing || isTransmitting} agent={activeAgentKey} />
                </div>
              </div>

              <div className="connector-footer">
                <button
                  className={`transmit-btn ${transmitGlow ? 'glowing' : ''}`}
                  onClick={handleTransmitClick}
                  disabled={isTransmitting}
                >
                  <Play size={10} fill="currentColor" />
                  <span>{isTransmitting ? 'Syncing...' : 'Sync Data'}</span>
                </button>
              </div>
            </div>

            {/* Widget 2.2: Visual Intelligence Hub */}
            <div className="dash-card visual-card">
              <div className="visual-header">
                <Layers size={14} className="card-icon green" />
                <span>Image & File Hub</span>
              </div>
              <div className="visual-body">
                <div className="visual-radar-wrapper">
                  <div className="radar-circle outer"></div>
                  <div className="radar-circle middle"></div>
                  <div className="radar-circle inner"></div>
                  <Cpu size={24} className="radar-cpu-icon" />
                </div>
                <div className="visual-details">
                  <h3>Visual Processing</h3>
                  <p>Images, files, and data (420 / 1024 synced)</p>
                  <div className="visual-badges">
                    <span className="badge green">Ready</span>
                    <span className="badge blue">7.2B Model</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* 3. Right Column */}
          <div className="dash-col right-col">
            {/* Widget 3.1: System activity logs */}
            <div className="dash-card logs-card">
              <div className="card-header">
                <Cpu size={14} className="card-icon green" />
                <span>Activity Logs</span>
              </div>
              <div className="activity-logs-feed">
                {activityLogs.map((log, i) => (
                  <div key={i} className="log-row animate-fade-in">
                    <div className="log-row-header">
                      <span className={`log-badge ${log.status.toLowerCase()}`}>{log.type}</span>
                      <span className="log-time">{log.time}</span>
                    </div>
                    <p className="log-text">{log.text}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Session Launcher */}
            <div className="dash-card quick-sessions-card">
              <div className="card-header">
                <span>RECENT CHATS</span>
              </div>
              <ul className="quick-sessions-list" style={{ listStyle: 'circle inside', paddingLeft: '6px', margin: 0 }}>
                {sessions.slice(0, 3).map((sess) => (
                  <li key={sess.id} className="quick-session-li-item" style={{ color: '#94a3b8', marginBottom: '4px' }}>
                    <div
                      className="quick-session-item"
                      onClick={() => onSelectSession(sess.id)}
                      style={{ display: 'inline-flex' }}
                    >
                      <div className="quick-session-meta">
                        <p className="quick-session-title">{sess.title}</p>
                        <span className="quick-session-tokens">{sess.tokens} tokens</span>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {dashboardTab === 'Agents' && (
        <div className="dashboard-tab-fallback animate-fade-in">
          <Layers size={48} className="fallback-icon" />
          <h2>AI Agents</h2>
          <p>View and select active AI agents.</p>
          <div className="nodes-mock-graph">
            <div 
              className={`mock-node clickable-node ${activeAgentKey === 'nexus' ? 'central' : 'edge'}`}
              onClick={() => onSelectAgent && onSelectAgent('nexus')}
            >
              Nexus Core
            </div>
            <div 
              className={`mock-node clickable-node ${activeAgentKey === 'codeforge' ? 'central' : 'edge'}`}
              onClick={() => onSelectAgent && onSelectAgent('codeforge')}
            >
              CodeForge
            </div>
            <div 
              className={`mock-node clickable-node ${activeAgentKey === 'synapse' ? 'central' : 'edge'}`}
              onClick={() => onSelectAgent && onSelectAgent('synapse')}
            >
              Synapse
            </div>
          </div>
          <p style={{ fontSize: '10px', color: 'rgba(255,255,255,0.3)', marginTop: '20px' }}>
            *Click an agent card above to select it.
          </p>
        </div>
      )}

      {dashboardTab === 'Tools' && (
        <div className="dashboard-tab-fallback animate-fade-in" style={{ padding: '24px' }}>
          <Database size={48} className="fallback-icon" />
          <h2>Tools & Features</h2>
          <p style={{ marginBottom: '20px' }}>Turn system tools and services on or off.</p>
          <div className="tools-mock-grid">
            <div className="mock-tool-card" style={{ display: 'flex', flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
              <div style={{ textAlign: 'left' }}>
                <strong style={{ display: 'block', fontSize: '12px' }}>System Telemetry</strong>
                <span style={{ fontSize: '10px', color: 'rgba(255,255,255,0.4)' }}>Logs system performance</span>
              </div>
              <button 
                onClick={() => toggleTool('oracle')}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: activeTools.oracle ? 'var(--color-cyan)' : 'rgba(255,255,255,0.2)' }}
              >
                {activeTools.oracle ? <ToggleRight size={28} /> : <ToggleLeft size={28} />}
              </button>
            </div>

            <div className="mock-tool-card" style={{ display: 'flex', flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
              <div style={{ textAlign: 'left' }}>
                <strong style={{ display: 'block', fontSize: '12px' }}>AI Classifier</strong>
                <span style={{ fontSize: '10px', color: 'rgba(255,255,255,0.4)' }}>Answers queries & classifies data</span>
              </div>
              <button 
                onClick={() => toggleTool('flask')}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: activeTools.flask ? 'var(--color-cyan)' : 'rgba(255,255,255,0.2)' }}
              >
                {activeTools.flask ? <ToggleRight size={28} /> : <ToggleLeft size={28} />}
              </button>
            </div>

            <div className="mock-tool-card" style={{ display: 'flex', flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
              <div style={{ textAlign: 'left' }}>
                <strong style={{ display: 'block', fontSize: '12px' }}>Web Search</strong>
                <span style={{ fontSize: '10px', color: 'rgba(255,255,255,0.4)' }}>Fetches latest info online</span>
              </div>
              <button 
                onClick={() => toggleTool('scraper')}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: activeTools.scraper ? 'var(--color-cyan)' : 'rgba(255,255,255,0.2)' }}
              >
                {activeTools.scraper ? <ToggleRight size={28} /> : <ToggleLeft size={28} />}
              </button>
            </div>

            <div className="mock-tool-card" style={{ display: 'flex', flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
              <div style={{ textAlign: 'left' }}>
                <strong style={{ display: 'block', fontSize: '12px' }}>Voice Output</strong>
                <span style={{ fontSize: '10px', color: 'rgba(255,255,255,0.4)' }}>Reads responses out loud</span>
              </div>
              <button 
                onClick={() => toggleTool('speech')}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: activeTools.speech ? 'var(--color-cyan)' : 'rgba(255,255,255,0.2)' }}
              >
                {activeTools.speech ? <ToggleRight size={28} /> : <ToggleLeft size={28} />}
              </button>
            </div>
          </div>
        </div>
      )}

      {dashboardTab === 'Console' && (
        <div className="dashboard-tab-fallback console-view animate-fade-in" style={{ background: '#000000' }}>
          <div className="console-header">
            <span className="console-dot red"></span>
            <span className="console-dot yellow"></span>
            <span className="console-dot green"></span>
            <span className="console-title">Console Terminal</span>
          </div>
          <div className="console-body" style={{ overflowY: 'auto', flex: 1, maxHeight: '380px', background: '#000000' }}>
            {consoleLines.map((line, idx) => (
              <p key={idx} className="console-line" style={{ whiteSpace: 'pre-wrap' }}>{line}</p>
            ))}
            <div ref={consoleEndRef} />
          </div>
          <form onSubmit={handleConsoleSubmit} className="console-input-row" style={{ display: 'flex', alignItems: 'center', borderTop: '1px solid rgba(255,255,255,0.08)', padding: '10px 16px', background: '#000000' }}>
            <span className="console-prompt" style={{ fontFamily: 'monospace', fontSize: '12px', color: 'var(--color-online)', marginRight: '8px' }}>&gt;</span>
            <input
              type="text"
              value={consoleInput}
              onChange={(e) => setConsoleInput(e.target.value)}
              placeholder="Type a command... (help, status, telemetry, agent <name>, clear)"
              style={{
                flex: 1,
                background: '#000000',
                border: 'none',
                outline: 'none',
                color: 'var(--color-online)',
                fontFamily: 'monospace',
                fontSize: '12px',
                width: '100%'
              }}
            />
          </form>
        </div>
      )}
    </div>
  );
}

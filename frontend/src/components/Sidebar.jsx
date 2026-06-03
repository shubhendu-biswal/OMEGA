import React from 'react';
import { 
  Plus, 
  MessageSquare, 
  Settings, 
  Cpu, 
  Terminal, 
  Mic, 
  Activity,
  Sparkles,
  Bot
} from 'lucide-react';

/**
 * Sidebar component for the Neural AI Assistant.
 */
export default function Sidebar({
  sessions,
  activeSessionId,
  onSelectSession,
  onNewSession,
  agents,
  activeAgentKey,
  onSelectAgent,
  isSimpleTextMode,
  onToggleSimpleTextMode
}) {
  return (
    <aside className="sidebar">
      {/* 1. Brand Section */}
      <div className="sidebar-header">
        <div className="brand-icon-wrapper">
          <Bot size={24} />
          <div className="brand-status-dot"></div>
        </div>
        <div className="brand-meta hide-on-mobile">
          <h1 className="brand-name">OMEGA</h1>
          <div className="brand-status-text">
            <span>● ONLINE</span>
            <span className="brand-version">v3.1</span>
          </div>
        </div>
      </div>

      {/* 2. New Session Trigger */}
      <div className="sidebar-actions">
        <button className="new-session-btn" onClick={onNewSession} title="New Session">
          <Plus size={16} />
          <span>NEW SESSION</span>
        </button>
      </div>

      {/* 3. Session Log history */}
      <div className="session-log-section">
        <div className="session-log-header hide-on-mobile">
          <span className="session-log-title">Session Log</span>
          <div className="session-log-divider"></div>
        </div>
        
        <div className="session-list">
          {sessions.map((session) => (
            <div
              key={session.id}
              className={`session-item ${activeSessionId === session.id ? 'active' : ''}`}
              onClick={() => onSelectSession(session.id)}
            >
              <MessageSquare size={16} className="session-icon" />
              <div className="session-details hide-on-mobile">
                <span className="session-title">{session.title}</span>
                <div className="session-meta">
                  <span>{session.timeAgo}</span>
                  <span>#</span>
                  <span className="session-stat">{session.tokens}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 4. AI Agents Hub */}
      <div className="agents-section">
        <div className="agents-header hide-on-mobile">
          <span className="agents-title">AI Agents</span>
          <div className="agents-divider"></div>
        </div>

        <div className="agents-grid">
          {agents.map((agent) => {
            const Icon = agent.icon;
            const isActive = activeAgentKey === agent.key;
            return (
              <div
                key={agent.key}
                className={`agent-card ${agent.color} ${isActive ? 'active' : ''}`}
                onClick={() => onSelectAgent(agent.key)}
                title={`${agent.name}: ${agent.desc}`}
              >
                <div className="agent-card-header">
                  <Icon size={16} className="agent-icon" />
                  <div className="agent-avatar-dot"></div>
                </div>
                <div className="agent-details hide-on-mobile">
                  <span className="agent-name">{agent.name}</span>
                  <span className="agent-desc">{agent.desc}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 5. Operator Panel Footer */}
      <div className="operator-panel">
        <div className="operator-info">
          <div className="operator-avatar">OP</div>
          <div className="operator-meta hide-on-mobile">
            <span className="operator-name">Operator</span>
            <div className="operator-plan-tag">
              <span>PRO</span>
              <span className="operator-plan-premium">• UNLIMITED</span>
            </div>
          </div>
        </div>
        <div className="operator-actions" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <button
            onClick={onToggleSimpleTextMode}
            title={isSimpleTextMode ? "Enable Futuristic Mode" : "Enable Readability Mode"}
            style={{
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              color: isSimpleTextMode ? 'var(--accent)' : 'var(--color-text-muted)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '4px',
              borderRadius: '4px',
              transition: 'all 0.2s'
            }}
            className="hide-on-mobile"
          >
            <span style={{ fontSize: '16px' }}>{isSimpleTextMode ? "📖" : "⚡"}</span>
          </button>
          <Settings size={18} className="settings-btn" title="System Settings" />
        </div>
      </div>
    </aside>
  );
}

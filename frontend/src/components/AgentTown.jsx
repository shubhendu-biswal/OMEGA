import React, { useState } from 'react';
import { 
  Share2, 
  List, 
  Grid, 
  Maximize2, 
  MessageSquareText, 
  UserCheck, 
  Cpu, 
  Monitor, 
  Coffee,
  CheckCircle2
} from 'lucide-react';

const AGENTS = [
  { id: 'alice', name: 'Alice', role: 'Architect', status: 'online', color: '#10b981', avatar: '👩‍💻' },
  { id: 'bob', name: 'Bob', role: 'Engineer', status: 'idle', color: '#f59e0b', avatar: '👨‍💻' },
  { id: 'carol', name: 'Carol', role: 'Researcher', status: 'busy', color: '#ec4899', avatar: '👩‍🔬' },
  { id: 'dave', name: 'Dave', role: 'Security', status: 'online', color: '#10b981', avatar: '👨‍🔧' }
];

export default function AgentTown({ onOpenChat }) {
  const [activeTab, setActiveTab] = useState('WORKSPACES');
  const [selectedAgent, setSelectedAgent] = useState('alice');

  return (
    <div className="agent-town-container">
      {/* 1. Top Header Bar */}
      <div className="agent-town-header">
        <div className="agent-town-title">
          <span className="cyan-dot">•</span>
          <span className="title-text">Agent Workspace</span>
        </div>

        {/* Center View Tabs */}
        <div className="agent-town-tabs">
          {['Workspaces', 'Visual Hub', 'Gestures'].map(tab => (
            <button
              key={tab}
              className={`town-tab-btn ${activeTab === tab ? 'active' : ''}`}
              onClick={() => setActiveTab(tab)}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Header Right Action Icons */}
        <div className="agent-town-actions">
          <button className="icon-action-btn" title="Share View"><Share2 size={13} /></button>
          <button className="icon-action-btn" title="List View"><List size={13} /></button>
          <button className="icon-action-btn" title="Grid Layout"><Grid size={13} /></button>
          <button className="icon-action-btn" title="Expand Canvas"><Maximize2 size={13} /></button>
        </div>
      </div>

      {/* 2. Agent Avatars Selection Row */}
      <div className="agent-avatars-row">
        {AGENTS.map(agent => (
          <div
            key={agent.id}
            className={`agent-avatar-card ${selectedAgent === agent.id ? 'selected' : ''}`}
            onClick={() => setSelectedAgent(agent.id)}
          >
            <div className="avatar-icon-box">
              <span className="avatar-emoji">{agent.avatar}</span>
            </div>
            <span className="agent-name">{agent.name}</span>
            <span 
              className="agent-status-badge" 
              style={{ backgroundColor: agent.color }} 
            />
          </div>
        ))}
      </div>

      {/* 3. Interactive Pixel-Art Top-Down Office Floor Plan Canvas */}
      <div className="pixel-office-viewport">
        {/* Office Blueprint Background & Desks Grid */}
        <div className="office-blueprint">
          {/* Top-left Office Suite: Workstations & Laptops */}
          <div className="office-room room-workstations">
            <div className="room-label">Dev Lab</div>
            <div className="desk-cluster">
              <div className="desk desk-1">
                <Monitor size={12} className="desktop-monitor" />
                <div className="agent-sprite desk-agent" title="Dave sitting at terminal">
                  <span className="sprite-head">👨‍🔧</span>
                  <span className="task-bubble key-bubble">🔑</span>
                </div>
              </div>
              <div className="desk desk-2">
                <Monitor size={12} className="desktop-monitor" />
                <div className="agent-sprite desk-agent" title="Alice coding">
                  <span className="sprite-head">👩‍💻</span>
                  <span className="task-bubble exclam-bubble">⚡</span>
                </div>
              </div>
            </div>
          </div>

          {/* Top-Right Room: Library & Knowledge Archives */}
          <div className="office-room room-library">
            <div className="room-label">Library</div>
            <div className="bookshelf-unit">
              <div className="bookshelf" />
              <div className="bookshelf" />
            </div>
            <div className="desk desk-3">
              <Monitor size={12} className="desktop-monitor" />
              <div className="agent-sprite desk-agent" title="Carol researching">
                <span className="sprite-head">👩‍🔬</span>
              </div>
            </div>
          </div>

          {/* Bottom-Center Room: Server Room & Breakroom Lounge */}
          <div className="office-room room-breakroom">
            <div className="room-label">Lounge</div>
            <div className="breakroom-items">
              <div className="coffee-station" title="Coffee Machine">
                <Coffee size={14} className="text-amber-400" />
              </div>
              <div className="server-rack" title="Neural Subsystem Rack">
                <Cpu size={14} className="text-cyan-400" />
                <div className="server-light blinking" />
              </div>
            </div>
            <div className="desk desk-4">
              <div className="agent-sprite walking-agent" title="Bob walking">
                <span className="sprite-head">👨‍💻</span>
                <span className="task-bubble coffee-bubble">☕</span>
              </div>
            </div>
          </div>
        </div>

        {/* Floating CHAT button bottom right */}
        <button className="floating-chat-btn" onClick={onOpenChat}>
          <MessageSquareText size={15} />
          <span>CHAT</span>
        </button>

        {/* Bottom Status Bar */}
        <div className="agent-town-bottom-bar">
          <div className="status-item">
            <span className="status-dot green-dot" />
            <span className="status-text font-bold">Online</span>
          </div>
          <div className="status-item">
            <UserCheck size={12} className="text-slate-400" />
            <span className="status-text">4/7 active</span>
          </div>
          <div className="status-item">
            <span className="status-badge-busy">0 busy</span>
          </div>
        </div>
      </div>
    </div>
  );
}

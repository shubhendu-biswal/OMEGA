import React, { useState, useEffect } from 'react';
import { 
  PanelLeft,
  Mic
} from 'lucide-react';
import Sidebar from './components/Sidebar';
import ChatPanel from './components/ChatPanel';
import VoiceAssistant from './components/VoiceAssistant';

const INITIAL_SESSIONS = [
  {
    id: 'session-1',
    title: 'New chat',
    messages: [],
    createdAt: Date.now()
  }
];

export default function App() {
  const [sessions, setSessions] = useState(() => {
    try {
      const saved = localStorage.getItem('omega_chat_sessions');
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) {
          const isValid = parsed.every(s => s && typeof s.id === 'string' && Array.isArray(s.messages));
          if (isValid) {
            return parsed.map(s => {
              const hasUserMsg = Array.isArray(s.messages) && s.messages.some(m => m.sender === 'user');
              if (!s.title || s.title === 'New OMEGA Session' || (s.title === 'New chat' && hasUserMsg)) {
                const firstUser = Array.isArray(s.messages) && s.messages.find(m => m.sender === 'user');
                const raw = firstUser && firstUser.content ? firstUser.content.trim().replace(/\s+/g, ' ') : '';
                const t = raw ? (raw.length > 30 ? raw.slice(0, 30) + '...' : raw) : 'New chat';
                return { ...s, title: t };
              }
              return s;
            });
          }
        }
      }
    } catch (e) {
      console.warn("Corrupted localStorage sessions cleared:", e);
      localStorage.removeItem('omega_chat_sessions');
    }
    return INITIAL_SESSIONS;
  });

  const [activeSessionId, setActiveSessionId] = useState(() => {
    const saved = localStorage.getItem('omega_active_session_id');
    const savedSessions = localStorage.getItem('omega_chat_sessions');
    if (saved && savedSessions) {
      try {
        const parsed = JSON.parse(savedSessions);
        if (Array.isArray(parsed) && parsed.some(s => s.id === saved)) {
          return saved;
        }
        // If saved active ID not found, select most recent session with user messages
        const withHistory = parsed.find(s => Array.isArray(s.messages) && s.messages.some(m => m.sender === 'user'));
        if (withHistory) return withHistory.id;
        if (parsed.length > 0) return parsed[0].id;
      } catch (e) {}
    }
    return saved || 'session-1';
  });

  const [inputValue, setInputValue] = useState('');
  const [computing, setComputing] = useState(false);
  const [isVoiceAssistantOpen, setIsVoiceAssistantOpen] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isListening, setIsListening] = useState(false);

  // Save sessions to localStorage
  useEffect(() => {
    try {
      localStorage.setItem('omega_chat_sessions', JSON.stringify(sessions));
    } catch (e) {
      console.warn("Unable to save sessions to localStorage", e);
    }
  }, [sessions]);

  useEffect(() => {
    try {
      localStorage.setItem('omega_active_session_id', activeSessionId);
    } catch (e) {
      console.warn("Unable to save activeSessionId to localStorage", e);
    }
  }, [activeSessionId]);

  // Fetch persistent sessions from Backend Database on Mount
  useEffect(() => {
    fetch('http://localhost:9090/api/sessions')
      .then(res => {
        if (!res.ok) throw new Error("Backend DB not ready");
        return res.json();
      })
      .then(data => {
        if (Array.isArray(data) && data.length > 0) {
          const formatted = data.map(s => {
            let title = s.title;
            const hasUserMsg = Array.isArray(s.messages) && s.messages.some(m => m.sender === 'user');
            if (!title || title === 'New OMEGA Session' || (title === 'New chat' && hasUserMsg)) {
              const firstUserMsg = Array.isArray(s.messages) && s.messages.find(m => m.sender === 'user');
              if (firstUserMsg && firstUserMsg.content) {
                const raw = firstUserMsg.content.trim().replace(/\s+/g, ' ');
                title = raw.length > 30 ? raw.slice(0, 30) + '...' : raw;
              } else {
                title = 'New chat';
              }
              if (title !== s.title) {
                fetch(`http://localhost:9090/api/sessions/${s.id}`, {
                  method: 'PUT',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ id: s.id, title })
                }).catch(() => {});
              }
            }
            return {
              id: s.id,
              title: title,
              createdAt: s.createdAt || Date.now(),
              messages: Array.isArray(s.messages)
                ? s.messages.map(m => ({
                    id: `msg-${m.id || Date.now()}`,
                    sender: m.sender,
                    content: m.content,
                    timestamp: m.timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                  }))
                : []
            };
          });
          setSessions(formatted);
          setActiveSessionId(prev => {
            const savedInStorage = localStorage.getItem('omega_active_session_id');
            const candidateId = prev || savedInStorage;
            if (candidateId && formatted.some(s => s.id === candidateId)) {
              return candidateId;
            }
            const sessionWithHistory = formatted.find(s => Array.isArray(s.messages) && s.messages.some(m => m.sender === 'user'));
            return sessionWithHistory ? sessionWithHistory.id : formatted[0].id;
          });
        }
      })
      .catch(err => {
        console.warn("Could not fetch sessions from DB backend, using local storage cache:", err);
      });
  }, []);

  const activeSession = (Array.isArray(sessions) && sessions.length > 0)
    ? (sessions.find(s => s && s.id === activeSessionId) || sessions[0])
    : INITIAL_SESSIONS[0];

  const safeMessages = (activeSession && Array.isArray(activeSession.messages))
    ? activeSession.messages
    : INITIAL_SESSIONS[0].messages;

  const handleSelectSession = (id) => {
    setActiveSessionId(id);
    if (window.innerWidth <= 768) {
      setIsSidebarOpen(false);
    }
  };

  const handleNewSession = () => {
    const newId = `session-${Date.now()}`;
    const newSession = {
      id: newId,
      title: 'New chat',
      messages: [],
      createdAt: Date.now()
    };
    setSessions(prev => [newSession, ...prev]);
    setActiveSessionId(newId);
    if (window.innerWidth <= 768) {
      setIsSidebarOpen(false);
    }

    // Save new session in backend database
    fetch('http://localhost:9090/api/sessions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: newId, title: 'New chat' })
    }).catch(err => console.warn("Failed to save new session to DB:", err));
  };

  const handleClearHistory = () => {
    const resetId = `session-${Date.now()}`;
    const freshSession = {
      id: resetId,
      title: 'New chat',
      messages: [],
      createdAt: Date.now()
    };
    setSessions([freshSession]);
    setActiveSessionId(resetId);

    // Clear all sessions in backend database
    fetch('http://localhost:9090/api/sessions', {
      method: 'DELETE'
    })
      .then(() => {
        fetch('http://localhost:9090/api/sessions', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ id: resetId, title: 'New chat' })
        });
      })
      .catch(err => console.warn("Failed to clear sessions in DB:", err));
  };

  const handleDeleteSession = (sessionId) => {
    setSessions(prev => {
      const filtered = prev.filter(s => s.id !== sessionId);
      if (filtered.length === 0) {
        const fresh = {
          id: `session-${Date.now()}`,
          title: 'New chat',
          messages: [],
          createdAt: Date.now()
        };
        setActiveSessionId(fresh.id);
        return [fresh];
      }
      if (sessionId === activeSessionId) {
        setActiveSessionId(filtered[0].id);
      }
      return filtered;
    });

    fetch(`http://localhost:9090/api/sessions/${sessionId}`, {
      method: 'DELETE'
    }).catch(err => console.warn("Failed to delete session in DB:", err));
  };

  const handleRenameSession = (sessionId, newTitle) => {
    if (!newTitle || !newTitle.trim()) return;
    setSessions(prev => prev.map(s => s.id === sessionId ? { ...s, title: newTitle.trim() } : s));

    fetch(`http://localhost:9090/api/sessions/${sessionId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: sessionId, title: newTitle.trim() })
    }).catch(err => console.warn("Failed to rename session in DB:", err));
  };

  const handlePinSession = (sessionId) => {
    setSessions(prev => prev.map(s => s.id === sessionId ? { ...s, isPinned: !s.isPinned } : s));
  };

  const handleSendPrompt = (promptText) => {
    if (!promptText || !promptText.trim()) return;

    const userMsg = {
      id: `msg-${Date.now()}`,
      sender: 'user',
      content: promptText.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setSessions(prev => prev.map(s => {
      if (s.id === activeSessionId) {
        const isFirstUserMsg = s.messages.filter(m => m.sender === 'user').length === 0;
        let newTitle = s.title;
        // Auto-generate title from first user message
        if (isFirstUserMsg || s.title === 'New chat' || s.title === 'New OMEGA Session') {
          const raw = promptText.trim().replace(/\s+/g, ' ');
          newTitle = raw.length > 30 ? raw.slice(0, 30) + '...' : raw;
        }
        return {
          ...s,
          title: newTitle,
          messages: [...s.messages, userMsg],
          updatedAt: Date.now()
        };
      }
      return s;
    }));

    setInputValue('');
    setComputing(true);

    // Call Backend Spring Boot / Ollama API
    fetch('http://localhost:9090/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        prompt: promptText.trim(),
        sessionId: activeSessionId
      })
    })
      .then(res => res.json())
      .then(data => {
        const replyText = data.content || data.response || data.message || "Processed query successfully.";
        const assistantMsg = {
          id: `msg-${Date.now() + 1}`,
          sender: 'assistant',
          content: replyText,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };

        setSessions(prev => prev.map(s => {
          if (s.id === activeSessionId) {
            return {
              ...s,
              messages: [...s.messages, assistantMsg],
              updatedAt: Date.now()
            };
          }
          return s;
        }));
        setComputing(false);
      })
      .catch(err => {
        console.warn("Backend not available, using fallback simulated reply:", err);
        setTimeout(() => {
          const fallbackMsg = {
            id: `msg-${Date.now() + 1}`,
            sender: 'assistant',
            content: `I received your request: "${promptText.trim()}". All systems are ready!`,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          };

          setSessions(prev => prev.map(s => {
            if (s.id === activeSessionId) {
              return {
                ...s,
                messages: [...s.messages, fallbackMsg],
                updatedAt: Date.now()
              };
            }
            return s;
          }));
          setComputing(false);
        }, 800);
      });
  };

  return (
    <div className="saas-app-root">
      {/* Mobile Backdrop for slide-over drawer */}
      {isSidebarOpen && (
        <div 
          className="saas-sidebar-backdrop md:hidden" 
          onClick={() => setIsSidebarOpen(false)} 
        />
      )}

      {/* Main Layout Container */}
      <div className="saas-main-layout">
        {/* 1. Left Collapsible Dark Sidebar */}
        <Sidebar 
          sessions={sessions}
          activeSessionId={activeSessionId}
          onSelectSession={handleSelectSession}
          onNewSession={handleNewSession}
          onClearHistory={handleClearHistory}
          onDeleteSession={handleDeleteSession}
          onRenameSession={handleRenameSession}
          onPinSession={handlePinSession}
          isOpen={isSidebarOpen}
          onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
          onOpenVoiceMode={() => setIsVoiceAssistantOpen(true)}
        />

        {/* 2. Main Workspace */}
        <main className="saas-workspace">
          {/* Top Bar Controls */}
          <header className="saas-top-bar">
            <div className="top-bar-left">
              <button 
                className="sidebar-toggle-btn"
                onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                title={isSidebarOpen ? "Collapse sidebar" : "Expand sidebar"}
                aria-label="Toggle sidebar"
              >
                <PanelLeft size={18} strokeWidth={1.5} />
              </button>
            </div>

            {/* Single Neutral Outlined Voice Mode Trigger */}
            <div className="top-bar-right">
              <button 
                className={`saas-voice-btn ${isVoiceAssistantOpen ? 'active' : ''}`}
                onClick={() => setIsVoiceAssistantOpen(!isVoiceAssistantOpen)}
                title={isVoiceAssistantOpen ? "Exit voice mode" : "Open voice mode"}
              >
                <Mic size={16} strokeWidth={1.5} />
                <span>{isVoiceAssistantOpen ? 'Exit voice' : 'Voice mode'}</span>
              </button>
            </div>
          </header>

          {/* Chat Panel / Voice Assistant */}
          <div className="saas-chat-workspace">
            {isVoiceAssistantOpen ? (
              <VoiceAssistant 
                computing={computing}
                setComputing={setComputing}
                onMicStateChange={setIsListening}
                onClose={() => setIsVoiceAssistantOpen(false)}
              />
            ) : (
              <ChatPanel 
                activeSessionId={activeSessionId}
                messages={safeMessages} 
                computing={computing} 
                inputValue={inputValue} 
                setInputValue={setInputValue} 
                onSend={handleSendPrompt} 
                onNewSession={handleNewSession}
                onClearHistory={handleClearHistory}
                onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
                onOpenVoiceMode={() => setIsVoiceAssistantOpen(true)}
              />
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

import React, { useState, useEffect, useRef } from 'react';
import { 
  Paperclip, 
  Image as ImageIcon, 
  Send, 
  Cpu, 
  Terminal, 
  Mic, 
  Activity,
  Plus,
  MessageSquare,
  Sparkles,
  Bot,
  X,
  Volume2,
  VolumeX
} from 'lucide-react';
import Sidebar from './components/Sidebar';
import HologramSphere from './components/HologramSphere';
import ChatPanel from './components/ChatPanel';

// 1. Initial Empty Session Log Data
const INITIAL_SESSIONS = [
  {
    id: 'session-1',
    title: 'New OMEGA Session',
    timeAgo: 'Just now',
    tokens: '0',
    messages: []
  }
];

// 2. Active AI Agents configuration
const AI_AGENTS = [
  {
    key: 'nexus',
    name: 'Nexus Core',
    desc: 'General Intelligence',
    icon: Cpu,
    color: 'cyan'
  },
  {
    key: 'codeforge',
    name: 'CodeForge',
    desc: 'Code Generation',
    icon: Terminal,
    color: 'cyan'
  },
  {
    key: 'voicepulse',
    name: 'VoicePulse',
    desc: 'Speech Interface',
    icon: Mic,
    color: 'cyan'
  },
  {
    key: 'synapse',
    name: 'Synapse',
    desc: 'Deep Analysis',
    icon: Activity,
    color: 'cyan'
  }
];

// 3. Quick Action Suggestions
const SUGGESTIONS = [
  {
    text: 'Generate a futuristic UI design',
    prompt: 'Create a premium CSS glassmorphic landing page styling mockup with floating neon orbs and glowing sidebar specs.'
  },
  {
    text: 'Review my React code',
    prompt: 'Can you review this React custom state updater for thread rendering and check for memory leaks or stale closures?'
  },
  {
    text: 'Create AI-generated artwork',
    prompt: 'Describe a highly detailed prompt for an AI-generated digital painting depicting a quantum mainframe cooled in an neon glowing ice matrix.'
  },
  {
    text: 'Analyze this dataset',
    prompt: 'Process this matrix telemetry dataset mapping core phase offset angles and suggest error mitigation guidelines.'
  }
];

export default function App() {
  const [sessions, setSessions] = useState(INITIAL_SESSIONS);
  const [activeSessionId, setActiveSessionId] = useState('session-1');
  const [activeAgentKey, setActiveAgentKey] = useState('nexus');
  const [inputValue, setInputValue] = useState('');
  const [computing, setComputing] = useState(false);
  const [attachment, setAttachment] = useState(null);
  const [isSimpleTextMode, setIsSimpleTextMode] = useState(true);
  
  const fileInputRef = useRef(null);

  // VOICE ASSISTANT FEATURE STATES & LOGIC
  const [isVoiceEnabled, setIsVoiceEnabled] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);
  const isVoiceEnabledRef = useRef(isVoiceEnabled);

  const activeAgentKeyRef = useRef(activeAgentKey);
  useEffect(() => {
    activeAgentKeyRef.current = activeAgentKey;
  }, [activeAgentKey]);

  const handleSendPromptRef = useRef(null);
  useEffect(() => {
    handleSendPromptRef.current = handleSendPrompt;
  });

  useEffect(() => {
    isVoiceEnabledRef.current = isVoiceEnabled;
  }, [isVoiceEnabled]);

  // Speech Recognition (Speech to Text) Setup
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const rec = new SpeechRecognition();
      rec.continuous = false;
      rec.interimResults = false;
      rec.lang = 'en-US';

      rec.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        if (transcript) {
          if (activeAgentKeyRef.current === 'voicepulse') {
            handleSendPromptRef.current?.(transcript);
          } else {
            setInputValue(prev => {
              const separator = prev.endsWith(' ') || prev === '' ? '' : ' ';
              return prev + separator + transcript;
            });
          }
        }
      };

      rec.onerror = (e) => {
        console.error("Speech Recognition Error", e);
        setIsListening(false);
      };

      rec.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = rec;
    }
  }, []);

  const playFriendlyChime = () => {
    if (!window.AudioContext && !window.webkitAudioContext) return;
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      const ctx = new AudioCtx();
      
      const now = ctx.currentTime;
      const playTone = (freq, delay, duration) => {
        const osc = ctx.createOscillator();
        const gainNode = ctx.createGain();
        
        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq, now + delay);
        
        gainNode.gain.setValueAtTime(0, now + delay);
        gainNode.gain.linearRampToValueAtTime(0.12, now + delay + 0.05);
        gainNode.gain.exponentialRampToValueAtTime(0.0001, now + delay + duration);
        
        osc.connect(gainNode);
        gainNode.connect(ctx.destination);
        
        osc.start(now + delay);
        osc.stop(now + delay + duration);
      };
      
      // Ascent major harmony chime
      playTone(523.25, 0.0, 0.35); // C5
      playTone(659.25, 0.08, 0.35); // E5
      playTone(783.99, 0.16, 0.35); // G5
      playTone(1046.50, 0.24, 0.55); // C6
    } catch (err) {
      console.error("Failed to play chime", err);
    }
  };

  const toggleSpeechRecognition = () => {
    if (!recognitionRef.current) {
      alert("Web Speech API is not fully supported in this browser. Please use Chrome or Edge for voice assistant features.");
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      // 1. Play warm friendly chime
      playFriendlyChime();

      if (activeAgentKeyRef.current === 'voicepulse') {
        try {
          recognitionRef.current.start();
          setIsListening(true);
        } catch (err) {
          console.error("Failed to start speech recognition", err);
        }
        return;
      }

      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
        
        // 2. Speak a highly friendly and welcoming greeting
        const utterance = new SpeechSynthesisUtterance("Hi there! Welcome to Omega. I'm so glad to help you today. How can I assist you?");
        utterance.rate = 1.0;
        utterance.pitch = 1.05; // Slightly elevated pitch for a warm, welcoming tone

        const voices = window.speechSynthesis.getVoices();
        const englishVoice = voices.find(v => v.lang.startsWith('en') && v.name.includes('Google')) || 
                            voices.find(v => v.lang.startsWith('en')) || 
                            voices[0];
        if (englishVoice) {
          utterance.voice = englishVoice;
        }

        // Start listening after greeting completes to avoid registering self-voice
        utterance.onend = () => {
          try {
            recognitionRef.current.start();
            setIsListening(true);
          } catch (err) {
            console.error("Failed to start speech recognition after greeting", err);
          }
        };

        window.speechSynthesis.speak(utterance);
      } else {
        try {
          recognitionRef.current.start();
          setIsListening(true);
        } catch (err) {
          console.error("Failed to start speech recognition", err);
        }
      }
    }
  };

  // Speech Synthesis (Text to Speech) Helper
  const speakText = (text) => {
    if (!window.speechSynthesis) return;

    window.speechSynthesis.cancel(); // Stop current speaking

    // Clean markdown formatting tags for a natural verbal reading
    const cleanText = text
      .replace(/#+\s+/g, '')
      .replace(/\*\*|__/g, '')
      .replace(/\*|_/g, '')
      .replace(/`[^`]+`/g, '')
      .replace(/```[\s\S]*?```/g, '[Code block skipped]')
      .replace(/\|.*?\|/g, '')
      .replace(/[-*]\s+/g, '');

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.05;
    utterance.pitch = 1.0;

    const voices = window.speechSynthesis.getVoices();
    const englishVoice = voices.find(v => v.lang.startsWith('en') && v.name.includes('Google')) || 
                        voices.find(v => v.lang.startsWith('en')) || 
                        voices[0];
    if (englishVoice) {
      utterance.voice = englishVoice;
    }

    if (activeAgentKeyRef.current === 'voicepulse') {
      utterance.onend = () => {
        try {
          recognitionRef.current?.start();
          setIsListening(true);
        } catch (err) {
          console.error("Failed to start speech recognition after reply", err);
        }
      };
    }

    window.speechSynthesis.speak(utterance);
  };

  // Synchronize AI Agent selection with CSS variable overrides for theme transitions
  useEffect(() => {
    const root = document.documentElement;
    // Set all agents to the cyan/Nexus Core color theme
    root.style.setProperty('--accent', 'var(--color-cyan)');
    root.style.setProperty('--accent-glow', 'var(--color-cyan-glow)');
    root.style.setProperty('--border-glass', 'rgba(0, 210, 255, 0.12)');
    root.style.setProperty('--border-glass-glow', 'rgba(0, 210, 255, 0.3)');
    root.style.setProperty('--accent-grid', 'rgba(0, 210, 255, 0.02)');
    root.style.setProperty('--accent-bg-glow', 'rgba(0, 210, 255, 0.08)');
    root.style.setProperty('--bg-primary', '#030814');
    root.style.setProperty('--bg-secondary', '#061026');
    root.style.setProperty('--sidebar-bg', 'rgba(6, 16, 38, 0.85)');
    root.style.setProperty('--status-bar-bg', 'rgba(6, 16, 38, 0.5)');
  }, [activeAgentKey]);

  // Find currently active session object
  const activeSession = sessions.find(s => s.id === activeSessionId);
  const activeAgentObj = AI_AGENTS.find(a => a.key === activeAgentKey);

  // Handle setting a different active session
  const handleSelectSession = (id) => {
    setActiveSessionId(id);
    if (activeAgentKey !== 'voicepulse') {
      window.speechSynthesis?.cancel();
      try {
        recognitionRef.current?.stop();
      } catch (e) {}
      setIsListening(false);
    }
  };

  const handleSelectAgent = (agentKey) => {
    setActiveAgentKey(agentKey);

    // Cancel any current voice/speech active states
    window.speechSynthesis?.cancel();
    try {
      recognitionRef.current?.stop();
    } catch (e) {}
    setIsListening(false);

    // Automatically start a new session for the selected agent
    const newId = `session-${Date.now()}`;
    const newSession = {
      id: newId,
      title: agentKey === 'voicepulse' ? 'Voice Communication Session' : 'New OMEGA Session',
      timeAgo: 'Just now',
      tokens: '0K',
      messages: []
    };
    setSessions(prev => [newSession, ...prev]);
    setActiveSessionId(newId);

    if (agentKey === 'voicepulse') {
      // 2. Play warm friendly chime and speak VoicePulse welcome message
      setTimeout(() => {
        playFriendlyChime();
        if (window.speechSynthesis) {
          window.speechSynthesis.cancel();
          
          const welcomeText = "Hello, welcome to Omega. How can I help you? I can assist you with system telemetry, quantum computing architectures, design parameters, or code synthesis. Let me know what we are building today.";
          const utterance = new SpeechSynthesisUtterance(welcomeText);
          utterance.rate = 1.0;
          utterance.pitch = 1.05;

          const voices = window.speechSynthesis.getVoices();
          const englishVoice = voices.find(v => v.lang.startsWith('en') && v.name.includes('Google')) || 
                              voices.find(v => v.lang.startsWith('en')) || 
                              voices[0];
          if (englishVoice) {
            utterance.voice = englishVoice;
          }

          // Automatically append welcome message to UI
          const systemMsg = {
            id: `msg-${Date.now()}-assistant`,
            role: 'assistant',
            content: welcomeText,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          };
          setSessions(prev => prev.map(s => {
            if (s.id === newId) {
              return {
                ...s,
                messages: [systemMsg]
              };
            }
            return s;
          }));

          utterance.onend = () => {
            try {
              recognitionRef.current?.start();
              setIsListening(true);
            } catch (err) {
              console.error("Failed to start speech recognition after welcome", err);
            }
          };

          window.speechSynthesis.speak(utterance);
        } else {
          try {
            recognitionRef.current?.start();
            setIsListening(true);
          } catch (err) {
            console.error("Failed to start speech recognition", err);
          }
        }
      }, 300);
    }
  };

  // Reset or create an empty chat view
  const handleNewSession = () => {
    const newId = `session-${Date.now()}`;
    const newSession = {
      id: newId,
      title: activeAgentKey === 'voicepulse' ? 'Voice Communication Session' : 'New OMEGA Session',
      timeAgo: 'Just now',
      tokens: '0K',
      messages: []
    };
    setSessions([newSession, ...sessions]);
    setActiveSessionId(newId);

    if (activeAgentKey === 'voicepulse') {
      window.speechSynthesis?.cancel();
      try {
        recognitionRef.current?.stop();
      } catch (e) {}
      setIsListening(false);

      setTimeout(() => {
        playFriendlyChime();
        if (window.speechSynthesis) {
          const welcomeText = "Hello, welcome to Omega. How can I help you? I can assist you with system telemetry, quantum computing architectures, design parameters, or code synthesis. Let me know what we are building today.";
          const utterance = new SpeechSynthesisUtterance(welcomeText);
          utterance.rate = 1.0;
          utterance.pitch = 1.05;

          const voices = window.speechSynthesis.getVoices();
          const englishVoice = voices.find(v => v.lang.startsWith('en') && v.name.includes('Google')) || 
                              voices.find(v => v.lang.startsWith('en')) || 
                              voices[0];
          if (englishVoice) {
            utterance.voice = englishVoice;
          }

          // Automatically append welcome message to UI
          const systemMsg = {
            id: `msg-${Date.now()}-assistant`,
            role: 'assistant',
            content: welcomeText,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          };
          setSessions(prev => prev.map(s => {
            if (s.id === newId) {
              return {
                ...s,
                messages: [systemMsg]
              };
            }
            return s;
          }));

          utterance.onend = () => {
            try {
              recognitionRef.current?.start();
              setIsListening(true);
            } catch (err) {
              console.error("Failed to start speech recognition after welcome", err);
            }
          };

          window.speechSynthesis.speak(utterance);
        }
      }, 300);
    }
  };

  // Trigger file attachment selection
  const handleAttachmentClick = () => {
    fileInputRef.current?.click();
  };

  // Handle browser actual file attachment loading
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setAttachment({
        name: file.name,
        size: (file.size / 1024).toFixed(1) + ' KB',
        type: file.name.split('.').pop()
      });
    }
  };

  // Remove the attached file node
  const handleClearAttachment = () => {
    setAttachment(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  // Process prompt submission and trigger mock AI replies
  const handleSendPrompt = (textToSend) => {
    const promptText = textToSend || inputValue;
    if (!promptText.trim() && !attachment) return;

    const userMsgTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    // 1. Create user message entry
    let fullUserContent = promptText;
    if (attachment) {
      fullUserContent += `\n\n*(Attached File: ${attachment.name} [Size: ${attachment.size}])*`;
    }

    const newUserMessage = {
      id: `msg-${Date.now()}-user`,
      role: 'user',
      content: fullUserContent,
      timestamp: userMsgTime
    };

    // 2. Append user message to the local session
    const updatedSessions = sessions.map(session => {
      if (session.id === activeSessionId) {
        // Compute new dynamic title based on prompt if session was empty/new
        let newTitle = session.title;
        if (session.messages.length === 0) {
          newTitle = promptText.length > 28 ? promptText.substring(0, 28) + '...' : promptText;
        }

        return {
          ...session,
          title: newTitle,
          messages: [...session.messages, newUserMessage]
        };
      }
      return session;
    });

    setSessions(updatedSessions);
    setInputValue('');
    setAttachment(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
    setComputing(true);

    // 3. Fetch reply from Spring Boot backend REST API
    fetch('http://localhost:9090/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        prompt: promptText,
        agent: activeAgentObj.name
      })
    })
      .then(res => {
        if (!res.ok) {
          throw new Error("HTTP error " + res.status);
        }
        return res.json();
      })
      .then(data => {
        const responseTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const newResponse = {
          id: `msg-${Date.now()}-assistant`,
          role: 'assistant',
          content: data.content,
          timestamp: responseTime
        };

        // Append assistant response to state
        setSessions(prev => prev.map(s => {
          if (s.id === activeSessionId) {
            // Increment token counter roughly
            const rawTokens = parseInt(s.tokens) || 0;
            const newTokensVal = (rawTokens + 1.2).toFixed(1) + 'K';
            return {
              ...s,
              tokens: newTokensVal,
              messages: [...s.messages, newResponse]
            };
          }
          return s;
        }));
        setComputing(false);
        if (isVoiceEnabledRef.current) {
          speakText(data.content);
        }
      })
      .catch(err => {
        console.error("Spring Boot Connection Error:", err);
        const responseTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const aiContent = `⚠️ Connection Error: Unable to reach OMEGA Core Backend at localhost:9090.\nPlease ensure that the Spring Boot server is started and running.`;
        const newResponse = {
          id: `msg-${Date.now()}-assistant`,
          role: 'assistant',
          content: aiContent,
          timestamp: responseTime
        };
        setSessions(prev => prev.map(s => {
          if (s.id === activeSessionId) {
            return {
              ...s,
              messages: [...s.messages, newResponse]
            };
          }
          return s;
        }));
        setComputing(false);
        if (isVoiceEnabledRef.current) {
          speakText("Connection error. Unable to reach backend.");
        }
      });
  };

  return (
    <div className={`app-container ${isSimpleTextMode ? 'simple-text-mode' : ''}`}>
      {/* A. Left Sidebar Section */}
      <Sidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={handleSelectSession}
        onNewSession={handleNewSession}
        agents={AI_AGENTS}
        activeAgentKey={activeAgentKey}
        onSelectAgent={handleSelectAgent}
        isSimpleTextMode={isSimpleTextMode}
        onToggleSimpleTextMode={() => setIsSimpleTextMode(!isSimpleTextMode)}
      />

      {/* B. Right Main Section */}
      <main className="main-workspace">
        {activeSession && activeSession.messages.length > 0 && activeAgentKey !== 'voicepulse' ? (
          // Active chat logs exist for selected session
          <ChatPanel
            messages={activeSession.messages}
            computing={computing}
            activeAgent={activeAgentObj}
            isSimpleTextMode={isSimpleTextMode}
            onToggleSimpleTextMode={() => setIsSimpleTextMode(!isSimpleTextMode)}
          />
        ) : (
          // No chat yet (or VoicePulse) - render beautiful Home intro + central Animated Hologram
          <div className="home-view">
            {/* 1. Concentric SVG orbits sphere */}
            <HologramSphere computing={computing} agent={activeAgentKey} />

            {/* 2. Brand Identity */}
            <div className="assistant-identity">
              <div className="assistant-title-row">
                <h2 className="assistant-name-heading">OMEGA Assistant</h2>
              </div>
              <p className="assistant-subtitle">Powered by Advanced Intelligence</p>
            </div>

          </div>
        )}

        {/* C. Bottom Input Deck Panel */}
        {activeAgentKey === 'voicepulse' ? (
          <div className="input-deck voice-only-deck animate-fade-in" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '24px 20px', gap: '12px' }}>
            <div className="voice-status-indicator" style={{ display: 'flex', alignItems: 'center', gap: '10px', background: 'var(--accent-bg-glow)', border: '1px solid var(--border-glass-glow)', padding: '10px 20px', borderRadius: '30px', boxShadow: '0 0 15px rgba(0, 210, 255, 0.15)' }}>
              <div className="voice-pulse-dot" style={{
                width: '8px',
                height: '8px',
                backgroundColor: isListening ? 'var(--accent)' : '#4e5e78',
                borderRadius: '50%',
                boxShadow: isListening ? '0 0 10px var(--accent)' : 'none',
                animation: isListening ? 'micPulse 1.2s infinite ease-in-out' : 'none'
              }}></div>
              <span style={{ fontSize: '13px', fontFamily: 'Orbitron, sans-serif', fontWeight: 600, color: isListening ? 'var(--accent)' : '#8c9cb5', letterSpacing: '0.5px' }}>
                {isListening ? "VOICEPULSE LISTENING..." : "VOICE ASSISTANT READY"}
              </span>
            </div>
            <div className="voice-mic-container" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <div 
                className={`voice-only-mic-btn ${isListening ? 'listening' : ''}`}
                onClick={toggleSpeechRecognition}
                style={{
                  width: '64px',
                  height: '64px',
                  borderRadius: '50%',
                  background: isListening ? 'rgba(0, 210, 255, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                  border: isListening ? '2px solid var(--accent)' : '1px solid rgba(255, 255, 255, 0.15)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                  color: isListening ? 'var(--accent)' : '#8c9cb5',
                  boxShadow: isListening ? '0 0 20px var(--accent-glow)' : 'none',
                  transition: 'all 0.3s ease',
                  position: 'relative'
                }}
              >
                <Mic size={28} />
                {isListening && (
                  <span style={{
                    position: 'absolute',
                    width: '100%',
                    height: '100%',
                    borderRadius: '50%',
                    border: '2px solid var(--accent)',
                    animation: 'micPulse 1.5s infinite ease-in-out',
                    left: 0,
                    top: 0
                  }}></span>
                )}
              </div>
            </div>
            <div className="input-disclaimer" style={{ marginTop: 0 }}>
              Voice Communication Mode Active. Speak to communicate.
            </div>
          </div>
        ) : (
          <div className="input-deck">
            {/* File Attachment glowing preview node */}
            {attachment && (
              <div className="attachment-preview-row">
                <div className="attached-node animate-fade-in">
                  <Paperclip size={12} />
                  <span>{attachment.name} ({attachment.size})</span>
                  <X size={12} className="attached-node-close" onClick={handleClearAttachment} />
                </div>
              </div>
            )}

            <div className="input-container">
              {/* Native file selection button hooks */}
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                className="hidden-file-input"
              />
              
              <div className="input-action-btn" onClick={handleAttachmentClick} title="Attach Files">
                <Paperclip size={18} />
              </div>
              
              <div className="input-action-btn" onClick={handleAttachmentClick} title="Attach Images">
                <ImageIcon size={18} />
              </div>

              <input
                type="text"
                className="prompt-field"
                placeholder={`Ask ${activeAgentObj.name} anything...`}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !computing) {
                    handleSendPrompt();
                  }
                }}
                disabled={computing}
              />

              {/* Voice Assistant Buttons */}
              <div 
                className={`input-action-btn voice-mic-btn ${isListening ? 'listening' : ''}`} 
                onClick={toggleSpeechRecognition} 
                title={isListening ? "Stop listening" : "Speech to Text"}
                style={{
                  color: isListening ? '#ef4444' : 'inherit',
                  marginRight: '6px',
                  position: 'relative',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                <Mic size={18} />
                {isListening && (
                  <span className="mic-glow-pulse" style={{
                    position: 'absolute',
                    width: '100%',
                    height: '100%',
                    left: 0,
                    top: 0,
                    borderRadius: '50%',
                    border: '2px solid #ef4444',
                    animation: 'micPulse 1.2s infinite ease-in-out'
                  }}></span>
                )}
              </div>

              <div 
                className="input-action-btn voice-speaker-btn" 
                onClick={() => {
                  const newVal = !isVoiceEnabled;
                  setIsVoiceEnabled(newVal);
                  if (newVal) {
                    speakText("Voice response active");
                  } else {
                    window.speechSynthesis?.cancel();
                  }
                }} 
                title={isVoiceEnabled ? "Mute voice responses" : "Read responses aloud"}
                style={{
                  color: isVoiceEnabled ? 'var(--accent)' : 'var(--color-text-muted)',
                  marginRight: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                {isVoiceEnabled ? <Volume2 size={18} /> : <VolumeX size={18} />}
              </div>

              <button
                className="send-action-btn"
                disabled={computing || (!inputValue.trim() && !attachment)}
                onClick={() => handleSendPrompt()}
                title="Submit Prompt"
              >
                <Send size={16} />
              </button>
            </div>
            <div className="input-disclaimer">
              OMEGA can make mistakes. Verify critical parameters.
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

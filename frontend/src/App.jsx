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

// 1. Initial High-Fidelity Mock Session Log Data (Fully Populated)
const INITIAL_SESSIONS = [
  {
    id: 'session-1',
    title: 'Quantum Architecture Design',
    timeAgo: '2m ago',
    tokens: '4.2K',
    messages: [
      {
        id: 'm1',
        role: 'user',
        content: 'Design a high-fidelity quantum architecture layer for a distributed neural mesh network.',
        timestamp: '17:38'
      },
      {
        id: 'm2',
        role: 'assistant',
        content: 'I have mapped the topological specifications for the distributed Neural Mesh Network.\n\n### ⚡ Topological Qubit Configuration\nWe will deploy major fault-tolerant Majorana Zero Modes (MZMs) structured on a 2D honeycomb lattice:\n- **Qubit Density**: 24 active topological pairs per node.\n- **Error Rate Target**: < 1.2e-6 per logical gate operation.\n- **Coherence Duration**: ~850 ms (under active dilution cooling).\n\n### 🛠️ Hardware Setup Protocol\n```python\nimport quantum_mesh as qm\n\n# Initialize topological qubit array\narray = qm.QubitArray(dimensions=(8, 8), braiding="majorana")\narray.apply_noise_model(qm.models.ThermalDilution(temp_mk=10))\n\n# Instantiate braiding gate array\ngates = qm.BraidingGateController(array)\ngates.braid_qubits(source=12, target=24)\n\nprint(f"Topological entanglement verified. Braiding fidelity: {gates.verify_fidelity():.6f}")\n```\nLet me know if you want to run a simulated braid benchmark on our local synthetic compiler.',
        timestamp: '17:38'
      }
    ]
  },
  {
    id: 'session-2',
    title: 'Neural Code Synthesis',
    timeAgo: '1h ago',
    tokens: '8.7K',
    messages: [
      {
        id: 'm3',
        role: 'user',
        content: 'Generate a parallel matrix multiplication kernel for neural code execution.',
        timestamp: '16:40'
      },
      {
        id: 'm4',
        role: 'assistant',
        content: 'Here is a high-speed CUDA kernel optimized for modern tensor core operations. It partitions computation into shared memory tiles for optimal L1 cache alignment:\n\n```cpp\n__global__ void MatrixMultiplyKernel(float* A, float* B, float* C, int N) {\n    // Dynamic block shared memory allocations\n    __shared__ float tileA[16][16];\n    __shared__ float tileB[16][16];\n    \n    int tx = threadIdx.x; \n    int ty = threadIdx.y;\n    int row = blockIdx.y * 16 + ty;\n    int col = blockIdx.x * 16 + tx;\n    \n    float sum = 0.0f;\n    \n    for (int t = 0; t < N / 16; ++t) {\n        tileA[ty][tx] = A[row * N + (t * 16 + tx)];\n        tileB[ty][tx] = B[(t * 16 + ty) * N + col];\n        __syncthreads();\n        \n        #pragma unroll\n        for (int k = 0; k < 16; ++k) {\n            sum += tileA[ty][k] * tileB[k][tx];\n        }\n        __syncthreads();\n    }\n    C[row * N + col] = sum;\n}\n```\n- **Tiling Factor**: 16x16 threads per block.\n- **Coalescing**: Sequential access alignment verified.',
        timestamp: '16:42'
      }
    ]
  },
  {
    id: 'session-3',
    title: 'Data Stream Analysis',
    timeAgo: '3h ago',
    tokens: '2.1K',
    messages: [
      {
        id: 'm5',
        role: 'user',
        content: 'Analyze our real-time telemetry from the holographic sensor array.',
        timestamp: '14:30'
      },
      {
        id: 'm6',
        role: 'assistant',
        content: 'I have compiled the telemetry packet from the outer holographic sensor array. Here is a breakdown of the anomalies detected in frequency spectrum emission:\n\n| Sensor Array | Frequency (GHz) | Error Rate (%) | Status | Recommendation |\n|---|---|---|---|---|\n| Core Array alpha | 84.22 | 0.04% | ACTIVE | Nominal. No action needed. |\n| Core Array beta | 85.04 | 1.84% | DEGRADED | Calibrate phase coherence registers immediately. |\n| Outer Node gamma | 120.91 | 0.01% | ACTIVE | Optimal braiding performance. |\n| Sector Node delta | 94.66 | 4.90% | CRITICAL | Resynchronize sub-visual focus anomaly sensors. |\n\n**Key Action Item**: Run `sensor_realign.sh --force` on **Sector Node delta** to recondition baseline focus values.',
        timestamp: '14:31'
      }
    ]
  },
  {
    id: 'session-4',
    title: 'Holographic UI Patterns',
    timeAgo: '1d ago',
    tokens: '6.5K',
    messages: [
      {
        id: 'm7',
        role: 'user',
        content: 'What are the core design principles for glassmorphic holographic interfaces?',
        timestamp: 'Yesterday'
      },
      {
        id: 'm8',
        role: 'assistant',
        content: 'Holographic UI requires depth perception and high legibility. Follow these guidelines:\n- **Backdrop Blur**: Target a Gaussian blur between `12px` and `24px` to blend with dark glowing grids.\n- **Border Alpha**: Use pure white/cyan borders with extremely low opacity (`0.08` to `0.15`) to isolate elements without heavy outlines.\n- **Layer Separation**: Implement layered drop-shadows with varying scale sizes (`box-shadow: 0 8px 32px rgba(0,0,0,0.4)`).\n- **High Contrast Accents**: Always combine a dark transparent background with micro neon green/cyan highlights to denote connectivity.',
        timestamp: 'Yesterday'
      }
    ]
  },
  {
    id: 'session-5',
    title: 'Autonomous Agent Config',
    timeAgo: '2d ago',
    tokens: '12K',
    messages: [
      {
        id: 'm9',
        role: 'user',
        content: 'Write an agent execution config file with custom memory anchors.',
        timestamp: 'May 31'
      },
      {
        id: 'm10',
        role: 'assistant',
        content: 'Here is the JSON specification file mapping active reflection parameters for autonomous loop nodes:\n\n```json\n{\n  "agent_id": "nexus-forge-v3",\n  "version": "3.1.2026",\n  "memory_anchors": {\n    "vector_store": "dilution_db_v1",\n    "similarity_threshold": 0.85,\n    "sliding_window_size": 25\n  },\n  "reflection_boundaries": {\n    "max_steps": 12,\n    "backoff_rate": 1.5,\n    "escalate_on_critical_fail": true\n  },\n  "system_instruction": "Act as a quantum mainframe interface. Answer queries using precise engineering notation."\n}\n```',
        timestamp: 'May 31'
      }
    ]
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
    color: 'purple'
  },
  {
    key: 'voicepulse',
    name: 'VoicePulse',
    desc: 'Speech Interface',
    icon: Mic,
    color: 'orange'
  },
  {
    key: 'synapse',
    name: 'Synapse',
    desc: 'Deep Analysis',
    icon: Activity,
    color: 'green'
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
          setInputValue(prev => {
            const separator = prev.endsWith(' ') || prev === '' ? '' : ' ';
            return prev + separator + transcript;
          });
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

    window.speechSynthesis.speak(utterance);
  };

  // Synchronize AI Agent selection with CSS variable overrides for theme transitions
  useEffect(() => {
    const root = document.documentElement;
    if (activeAgentKey === 'nexus') {
      root.style.setProperty('--accent', 'var(--color-cyan)');
      root.style.setProperty('--accent-glow', 'var(--color-cyan-glow)');
    } else if (activeAgentKey === 'codeforge') {
      root.style.setProperty('--accent', 'var(--color-purple)');
      root.style.setProperty('--accent-glow', 'var(--color-purple-glow)');
    } else if (activeAgentKey === 'voicepulse') {
      root.style.setProperty('--accent', 'var(--color-orange)');
      root.style.setProperty('--accent-glow', 'var(--color-orange-glow)');
    } else if (activeAgentKey === 'synapse') {
      root.style.setProperty('--accent', 'var(--color-green)');
      root.style.setProperty('--accent-glow', 'var(--color-green-glow)');
    }
  }, [activeAgentKey]);

  // Find currently active session object
  const activeSession = sessions.find(s => s.id === activeSessionId);
  const activeAgentObj = AI_AGENTS.find(a => a.key === activeAgentKey);

  // Handle setting a different active session
  const handleSelectSession = (id) => {
    setActiveSessionId(id);
  };

  // Reset or create an empty chat view
  const handleNewSession = () => {
    const newId = `session-${Date.now()}`;
    const newSession = {
      id: newId,
      title: 'New Neural Session',
      timeAgo: 'Just now',
      tokens: '0K',
      messages: []
    };
    setSessions([newSession, ...sessions]);
    setActiveSessionId(newId);
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

    // 3. Trigger mock high-speed AI computing timeout
    setTimeout(() => {
      const responseTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      let aiContent = '';

      // Determine smart futuristic answer matching key terms in user prompt
      const promptLower = promptText.toLowerCase();
      
      if (promptLower.includes('css') || promptLower.includes('ui') || promptLower.includes('design')) {
        aiContent = "Here is a custom glassmorphism layout specification matching your prompt details:\n\n```css\n.futuristic-card {\n  background: rgba(13, 20, 42, 0.45);\n  border: 1px solid rgba(0, 240, 255, 0.15);\n  backdrop-filter: blur(20px);\n  box-shadow: 0 8px 32px 0 rgba(0, 210, 255, 0.05);\n  border-radius: 16px;\n  padding: 24px;\n  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);\n}\n.futuristic-card:hover {\n  border-color: #00d2ff;\n  box-shadow: 0 0 15px rgba(0, 210, 255, 0.3);\n  transform: translateY(-2px);\n}\n```\n- **Blur Filter**: 20px Gaussian depth.\n- **Hover Response**: Active glow projection.";
      } else if (promptLower.includes('react') || promptLower.includes('code') || promptLower.includes('leak')) {
        aiContent = "I have completed the state updater assessment for your React codebase:\n\n- **Anomaly Detected**: A potential stale closure inside the asynchronous `useEffect` state dispatch loop.\n- **Fidelity Mitigation**: Cleaned up active interval timers and wrapped listeners in a native `useCallback` hook.\n\n```jsx\n// Mitigation Refactoring\nconst handleThreadRender = useCallback((threadId) => {\n  setThreadState(prev => {\n    const active = prev.find(t => t.id === threadId);\n    return active ? [...prev] : [...prev, { id: threadId, status: \"nominal\" }];\n  });\n}, []);\n```\nThis resolves any race-conditions and prevents stale component renderings during automated updates.";
      } else if (promptLower.includes('art') || promptLower.includes('painting') || promptLower.includes('prompt')) {
        aiContent = "Here is a highly precise visual rendering prompt optimized for midjourney or stable diffusion generators:\n\n> *A cinematic, ultra-detailed architectural rendering of a glowing quantum core container suspended inside a glass dilution cooling column. Multi-layered cyan light beams emanating, intricate circuits, ambient dark laboratory environment, cinematic volumetric mist, 8k resolution, raytraced reflection aesthetics, cool teal and deep purple color accents.*";
      } else if (promptLower.includes('dataset') || promptLower.includes('matrix') || promptLower.includes('telemetry') || promptLower.includes('analyze')) {
        aiContent = "Phase offset matrix analysis complete. Telemetry statistics identify a slight oscillation drift:\n\n| Quantum Node | Amplitude Error | Coherence Offset | Stability Status |\n|---|---|---|---|\n| Core-01 | 0.04% | +0.02 GHz | Nominal |\n| Braiding-04 | 1.95% | -1.14 GHz | Degraded (Tune Needed) |\n| Register-09 | 0.01% | 0.00 GHz | Nominal |\n\n**Direct Recommendation**: Adjust voltage bias registers on Braiding-04 by **+12.4mV** to counteract the microwave offset drift.";
      } else {
        // Generic smart futuristic response
        aiContent = "Mainframe query received. Synthesizing quantum nodes to formulate optimal response guidelines:\n\n- **Target Agent**: " + activeAgentObj.name + "\n- **Direct Summary**: I have processed your instruction relative to current state anchors.\n- **Telemetry**: Core logic execution returned nominal telemetry status. Let me know if you would like me to output code kernels or deep phase analytical charts.";
      }

      const newResponse = {
        id: `msg-${Date.now()}-assistant`,
        role: 'assistant',
        content: aiContent,
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
        speakText(aiContent);
      }
    }, 1800);
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
        onSelectAgent={setActiveAgentKey}
        isSimpleTextMode={isSimpleTextMode}
        onToggleSimpleTextMode={() => setIsSimpleTextMode(!isSimpleTextMode)}
      />

      {/* B. Right Main Section */}
      <main className="main-workspace">
        {activeSession && activeSession.messages.length > 0 ? (
          // Active chat logs exist for selected session
          <ChatPanel
            messages={activeSession.messages}
            computing={computing}
            activeAgent={activeAgentObj}
            isSimpleTextMode={isSimpleTextMode}
            onToggleSimpleTextMode={() => setIsSimpleTextMode(!isSimpleTextMode)}
          />
        ) : (
          // No chat yet - render beautiful Home intro + central Animated Hologram
          <div className="home-view">
            {/* 1. Concentric SVG orbits sphere */}
            <HologramSphere computing={computing} agent={activeAgentKey} />

            {/* 2. Brand Identity */}
            <div className="assistant-identity">
              <div className="assistant-title-row">
                <h2 className="assistant-name-heading">Neural AI Assistant</h2>
                <div className="connected-pill">
                  <span className="brand-status-dot" style={{ position: 'relative', display: 'inline-block', border: 'none', right: 0, bottom: 0 }}></span>
                  <span>CONNECTED</span>
                </div>
              </div>
              <p className="assistant-subtitle">Powered by Advanced Intelligence</p>
            </div>

            {/* Ready overlay indicator */}
            <div className="ready-pill-overlay">
              <div className="ready-pill-dot"></div>
              <span>Ready</span>
            </div>

          </div>
        )}

        {/* C. Bottom Input Deck Panel */}
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
            NEURAL AI can make mistakes. Verify critical parameters.
          </div>
        </div>
      </main>
    </div>
  );
}

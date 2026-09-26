import React, { useState, useEffect, useRef } from 'react';
import { Mic, Volume2 } from 'lucide-react';
import HologramSphere from './HologramSphere';

export default function VoiceAssistant({ 
  computing, 
  setComputing,
  onMicStateChange,
  onClose
}) {
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isMuted] = useState(false);
  const [liveTranscript, setLiveTranscript] = useState('');
  const [statusMessage, setStatusMessage] = useState('');
  const [availableVoices, setAvailableVoices] = useState([]);
  const [selectedVoiceIndex, setSelectedVoiceIndex] = useState(0);

  const recognitionRef = useRef(null);

  // Load browser speech synthesis voices
  useEffect(() => {
    const updateVoices = () => {
      if (typeof window !== 'undefined' && window.speechSynthesis) {
        const voices = window.speechSynthesis.getVoices();
        setAvailableVoices(voices);
        const defaultIdx = voices.findIndex(v => v.lang.startsWith('en'));
        if (defaultIdx !== -1) setSelectedVoiceIndex(defaultIdx);
      }
    };

    updateVoices();
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.onvoiceschanged = updateVoices;
    }

    return () => {
      if (recognitionRef.current) {
        try { recognitionRef.current.abort(); } catch (e) {}
      }
      if (typeof window !== 'undefined' && window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  const stopListening = () => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (e) {
        try { recognitionRef.current.abort(); } catch (err) {}
      }
      recognitionRef.current = null;
    }
    setIsListening(false);
    if (onMicStateChange) onMicStateChange(false);
  };

  const startListening = async () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setStatusMessage("Speech recognition not supported in this browser");
      return;
    }

    try {
      if (window.speechSynthesis) window.speechSynthesis.cancel();
      setIsSpeaking(false);
      setLiveTranscript('');
      setStatusMessage('');

      if (recognitionRef.current) {
        try { recognitionRef.current.abort(); } catch (e) {}
        recognitionRef.current = null;
      }

      // Request mic permission if mediaDevices is supported
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        try {
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          stream.getTracks().forEach(t => t.stop());
        } catch (mediaErr) {
          console.warn("Microphone access prompt error:", mediaErr);
          if (mediaErr.name === 'NotAllowedError' || mediaErr.name === 'PermissionDeniedError') {
            setStatusMessage("Microphone permission blocked. Please allow mic");
            setIsListening(false);
            if (onMicStateChange) onMicStateChange(false);
            return;
          }
        }
      }

      const rec = new SpeechRecognition();
      rec.continuous = false;
      rec.interimResults = true;
      rec.lang = 'en-US';

      rec.onstart = () => {
        setIsListening(true);
        setStatusMessage('');
        if (onMicStateChange) onMicStateChange(true);
      };

      rec.onresult = (event) => {
        let currentText = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          currentText += event.results[i][0].transcript;
        }
        setLiveTranscript(currentText);

        if (event.results && event.results[0] && event.results[0].isFinal) {
          handleVoiceQuery(currentText);
        }
      };

      rec.onerror = (err) => {
        console.warn("Speech recognition error:", err.error || err);
        if (err.error === 'not-allowed') {
          setStatusMessage("Microphone permission denied. Allow mic access");
        } else if (err.error === 'audio-capture') {
          setStatusMessage("No microphone detected. Check audio input");
        } else if (err.error === 'network') {
          setStatusMessage("Network error during speech recognition");
        }
        setIsListening(false);
        if (onMicStateChange) onMicStateChange(false);
      };

      rec.onend = () => {
        setIsListening(false);
        if (onMicStateChange) onMicStateChange(false);
      };

      recognitionRef.current = rec;
      rec.start();
      setIsListening(true);
      if (onMicStateChange) onMicStateChange(true);
    } catch (err) {
      console.error("Error starting speech recognition:", err);
      setIsListening(false);
      if (onMicStateChange) onMicStateChange(false);
    }
  };

  const toggleListening = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  const speakText = (text) => {
    if (isMuted || !window.speechSynthesis) return;

    window.speechSynthesis.cancel();
    const cleanText = text.replace(/[*#_`]/g, '').slice(0, 400);
    const utterance = new SpeechSynthesisUtterance(cleanText);

    if (availableVoices[selectedVoiceIndex]) {
      utterance.voice = availableVoices[selectedVoiceIndex];
    }
    utterance.rate = 1.0;
    utterance.pitch = 1.0;

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    window.speechSynthesis.speak(utterance);
  };

  const handleVoiceQuery = (queryText) => {
    const text = queryText.trim();
    if (!text) return;

    setLiveTranscript('');
    if (setComputing) setComputing(true);

    fetch('http://localhost:9090/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: text, agent: 'VoicePulse' })
    })
      .then(res => res.json())
      .then(data => {
        const responseText = data.content || "Voice query processed successfully.";
        if (setComputing) setComputing(false);
        speakText(responseText);
      })
      .catch(err => {
        const fallbackText = `I heard: "${text}". OMEGA Voice Assistant is online!`;
        if (setComputing) setComputing(false);
        speakText(fallbackText);
      });
  };

  return (
    <div className="voice-assistant-view-container">
      {/* Top HUD Bar */}
      <div className="voice-hud-top-bar">
        <div className="voice-engine-badge">
          <span className="voice-badge-dot" />
          <span>{isListening ? 'Listening...' : 'Voice Assistant Online'}</span>
        </div>
      </div>

      {/* Center 3D Hologram Stage */}
      <div className="voice-hologram-stage">
        <div className="voice-orb-wrapper">
          <HologramSphere 
            computing={computing || isSpeaking}
            isListening={isListening}
            onMicToggle={toggleListening}
            agent="voicepulse"
            scale={1.0}
          />
        </div>

        {/* Floating Status Pill */}
        <button 
          type="button"
          onClick={toggleListening}
          className={`voice-status-pill-floating ${isListening ? 'listening' : (isSpeaking ? 'speaking' : 'idle')}`}
          title={isListening ? "Click to stop listening" : "Click to speak"}
        >
          {isListening ? (
            <>
              <Mic size={16} className="animate-bounce" />
              <span>Listening... Click sphere to stop</span>
            </>
          ) : isSpeaking ? (
            <>
              <Volume2 size={16} className="animate-pulse" />
              <span>Speaking... Click sphere to pause</span>
            </>
          ) : (
            <>
              <Mic size={16} />
              <span>{statusMessage || 'Click sphere to speak'}</span>
            </>
          )}
        </button>
      </div>

      {/* Live Voice Stream Preview */}
      {liveTranscript && (
        <div className="voice-stream-container">
          <span className="voice-stream-label">Speech Input</span>
          <p className="voice-stream-text">"{liveTranscript}"</p>
        </div>
      )}
    </div>
  );
}

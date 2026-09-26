import React, { useEffect, useRef, useState } from 'react';
import { 
  Send, 
  Plus, 
  ChevronDown, 
  Mic, 
  Paperclip,
  Copy, 
  Check, 
  RotateCcw,
  ThumbsUp,
  ThumbsDown,
  Code,
  FileText,
  Lightbulb,
  Mail
} from 'lucide-react';

const SUGGESTION_CHIPS = [
  {
    id: 'code',
    label: 'Write code',
    icon: Code,
    prompt: 'Write a clean Python script to parse and analyze CSV data with error handling.'
  },
  {
    id: 'summarize',
    label: 'Summarize a document',
    icon: FileText,
    prompt: 'Summarize the key findings and executive takeaways of this document in bullet points.'
  },
  {
    id: 'explain',
    label: 'Explain a concept',
    icon: Lightbulb,
    prompt: 'Explain how neural network attention mechanisms work using a clear, intuitive analogy.'
  },
  {
    id: 'email',
    label: 'Draft an email',
    icon: Mail,
    prompt: 'Draft a concise, professional follow-up email after a product demonstration meeting.'
  }
];

const AVAILABLE_MODELS = [
  { id: 'omega-4.1', name: 'OMEGA 4.1', desc: 'Fast, balanced general intelligence' },
  { id: 'omega-solver', name: 'OMEGA Reasoning', desc: 'Code & mathematical problem solving' },
  { id: 'nexora-pro', name: 'Nexora Pro', desc: 'Complex multi-domain analysis' }
];

function CodeBlock({ code, lang }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="msg-code-container">
      <div className="code-header-bar">
        <span>{lang || 'code'}</span>
        <button className="code-copy-btn" onClick={handleCopy} title="Copy code snippet">
          {copied ? <Check size={13} className="text-emerald-400" /> : <Copy size={13} />}
          <span>{copied ? 'Copied!' : 'Copy'}</span>
        </button>
      </div>
      <pre className="code-pre-block">
        <code>{code}</code>
      </pre>
    </div>
  );
}

function parseInlineMarkdown(inlineText) {
  if (typeof inlineText !== 'string') return inlineText;
  const regex = /(\[.*?\]\(https?:\/\/[^\s\)]+\)|\*\*.*?\*\*|\*.*?\*|`.*?`|https?:\/\/[^\s<]+)/g;
  const tokens = inlineText.split(regex);

  return tokens.map((token, i) => {
    if (!token) return null;

    // Link: [text](url)
    const linkMatch = token.match(/^\[(.*?)\]\((https?:\/\/[^\s\)]+)\)$/);
    if (linkMatch) {
      return (
        <a 
          key={i} 
          href={linkMatch[2]} 
          target="_blank" 
          rel="noopener noreferrer" 
          className="msg-link"
          style={{ color: 'var(--accent)', textDecoration: 'underline' }}
        >
          {linkMatch[1] || linkMatch[2]}
        </a>
      );
    }

    // Bold: **text**
    if (token.startsWith('**') && token.endsWith('**') && token.length >= 4) {
      return <strong key={i} style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{token.slice(2, -2)}</strong>;
    }

    // Italic: *text*
    if (token.startsWith('*') && token.endsWith('*') && token.length >= 2) {
      return <em key={i} style={{ color: 'var(--text-secondary)', fontStyle: 'italic' }}>{token.slice(1, -1)}</em>;
    }

    // Inline Code: `code`
    if (token.startsWith('`') && token.endsWith('`') && token.length >= 2) {
      return <code key={i} className="inline-code-snippet">{token.slice(1, -1)}</code>;
    }

    // Raw URL: https://...
    if (/^https?:\/\/[^\s<]+$/.test(token)) {
      return (
        <a 
          key={i} 
          href={token} 
          target="_blank" 
          rel="noopener noreferrer" 
          style={{ color: 'var(--accent)', textDecoration: 'underline' }}
        >
          {token}
        </a>
      );
    }

    return token;
  });
}

function parseBlocks(blockText) {
  if (typeof blockText !== 'string') return blockText;
  const formattedText = blockText.replace(/([^\n])\s*(#{1,6}\s+)/g, '$1\n\n$2');
  const lines = formattedText.split('\n');
  const elements = [];
  let currentList = null;

  const flushList = () => {
    if (currentList) {
      const ListTag = currentList.type;
      elements.push(
        <ListTag key={`list-${elements.length}`} style={{ paddingLeft: '20px', margin: '8px 0' }}>
          {currentList.items.map((item, idx) => (
            <li key={idx} style={{ marginBottom: '4px' }}>{parseInlineMarkdown(item)}</li>
          ))}
        </ListTag>
      );
      currentList = null;
    }
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();

    if (!trimmed) continue;

    if (trimmed.startsWith('#')) {
      flushList();
      const match = trimmed.match(/^(#{1,6})\s+(.*)$/);
      if (match && match[2].trim()) {
        const level = match[1].length;
        const HeadingTag = `h${Math.min(level, 4)}`;
        elements.push(
          <HeadingTag key={`h-${elements.length}`} style={{ fontWeight: 600, margin: '14px 0 6px', color: 'var(--text-primary)' }}>
            {parseInlineMarkdown(match[2].trim())}
          </HeadingTag>
        );
        continue;
      }
    }

    const listMatch = trimmed.match(/^([-*]|\d+\.)\s+(.*)$/);
    if (listMatch) {
      const marker = listMatch[1];
      const content = listMatch[2];
      const listType = /^\d+\./.test(marker) ? 'ol' : 'ul';

      if (currentList && currentList.type !== listType) flushList();

      if (!currentList) {
        currentList = { type: listType, items: [content] };
      } else {
        currentList.items.push(content);
      }
      continue;
    } else {
      flushList();
    }

    elements.push(
      <p key={`p-${elements.length}`} style={{ marginBottom: '8px' }}>
        {parseInlineMarkdown(trimmed)}
      </p>
    );
  }

  flushList();
  return elements;
}

function parseMessageContent(text) {
  if (!text) return null;
  const parts = text.split(/```/g);

  return parts.map((part, index) => {
    if (index % 2 === 1) {
      const firstLineBreak = part.indexOf('\n');
      let lang = 'code';
      let code = part;

      if (firstLineBreak !== -1) {
        const potentialLang = part.substring(0, firstLineBreak).trim();
        if (potentialLang.length < 15) {
          lang = potentialLang;
          code = part.substring(firstLineBreak + 1);
        }
      }

      return <CodeBlock key={index} code={code.trim()} lang={lang} />;
    }

    return <React.Fragment key={index}>{parseBlocks(part)}</React.Fragment>;
  });
}

export default function ChatPanel({ 
  messages = [], 
  computing = false, 
  inputValue = '', 
  setInputValue, 
  onSend, 
  onOpenVoiceMode
}) {
  const [selectedModel, setSelectedModel] = useState(AVAILABLE_MODELS[0]);
  const [isModelDropdownOpen, setIsModelDropdownOpen] = useState(false);
  const [copiedMsgId, setCopiedMsgId] = useState(null);
  const [likedMsgIds, setLikedMsgIds] = useState(new Set());
  const [dislikedMsgIds, setDislikedMsgIds] = useState(new Set());
  const [attachment, setAttachment] = useState(null);

  const bottomRef = useRef(null);
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);
  const modelMenuRef = useRef(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }, [messages, computing]);

  // Auto-grow textarea up to 200px
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [inputValue]);

  // Close model menu on outside click
  useEffect(() => {
    const handleOutsideClick = (e) => {
      if (modelMenuRef.current && !modelMenuRef.current.contains(e.target)) {
        setIsModelDropdownOpen(false);
      }
    };
    if (isModelDropdownOpen) {
      document.addEventListener('mousedown', handleOutsideClick);
    }
    return () => {
      document.removeEventListener('mousedown', handleOutsideClick);
    };
  }, [isModelDropdownOpen]);

  const handleCopyText = (msgId, text) => {
    navigator.clipboard.writeText(text);
    setCopiedMsgId(msgId);
    setTimeout(() => setCopiedMsgId(null), 2000);
  };

  const handleToggleLike = (msgId) => {
    setLikedMsgIds(prev => {
      const next = new Set(prev);
      if (next.has(msgId)) {
        next.delete(msgId);
      } else {
        next.add(msgId);
        setDislikedMsgIds(d => {
          const updated = new Set(d);
          updated.delete(msgId);
          return updated;
        });
      }
      return next;
    });
  };

  const handleToggleDislike = (msgId) => {
    setDislikedMsgIds(prev => {
      const next = new Set(prev);
      if (next.has(msgId)) {
        next.delete(msgId);
      } else {
        next.add(msgId);
        setLikedMsgIds(l => {
          const updated = new Set(l);
          updated.delete(msgId);
          return updated;
        });
      }
      return next;
    });
  };

  const handleRegenerate = () => {
    // Find last user message content
    const lastUserMsg = [...messages].reverse().find(m => m.sender === 'user' || m.role === 'user');
    if (lastUserMsg && lastUserMsg.content) {
      onSend?.(lastUserMsg.content);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setAttachment({
        name: file.name,
        size: (file.size / 1024).toFixed(1) + ' KB'
      });
    }
  };

  const handleSendWrapper = (overrideText) => {
    let finalPrompt = overrideText || inputValue;
    if (!finalPrompt.trim() && !attachment) return;

    if (attachment) {
      finalPrompt += `\n*(Attached: ${attachment.name} [${attachment.size}])*`;
    }

    onSend?.(finalPrompt);
    setAttachment(null);
  };

  const handleChipClick = (promptText) => {
    setInputValue?.(promptText);
    textareaRef.current?.focus();
  };

  const displayMessages = Array.isArray(messages) ? messages : [];
  const isInputValid = Boolean(inputValue.trim() || attachment);

  // Common Chat Input Container JSX
  const renderChatInputBox = () => (
    <div className="saas-input-box-container">
      {/* File Attachment Pill */}
      {attachment && (
        <div className="input-attachment-strip">
          <div className="attachment-pill">
            <Paperclip size={12} />
            <span className="truncate max-w-[200px]">{attachment.name}</span>
            <button onClick={() => setAttachment(null)}>×</button>
          </div>
        </div>
      )}

      {/* Auto-growing Textarea */}
      <textarea
        ref={textareaRef}
        rows={1}
        className="saas-textarea"
        placeholder="Message OMEGA..."
        value={inputValue}
        onChange={(e) => setInputValue?.(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey && !computing && isInputValid) {
            e.preventDefault();
            handleSendWrapper();
          }
        }}
        disabled={computing}
      />

      {/* Input Bottom Controls */}
      <div className="saas-input-controls-row">
        <div className="input-left-controls">
          <button 
            type="button"
            className="saas-icon-btn" 
            onClick={() => fileInputRef.current?.click()} 
            title="Attach file"
            aria-label="Attach file"
          >
            <Plus size={18} strokeWidth={1.5} />
          </button>
        </div>

        <div className="input-right-controls" ref={modelMenuRef}>
          {/* Subtle Model Selector */}
          <div className="saas-model-selector-pill">
            <button
              type="button"
              className="saas-model-btn"
              onClick={() => setIsModelDropdownOpen(!isModelDropdownOpen)}
              title="Select model"
            >
              <span className="saas-model-name">{selectedModel.name}</span>
              <ChevronDown size={13} className="saas-model-chevron" strokeWidth={1.5} />
            </button>

            {isModelDropdownOpen && (
              <div className="saas-model-dropdown">
                {AVAILABLE_MODELS.map((model) => (
                  <button
                    key={model.id}
                    className={`model-option-btn ${selectedModel.id === model.id ? 'active' : ''}`}
                    onClick={() => {
                      setSelectedModel(model);
                      setIsModelDropdownOpen(false);
                    }}
                  >
                    <span>{model.name}</span>
                    {selectedModel.id === model.id && <Check size={14} className="text-cyan-400" />}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Voice Mode Mic Trigger */}
          <button 
            type="button"
            className="saas-icon-btn" 
            onClick={onOpenVoiceMode}
            title="Voice mode"
            aria-label="Voice mode"
          >
            <Mic size={17} strokeWidth={1.5} />
          </button>

          {/* Send Button */}
          <button
            type="button"
            className={`saas-send-btn ${isInputValid && !computing ? 'active' : ''}`}
            disabled={computing || !isInputValid}
            onClick={() => handleSendWrapper()}
            title="Send message"
            aria-label="Send message"
          >
            <Send size={15} strokeWidth={2} />
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="saas-chat-workspace">
      {/* Hidden File Input */}
      <input 
        type="file" 
        ref={fileInputRef} 
        onChange={handleFileChange} 
        style={{ display: 'none' }} 
      />

      {/* Messages / Empty State Viewport */}
      <div className="saas-messages-viewport">
        {displayMessages.length === 0 ? (
          /* Empty State: Centered greeting, input, and 4 suggestion chips */
          <div className="saas-empty-state-wrap">
            <div className="empty-state-hero">
              <h1 className="empty-state-headline">
                <span className="empty-state-omega-symbol">Ω</span>
                <span className="empty-state-headline-text">Hello, Let's forge something legendary!</span>
              </h1>
            </div>

            {/* Input Container */}
            <div style={{ width: '100%' }}>
              {renderChatInputBox()}
              <div className="saas-input-footer-note">
                OMEGA can make mistakes. Please verify important information.
              </div>
            </div>

            {/* 4 Suggestion Chips */}
            <div className="saas-suggestion-grid">
              {SUGGESTION_CHIPS.map((chip) => {
                const IconComp = chip.icon;
                return (
                  <button
                    key={chip.id}
                    className="suggestion-chip-btn"
                    onClick={() => handleChipClick(chip.prompt)}
                  >
                    <IconComp size={16} className="suggestion-chip-icon" strokeWidth={1.5} />
                    <span>{chip.label}</span>
                  </button>
                );
              })}
            </div>
          </div>
        ) : (
          /* Active Conversation: Centered Max-Width 720px */
          <div className="saas-content-constraint">
            {displayMessages.map((msg, index) => {
              if (!msg) return null;
              const currentMsgId = msg.id || `msg-${index}`;
              const isUser = (msg.role === 'user' || msg.sender === 'user');

              if (isUser) {
                return (
                  <div key={currentMsgId} className="saas-message-row user">
                    <div className="user-msg-bubble">
                      {msg.content || ''}
                    </div>
                  </div>
                );
              }

              const isLiked = likedMsgIds.has(currentMsgId);
              const isDisliked = dislikedMsgIds.has(currentMsgId);

              return (
                <div key={currentMsgId} className="saas-message-row assistant">
                  {/* Small AI Logo Avatar */}
                  <div className="assistant-avatar-mark">Ω</div>

                  {/* AI Message Body */}
                  <div className="assistant-body-column">
                    <div>
                      {parseMessageContent(msg.content)}
                    </div>

                    {/* Action Buttons Visible on Hover */}
                    <div className="ai-actions-row">
                      <button 
                        className="ai-action-btn"
                        onClick={() => handleCopyText(currentMsgId, msg.content)}
                        title="Copy answer"
                      >
                        {copiedMsgId === currentMsgId ? <Check size={13} className="text-emerald-400" /> : <Copy size={13} strokeWidth={1.5} />}
                        <span>{copiedMsgId === currentMsgId ? 'Copied' : 'Copy'}</span>
                      </button>

                      <button 
                        className="ai-action-btn"
                        onClick={handleRegenerate}
                        title="Regenerate response"
                      >
                        <RotateCcw size={13} strokeWidth={1.5} />
                        <span>Regenerate</span>
                      </button>

                      <button 
                        className={`ai-action-btn ${isLiked ? 'active' : ''}`}
                        onClick={() => handleToggleLike(currentMsgId)}
                        title="Good response"
                      >
                        <ThumbsUp size={13} strokeWidth={1.5} />
                      </button>

                      <button 
                        className={`ai-action-btn ${isDisliked ? 'active' : ''}`}
                        onClick={() => handleToggleDislike(currentMsgId)}
                        title="Bad response"
                      >
                        <ThumbsDown size={13} strokeWidth={1.5} />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}

            {/* Typing / Computing Indicator */}
            {computing && (
              <div className="saas-message-row assistant">
                <div className="assistant-avatar-mark">Ω</div>
                <div className="assistant-body-column">
                  <div className="typing-indicator-row">
                    <div className="typing-dot" />
                    <div className="typing-dot" />
                    <div className="typing-dot" />
                  </div>
                </div>
              </div>
            )}

            <div ref={bottomRef} style={{ height: '20px' }} />
          </div>
        )}
      </div>

      {/* Floating Bottom Input Bar for Active Conversation */}
      {displayMessages.length > 0 && (
        <div className="saas-bottom-input-bar">
          <div className="saas-content-constraint">
            {renderChatInputBox()}
            <div className="saas-input-footer-note">
              OMEGA can make mistakes. Please verify important information.
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

import React, { useEffect, useRef } from 'react';
import { Bot, User, Wifi } from 'lucide-react';

/**
 * Parses simple markdown elements (code blocks, bullet lists, bold text)
 * into semantic React nodes with beautiful styles.
 */
/**
 * Parses inline elements like bold (**text**), italic (*text*), and inline code (`code`)
 * into React components.
 */
function parseInlineMarkdown(inlineText) {
  if (typeof inlineText !== 'string') return inlineText;

  // Regex to split text by bold (**), italic (*), and inline code (`)
  const regex = /(\*\*.*?\*\*|\*.*?\*|`.*?`)/g;
  const tokens = inlineText.split(regex);

  return tokens.map((token, i) => {
    if (token.startsWith('**') && token.endsWith('**')) {
      return <strong key={i}>{token.slice(2, -2)}</strong>;
    }
    if (token.startsWith('*') && token.endsWith('*')) {
      return <em key={i}>{token.slice(1, -1)}</em>;
    }
    if (token.startsWith('`') && token.endsWith('`')) {
      return <code key={i} className="inline-code">{token.slice(1, -1)}</code>;
    }
    return token;
  });
}

/**
 * Parses block level elements like headings, lists, tables, and paragraphs.
 */
function parseBlocks(blockText) {
  const lines = blockText.split('\n');
  const elements = [];

  let currentList = null; // { type: 'ul' | 'ol', items: [] }
  let currentTable = null; // { headers: [], rows: [] }

  const flushList = () => {
    if (currentList) {
      const ListTag = currentList.type;
      elements.push(
        <ListTag key={`list-${elements.length}`} className="msg-list">
          {currentList.items.map((item, idx) => (
            <li key={idx}>{parseInlineMarkdown(item)}</li>
          ))}
        </ListTag>
      );
      currentList = null;
    }
  };

  const flushTable = () => {
    if (currentTable) {
      elements.push(
        <div key={`table-wrapper-${elements.length}`} className="table-responsive">
          <table className="msg-table">
            <thead>
              <tr>
                {currentTable.headers.map((h, idx) => (
                  <th key={idx}>{parseInlineMarkdown(h)}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {currentTable.rows.map((row, rIdx) => (
                <tr key={rIdx}>
                  {row.map((cell, cIdx) => (
                    <td key={cIdx}>{parseInlineMarkdown(cell)}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
      currentTable = null;
    }
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();

    // 1. Check if it's a table line
    if (trimmed.startsWith('|')) {
      flushList();

      const cells = line.split('|').map(c => c.trim()).filter((c, idx, arr) => idx > 0 && idx < arr.length - 1);

      // Check if it's a separator line like |---|---|
      const isSeparator = cells.every(c => /^:-*|-*:-*|-*:$/.test(c) || c.startsWith('-'));

      if (isSeparator) {
        // Just skip the separator line
        continue;
      }

      if (!currentTable) {
        currentTable = { headers: cells, rows: [] };
      } else {
        currentTable.rows.push(cells);
      }
      continue;
    } else {
      flushTable();
    }

    // 2. Check if it's a heading
    if (trimmed.startsWith('#')) {
      flushList();
      const match = trimmed.match(/^(#{1,6})\s+(.*)$/);
      if (match) {
        const level = match[1].length;
        const HeadingTag = `h${level}`;
        elements.push(
          <HeadingTag key={`h-${elements.length}`} className={`msg-heading h${level}`}>
            {parseInlineMarkdown(match[2])}
          </HeadingTag>
        );
        continue;
      }
    }

    // 3. Check if it's a list item
    const listMatch = trimmed.match(/^([-*]|\d+\.)\s+(.*)$/);
    if (listMatch) {
      const marker = listMatch[1];
      const content = listMatch[2];
      const listType = /^\d+\./.test(marker) ? 'ol' : 'ul';

      if (currentList && currentList.type !== listType) {
        flushList();
      }

      if (!currentList) {
        currentList = { type: listType, items: [content] };
      } else {
        currentList.items.push(content);
      }
      continue;
    } else {
      flushList();
    }

    // 4. Regular paragraph
    if (trimmed) {
      elements.push(
        <p key={`p-${elements.length}`} className="msg-paragraph">
          {parseInlineMarkdown(trimmed)}
        </p>
      );
    }
  }

  // Flush remaining blocks
  flushList();
  flushTable();

  return elements;
}

function parseMessageContent(text) {
  if (!text) return null;

  // Split by code blocks ```
  const parts = text.split(/```/g);

  return parts.map((part, index) => {
    // If odd index, it's code block
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

      return (
        <pre key={index} className="msg-code-block">
          <code>{code.trim()}</code>
        </pre>
      );
    }

    // Process normal text with custom block-level and inline markdown
    return <React.Fragment key={index}>{parseBlocks(part)}</React.Fragment>;
  });
}

export default function ChatPanel({ messages, computing, activeAgent, isSimpleTextMode, onToggleSimpleTextMode }) {
  const bottomRef = useRef(null);

  // Auto scroll to bottom
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, computing]);

  const AgentIcon = activeAgent?.icon || Bot;

  return (
    <div className="chat-view">
      {/* 1. Chat Header */}
      <div className="chat-status-bar">
        <div className="status-agent-info">
          <div className="status-agent-avatar chat-view-header-avatar">
            <AgentIcon size={18} />
          </div>
          <div className="status-agent-meta">
            <span className="status-agent-name">{activeAgent?.name || 'OMEGA'}</span>
            <div className="status-agent-status">
              <span className="brand-status-dot" style={{ position: 'relative', display: 'inline-block', border: 'none', right: 0, bottom: 0 }}></span>
              <span>ACTIVE AGENT</span>
            </div>
          </div>
        </div>

        <div className="chat-header-actions" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button
            className={`readability-toggle-btn ${isSimpleTextMode ? 'active' : ''}`}
            onClick={onToggleSimpleTextMode}
            title={isSimpleTextMode ? "Switch to Sci-Fi Mode" : "Switch to Readability Mode"}
            style={{
              background: isSimpleTextMode ? 'rgba(0, 240, 255, 0.1)' : 'rgba(255, 255, 255, 0.03)',
              border: isSimpleTextMode ? '1px solid var(--accent)' : '1px solid var(--border-glass)',
              borderRadius: '8px',
              padding: '6px 12px',
              color: isSimpleTextMode ? 'var(--accent)' : 'var(--color-text-secondary)',
              fontSize: '11px',
              fontFamily: 'inherit',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              transition: 'all 0.25s ease'
            }}
          >
            <span>{isSimpleTextMode ? "📖 Simple Text" : "⚡ Futuristic"}</span>
          </button>

          <div className="connected-pill">
            <Wifi size={12} />
            <span>CONNECTED</span>
          </div>
        </div>
      </div>

      {/* 2. Message History Pane */}
      <div className="message-history-pane">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`message-bubble-row ${msg.role}`}
          >
            <div className={`msg-avatar ${msg.role}`}>
              {msg.role === 'user' ? <User size={18} /> : <AgentIcon size={18} />}
            </div>

            <div className="msg-content-wrapper">
              <div className="msg-bubble">
                {msg.role === 'user' ? (
                  <p>{msg.content}</p>
                ) : (
                  parseMessageContent(msg.content)
                )}
              </div>
              <span className="msg-time">{msg.timestamp}</span>
            </div>
          </div>
        ))}

        {/* 3. Typing / Computing indicator */}
        {computing && (
          <div className="message-bubble-row assistant">
            <div className="msg-avatar assistant">
              <AgentIcon size={18} />
            </div>
            <div className="msg-content-wrapper">
              <div className="msg-bubble typing-bubble">
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
              </div>
            </div>
          </div>
        )}

        {/* Scroll anchor */}
        <div ref={bottomRef}></div>
      </div>
    </div>
  );
}

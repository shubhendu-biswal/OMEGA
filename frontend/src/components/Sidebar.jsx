import React, { useState, useEffect, useRef, useMemo } from 'react';
import { createPortal } from 'react-dom';
import { 
  Plus, 
  Trash2,
  User,
  MoreHorizontal,
  Pin,
  Pencil,
  Settings,
  Sparkles,
  LogOut,
  Check,
  Search,
  SlidersHorizontal,
  X
} from 'lucide-react';

export default function Sidebar({
  sessions = [],
  activeSessionId,
  onSelectSession,
  onNewSession,
  onDeleteSession,
  onRenameSession,
  onPinSession,
  isOpen = true
}) {
  // Context Menu State
  const [menuSessionId, setMenuSessionId] = useState(null);
  const [menuPosition, setMenuPosition] = useState({ top: 0, left: 0 });

  // Inline Rename State
  const [editingSessionId, setEditingSessionId] = useState(null);
  const [editTitle, setEditTitle] = useState('');

  // User Profile Dropdown State
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

  // Delete Confirmation Modal State
  const [deleteModalSessionId, setDeleteModalSessionId] = useState(null);

  // Feedback Toast
  const [toastMessage, setToastMessage] = useState(null);

  const menuRef = useRef(null);
  const userMenuRef = useRef(null);
  const renameInputRef = useRef(null);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage(null);
    }, 2200);
  };

  // Search & Filter State
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [sortOrder, setSortOrder] = useState('recent'); // 'recent' | 'alphabetical'

  // Filtered & Sorted Sessions
  const displaySessions = useMemo(() => {
    let result = [...sessions];
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim();
      result = result.filter(s => (s.title || '').toLowerCase().includes(q));
    }
    return result.sort((a, b) => {
      if (a.isPinned && !b.isPinned) return -1;
      if (!a.isPinned && b.isPinned) return 1;
      if (sortOrder === 'alphabetical') {
        return (a.title || '').localeCompare(b.title || '');
      }
      const timeA = a.updatedAt || a.createdAt || 0;
      const timeB = b.updatedAt || b.createdAt || 0;
      return timeB - timeA;
    });
  }, [sessions, searchQuery, sortOrder]);

  const activeMenuSession = sessions.find((s) => s.id === menuSessionId);

  // Open context menu anchored to 3-dots button
  const handleOpenMenu = (e, session) => {
    e.stopPropagation();
    if (menuSessionId === session.id) {
      setMenuSessionId(null);
      return;
    }

    const rect = e.currentTarget.getBoundingClientRect();
    const menuWidth = 180;
    const menuHeight = 110;

    let left = rect.right - menuWidth;
    if (left < 10) left = 10;
    if (left + menuWidth > window.innerWidth - 10) {
      left = window.innerWidth - menuWidth - 10;
    }

    let top = rect.bottom + 4;
    if (top + menuHeight > window.innerHeight - 10) {
      top = Math.max(10, rect.top - menuHeight - 4);
    }

    setMenuPosition({ top, left });
    setMenuSessionId(session.id);
  };

  // Close context menu & user menu on click outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setMenuSessionId(null);
      }
      if (userMenuRef.current && !userMenuRef.current.contains(e.target)) {
        setIsUserMenuOpen(false);
      }
    };

    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        setMenuSessionId(null);
        setIsUserMenuOpen(false);
        return;
      }
      if (menuSessionId && document.activeElement?.tagName !== 'INPUT') {
        const key = e.key.toLowerCase();
        if (key === 'r') {
          e.preventDefault();
          const target = sessions.find((s) => s.id === menuSessionId);
          if (target) handleStartRename(target);
        } else if (key === 'd') {
          e.preventDefault();
          handleRequestDelete(menuSessionId);
        }
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [menuSessionId, sessions]);

  // Handle keyboard events for Delete Confirmation Modal
  useEffect(() => {
    if (!deleteModalSessionId) return;

    const handleModalKeyDown = (e) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        setDeleteModalSessionId(null);
      } else if (e.key === 'Enter') {
        e.preventDefault();
        handleConfirmDelete();
      }
    };

    document.addEventListener('keydown', handleModalKeyDown);
    return () => {
      document.removeEventListener('keydown', handleModalKeyDown);
    };
  }, [deleteModalSessionId]);

  // Focus rename input on rename start
  useEffect(() => {
    if (editingSessionId && renameInputRef.current) {
      renameInputRef.current.focus();
      renameInputRef.current.select();
    }
  }, [editingSessionId]);

  const handleStartRename = (session) => {
    setEditingSessionId(session.id);
    setEditTitle(session.title || '');
    setMenuSessionId(null);
  };

  const handleSaveRename = (sessionId) => {
    if (editTitle.trim()) {
      onRenameSession?.(sessionId, editTitle.trim());
    }
    setEditingSessionId(null);
  };

  const handleRenameKeyDown = (e, sessionId) => {
    if (e.key === 'Enter') {
      handleSaveRename(sessionId);
    } else if (e.key === 'Escape') {
      setEditingSessionId(null);
    }
  };

  const handleRequestDelete = (sessionId) => {
    setMenuSessionId(null);
    setDeleteModalSessionId(sessionId);
  };

  const handleConfirmDelete = () => {
    if (deleteModalSessionId) {
      onDeleteSession?.(deleteModalSessionId);
      showToast('Chat deleted');
      setDeleteModalSessionId(null);
    }
  };

  const handleCancelDelete = () => {
    setDeleteModalSessionId(null);
  };

  return (
    <aside className={`saas-sidebar ${isOpen ? 'open' : 'collapsed'}`}>
      {/* 1. Header: Logo + OMEGA Wordmark (v4.8 removed as requested) */}
      <div className="sidebar-header">
        <div className="sidebar-brand-link" onClick={() => onSelectSession?.(sessions[0]?.id)}>
          <div className="brand-icon-mark">Ω</div>
          {isOpen && <span className="brand-wordmark">OMEGA</span>}
        </div>
      </div>

      {/* 2. New Chat Button: Full width, solid surface background, no glow */}
      <div className="sidebar-action-wrap">
        <button 
          className="new-chat-btn"
          onClick={onNewSession}
          title="Start a new chat"
        >
          <Plus size={16} strokeWidth={1.5} />
          {isOpen && <span>New chat</span>}
        </button>
      </div>

      {/* 3. Chat History List: 'Chats' header with search/filter icons, then circle bullet list */}
      <div className="sidebar-history-viewport">
        {isOpen && (
          <>
            <div className="sidebar-section-header">
              <span className="sidebar-section-title">Chats</span>
              <div className="sidebar-section-actions">
                <button 
                  className={`sidebar-section-action-btn ${isSearchOpen ? 'active' : ''}`}
                  onClick={() => {
                    setIsSearchOpen(!isSearchOpen);
                    if (isSearchOpen) setSearchQuery('');
                  }}
                  title="Search chats"
                  aria-label="Search chats"
                >
                  <Search size={15} strokeWidth={1.5} />
                </button>
                <button 
                  className={`sidebar-section-action-btn ${sortOrder === 'alphabetical' ? 'active' : ''}`}
                  onClick={() => {
                    const next = sortOrder === 'recent' ? 'alphabetical' : 'recent';
                    setSortOrder(next);
                    showToast(next === 'alphabetical' ? 'Sorted A to Z' : 'Sorted by recent');
                  }}
                  title="Filter / Sort chats"
                  aria-label="Filter / Sort chats"
                >
                  <SlidersHorizontal size={15} strokeWidth={1.5} />
                </button>
              </div>
            </div>

            {isSearchOpen && (
              <div className="sidebar-search-wrap">
                <Search size={13} className="sidebar-search-icon" />
                <input
                  type="text"
                  placeholder="Search chats..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="sidebar-search-input"
                  autoFocus
                />
                {searchQuery && (
                  <button 
                    onClick={() => setSearchQuery('')}
                    className="sidebar-search-clear"
                  >
                    <X size={12} />
                  </button>
                )}
              </div>
            )}

            <ul className="sidebar-chat-list">
              {displaySessions.map((session) => {
                const isActive = session.id === activeSessionId;
                const isEditing = editingSessionId === session.id;
                const isMenuOpen = menuSessionId === session.id;

                return (
                  <li
                    key={session.id}
                    className={`sidebar-chat-item ${isActive ? 'active' : ''} ${isMenuOpen ? 'menu-open' : ''}`}
                    onClick={() => {
                      if (!isEditing) onSelectSession(session.id);
                    }}
                    title={session.title}
                  >
                    <div className="chat-item-content">
                      <span className="chat-bullet-circle" />
                      {session.isPinned && (
                        <Pin size={12} className="chat-pin-icon" strokeWidth={1.5} />
                      )}
                      {isEditing ? (
                        <input
                          ref={renameInputRef}
                          type="text"
                          className="chat-rename-input"
                          value={editTitle}
                          onChange={(e) => setEditTitle(e.target.value)}
                          onKeyDown={(e) => handleRenameKeyDown(e, session.id)}
                          onBlur={() => handleSaveRename(session.id)}
                          onClick={(e) => e.stopPropagation()}
                        />
                      ) : (
                        <span className="chat-item-title">{session.title}</span>
                      )}
                    </div>

                    {!isEditing && (
                      <button 
                        className={`chat-item-menu-btn ${isMenuOpen ? 'menu-active' : ''}`}
                        onClick={(e) => handleOpenMenu(e, session)}
                        title="Chat options"
                        aria-label="Chat options"
                      >
                        <MoreHorizontal size={16} strokeWidth={1.5} />
                      </button>
                    )}
                  </li>
                );
              })}
            </ul>
          </>
        )}
      </div>

      {/* 4. Bottom User Section: Avatar + Name + Pro Pill Badge + Dropdown Menu */}
      <div className="sidebar-footer" ref={userMenuRef}>
        <button 
          className={`user-profile-btn ${isUserMenuOpen ? 'active' : ''}`}
          onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
          title="User Account"
        >
          <div className="user-profile-left">
            <div className="user-avatar-circle">
              <User size={15} strokeWidth={1.5} />
            </div>
            {isOpen && (
              <>
                <span className="user-meta-name">Shubhendu</span>
                <span className="user-plan-badge">Pro</span>
              </>
            )}
          </div>
        </button>

        {/* User Account Dropdown */}
        {isUserMenuOpen && (
          <div className="user-dropdown-menu">
            <button className="user-menu-item" onClick={() => { setIsUserMenuOpen(false); showToast("Settings opened"); }}>
              <div className="user-menu-item-left">
                <Settings size={15} strokeWidth={1.5} />
                <span>Settings</span>
              </div>
              <span className="user-menu-badge">v4.8</span>
            </button>
            <button className="user-menu-item" onClick={() => { setIsUserMenuOpen(false); showToast("Current Plan: Pro Member"); }}>
              <div className="user-menu-item-left">
                <Sparkles size={15} strokeWidth={1.5} />
                <span>Upgrade plan</span>
              </div>
            </button>
            <div className="chat-menu-divider" />
            <button className="user-menu-item" onClick={() => { setIsUserMenuOpen(false); showToast("Logged out"); }}>
              <div className="user-menu-item-left">
                <LogOut size={15} strokeWidth={1.5} />
                <span>Log out</span>
              </div>
            </button>
          </div>
        )}
      </div>

      {/* 5. Floating Chat Context Menu (Rename, Delete) */}
      {menuSessionId && activeMenuSession && createPortal(
        <div 
          className="chat-context-menu" 
          ref={menuRef} 
          style={{ top: menuPosition.top, left: menuPosition.left }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Rename */}
          <button 
            className="chat-menu-item"
            onClick={() => handleStartRename(activeMenuSession)}
          >
            <div className="chat-menu-item-left">
              <Pencil size={15} className="chat-menu-icon" strokeWidth={1.5} />
              <span>Rename</span>
            </div>
            <span className="chat-menu-shortcut">R</span>
          </button>

          <div className="chat-menu-divider" />

          {/* Delete */}
          <button 
            className="chat-menu-item delete-item"
            onClick={() => handleRequestDelete(activeMenuSession.id)}
          >
            <div className="chat-menu-item-left">
              <Trash2 size={15} className="chat-menu-icon" strokeWidth={1.5} />
              <span>Delete</span>
            </div>
            <span className="chat-menu-shortcut">D</span>
          </button>
        </div>,
        document.body
      )}

      {/* 6. Delete Confirmation Modal */}
      {deleteModalSessionId && createPortal(
        <div className="chat-modal-overlay" onClick={handleCancelDelete}>
          <div 
            className="chat-delete-modal" 
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
            aria-labelledby="delete-chat-title"
          >
            <h2 id="delete-chat-title" className="chat-delete-modal-title">Delete chat?</h2>
            <p className="chat-delete-modal-desc">Are you sure you want to delete this chat?</p>
            <div className="chat-delete-modal-actions">
              <button 
                type="button"
                className="chat-modal-btn-cancel" 
                onClick={handleCancelDelete}
              >
                Cancel
              </button>
              <button 
                type="button"
                className="chat-modal-btn-delete" 
                onClick={handleConfirmDelete}
                autoFocus
              >
                Delete
              </button>
            </div>
          </div>
        </div>,
        document.body
      )}

      {/* 7. Action Toast Notification */}
      {toastMessage && createPortal(
        <div className="chat-action-toast">
          <Check size={14} className="text-cyan-400" />
          <span>{toastMessage}</span>
        </div>,
        document.body
      )}
    </aside>
  );
}

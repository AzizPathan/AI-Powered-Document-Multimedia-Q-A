import React, { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import {
  Bot,
  ChevronDown,
  CirclePlus,
  CheckCircle,
  Clock,
  Database,
  FileAudio,
  Files,
  FileText,
  FileVideo,
  Loader2,
  LogIn,
  LogOut,
  MessageSquareText,
  MoreVertical,
  PanelLeftClose,
  Pencil,
  Play,
  PlayCircle,
  Search,
  Send,
  ShieldCheck,
  Sparkles,
  SquarePlus,
  UploadCloud,
  Zap,
} from 'lucide-react';
import './styles.css';

const configuredApiBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();
const API_BASE_URL = configuredApiBaseUrl
  ? configuredApiBaseUrl.replace(/\/$/, '')
  : import.meta.env.DEV
    ? 'http://127.0.0.1:8001'
    : '';

async function api(path, options = {}, token) {
  const headers = { ...(options.headers || {}) };
  if (token) headers.Authorization = `Bearer ${token}`;
  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
  } catch (err) {
    throw new Error(`Cannot reach the backend API at ${API_BASE_URL}. Start the backend on port 8001, then try again.`);
  }
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || 'Request failed');
  }
  return response.json();
}

function iconFor(contentType) {
  if (contentType?.startsWith('audio/')) return <FileAudio size={18} />;
  if (contentType?.startsWith('video/')) return <FileVideo size={18} />;
  return <FileText size={18} />;
}

function isMediaWithoutTranscript(file) {
  return file?.transcription_status === 'unavailable';
}

function summaryFor(file) {
  if (!file) return 'Summaries appear after upload.';
  if (isMediaWithoutTranscript(file)) {
    return 'Media uploaded successfully. Transcript features will be available after transcription is configured.';
  }
  return file.summary || 'Summaries appear after upload.';
}

function dateFromFile(file, fallbackDate) {
  if (!file?.created_at) return fallbackDate;
  const fileDate = new Date(file.created_at);
  return Number.isNaN(fileDate.getTime()) ? fallbackDate : fileDate;
}

function formatExactDateTime(date) {
  return new Intl.DateTimeFormat(undefined, {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  }).format(date);
}

function formatTranscriptDate(date) {
  return new Intl.DateTimeFormat(undefined, {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(date);
}

function AuthPanel({ onToken }) {
  const [email, setEmail] = useState('demo@example.com');
  const [password, setPassword] = useState('password123');
  const [mode, setMode] = useState('register');
  const [error, setError] = useState('');

  async function submit(event) {
    event.preventDefault();
    setError('');
    try {
      const data = await api(`/api/auth/${mode}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      onToken(data.access_token);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <main className="qinsight-landing">
      <nav className="q-nav">
        <a className="q-brand" href="#top" aria-label="Q-Insight home">
          <span><Zap size={20} /></span>
          Q-Insight
        </a>
        <div className="q-nav-links">
          <a href="#features">Features</a>
          <a href="#tech">Tech Stack</a>
          <a href="#docs">Docs</a>
        </div>
        <div className="q-nav-actions">
          <button type="button" className="q-link-button" onClick={() => setMode('login')}>Login -&gt;</button>
          <a className="q-primary-pill" href="#access" onClick={() => setMode('register')}>Get Started</a>
        </div>
      </nav>

      <section id="top" className="q-hero">
        <div className="q-hero-copy">
          <h1>
            AI answers for <br />
            <span>all your documents.</span>
          </h1>
          <div className="q-search-mockup">
            <div>What are the main topics in the Q3 transcript?</div>
            <a href="#access">Ask AI</a>
          </div>
          <p className="q-support-line">
            <span>*</span> PDF, audio, and video support <span>*</span>
          </p>
        </div>

        <div className="q-floating-stage" aria-label="Q-Insight product preview">
          <article className="q-float-card q-pdf-card">
            <div className="q-card-head">
              <span className="q-icon-soft red"><FileText size={20} /></span>
              <div>
                <strong>Annual Report.pdf</strong>
                <small>Extracted with PyPDF</small>
              </div>
            </div>
            <div className="q-lines">
              <span />
              <span />
              <span />
            </div>
          </article>

          <section className="q-browser-card">
            <div className="q-browser-top">
              <div><span /><span /><span /></div>
              <code>localhost:5173</code>
            </div>
            <div className="q-browser-body">
              <div className="q-assistant-label"><MessageSquareText size={19} /> AI Assistant</div>
              <div className="q-chat-bubble ai">I've analyzed your video and PDF. What would you like to know about the strategy?</div>
              <div className="q-chat-bubble user">Summarize the pricing discussion in the meeting.</div>
              <div className="q-chat-bubble citation">
                <p>The pricing strategy centers around three tiers. It was discussed in the video at <strong>04:22</strong>.</p>
                <button type="button"><PlayCircle size={16} /> Jump to citation</button>
              </div>
            </div>
          </section>

          <article className="q-float-card q-video-card">
            <div className="q-video-thumb">
              <img src="https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=500&q=80" alt="" />
              <Play size={30} />
            </div>
            <strong>Meeting_Recording.mp4</strong>
            <small>Transcribed via Whisper</small>
          </article>
        </div>
      </section>

      <section id="access" className="q-access-section">
        <form className="q-auth-card" onSubmit={submit}>
          <div className="q-auth-copy">
            <span><ShieldCheck size={18} /> Secure workspace access</span>
            <h2>{mode === 'register' ? 'Create your Q-Insight account' : 'Welcome back to Q-Insight'}</h2>
            <p>Use the demo credentials or bring your own account into the document Q&A workspace.</p>
          </div>
          <div className="q-auth-tabs" role="tablist" aria-label="Authentication mode">
            <button type="button" className={mode === 'register' ? 'active' : ''} onClick={() => setMode('register')}>Register</button>
            <button type="button" className={mode === 'login' ? 'active' : ''} onClick={() => setMode('login')}>Login</button>
          </div>
          <label>
            Email
            <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@example.com" required />
          </label>
          <label>
            Password
            <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="password123" required />
          </label>
          {error && <div className="q-auth-error">{error}</div>}
          <button className="q-auth-submit" type="submit">
            <LogIn size={18} />
            {mode === 'register' ? 'Create Account' : 'Sign In'}
          </button>
          <p className="q-demo-hint">Demo: demo@example.com / password123</p>
        </form>
      </section>

      <section id="features" className="q-features">
        <div className="q-section-heading">
          <h2>Simplify access to information</h2>
          <p>Upload PDFs, audio, or video. Q-Insight handles extraction and indexing so you can find answers instantly through one search bar.</p>
        </div>
        <div className="q-feature-layout">
          <aside className="q-feature-nav">
            <span className="active">Document Insights</span>
            <span>Media Transcription</span>
            <span>Vector Search (FAISS)</span>
            <span>JWT Authentication</span>
            <span>Streaming Responses</span>
          </aside>
          <div className="q-feature-grid">
            <article>
              <span><FileText size={21} /></span>
              <h3>Text & Media Extraction</h3>
              <p>Robust extraction with pypdf for documents and OpenAI Whisper for high-accuracy audio and video transcription.</p>
            </article>
            <article>
              <span><Search size={21} /></span>
              <h3>Hybrid Search Engine</h3>
              <p>A retrieval system combining FAISS-backed vector search with TF-IDF fallbacks for deterministic reliability.</p>
            </article>
            <article>
              <span><Clock size={21} /></span>
              <h3>Interactive Timestamps</h3>
              <p>Citations link directly to video and audio timestamps with built-in playback control.</p>
            </article>
            <article>
              <span><Database size={21} /></span>
              <h3>PostgreSQL & Redis</h3>
              <p>Production persistence for chat history, file metadata, and efficient rate limiting.</p>
            </article>
          </div>
        </div>
      </section>

      <section id="tech" className="q-tech">
        <div className="q-tech-panel">
          <div>
            <span className="q-kicker">Deployment Ready</span>
            <h2>Built for performance and scale.</h2>
            <ul>
              <li><CheckCircle size={17} /> Docker & Docker Compose Support</li>
              <li><CheckCircle size={17} /> Backend coverage with Pytest</li>
              <li><CheckCircle size={17} /> GitHub Actions CI/CD Workflows</li>
              <li><CheckCircle size={17} /> React + Vite Frontend / FastAPI Backend</li>
            </ul>
          </div>
          <div className="q-terminal">
            <div><span /><span /><span /></div>
            <code>$ docker compose up --build</code>
            <p>Building services...</p>
            <strong>backend (FastAPI) listening on :8000</strong>
            <strong>frontend (Vite) listening on :5173</strong>
            <strong>postgres:5432 is healthy</strong>
            <em># Ready to extract and query your knowledge base</em>
          </div>
        </div>
      </section>

      <section id="docs" className="q-docs">
        <h2>Implementation Details</h2>
        <article>
          <span>1</span>
          <div>
            <h3>JWT Authentication</h3>
            <p>Secure user registration and login flows. Protected upload, chat, and timestamp endpoints require bearer tokens.</p>
          </div>
        </article>
        <article>
          <span>2</span>
          <div>
            <h3>Streaming Chat via SSE</h3>
            <p>Real-time AI responses generate progressively for a faster document analysis experience.</p>
          </div>
        </article>
        <article>
          <span>3</span>
          <div>
            <h3>Topic Analysis & Summaries</h3>
            <p>Automatic file summaries and topic-specific segments help navigate long documents and recordings.</p>
          </div>
        </article>
      </section>

      <footer className="q-footer">
        <div className="q-brand">
          <span><Zap size={17} /></span>
          Q-Insight
        </div>
        <p>2026 AI-Powered Document Q&A. Built for the modern enterprise.</p>
        <div>
          <a href="#features">Privacy</a>
          <a href="#docs">Terms</a>
          <a href="#tech">GitHub</a>
        </div>
      </footer>
    </main>
  );
}

function App() {
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [files, setFiles] = useState([]);
  const [activeFile, setActiveFile] = useState(null);
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState([]);
  const [topic, setTopic] = useState('');
  const [timestamps, setTimestamps] = useState([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [now, setNow] = useState(() => new Date());
  const mediaRef = useRef(null);
  const assistantMessagesRef = useRef(null);

  const [mediaUrl, setMediaUrl] = useState('');

  useEffect(() => {
    let objectUrl = '';
    setMediaUrl('');
    if (!activeFile || activeFile.content_type === 'application/pdf') return undefined;
    fetch(`${API_BASE_URL}/api/files/${activeFile.id}/media`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((response) => {
        if (!response.ok) throw new Error(response.statusText || 'Could not load media');
        return response.blob();
      })
      .then((blob) => {
        objectUrl = URL.createObjectURL(blob);
        setMediaUrl(objectUrl);
      })
      .catch((err) => {
        setError(err.message);
      });
    return () => {
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [activeFile, token]);

  useEffect(() => {
    const messagesElement = assistantMessagesRef.current;
    if (!messagesElement) return;
    messagesElement.scrollTo({
      top: messagesElement.scrollHeight,
      behavior: 'smooth',
    });
  }, [messages, busy]);

  useEffect(() => {
    const timer = window.setInterval(() => setNow(new Date()), 1000);
    return () => window.clearInterval(timer);
  }, []);

  async function saveToken(nextToken) {
    localStorage.setItem('token', nextToken);
    setToken(nextToken);
    const list = await api('/api/files', {}, nextToken);
    setFiles(list);
    setActiveFile(list[0] || null);
  }

  function signOut() {
    localStorage.removeItem('token');
    setToken('');
    setFiles([]);
    setActiveFile(null);
    setMessages([]);
    setQuestion('');
    setTopic('');
    setTimestamps([]);
    setError('');
  }

  async function upload(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    const body = new FormData();
    body.append('upload', file);
    setBusy(true);
    setError('');
    try {
      const uploaded = await api('/api/files/upload', { method: 'POST', body }, token);
      const list = await api('/api/files', {}, token);
      setFiles(list);
      setActiveFile(uploaded);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
      event.target.value = '';
    }
  }

  async function ask(event) {
    event.preventDefault();
    if (!question.trim() || !activeFile) return;
    const asked = question.trim();
    setMessages((items) => [...items, { role: 'user', text: asked }]);
    setQuestion('');
    setBusy(true);
    setError('');
    try {
      const answer = await api('/api/chat/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ file_id: activeFile.id, question: asked }),
      }, token);
      setMessages((items) => [...items, { role: 'assistant', text: answer.answer, citations: answer.citations }]);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function findTimestamps(event) {
    event.preventDefault();
    if (!topic.trim() || !activeFile) return;
    setError('');
    try {
      const data = await api(`/api/files/${activeFile.id}/timestamps?topic=${encodeURIComponent(topic)}`, {}, token);
      setTimestamps(data.matches);
    } catch (err) {
      setError(err.message);
    }
  }

  function playAt(seconds = 0) {
    if (!mediaRef.current) return;
    mediaRef.current.currentTime = seconds;
    mediaRef.current.play();
  }

  if (!token) return <AuthPanel onToken={saveToken} />;

  const visibleFiles = files.length ? files : [
    { id: 'demo-new', filename: 'New transcription', content_type: 'text/plain' },
    { id: 'demo-team', filename: 'Team building', content_type: 'text/plain' },
    { id: 'demo-market', filename: 'Cypriot job market problems', content_type: 'text/plain' },
  ];

  const transcriptLines = [
    {
      time: '00:00:00',
      text: summaryFor(activeFile) || 'Welcome, everyone. Let us kick off the design meeting. Today agenda includes the discussion of the new user interface overhaul, component library updates, and the final decision on micro-interactions for the notification system.',
      selected: true,
    },
    {
      time: '00:00:48',
      text: 'Sure. We have implemented a material-based approach with elevated card designs, leveraging layered translucency. We are aiming for a balance between usability and aesthetics.',
    },
    {
      time: '00:01:24',
      text: 'By dynamic layouts, are you referring to the CSS grid-based adaptive system we discussed last week?',
    },
    {
      time: '00:01:48',
      text: 'Exactly. The adaptive grid needs adjustments, particularly for nested components and smaller breakpoints.',
    },
  ];
  const displayDate = dateFromFile(activeFile, now);

  return (
    <main className="workspace">
      <aside className="sidebar">
        <div className="brand-row">
          <div className="brand"><Bot size={22} /> meetia.io</div>
          <button className="ghost-icon" aria-label="Collapse sidebar"><PanelLeftClose size={18} /></button>
        </div>

        <div className="tabs">
          <button className="active">Recent records</button>
          <button>Archived</button>
        </div>

        <label className="upload">
          <span className="record-dot" />
          <span>{busy ? 'Processing...' : 'Start transcription'}</span>
          <input type="file" accept="application/pdf,audio/*,video/*" onChange={upload} disabled={busy} />
        </label>

        <div className="records-heading">
          <span>Records</span>
          <CirclePlus size={17} />
        </div>

        <div className="file-list">
          {visibleFiles.map((file, index) => (
            <button
              key={file.id}
              className={activeFile?.id === file.id || (!activeFile && index === 0) ? 'file active' : 'file'}
              onClick={() => files.length && setActiveFile(file)}
            >
              <span>{file.filename}</span>
            </button>
          ))}
        </div>

        <div className="profile-area">
          <div className="profile-chip">
            <div className="avatar">OM</div>
            <div>
              <strong>Oksana Martunkova</strong>
              <span>oksana@emphastudio...</span>
            </div>
            <ChevronDown size={16} />
          </div>
          <button className="signout-button" type="button" onClick={signOut}>
            <LogOut size={17} /> Sign out
          </button>
        </div>
      </aside>

      <section className="content">
        <header className="topbar">
          <div className="title-edit">
            <h1>{activeFile ? activeFile.filename : "Oksana's new transcription"}</h1>
            <button className="ghost-icon" aria-label="Edit title"><Pencil size={18} /></button>
          </div>
          <div className="top-actions">
            <span>Last edit {formatExactDateTime(displayDate)}</span>
            <button className="feedback">Feedback</button>
            <button className="ghost-icon" aria-label="More options"><MoreVertical size={19} /></button>
          </div>
        </header>

        {error && <div className="error">{error}</div>}
        {isMediaWithoutTranscript(activeFile) && (
          <div className="notice">
            Media uploaded and ready to play. Transcript, timestamps, summary, and Q&A need transcription to be configured.
          </div>
        )}

        <section className="board">
          <div className="left-stage">
            <form onSubmit={findTimestamps} className="search-box">
              <Search size={18} />
              <input value={topic} onChange={(event) => setTopic(event.target.value)} placeholder="Search key words in transcript" />
            </form>

            {mediaUrl && (
              <section className="media-band">
                {activeFile.content_type.startsWith('video/') ? (
                  <video ref={mediaRef} controls src={mediaUrl} />
                ) : (
                  <audio ref={mediaRef} controls src={mediaUrl} />
                )}
              </section>
            )}

            <section className="transcript-card">
              <div className="date-line">{formatTranscriptDate(displayDate)}</div>
              <div className="transcript-list">
                {transcriptLines.map((line) => (
                  <article key={line.time} className={line.selected ? 'transcript-line selected' : 'transcript-line'}>
                    <time>{line.time}</time>
                    <p>{line.text}</p>
                  </article>
                ))}
              </div>
              <div className="continue-row">
                <span />
                <button><SquarePlus size={17} /> Continue recording</button>
                <span />
              </div>
              {timestamps.length > 0 && (
                <div className="timestamp-list">
                  {timestamps.map((match, index) => (
                    <button key={index} onClick={() => playAt(match.start_seconds || 0)}>
                      <Play size={15} />
                      <span>{Math.round(match.start_seconds || 0)}s</span>
                      <p>{match.text}</p>
                    </button>
                  ))}
                </div>
              )}
            </section>
          </div>

          <aside className="assistant-pane">
            <div className="assistant-title"><Sparkles size={18} /> Ask AI Assistant</div>
            <div className="assistant-chat-area">
              {!messages.length && !busy && (
                <div className="assistant-empty">
                  <div className="bot-mark"><Bot size={42} /></div>
                  <h2>How can I assist you today?</h2>
                  <p>Tap suggestions below or write your own questions about transcriptions.</p>
                </div>
              )}

              <div className="messages" ref={assistantMessagesRef}>
                {messages.map((message, index) => (
                  <article key={index} className={`message ${message.role}`}>
                    <p>{message.text}</p>
                    {message.citations?.map((citation, citationIndex) => (
                      <button key={citationIndex} className="citation" onClick={() => playAt(citation.start_seconds || 0)}>
                        {citation.start_seconds != null && <Play size={14} />} {citation.text}
                      </button>
                    ))}
                  </article>
                ))}
                {busy && <div className="typing"><Loader2 size={16} className="spin" /> Thinking</div>}
              </div>
            </div>

            <div className="suggestions">
              <div className="suggestion-head">
                <strong>Suggestions for you</strong>
                <button className="mini-icon" aria-label="Refresh suggestions"><Sparkles size={15} /></button>
              </div>
              <div className="suggestion-pills">
                <button type="button" onClick={() => setQuestion('Summarise this meeting')}>Summarise this meeting</button>
                <button type="button" onClick={() => setQuestion('Questions I may ask about this meeting')}>Questions I may ask about this meeting</button>
                <button type="button" onClick={() => setQuestion('Highlight important statements')}>Highlight important statements</button>
              </div>
              <form className="ask-box" onSubmit={ask}>
                <button className="add-button" type="button"><CirclePlus size={18} /></button>
                <input value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Ask Meetia AI anything..." />
                <button className="send-button" disabled={!activeFile || busy || isMediaWithoutTranscript(activeFile)}><Send size={18} /></button>
              </form>
            </div>
          </aside>
        </section>
      </section>
    </main>
  );
}

const rootElement = document.getElementById('root');
const root = window.__aiQaRoot || createRoot(rootElement);
window.__aiQaRoot = root;
root.render(<App />);

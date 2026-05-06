'use client';
import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Loader2, Send, Menu, Plus, X, MessageSquare, BookOpen } from 'lucide-react';
import mermaid from 'mermaid';

// Initialize mermaid once outside the component
mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
});

// Updated Mermaid component that works safely with React
const Mermaid = ({ chart }: { chart: string }) => {
  const [svg, setSvg] = useState<string>('');

  useEffect(() => {
    const renderDiagram = async () => {
      try {
        // Sanitize common AI mistakes in Mermaid syntax
        let cleanChart = chart
          .replace(/\[\/api\]/g, '(api)') // Fix slash in brackets
          .replace(/\[/g, '(')           // Convert square brackets to round
          .replace(/\]/g, ')')
          .trim();

        const id = `mermaid-${Math.random().toString(36).substring(2, 9)}`;
        const { svg: renderedSvg } = await mermaid.render(id, cleanChart);
        setSvg(renderedSvg);
      } catch (err) {
        console.error('Mermaid render error:', err);
        setSvg(`<div class="text-red-500 text-xs">Failed to render diagram</div>`);
      }
    };
    
    if (chart) {
      renderDiagram();
    }
  }, [chart]);

  return (
    <div 
      className="flex justify-center my-6 bg-zinc-800 p-4 rounded-lg overflow-x-auto"
      dangerouslySetInnerHTML={{ __html: svg || '<span class="text-zinc-500 text-sm animate-pulse">Rendering diagram...</span>' }}
    />
  );
};

export default function Dashboard() {

  const fetchSessions = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/sessions/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setSessions(data);
      }
    } catch(err) {
      console.error(err);
    }
  };

  const createNewSession = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/sessions/`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setActiveSessionId(data.id);
        setNotes([]);
        setChatHistory([]);
        localStorage.setItem('activeSessionId', data.id.toString());
        fetchSessions();
        setSidebarOpen(false);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const loadSession = async (id: number) => {
    try {
        const token = localStorage.getItem('token');
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/sessions/${id}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
            const data = await res.json();
            setActiveSessionId(data.id);
            setNotes(data.notes || []);
            setChatHistory(data.chats || []);
            localStorage.setItem('activeSessionId', data.id.toString());
            setSidebarOpen(false);
        }
    } catch (err) {
        console.error(err);
    }
  };
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeSessionId, setActiveSessionId] = useState<number | null>(null);
  const [notes, setNotes] = useState<any[]>([]); // array of notes
  const [chatMessage, setChatMessage] = useState('');
  const [chatHistory, setChatHistory] = useState<any[]>([]);
  const [sessions, setSessions] = useState<any[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      window.location.href = '/login';
    } else {
      fetchSessions();
      
      const savedSessionId = localStorage.getItem('activeSessionId');
      if (savedSessionId) {
        const sid = parseInt(savedSessionId);
        setActiveSessionId(sid);
        loadSession(sid);
      }
    }
  }, []);

  const handleGenerate = async () => {
    if (!url) return;
    
    let currentSessionId = activeSessionId;
    if (!currentSessionId) {
      try {
        const token = localStorage.getItem('token');
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/sessions/`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          currentSessionId = data.id;
          setActiveSessionId(data.id);
          localStorage.setItem('activeSessionId', data.id.toString());
          fetchSessions();
        }
      } catch (err) {
        console.error(err);
        return;
      }
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/notes/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ video_url: url, session_id: currentSessionId })
      });
      const data = await res.json();
      if (res.ok) {
        setNotes(prev => [...prev, data]);
        setUrl('');
        fetchSessions(); 
      } else {
        alert(data.detail || "Generation failed.");
      }
    } catch(err) {
      alert("Network err");
    }
    setLoading(false);
  };

  const handleSendMessage = async () => {
    if (!chatMessage.trim() || !activeSessionId) return;
    
    const newMsg = { role: 'user', content: chatMessage };
    setChatHistory(prev => [...prev, newMsg]);
    setChatMessage('');

    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ session_id: activeSessionId, message: newMsg.content })
      });
      const data = await res.json();
      if (res.ok) {
        setChatHistory(prev => [...prev, data]);
      }
    } catch(err) {
      console.error(err);
    }
  };

  return (
    <div className="flex h-screen bg-zinc-950 text-white overflow-hidden relative">
      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Left Sidebar */}
      <div className={`fixed inset-y-0 left-0 transform ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} md:relative md:translate-x-0 transition duration-200 ease-in-out z-50 w-64 bg-zinc-900 border-r border-zinc-800 flex flex-col h-full`}>
        <div className="p-4 border-b border-zinc-800 flex items-center justify-between">
          <h1 className="text-xl font-bold bg-clip-text text-transparent bg-linear-to-r from-red-500 to-purple-600">Sessions</h1>
          <button className="md:hidden text-zinc-400 hover:text-white" onClick={() => setSidebarOpen(false)}>
            <X className="w-5 h-5"/>
          </button>
        </div>
        <div className="p-4">
          <button 
            onClick={createNewSession}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg font-semibold transition"
          >
            <Plus className="w-4 h-4"/> New Session
          </button>
        </div>
        <div className="flex-1 overflow-y-auto w-full">
          {sessions.map(s => (
            <button 
              key={s.id} 
              onClick={() => loadSession(s.id)}
              className={`w-full text-left px-4 py-3 border-b border-zinc-800 hover:bg-zinc-800 transition ${activeSessionId === s.id ? 'bg-zinc-800 border-l-4 border-l-red-500' : ''}`}
            >
              <h3 className="font-semibold truncate">{s.title}</h3>
              <p className="text-xs text-zinc-500">{new Date(s.created_at).toLocaleDateString()}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col md:flex-row h-full w-full">
        {/* Middle Pane - Notes */}
        <div className="md:w-2/3 border-r border-zinc-800 flex flex-col h-full bg-zinc-950">
          {/* Header bar */}
          <div className="p-4 border-b border-zinc-800 bg-zinc-900 flex items-center gap-4">
             <button className="md:hidden text-zinc-400 hover:text-white" onClick={() => setSidebarOpen(true)}>
                <Menu className="w-6 h-6"/>
             </button>
             <div className="flex-1 flex items-center gap-2">
              <input 
                type="text" 
                placeholder="Paste YouTube Link to add to session..." 
                value={url}
                onChange={e=>setUrl(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleGenerate()}
                className="flex-1 px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg focus:outline-none"
              />
              <button onClick={handleGenerate} disabled={loading || !url} className="px-4 py-2 bg-red-600 rounded-lg hover:bg-red-500 font-semibold disabled:opacity-50 whitespace-nowrap">
                {loading ? <Loader2 className="animate-spin w-5 h-5 mx-auto" /> : "Add Video"}
              </button>
            </div>
          </div>

          {/* Notes Area */}
          <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-8">
            {notes.length > 0 ? (
              notes.map((note, idx) => (
                <div key={idx} className="prose prose-invert max-w-none">
                   {note.title && <h2 className="border-b border-zinc-700 pb-2 mb-4">{note.title}</h2>}
                   <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        code({node, inline, className, children, ...props}: any) {
                          const match = /language-(\w+)/.exec(className || '');
                          
                          // Intercept mermaid blocks and render the diagram
                          if (!inline && match && match[1] === 'mermaid') {
                            return <Mermaid chart={String(children).replace(/\n$/, '')} />;
                          }

                          return !inline && match ? (
                            <SyntaxHighlighter
                              style={vscDarkPlus as any}
                              language={match[1]}
                              PreTag="div"
                              {...props}
                            >
                              {String(children).replace(/\n$/, '')}
                            </SyntaxHighlighter>
                          ) : (
                            <code className={className} {...props}>{children}</code>
                          )
                        }
                      }}
                    >
                      {note.markdown_notes}
                    </ReactMarkdown>
                </div>
              ))
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-zinc-600">
                <BookOpen className="w-12 h-12 mb-4 opacity-50"/>
                <p>Paste a link above to start a new notes session.</p>
              </div>
            )}
          </div>
        </div>

        {/* Right Pane - Chat */}
        <div className="md:w-1/3 bg-zinc-900 flex flex-col h-full border-l border-zinc-800 md:border-none">
          <div className="p-4 border-b border-zinc-800 font-semibold flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-blue-500"/>
            Session Chat
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-zinc-900">
            {notes.length === 0 && (
              <p className="text-sm text-zinc-500 text-center mt-10">Add videos to chat with their context.</p>
            )}
            {chatHistory.map((msg, index) => (
              <div key={index} className={msg.role === 'user' ? 'text-right' : 'text-left'}>
                <div className={`inline-block p-3 rounded-lg ${msg.role === 'user' ? 'bg-blue-600' : 'bg-zinc-800 border border-zinc-700'}`}>
                  {msg.role === 'model' ? (
                    <div className="prose prose-invert prose-sm max-w-none text-left text-zinc-200">
                      <ReactMarkdown 
                        remarkPlugins={[remarkGfm]}
                        components={{
                          code({node, inline, className, children, ...props}: any) {
                            const match = /language-(\w+)/.exec(className || '');
                            if (!inline && match && match[1] === 'mermaid') {
                              return <Mermaid chart={String(children).replace(/\n$/, '')} />;
                            }
                            return !inline && match ? (
                              <SyntaxHighlighter style={vscDarkPlus as any} language={match[1]} PreTag="div" {...props}>
                                {String(children).replace(/\n$/, '')}
                              </SyntaxHighlighter>
                            ) : (<code className={className} {...props}>{children}</code>)
                          }
                        }}
                      >
                        {msg.content}
                      </ReactMarkdown>
                    </div>
                  ) : (
                    <span>{msg.content}</span>
                  )}
                </div>
              </div>
            ))}
          </div>

          <div className="p-4 border-t border-zinc-800 bg-zinc-950">
            <div className="flex bg-zinc-800 rounded-lg overflow-hidden border border-zinc-700 focus-within:border-blue-500">
              <input 
                type="text" 
                placeholder="Ask about this session..." 
                value={chatMessage}
                onChange={e=>setChatMessage(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSendMessage()}
                disabled={notes.length === 0}
                className="flex-1 bg-transparent px-4 py-3 focus:outline-none disabled:opacity-50"
              />
              <button 
                onClick={handleSendMessage}
                disabled={notes.length === 0 || !chatMessage.trim()}
                className="px-4 text-blue-500 hover:text-blue-400 rounded-r-lg bg-zinc-800 disabled:opacity-50"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

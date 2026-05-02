import re

with open('src/app/dashboard/page.tsx', 'r') as f:
    content = f.read()

# The functions are inside Mermaid
mermaid_start = content.find('const Mermaid = ({ chart }: { chart: string }) => {')
mermaid_end_idx = content.find('export default function Dashboard() {')

mermaid_block = content[mermaid_start:mermaid_end_idx]

# Let's cleanly separate them.
# The Mermaid component should just be:
real_mermaid = """const Mermaid = ({ chart }: { chart: string }) => {
  const [svg, setSvg] = useState<string>('');

  useEffect(() => {
    const renderDiagram = async () => {
      try {
        const id = `mermaid-${Math.random().toString(36).substring(2, 9)}`;
        const { svg: renderedSvg } = await mermaid.render(id, chart);
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
"""

dashboard_functions = """
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
"""

content = content[:mermaid_start] + real_mermaid + '\nexport default function Dashboard() {\n' + dashboard_functions + content[mermaid_end_idx + len('export default function Dashboard() {\n'):]

with open('src/app/dashboard/page.tsx', 'w') as f:
    f.write(content)


import React, { useState, useEffect, useRef } from 'react';
import { useAutomationStore } from './store/store';
import { BrowserView } from './components/BrowserView';
import { LogConsole } from './components/LogConsole';
import { InterventionChat } from './components/InterventionChat';
import { 
  runAgent, 
  stopAgent, 
  getWebSocketUrl 
} from './services/api';
import { Play, Square, Settings, Sparkles, AlertTriangle, Globe, BookOpen, Award, CheckCircle2 } from 'lucide-react';

export const App: React.FC = () => {
  const {
    sessionId,
    setSessionId,
    status,
    setStatus,
    goal,
    setGoal,
    history,
    updateFromSocket,
    reset
  } = useAutomationStore();

  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [startUrl, setStartUrl] = useState('');
  const [copied, setCopied] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  // Close WebSocket on unmount
  useEffect(() => {
    return () => {
      wsRef.current?.close();
    };
  }, []);

  // Connect to WebSocket once sessionId is generated
  const connectWebSocket = (sessId: string) => {
    if (wsRef.current) {
      wsRef.current.close();
    }

    const wsUrl = getWebSocketUrl(sessId);
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        updateFromSocket({
          status: data.status,
          currentStep: data.step,
          currentUrl: data.current_url,
          currentAction: data.current_action,
          screenshotUrl: data.screenshot_url || useAutomationStore.getState().screenshotUrl,
          history: data.history || [],
          validationErrors: data.validation_errors || null
        });

        if (['completed', 'error', 'stopped'].includes(data.status)) {
          setLoading(false);
          ws.close();
        }
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
      }
    };

    ws.onerror = (err) => {
      console.error('WebSocket Error:', err);
      setErrorMsg('WebSocket connection error.');
      setLoading(false);
    };

    ws.onclose = () => {
      setLoading(false);
    };
  };

  const handleStart = async (e: React.FormEvent) => {
    e.preventDefault();
    reset();
    setLoading(true);
    setErrorMsg(null);
    setStatus('running');

    if (!goal.trim()) {
      setErrorMsg('Goal / Objective prompt is required.');
      setLoading(false);
      setStatus('idle');
      return;
    }

    try {
      const res = await runAgent(goal, startUrl);
      if (res && res.session_id) {
        setSessionId(res.session_id);
        connectWebSocket(res.session_id);
      } else {
        throw new Error('No session ID returned from server.');
      }
    } catch (err: any) {
      console.error('Start error:', err);
      setErrorMsg(err.response?.data?.detail || err.message || 'Failed to start session.');
      setLoading(false);
      setStatus('error');
    }
  };

  const handleStop = async () => {
    if (!sessionId) return;
    try {
      await stopAgent(sessionId);
      setStatus('stopped');
      wsRef.current?.close();
      setLoading(false);
    } catch (err) {
      console.error('Stop error:', err);
    }
  };

  const applyPreset = (presetGoal: string, presetUrl: string) => {
    if (loading) return;
    setGoal(presetGoal);
    setStartUrl(presetUrl);
  };

  // Find AI's final output in session history
  const finalOutput = history.find(h => h.tool === 'finish_task')?.message || '';

  // CLI Command display string
  const cliCommand = `python cli.py --goal "${goal.replace(/"/g, '\\"') || 'Identify form fields...'}"${startUrl ? ` --url "${startUrl}"` : ''}`;

  const copyToClipboard = () => {
    navigator.clipboard.writeText(cliCommand);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex flex-col h-screen bg-black text-neutral-100 overflow-hidden">
      {/* Navbar Header */}
      <header className="h-16 flex items-center justify-between px-6 glass border-b border-neutral-900 select-none shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-white flex items-center justify-center shadow-lg shadow-white/10 text-black font-extrabold tracking-wider border border-white">
            EB
          </div>
          <div>
            <h1 className="text-base font-bold tracking-tight text-white flex items-center gap-1.5">
              EasyBrowse
              <span className="text-[10px] py-0.5 px-2 bg-neutral-900 text-neutral-300 font-semibold rounded-full border border-neutral-800 uppercase tracking-wider">
                Agent v2.0
              </span>
            </h1>
            <p className="text-[10px] text-neutral-500 font-medium font-mono">Autonomous Web Automation Agent</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {sessionId && (
            <div className="px-3 py-1.5 bg-neutral-950 border border-neutral-800 rounded-lg text-neutral-400 font-mono text-[10px]">
              ID: {sessionId}
            </div>
          )}
        </div>
      </header>

      {/* Main Content Workspace */}
      <main className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 p-6 max-w-full px-8 w-full mx-auto overflow-hidden min-h-0">
        
        {/* Left Side: Configuration, Success Banner, Logs (lg:col-span-5) */}
        <section className="lg:col-span-5 flex flex-col gap-5 overflow-y-auto min-h-0 pr-1">
          
          {/* Unified Configure Mission Card (includes presets inside) */}
          <div className="flex flex-col p-5 rounded-2xl border border-neutral-800 bg-neutral-950 shadow-xl space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-bold tracking-wide uppercase text-neutral-400 flex items-center gap-2">
                <Settings size={16} className="text-white shrink-0" />
                <span>Configure Mission</span>
              </h2>
            </div>

            {/* Compact Quick Presets */}
            <div className="space-y-1.5">
              <span className="text-[10px] uppercase font-bold text-neutral-500 tracking-wider">Preset Templates:</span>
              <div className="flex flex-wrap gap-1.5">
                <button
                  type="button"
                  disabled={loading}
                  onClick={() => applyPreset(
                    "Identify the Name and Description input fields, type a custom name and description into them, click the Submit button, and wait for confirmation.",
                    "https://ui.shadcn.com/docs/forms/react-hook-form"
                  )}
                  className="px-2.5 py-1 bg-neutral-900 hover:bg-neutral-800 border border-neutral-800 rounded-lg text-[10px] font-semibold text-neutral-300 transition-colors flex items-center gap-1"
                >
                  <Award size={10} className="text-blue-400" />
                  Shadcn Form
                </button>
                <button
                  type="button"
                  disabled={loading}
                  onClick={() => applyPreset(
                    "Click the search input field, type \"Artificial Intelligence\", press Enter or click search, scroll down to see the intro text.",
                    "https://www.wikipedia.org/"
                  )}
                  className="px-2.5 py-1 bg-neutral-900 hover:bg-neutral-800 border border-neutral-800 rounded-lg text-[10px] font-semibold text-neutral-300 transition-colors flex items-center gap-1"
                >
                  <BookOpen size={10} className="text-emerald-400" />
                  Wikipedia Search
                </button>
                <button
                  type="button"
                  disabled={loading}
                  onClick={() => applyPreset(
                    "Go to youtube.com, find the search bar, search for \"lofi beats\", and select/click the first video.",
                    "https://www.youtube.com"
                  )}
                  className="px-2.5 py-1 bg-neutral-900 hover:bg-neutral-800 border border-neutral-800 rounded-lg text-[10px] font-semibold text-neutral-300 transition-colors flex items-center gap-1"
                >
                  <Globe size={10} className="text-red-400" />
                  YouTube Navigation
                </button>
              </div>
            </div>

            <form onSubmit={handleStart} className="space-y-4 border-b border-neutral-900 pb-4">
              <div className="space-y-3.5">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-neutral-400 flex items-center gap-1.5 font-mono">
                    <Sparkles size={13} className="text-neutral-500" /> Goal / Objective
                  </label>
                  <textarea
                    rows={3}
                    disabled={loading}
                    value={goal}
                    onChange={(e) => setGoal(e.target.value)}
                    placeholder="e.g. Open wikipedia.org, search for Artificial Intelligence, and scroll down."
                    className="w-full px-3.5 py-2 bg-neutral-900 border border-neutral-800 rounded-xl text-xs focus:outline-none focus:border-white transition-all resize-none disabled:opacity-50 text-neutral-200"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-neutral-400 flex items-center gap-1.5 font-mono">
                    <Settings size={13} className="text-neutral-500" /> Starting URL (Optional)
                  </label>
                  <input
                    type="text"
                    disabled={loading}
                    value={startUrl}
                    onChange={(e) => setStartUrl(e.target.value)}
                    placeholder="e.g. https://www.google.com"
                    className="w-full px-3.5 py-2 bg-neutral-900 border border-neutral-800 rounded-xl text-xs focus:outline-none focus:border-white transition-all disabled:opacity-50 text-neutral-200"
                  />
                </div>
              </div>

              {/* Error Box */}
              {errorMsg && (
                <div className="p-3 bg-neutral-900 border border-red-950 text-red-400 rounded-xl text-xs flex items-center gap-2 animate-shake">
                  <AlertTriangle size={14} className="shrink-0" />
                  <span>{errorMsg}</span>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-3 pt-1">
                {status === 'running' || status === 'waiting_for_input' ? (
                  <button
                    type="button"
                    onClick={handleStop}
                    className="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 bg-neutral-900 hover:bg-neutral-900 border border-neutral-800 hover:border-red-600 text-red-400 text-xs font-semibold rounded-xl transition-all shadow-lg"
                  >
                    <Square size={14} fill="currentColor" />
                    <span>STOP MISSION</span>
                  </button>
                ) : (
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 flex-row flex items-center justify-center gap-2 py-2.5 px-4 bg-white hover:bg-neutral-200 disabled:bg-neutral-800 disabled:text-neutral-500 text-black text-xs font-bold rounded-xl border border-white hover:border-white transition-all shadow-lg"
                  >
                    <Play size={14} fill="black" />
                    <span>LAUNCH AGENT</span>
                  </button>
                )}
              </div>
            </form>

            {/* Equivalent CLI Display inside UI */}
            <div className="space-y-1.5 pt-1">
              <span className="text-[10px] uppercase font-bold text-neutral-500 tracking-wider">Equivalent CLI Command:</span>
              <div className="flex items-center gap-3 p-3 bg-neutral-950 border border-neutral-900 rounded-xl font-mono text-[10px] text-neutral-300 overflow-hidden">
                <span className="text-neutral-600 select-none">$</span>
                <code className="flex-1 overflow-x-auto whitespace-nowrap scrollbar-thin py-0.5">
                  {cliCommand}
                </code>
                <button
                  type="button"
                  onClick={copyToClipboard}
                  className="px-2 py-1 bg-neutral-900 hover:bg-neutral-800 border border-neutral-800 text-neutral-400 hover:text-white rounded-lg text-[9px] font-semibold transition-colors shrink-0"
                >
                  {copied ? 'Copied!' : 'Copy'}
                </button>
              </div>
            </div>
          </div>

          {/* AI Result Card (Shows only when completed successfully) */}
          {status === 'completed' && (
            <div className="flex flex-col p-5 rounded-2xl border border-emerald-500/20 bg-emerald-950/15 shadow-xl animate-in fade-in zoom-in-95 duration-300">
              <div className="flex items-center gap-2 text-emerald-400 mb-2">
                <CheckCircle2 size={18} className="shrink-0" />
                <span className="text-xs font-bold uppercase tracking-wider">Mission Success Outcome</span>
              </div>
              <p className="text-xs text-neutral-300 leading-relaxed font-mono bg-neutral-950/40 p-3 rounded-lg border border-emerald-500/10 whitespace-pre-wrap">
                {finalOutput || 'Goal accomplished successfully!'}
              </p>
            </div>
          )}

          {/* Console Log Component */}
          <LogConsole />
        </section>

        {/* Right Side: Live Browser View Screen (lg:col-span-7) */}
        <section className="lg:col-span-7 flex flex-col h-full gap-6 overflow-y-auto min-h-0 pr-1">
          <BrowserView />
          <InterventionChat />
        </section>

      </main>
    </div>
  );
};

import React, { useState } from 'react';
import { useAutomationStore } from '../store/store';
import { resumeAgent } from '../services/api';
import { Send, HelpCircle, CornerDownLeft } from 'lucide-react';

export const InterventionChat: React.FC = () => {
  const { sessionId, status, currentAction, setStatus } = useAutomationStore();
  const [inputVal, setInputVal] = useState('');
  const [sending, setSending] = useState(false);

  if (status !== 'waiting_for_input' || !sessionId) {
    return null;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputVal.trim() || sending) return;

    setSending(true);
    try {
      await resumeAgent(sessionId, inputVal);
      setInputVal('');
      setStatus('running');
    } catch (err) {
      console.error('Failed to send intervention input:', err);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="flex flex-col rounded-2xl border border-neutral-800 bg-neutral-950 overflow-hidden shadow-2xl animate-in fade-in slide-in-from-bottom-4 duration-300">
      {/* Header */}
      <div className="flex items-center gap-3 px-4 py-3 bg-neutral-900 border-b border-neutral-800">
        <div className="w-2 h-2 rounded-full bg-white animate-pulse" />
        <h3 className="text-xs font-bold tracking-widest text-neutral-200 uppercase flex items-center gap-2">
          <HelpCircle size={14} className="text-neutral-400" />
          <span>Agent Requesting Guidance</span>
        </h3>
      </div>

      {/* Main Content Area */}
      <div className="p-4 space-y-4">
        {/* Dynamic Context Description */}
        <div className="p-3 bg-neutral-900 border border-neutral-800 rounded-xl space-y-2">
          <p className="text-[11px] text-neutral-400 leading-relaxed font-mono">
            {currentAction || 'The automation run is currently paused awaiting user feedback.'}
          </p>
        </div>

        {/* Suggestion Prompt */}
        <div className="text-[11px] text-neutral-500 italic">
          Provide guidance or specify the next action details for the planner.
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="relative">
          <textarea
            rows={3}
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
            placeholder="Type guidance here..."
            className="w-full px-4 py-3 pb-12 bg-neutral-900 border border-neutral-800 rounded-xl text-sm focus:outline-none focus:border-white focus:ring-1 focus:ring-white transition-all text-neutral-200 resize-none placeholder-neutral-600 hover:border-neutral-700"
            disabled={sending}
          />
          <div className="absolute right-3 bottom-3 flex items-center gap-2">
            <span className="text-[10px] text-neutral-600 font-mono flex items-center gap-1">
              <span>Press enter</span>
              <CornerDownLeft size={10} />
            </span>
            <button
              type="submit"
              disabled={!inputVal.trim() || sending}
              className="p-2 rounded-lg bg-neutral-100 text-neutral-950 hover:bg-white disabled:bg-neutral-800 disabled:text-neutral-500 transition-colors shadow-md hover:shadow-white/10"
            >
              <Send size={14} />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};


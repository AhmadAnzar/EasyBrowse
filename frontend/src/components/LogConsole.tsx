import React, { useEffect, useRef } from 'react';
import { useAutomationStore } from '../store/store';
import { Terminal, ShieldCheck, AlertCircle, Play } from 'lucide-react';

export const LogConsole: React.FC = () => {
  const { history, status, currentAction } = useAutomationStore();
  const consoleEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    consoleEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history, currentAction]);

  return (
    <div className="flex flex-col h-[320px] rounded-2xl border border-slate-800 bg-black/50 overflow-hidden shadow-xl">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-dark-950/80 border-b border-slate-800">
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-400">
          <Terminal size={14} className="text-indigo-400" />
          <span>EXECUTION CONSOLE LOGS</span>
        </div>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${status === 'running' ? 'bg-indigo-500 animate-pulse' : 'bg-slate-600'}`} />
          <span className="text-[10px] text-slate-500 font-mono uppercase tracking-wider">{status}</span>
        </div>
      </div>

      {/* Terminal lines */}
      <div className="flex-1 overflow-y-auto p-4 font-mono text-xs space-y-3">
        {history.length === 0 && (
          <div className="text-slate-600 italic">Console idle. Awaiting action trigger...</div>
        )}

        {history.map((log, index) => (
          <div key={index} className="border-l-2 border-slate-800 pl-3 py-1 space-y-1">
            <div className="flex items-center gap-2">
              <span className="text-indigo-400 font-bold shrink-0">[Step {log.step}]</span>
              <span className="text-slate-500 shrink-0">TOOL:</span>
              <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 font-bold uppercase text-[10px]">
                {log.tool}
              </span>
              <span className={`text-[10px] uppercase font-bold tracking-wider ml-auto px-1 rounded ${log.success ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'}`}>
                {log.success ? 'Success' : 'Failed'}
              </span>
            </div>

            {log.reasoning && (
              <div className="text-amber-400/90 text-[11px] leading-relaxed">
                <span className="text-slate-500 font-normal">Reasoning:</span> {log.reasoning}
              </div>
            )}

            {log.message && (
              <div className="text-slate-300 break-all leading-normal whitespace-pre-wrap">
                <span className="text-slate-500 font-normal">Result:</span> {log.message}
              </div>
            )}

            {log.verification && (
              <div className="flex items-center gap-1.5 text-[10px] text-indigo-300 font-medium">
                {log.verification.includes('alert') ? (
                  <AlertCircle size={10} className="text-red-400 shrink-0" />
                ) : (
                  <ShieldCheck size={10} className="text-green-400 shrink-0" />
                )}
                <span>{log.verification}</span>
              </div>
            )}
          </div>
        ))}

        {status === 'running' && currentAction && (
          <div className="flex items-start gap-2 text-indigo-400 animate-pulse border-l-2 border-indigo-500/30 pl-3 py-1">
            <Play size={12} className="shrink-0 mt-0.5" />
            <div>
              <span className="font-bold mr-1.5">[Processing...]</span>
              <span className="text-slate-300">{currentAction}</span>
            </div>
          </div>
        )}

        <div ref={consoleEndRef} />
      </div>
    </div>
  );
};

import React from 'react';
import { useAutomationStore } from '../store/store';
import { getScreenshotFullUrl } from '../services/api';
import { Globe, RefreshCw, Eye } from 'lucide-react';

export const BrowserView: React.FC = () => {
  const { currentUrl, screenshotUrl, status, currentAction } = useAutomationStore();

  return (
    <div className="flex flex-col flex-1 rounded-2xl border border-slate-800 bg-dark-900 overflow-hidden shadow-2xl">
      {/* Browser Bar */}
      <div className="flex items-center gap-3 px-4 py-3 bg-dark-950 border-b border-slate-800 select-none">
        {/* Mock window buttons */}
        <div className="flex gap-1.5 mr-2">
          <div className="w-3 h-3 rounded-full bg-red-500/80" />
          <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
          <div className="w-3 h-3 rounded-full bg-green-500/80" />
        </div>

        {/* URL Input Box */}
        <div className="flex-1 flex items-center gap-2 px-3 py-1.5 bg-dark-900 border border-slate-800 rounded-lg text-slate-400 text-xs">
          <Globe size={14} className="text-slate-500 shrink-0" />
          <div className="truncate font-mono select-all flex-1 text-slate-300">
            {currentUrl || 'about:blank'}
          </div>
          {status === 'running' && (
            <RefreshCw size={12} className="animate-spin text-indigo-500 shrink-0" />
          )}
        </div>
      </div>

      {/* Screen Frame Content */}
      <div className="flex-1 relative bg-dark-950 flex items-center justify-center p-2 min-h-[300px] overflow-auto">
        {screenshotUrl ? (
          <img
            src={getScreenshotFullUrl(screenshotUrl)}
            alt="Browser Live Frame"
            className="max-w-full max-h-full object-contain rounded border border-slate-800 shadow-lg"
          />
        ) : (
          <div className="flex flex-col items-center gap-3 text-slate-500">
            <div className="w-16 h-16 rounded-full bg-dark-800 flex items-center justify-center text-slate-400 border border-slate-700 animate-pulse">
              <Eye size={28} />
            </div>
            <p className="text-sm font-medium">No active browser frame</p>
            <p className="text-xs text-slate-600">Start an automation task to see live output.</p>
          </div>
        )}

        {/* Floating status banner */}
        {status === 'running' && (
          <div className="absolute bottom-4 left-4 right-4 py-2 px-4 glass rounded-xl flex items-center gap-2 text-xs border border-indigo-500/20 text-indigo-300 animate-pulse">
            <RefreshCw size={12} className="animate-spin" />
            <span className="font-semibold uppercase tracking-wider shrink-0 text-indigo-400">Current Action:</span>
            <span className="truncate">{currentAction || 'Processing...'}</span>
          </div>
        )}
      </div>
    </div>
  );
};

import React from 'react';
import { 
  Film, 
  Play, 
  AlertTriangle, 
  CheckCircle, 
  Bot, 
  Search, 
  RefreshCw,
  Sparkles
} from 'lucide-react';
import { Project } from '../types';

interface HeaderProps {
  currentProject: Project | null;
  projects: Project[];
  onSelectProject: (id: string) => void;
  onRunCheck: () => void;
  isChecking: boolean;
  onOpenAssistant: () => void;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Header: React.FC<HeaderProps> = ({
  currentProject,
  projects,
  onSelectProject,
  onRunCheck,
  isChecking,
  onOpenAssistant,
  searchQuery,
  onSearchChange,
  activeTab,
  setActiveTab
}) => {
  const healthScore = currentProject?.health_score ?? 82;
  const healthColor = healthScore >= 85 ? 'text-emerald-400 border-emerald-500/40 bg-emerald-500/10' :
                      healthScore >= 70 ? 'text-amber-400 border-amber-500/40 bg-amber-500/10' :
                      'text-rose-400 border-rose-500/40 bg-rose-500/10';

  return (
    <header className="border-b border-[#202636] bg-[#0d1017]/90 backdrop-blur-md sticky top-0 z-40">
      {/* Top Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 gap-4">
          
          {/* Brand Logo & Name */}
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-amber-500 to-amber-700 flex items-center justify-center shadow-lg shadow-amber-500/20 border border-amber-400/30">
              <Film className="w-5 h-5 text-black font-bold" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-black text-lg tracking-wider text-white uppercase">
                  Continuity<span className="text-amber-400">Guardian</span>
                </span>
                <span className="text-[10px] uppercase font-bold tracking-widest px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                  Agentic AI
                </span>
              </div>
              <p className="text-[11px] text-slate-400 tracking-tight hidden sm:block">
                Your movie remembers. Your production doesn't have to.
              </p>
            </div>
          </div>

          {/* Project Selector & Search */}
          <div className="flex-1 max-w-md mx-2 hidden md:flex items-center gap-3">
            <div className="relative w-full">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search scenes, characters, props, issues..."
                value={searchQuery}
                onChange={(e) => onSearchChange(e.target.value)}
                className="w-full pl-9 pr-3 py-1.5 text-xs bg-[#141923] text-slate-200 placeholder-slate-500 rounded-md border border-[#262f42] focus:outline-none focus:border-amber-400/60"
              />
            </div>

            <select
              value={currentProject?.id || ''}
              onChange={(e) => onSelectProject(e.target.value)}
              className="bg-[#141923] text-xs text-slate-200 border border-[#262f42] rounded-md px-3 py-1.5 focus:outline-none focus:border-amber-400/60"
            >
              {projects.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.title}
                </option>
              ))}
            </select>
          </div>

          {/* Health Gauge & Primary Actions */}
          <div className="flex items-center gap-3">
            {/* Health Score Pill */}
            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-semibold ${healthColor}`}>
              <div className="w-2 h-2 rounded-full bg-current animate-pulse" />
              <span>Health: {healthScore}%</span>
            </div>

            {/* Run Continuity Check Button */}
            <button
              onClick={onRunCheck}
              disabled={isChecking}
              className="flex items-center gap-2 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-black px-4 py-2 rounded-md font-bold text-xs shadow-lg shadow-amber-500/20 transition-all active:scale-95 disabled:opacity-50 cursor-pointer"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isChecking ? 'animate-spin' : ''}`} />
              <span>{isChecking ? 'Analyzing State...' : 'Run Continuity Check'}</span>
            </button>

            {/* AI Assistant Copilot Trigger */}
            <button
              onClick={onOpenAssistant}
              className="flex items-center gap-1.5 bg-[#181f2c] hover:bg-[#20293a] text-slate-200 border border-[#2a3449] px-3 py-2 rounded-md font-medium text-xs transition-colors cursor-pointer"
            >
              <Bot className="w-4 h-4 text-amber-400" />
              <span className="hidden sm:inline">AI Copilot</span>
            </button>
          </div>

        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="border-t border-[#1a202c] bg-[#0a0d13]/90">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-1 sm:space-x-6 overflow-x-auto py-2 text-xs font-medium">
            {[
              { id: 'dashboard', label: 'Dashboard Overview' },
              { id: 'issues', label: 'Continuity Issues' },
              { id: 'scenes', label: 'Scene Explorer' },
              { id: 'characters', label: 'Character Timeline' },
              { id: 'props', label: 'Prop Tracking' },
              { id: 'analytics', label: 'ClickHouse Analytics' }
            ].map((tab) => {
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-3 py-1.5 rounded-md whitespace-nowrap transition-all cursor-pointer ${
                    isActive
                      ? 'bg-amber-400/10 text-amber-400 border border-amber-400/30 font-semibold'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-[#141924]'
                  }`}
                >
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>
      </div>
    </header>
  );
};

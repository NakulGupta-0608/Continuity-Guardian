import React, { useState } from 'react';
import { 
  AlertOctagon, 
  AlertTriangle, 
  CheckCircle2, 
  Filter, 
  Check, 
  Sparkles, 
  ArrowRight,
  ShieldAlert,
  SlidersHorizontal,
  FileCheck
} from 'lucide-react';
import { ContinuityIssue, SuggestedFix } from '../types';

interface IssuesDashboardProps {
  issues: ContinuityIssue[];
  onResolveIssue: (issueId: string, fix: SuggestedFix) => Promise<void>;
  resolvingId: string | null;
}

export const IssuesDashboard: React.FC<IssuesDashboardProps> = ({
  issues,
  onResolveIssue,
  resolvingId
}) => {
  const [severityFilter, setSeverityFilter] = useState<string>('ALL');
  const [categoryFilter, setCategoryFilter] = useState<string>('ALL');
  const [statusFilter, setStatusFilter] = useState<string>('OPEN');
  const [selectedIssue, setSelectedIssue] = useState<ContinuityIssue | null>(null);

  const filteredIssues = issues.filter((iss) => {
    if (severityFilter !== 'ALL' && iss.severity !== severityFilter) return false;
    if (categoryFilter !== 'ALL' && iss.issue_type !== categoryFilter) return false;
    if (statusFilter !== 'ALL' && iss.status !== statusFilter) return false;
    return true;
  });

  const categories = ['ALL', 'WARDROBE', 'PROP', 'LOCATION', 'CHARACTER_STATE', 'TIMELINE', 'KNOWLEDGE', 'WEATHER'];

  return (
    <div className="space-y-6">
      {/* Header & Filter Controls */}
      <div className="bg-[#121622] border border-[#20283b] rounded-xl p-5 shadow-lg">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <ShieldAlert className="w-5 h-5 text-amber-400" />
              Continuity Issue Sentinel
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Autonomous contradiction detector cross-referencing wardrobe, props, travel sequences, injuries, and facts.
            </p>
          </div>

          <div className="flex items-center gap-2 text-xs">
            <span className="text-slate-400">Total Flagged: <strong className="text-white">{issues.length}</strong></span>
            <span className="text-slate-600">|</span>
            <span className="text-rose-400">Critical: <strong>{issues.filter(i => i.severity === 'CRITICAL' && i.status === 'OPEN').length}</strong></span>
            <span className="text-slate-600">|</span>
            <span className="text-emerald-400">Resolved: <strong>{issues.filter(i => i.status === 'RESOLVED').length}</strong></span>
          </div>
        </div>

        {/* Filter Pills */}
        <div className="flex flex-wrap items-center gap-3 mt-4 pt-4 border-t border-[#1d2433]">
          {/* Status Filters */}
          <div className="flex items-center rounded-lg bg-[#0a0d14] p-1 border border-[#232b3d]">
            {['ALL', 'OPEN', 'RESOLVED'].map((stat) => (
              <button
                key={stat}
                onClick={() => setStatusFilter(stat)}
                className={`px-3 py-1 rounded-md text-xs font-semibold transition-all cursor-pointer ${
                  statusFilter === stat
                    ? 'bg-amber-500 text-black shadow-sm'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {stat}
              </button>
            ))}
          </div>

          {/* Severity Filters */}
          <div className="flex items-center rounded-lg bg-[#0a0d14] p-1 border border-[#232b3d]">
            {[
              { id: 'ALL', label: 'All Severities' },
              { id: 'CRITICAL', label: '🔴 Critical' },
              { id: 'HIGH', label: '🟠 High' },
              { id: 'MEDIUM', label: '🟡 Medium' },
              { id: 'LOW', label: '🔵 Low' }
            ].map((sev) => (
              <button
                key={sev.id}
                onClick={() => setSeverityFilter(sev.id)}
                className={`px-2.5 py-1 rounded-md text-xs font-medium transition-all cursor-pointer ${
                  severityFilter === sev.id
                    ? 'bg-slate-700 text-white font-bold'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {sev.label}
              </button>
            ))}
          </div>

          {/* Category Dropdown */}
          <div className="flex items-center gap-2 text-xs">
            <span className="text-slate-400 flex items-center gap-1">
              <Filter className="w-3.5 h-3.5" /> Category:
            </span>
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="bg-[#0a0d14] border border-[#232b3d] rounded-lg px-2.5 py-1 text-slate-200 focus:outline-none focus:border-amber-400 text-xs"
            >
              {categories.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Issues List */}
      <div className="space-y-4">
        {filteredIssues.map((iss) => {
          const isResolved = iss.status === 'RESOLVED';
          const isSelected = selectedIssue?.id === iss.id;

          return (
            <div
              key={iss.id}
              className={`rounded-xl border transition-all duration-200 overflow-hidden shadow-lg ${
                isResolved
                  ? 'bg-[#0f141d]/70 border-emerald-500/30 opacity-75'
                  : isSelected
                  ? 'bg-[#151b29] border-amber-500/60 shadow-amber-500/10'
                  : 'bg-[#121622] border-[#20283b] hover:border-[#2a354d]'
              }`}
            >
              {/* Card Header */}
              <div className="p-5">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className={`px-2.5 py-0.5 text-xs font-black uppercase rounded ${
                      iss.severity === 'CRITICAL' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40' :
                      iss.severity === 'HIGH' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40' :
                      'bg-sky-500/20 text-sky-400 border border-sky-500/40'
                    }`}>
                      {iss.severity}
                    </span>
                    <span className="px-2 py-0.5 text-[11px] font-bold text-slate-300 uppercase bg-slate-800 rounded border border-slate-700">
                      {iss.issue_type}
                    </span>
                    <span className="text-xs font-mono text-amber-300 font-bold">
                      {iss.scene_id ? iss.scene_id.replace('scene_', 'Scene ') : 'Project Level'}
                    </span>
                    <span className="text-sm font-bold text-white">
                      — {iss.entity_name} ({iss.entity_type})
                    </span>
                  </div>

                  <div className="flex items-center gap-3">
                    <span className="text-xs font-mono text-slate-400">
                      Confidence: <strong className="text-amber-400">{iss.confidence}%</strong>
                    </span>
                    <span className={`text-xs px-2.5 py-0.5 rounded-full font-bold uppercase ${
                      isResolved
                        ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                        : 'bg-rose-500/20 text-rose-400 border border-rose-500/40'
                    }`}>
                      {iss.status}
                    </span>
                  </div>
                </div>

                {/* Description */}
                <p className="text-xs sm:text-sm text-slate-200 leading-relaxed mb-4">
                  {iss.description}
                </p>

                {/* State Comparison Box */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4 text-xs font-mono">
                  <div className="p-3 rounded-lg bg-[#0a0d14] border border-[#1e2535]">
                    <div className="text-[10px] text-slate-500 uppercase tracking-wider font-bold mb-1">Established / Previous State</div>
                    <div className="text-slate-300 break-words">{iss.previous_state || 'None established'}</div>
                  </div>
                  <div className="p-3 rounded-lg bg-[#0a0d14] border border-rose-500/20">
                    <div className="text-[10px] text-rose-400 uppercase tracking-wider font-bold mb-1">Contradictory / Current State</div>
                    <div className="text-white font-semibold break-words">{iss.current_state}</div>
                  </div>
                </div>

                {/* Resolution Notice if already resolved */}
                {isResolved && (
                  <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center gap-2 text-xs text-emerald-300">
                    <FileCheck className="w-4 h-4 shrink-0" />
                    <span><b>Resolution Applied:</b> {iss.resolution_note || 'Resolved by script supervisor'}</span>
                  </div>
                )}

                {/* Suggested Fixes Section (If Open) */}
                {!isResolved && iss.suggested_fixes && iss.suggested_fixes.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-[#1d2535]">
                    <div className="text-xs font-bold text-amber-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5" />
                      Agent Recommended Resolutions
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                      {iss.suggested_fixes.map((fix, idx) => (
                        <div
                          key={fix.id || idx}
                          className={`p-3 rounded-lg border text-xs flex flex-col justify-between transition-all ${
                            idx === 0
                              ? 'bg-amber-500/10 border-amber-500/40 text-amber-200'
                              : 'bg-[#0a0d14] border-[#1e2535] text-slate-300'
                          }`}
                        >
                          <div>
                            <div className="flex items-center justify-between mb-1">
                              <span className="font-bold text-[11px] uppercase tracking-wider text-white">
                                {idx === 0 ? 'Option 1 (Recommended)' : `Option ${idx + 1}`}
                              </span>
                            </div>
                            <p className="text-[11px] leading-relaxed mb-3">
                              {fix.title}
                            </p>
                          </div>
                          
                          <button
                            onClick={() => onResolveIssue(iss.id, fix)}
                            disabled={resolvingId === iss.id}
                            className={`w-full py-1.5 px-3 rounded text-[11px] font-bold flex items-center justify-center gap-1.5 transition-all cursor-pointer ${
                              idx === 0
                                ? 'bg-amber-500 hover:bg-amber-400 text-black shadow-md'
                                : 'bg-slate-800 hover:bg-slate-700 text-slate-200'
                            }`}
                          >
                            <Check className="w-3.5 h-3.5" />
                            <span>{resolvingId === iss.id ? 'Applying...' : 'Apply Fix'}</span>
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

              </div>
            </div>
          );
        })}

        {filteredIssues.length === 0 && (
          <div className="bg-[#121622] border border-[#20283b] rounded-xl p-12 text-center text-slate-400 text-xs">
            <CheckCircle2 className="w-12 h-12 text-emerald-400 mx-auto mb-3" />
            <div className="text-base font-bold text-white mb-1">No Continuity Issues Match Filter</div>
            <p>Adjust your severity, category, or status filters above to view other records.</p>
          </div>
        )}
      </div>
    </div>
  );
};

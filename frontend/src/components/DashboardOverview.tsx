import React from 'react';
import { 
  Film, 
  Users, 
  Package, 
  AlertOctagon, 
  AlertTriangle, 
  CheckCircle2, 
  Activity, 
  ArrowRight,
  ShieldCheck,
  Zap
} from 'lucide-react';
import { Project, ContinuityIssue, Scene } from '../types';

interface DashboardOverviewProps {
  project: Project | null;
  scenes: Scene[];
  issues: ContinuityIssue[];
  onNavigateTab: (tab: string) => void;
  onSelectScene: (sceneId: string) => void;
  onOpenIssue: (issueId: string) => void;
}

export const DashboardOverview: React.FC<DashboardOverviewProps> = ({
  project,
  scenes,
  issues,
  onNavigateTab,
  onSelectScene,
  onOpenIssue
}) => {
  const openIssues = issues.filter((i) => i.status === 'OPEN');
  const criticalCount = openIssues.filter((i) => i.severity === 'CRITICAL').length;
  const highCount = openIssues.filter((i) => i.severity === 'HIGH').length;
  const resolvedCount = issues.filter((i) => i.status === 'RESOLVED').length;
  const healthScore = project?.health_score ?? 82;

  return (
    <div className="space-y-6">
      {/* Project Hero Header */}
      <div className="relative rounded-xl overflow-hidden border border-[#232b3d] bg-gradient-to-r from-[#111622] via-[#141a29] to-[#0e121a] p-6 shadow-2xl">
        <div className="clapper-stripes h-2 w-full absolute top-0 left-0 opacity-40" />
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mt-2">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                {project?.genre || 'Neo-Noir Mystery'}
              </span>
              <span className="px-2 py-0.5 text-[10px] font-semibold uppercase rounded bg-slate-800 text-slate-300 border border-slate-700">
                {project?.status || 'Production'}
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black tracking-wide text-white uppercase font-mono">
              {project?.title || 'Midnight at Platform 7'}
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-2xl leading-relaxed">
              {project?.description || 'Autonomous Continuity Sentinel tracking wardrobe, props, character states, and dialogue facts across all filming units.'}
            </p>
          </div>

          {/* Health Score Gauge */}
          <div className="flex items-center gap-4 bg-[#0a0d14]/80 p-4 rounded-xl border border-[#252f44]">
            <div className="text-right">
              <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Continuity Health</div>
              <div className="text-2xl sm:text-3xl font-black text-amber-400 font-mono">{healthScore}<span className="text-sm font-normal text-slate-500"> / 100</span></div>
              <div className="text-[10px] text-emerald-400 font-medium">Internal Production Index</div>
            </div>
            <div className="relative w-14 h-14 flex items-center justify-center">
              <svg className="w-14 h-14 transform -rotate-90">
                <circle cx="28" cy="28" r="22" stroke="#1e2535" strokeWidth="5" fill="transparent" />
                <circle
                  cx="28"
                  cy="28"
                  r="22"
                  stroke={healthScore >= 80 ? '#e5a93c' : '#f43f5e'}
                  strokeWidth="5"
                  fill="transparent"
                  strokeDasharray="138"
                  strokeDashoffset={138 - (138 * healthScore) / 100}
                  className="transition-all duration-1000 ease-out"
                />
              </svg>
              <Activity className="w-5 h-5 text-amber-400 absolute" />
            </div>
          </div>
        </div>
      </div>

      {/* Overview Stat Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {[
          { label: 'Total Scenes', value: scenes.length || 14, icon: Film, color: 'text-sky-400', tab: 'scenes' },
          { label: 'Characters', value: 5, icon: Users, color: 'text-violet-400', tab: 'characters' },
          { label: 'Props Tracked', value: 8, icon: Package, color: 'text-amber-400', tab: 'props' },
          { label: 'Open Issues', value: openIssues.length, icon: AlertOctagon, color: 'text-rose-400', tab: 'issues' },
          { label: 'Critical Errors', value: criticalCount, icon: AlertTriangle, color: 'text-rose-500', tab: 'issues' },
          { label: 'Resolved Deficiencies', value: resolvedCount, icon: CheckCircle2, color: 'text-emerald-400', tab: 'issues' },
        ].map((kpi, idx) => {
          const Icon = kpi.icon;
          return (
            <div
              key={idx}
              onClick={() => onNavigateTab(kpi.tab)}
              className="bg-[#121622] hover:bg-[#161c2b] border border-[#20283b] rounded-xl p-4 transition-all duration-200 cursor-pointer group shadow-md"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">{kpi.label}</span>
                <Icon className={`w-4 h-4 ${kpi.color} group-hover:scale-110 transition-transform`} />
              </div>
              <div className="text-2xl font-black text-white font-mono">{kpi.value}</div>
            </div>
          );
        })}
      </div>

      {/* Intentional Demo Flaws Alert Banner */}
      <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="p-2 rounded-lg bg-amber-500/20 text-amber-400 shrink-0">
            <Zap className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-amber-300">Hackathon Demo Dataset: 6 Intentional Flaws Pre-Loaded</h2>
            <p className="text-xs text-slate-300 mt-0.5">
              The project includes real-time detection for: <b>Rahul's wardrobe swap</b> (Sc 10→11), <b>Red notebook teleportation</b> (Sc 08→10), <b>Priya hospital warp</b> (Sc 12→13), <b>disappearing injury</b> (Sc 04→06), <b>timeline inversion</b> (Sc 02→03), and <b>premature dialogue secret</b> (Sc 02).
            </p>
          </div>
        </div>
        <button
          onClick={() => onNavigateTab('issues')}
          className="px-4 py-2 bg-amber-500 hover:bg-amber-400 text-black text-xs font-bold rounded-lg transition-colors shrink-0 cursor-pointer"
        >
          View Flagged Issues
        </button>
      </div>

      {/* Two-Column Grid: Active Flagged Issues & Scene Quick Timeline */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left 2 Cols: High Priority Issues List */}
        <div className="lg:col-span-2 bg-[#121622] border border-[#20283b] rounded-xl p-5 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <AlertOctagon className="w-4 h-4 text-rose-400" />
                Continuity Radar: Urgent Flaws
              </h2>
              <p className="text-[11px] text-slate-400">Contradictions needing script supervisor or director resolution</p>
            </div>
            <button
              onClick={() => onNavigateTab('issues')}
              className="text-xs text-amber-400 hover:text-amber-300 flex items-center gap-1 font-semibold cursor-pointer"
            >
              View all ({issues.length}) <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          <div className="space-y-3">
            {openIssues.slice(0, 4).map((iss) => (
              <div
                key={iss.id}
                onClick={() => onOpenIssue(iss.id)}
                className="p-3.5 rounded-lg bg-[#0e121a] hover:bg-[#141926] border border-[#222a3d] transition-all cursor-pointer group"
              >
                <div className="flex items-center justify-between gap-2 mb-1.5">
                  <div className="flex items-center gap-2">
                    <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded ${
                      iss.severity === 'CRITICAL' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' :
                      iss.severity === 'HIGH' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                      'bg-sky-500/20 text-sky-400 border border-sky-500/30'
                    }`}>
                      {iss.severity}
                    </span>
                    <span className="text-[10px] font-medium text-slate-400 uppercase tracking-wider bg-slate-800 px-1.5 py-0.5 rounded">
                      {iss.issue_type}
                    </span>
                    <span className="text-xs font-bold text-white group-hover:text-amber-300 transition-colors">
                      {iss.entity_name} in {iss.scene_id?.replace('scene_', 'Scene ') || 'Scene'}
                    </span>
                  </div>
                  <span className="text-[11px] font-mono text-slate-400">{iss.confidence}% Confidence</span>
                </div>
                <p className="text-xs text-slate-300 line-clamp-2 leading-relaxed">{iss.description}</p>
              </div>
            ))}

            {openIssues.length === 0 && (
              <div className="text-center py-8 text-slate-400 text-xs">
                <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
                All continuity issues in this project have been successfully resolved!
              </div>
            )}
          </div>
        </div>

        {/* Right Col: Scene Strip & Director Presets */}
        <div className="space-y-5">
          {/* Quick Demo Shortcuts */}
          <div className="bg-[#121622] border border-[#20283b] rounded-xl p-5 shadow-lg">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider mb-2 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-amber-400" />
              Demo Quick Links
            </h2>
            <p className="text-[11px] text-slate-400 mb-4">Jump directly into the primary demo test cases</p>

            <div className="space-y-2">
              <button
                onClick={() => onNavigateTab('issues')}
                className="w-full text-left p-2.5 rounded-lg bg-[#0e121a] hover:bg-[#161c29] border border-[#20283b] text-xs text-slate-200 transition-all flex items-center justify-between cursor-pointer"
              >
                <span>🔴 Wardrobe swap (Sc 10 vs 11)</span>
                <ArrowRight className="w-3.5 h-3.5 text-amber-400" />
              </button>
              <button
                onClick={() => onNavigateTab('props')}
                className="w-full text-left p-2.5 rounded-lg bg-[#0e121a] hover:bg-[#161c29] border border-[#20283b] text-xs text-slate-200 transition-all flex items-center justify-between cursor-pointer"
              >
                <span>🔴 Red Notebook Teleportation</span>
                <ArrowRight className="w-3.5 h-3.5 text-amber-400" />
              </button>
              <button
                onClick={() => onNavigateTab('characters')}
                className="w-full text-left p-2.5 rounded-lg bg-[#0e121a] hover:bg-[#161c29] border border-[#20283b] text-xs text-slate-200 transition-all flex items-center justify-between cursor-pointer"
              >
                <span>🟠 Rahul Character Timeline</span>
                <ArrowRight className="w-3.5 h-3.5 text-amber-400" />
              </button>
              <button
                onClick={() => onNavigateTab('analytics')}
                className="w-full text-left p-2.5 rounded-lg bg-[#0e121a] hover:bg-[#161c29] border border-[#20283b] text-xs text-slate-200 transition-all flex items-center justify-between cursor-pointer"
              >
                <span>⚡ ClickHouse Event Stream</span>
                <ArrowRight className="w-3.5 h-3.5 text-amber-400" />
              </button>
            </div>
          </div>

          {/* Script Overview Card */}
          <div className="bg-[#121622] border border-[#20283b] rounded-xl p-5 shadow-lg">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider mb-2">Screenplay Stats</h2>
            <div className="space-y-2 text-xs text-slate-300">
              <div className="flex justify-between py-1 border-b border-[#1c2333]">
                <span className="text-slate-400">Total Filming Scenes:</span>
                <span className="font-mono text-white font-bold">{scenes.length}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-[#1c2333]">
                <span className="text-slate-400">Primary Locations:</span>
                <span className="font-mono text-white font-bold">4 (Platform 7, Café, Car, Hospital)</span>
              </div>
              <div className="flex justify-between py-1 border-b border-[#1c2333]">
                <span className="text-slate-400">Story Time Span:</span>
                <span className="font-mono text-white font-bold">11:58 PM - 1:30 AM</span>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};

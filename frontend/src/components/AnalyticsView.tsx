import React, { useEffect, useState } from 'react';
import { 
  BarChart3, 
  Database, 
  Activity, 
  PieChart, 
  Layers, 
  AlertTriangle,
  RefreshCw,
  Cpu,
  Clock
} from 'lucide-react';
import { ProjectAnalytics } from '../types';
import { api } from '../services/api';

interface AnalyticsViewProps {
  projectId: string;
}

export const AnalyticsView: React.FC<AnalyticsViewProps> = ({ projectId }) => {
  const [analytics, setAnalytics] = useState<ProjectAnalytics | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const data = await api.getAnalytics(projectId);
      setAnalytics(data);
    } catch (err) {
      console.error('Analytics load error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [projectId]);

  if (isLoading && !analytics) {
    return (
      <div className="p-12 text-center text-slate-400 text-xs font-mono">
        <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-amber-400" />
        Connecting to ClickHouse analytical stream...
      </div>
    );
  }

  const chTelemetry = analytics?.clickhouse_telemetry;
  const isChConnected = chTelemetry?.status === 'connected';

  return (
    <div className="space-y-6">
      {/* ClickHouse Integration Status Banner */}
      <div className="bg-[#121622] border border-[#20283b] rounded-xl p-5 shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className={`p-2.5 rounded-lg border ${
            isChConnected ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' : 'bg-amber-500/20 text-amber-400 border-amber-500/30'
          }`}>
            <Database className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold text-white uppercase tracking-wider">
                ClickHouse Event Analytical Layer
              </h2>
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                isChConnected
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                  : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
              }`}>
                {isChConnected ? 'ClickHouse Live Node Connected' : 'High-Performance Embedded Analytics Engine'}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              High-throughput columnar event capture for scene transitions, prop custody migrations, and continuity mutations.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 text-xs font-mono">
          <div className="bg-[#0a0d14] px-3 py-1.5 rounded-lg border border-[#232b3d]">
            <span className="text-slate-500">Ingested Events:</span>{' '}
            <strong className="text-amber-400">{chTelemetry?.total_event_records || 0}</strong>
          </div>
          <button
            onClick={loadData}
            className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg transition-colors cursor-pointer"
            title="Refresh stream"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Analytics Metric Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Severity Distribution */}
        <div className="bg-[#121622] border border-[#20283b] rounded-xl p-5 shadow-md">
          <h2 className="text-xs font-bold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
            <PieChart className="w-4 h-4 text-amber-400" />
            Issue Severity Distribution
          </h2>
          <div className="space-y-2.5 text-xs">
            {Object.entries(analytics?.severity_distribution || {}).map(([sev, count]) => {
              const color = sev === 'CRITICAL' ? 'bg-rose-500' :
                            sev === 'HIGH' ? 'bg-amber-500' :
                            sev === 'MEDIUM' ? 'bg-sky-500' : 'bg-slate-500';
              const total = analytics?.total_issues || 1;
              const pct = Math.round((count / total) * 100);

              return (
                <div key={sev} className="space-y-1">
                  <div className="flex justify-between text-[11px]">
                    <span className="font-semibold text-slate-300">{sev}</span>
                    <span className="font-mono text-slate-400">{count} ({pct}%)</span>
                  </div>
                  <div className="w-full h-2 bg-[#0a0d14] rounded-full overflow-hidden">
                    <div className={`h-full ${color}`} style={{ width: `${pct}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Defect Categories */}
        <div className="bg-[#121622] border border-[#20283b] rounded-xl p-5 shadow-md">
          <h2 className="text-xs font-bold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
            <Layers className="w-4 h-4 text-violet-400" />
            Flaws by Continuity Category
          </h2>
          <div className="space-y-2 text-xs font-mono max-h-48 overflow-y-auto pr-1">
            {Object.entries(analytics?.category_distribution || {}).map(([cat, count]) => (
              <div key={cat} className="flex items-center justify-between p-2 rounded bg-[#0a0d14] border border-[#1e2535]">
                <span className="text-slate-300 font-medium">{cat}</span>
                <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 text-[11px] font-bold">
                  {count} flaws
                </span>
              </div>
            ))}
            {Object.keys(analytics?.category_distribution || {}).length === 0 && (
              <div className="text-slate-500 py-4 text-center">No categories recorded</div>
            )}
          </div>
        </div>

        {/* Problematic Entities Ranking */}
        <div className="bg-[#121622] border border-[#20283b] rounded-xl p-5 shadow-md">
          <h2 className="text-xs font-bold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-rose-400" />
            Defect Density Ranking
          </h2>
          <div className="space-y-3 text-xs">
            <div>
              <div className="text-[10px] text-slate-400 uppercase font-bold mb-1.5">Characters with Inconsistencies:</div>
              <div className="space-y-1">
                {Object.entries(analytics?.problematic_characters || {}).map(([name, count]) => (
                  <div key={name} className="flex justify-between items-center text-[11px] p-1.5 rounded bg-[#0a0d14]">
                    <span className="text-white font-medium">{name}</span>
                    <span className="text-rose-400 font-mono font-bold">{count} issues</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="pt-2 border-t border-[#1d2535]">
              <div className="text-[10px] text-slate-400 uppercase font-bold mb-1.5">Props with Inconsistencies:</div>
              <div className="space-y-1">
                {Object.entries(analytics?.problematic_props || {}).map(([prop, count]) => (
                  <div key={prop} className="flex justify-between items-center text-[11px] p-1.5 rounded bg-[#0a0d14]">
                    <span className="text-amber-300 font-medium">{prop}</span>
                    <span className="text-amber-400 font-mono font-bold">{count} issues</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* Live ClickHouse Event Stream Table */}
      <div className="bg-[#121622] border border-[#20283b] rounded-xl p-5 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Activity className="w-4 h-4 text-amber-400" />
              Live ClickHouse Production Event Stream
            </h2>
            <p className="text-[11px] text-slate-400">Append-only audit log streamed from set cameras, scripts, and agent tool executions</p>
          </div>
          <span className="text-[11px] font-mono text-emerald-400 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            Real-time Ingest Active
          </span>
        </div>

        <div className="overflow-x-auto rounded-lg border border-[#1d2535]">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-[#0a0d14] text-slate-400 uppercase text-[10px] border-b border-[#1d2535]">
              <tr>
                <th className="p-2.5">Timestamp</th>
                <th className="p-2.5">Event Type</th>
                <th className="p-2.5">Actor</th>
                <th className="p-2.5">Entity</th>
                <th className="p-2.5">Description</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#171e2c] text-slate-300">
              {chTelemetry?.recent_stream?.map((ev, idx) => (
                <tr key={idx} className="hover:bg-[#151b29] transition-colors">
                  <td className="p-2.5 text-slate-500 whitespace-nowrap">
                    {ev.timestamp ? new Date(ev.timestamp).toLocaleTimeString() : 'Recent'}
                  </td>
                  <td className="p-2.5">
                    <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/30 text-[10px] font-bold">
                      {ev.event_type}
                    </span>
                  </td>
                  <td className="p-2.5 text-slate-400 font-medium">
                    {ev.actor || 'System'}
                  </td>
                  <td className="p-2.5 text-white font-semibold">
                    {ev.character || ev.prop || (ev.scene_number ? `Scene #${ev.scene_number}` : 'Project')}
                  </td>
                  <td className="p-2.5 text-slate-300 max-w-md truncate">
                    {ev.description || '-'}
                  </td>
                </tr>
              ))}
              {(!chTelemetry?.recent_stream || chTelemetry.recent_stream.length === 0) && (
                <tr>
                  <td colSpan={5} className="p-6 text-center text-slate-500">
                    No stream events recorded yet. Run a continuity check to populate telemetry.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

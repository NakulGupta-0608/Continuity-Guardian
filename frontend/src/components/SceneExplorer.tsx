import React, { useState } from 'react';
import { 
  Film, 
  Clock, 
  CloudRain, 
  MapPin, 
  Users, 
  Package, 
  AlertTriangle, 
  ChevronRight,
  Sparkles,
  FileText,
  Eye
} from 'lucide-react';
import { Scene } from '../types';

interface SceneExplorerProps {
  scenes: Scene[];
  selectedSceneId?: string;
}

export const SceneExplorer: React.FC<SceneExplorerProps> = ({
  scenes,
  selectedSceneId
}) => {
  const [activeSceneId, setActiveSceneId] = useState<string>(selectedSceneId || (scenes[0]?.id || 'scene_01'));
  const activeScene = scenes.find((s) => s.id === activeSceneId) || scenes[0];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
      
      {/* Left 4 Cols: Scene List Timeline */}
      <div className="lg:col-span-4 space-y-2">
        <div className="bg-[#121622] border border-[#20283b] rounded-xl p-4 shadow-md">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Film className="w-4 h-4 text-amber-400" />
              Scene Sequence Timeline ({scenes.length})
            </h2>
            <span className="text-[10px] text-slate-400 font-mono">11:58 PM - 1:30 AM</span>
          </div>

          <div className="space-y-1.5 max-h-[700px] overflow-y-auto pr-1">
            {scenes.map((scene) => {
              const isSelected = activeScene?.id === scene.id;
              const hasIssues = scene.issues && scene.issues.length > 0;
              const openIssues = scene.issues?.filter(i => i.status === 'OPEN') || [];

              return (
                <button
                  key={scene.id}
                  onClick={() => setActiveSceneId(scene.id)}
                  className={`w-full text-left p-2.5 rounded-lg border transition-all cursor-pointer flex items-center justify-between gap-2 ${
                    isSelected
                      ? 'bg-[#1c2333] border-amber-500/60 text-white shadow-md'
                      : 'bg-[#0a0d14] border-[#1a2130] text-slate-300 hover:bg-[#121724]'
                  }`}
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <span className="font-mono text-xs font-black text-amber-400 shrink-0">
                      #{scene.scene_number.toString().padStart(2, '0')}
                    </span>
                    <div className="truncate">
                      <div className="text-xs font-semibold truncate text-white">{scene.title}</div>
                      <div className="text-[10px] text-slate-400 flex items-center gap-2">
                        <span>{scene.location_name}</span>
                        <span>•</span>
                        <span>{scene.time_of_day}</span>
                      </div>
                    </div>
                  </div>

                  {openIssues.length > 0 && (
                    <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30 shrink-0">
                      {openIssues.length} {openIssues.length === 1 ? 'Error' : 'Errors'}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Right 8 Cols: Active Scene Detailed Slate */}
      <div className="lg:col-span-8">
        {activeScene ? (
          <div className="space-y-6">
            
            {/* Slate Header */}
            <div className="bg-[#121622] border border-[#20283b] rounded-xl p-6 shadow-xl relative overflow-hidden">
              <div className="clapper-stripes h-2 w-full absolute top-0 left-0 opacity-40" />
              
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mt-2">
                <div>
                  <div className="flex items-center gap-2 mb-1 text-xs">
                    <span className="font-mono text-amber-400 font-bold bg-amber-500/10 border border-amber-500/30 px-2 py-0.5 rounded">
                      SCENE {activeScene.scene_number.toString().padStart(2, '0')}
                    </span>
                    <span className="text-slate-400 font-semibold">{activeScene.location_name}</span>
                    {activeScene.is_flashback && (
                      <span className="bg-purple-500/20 text-purple-300 px-2 py-0.5 rounded text-[10px] font-bold uppercase">
                        Flashback
                      </span>
                    )}
                  </div>
                  <h1 className="text-xl sm:text-2xl font-black text-white uppercase tracking-wide">
                    {activeScene.title}
                  </h1>
                </div>

                <div className="flex flex-wrap items-center gap-2 text-xs">
                  <span className="flex items-center gap-1 bg-[#0a0d14] px-2.5 py-1 rounded border border-[#232b3d] text-slate-300">
                    <Clock className="w-3.5 h-3.5 text-amber-400" />
                    {activeScene.time_of_day}
                  </span>
                  <span className="flex items-center gap-1 bg-[#0a0d14] px-2.5 py-1 rounded border border-[#232b3d] text-slate-300">
                    <CloudRain className="w-3.5 h-3.5 text-sky-400" />
                    {activeScene.weather}
                  </span>
                </div>
              </div>

              {/* Scene Summary */}
              <p className="text-xs sm:text-sm text-slate-300 mt-4 leading-relaxed bg-[#0a0d14] p-3 rounded-lg border border-[#1d2535]">
                {activeScene.summary}
              </p>

              {/* Flagged Inconsistencies for this Scene */}
              {activeScene.issues && activeScene.issues.length > 0 && (
                <div className="mt-4 p-3 rounded-lg bg-rose-500/10 border border-rose-500/30">
                  <div className="flex items-center gap-1.5 text-xs font-bold text-rose-400 uppercase tracking-wider mb-2">
                    <AlertTriangle className="w-4 h-4" />
                    Continuity Flaws In This Scene ({activeScene.issues.length})
                  </div>
                  <div className="space-y-1.5">
                    {activeScene.issues.map((iss) => (
                      <div key={iss.id} className="text-xs text-slate-200 flex items-start gap-2">
                        <span className="font-bold text-rose-400 shrink-0">[{iss.severity}]</span>
                        <span>{iss.description}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Characters & Props State Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              
              {/* Characters Present in Scene */}
              <div className="bg-[#121622] border border-[#20283b] rounded-xl p-4 shadow-md">
                <h2 className="text-xs font-bold text-white uppercase tracking-wider mb-3 flex items-center gap-2">
                  <Users className="w-4 h-4 text-violet-400" />
                  Characters & Wardrobe ({activeScene.characters?.length || 0})
                </h2>
                <div className="space-y-2">
                  {activeScene.characters?.map((c) => (
                    <div key={c.character_id} className="p-2.5 rounded-lg bg-[#0a0d14] border border-[#1e2535] text-xs">
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-bold text-white text-sm">{c.name}</span>
                        <span className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase ${
                          c.condition.toLowerCase().includes('injured')
                            ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                            : 'bg-emerald-500/20 text-emerald-400'
                        }`}>
                          {c.condition}
                        </span>
                      </div>
                      <div className="text-[11px] text-slate-400 mb-1">
                        <strong className="text-slate-300">Wardrobe:</strong> {c.wardrobe || 'Standard costume'}
                      </div>
                      {c.dialogue && c.dialogue.length > 0 && (
                        <div className="text-[10px] italic text-slate-400 border-l-2 border-amber-400/40 pl-2 mt-1">
                          "{c.dialogue[0]}"
                        </div>
                      )}
                    </div>
                  ))}
                  {(!activeScene.characters || activeScene.characters.length === 0) && (
                    <div className="text-xs text-slate-500 py-3 text-center">No characters registered in this scene</div>
                  )}
                </div>
              </div>

              {/* Props Present in Scene */}
              <div className="bg-[#121622] border border-[#20283b] rounded-xl p-4 shadow-md">
                <h2 className="text-xs font-bold text-white uppercase tracking-wider mb-3 flex items-center gap-2">
                  <Package className="w-4 h-4 text-amber-400" />
                  Props & Custody ({activeScene.props?.length || 0})
                </h2>
                <div className="space-y-2">
                  {activeScene.props?.map((p) => (
                    <div key={p.prop_id} className="p-2.5 rounded-lg bg-[#0a0d14] border border-[#1e2535] text-xs">
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-bold text-amber-300">{p.name}</span>
                        <span className="text-[10px] text-slate-400 font-mono">
                          {p.holder ? `Held by: ${p.holder}` : 'Unheld'}
                        </span>
                      </div>
                      <div className="text-[11px] text-slate-300">
                        <strong className="text-slate-400">Position:</strong> {p.location}
                      </div>
                      {p.state_description && (
                        <div className="text-[10px] text-slate-400 mt-0.5">
                          {p.state_description}
                        </div>
                      )}
                    </div>
                  ))}
                  {(!activeScene.props || activeScene.props.length === 0) && (
                    <div className="text-xs text-slate-500 py-3 text-center">No hero props tracked in this scene</div>
                  )}
                </div>
              </div>

            </div>

            {/* Screenplay Content Drawer */}
            <div className="bg-[#121622] border border-[#20283b] rounded-xl p-4 shadow-md">
              <h2 className="text-xs font-bold text-white uppercase tracking-wider mb-2 flex items-center gap-2">
                <FileText className="w-4 h-4 text-slate-400" />
                Script Excerpt
              </h2>
              <pre className="p-4 rounded-lg bg-[#07090e] border border-[#181f2c] text-xs font-mono text-slate-300 whitespace-pre-wrap leading-relaxed overflow-x-auto max-h-56">
                {activeScene.script_content || 'No script text entered.'}
              </pre>
            </div>

          </div>
        ) : (
          <div className="p-12 text-center text-slate-500">Select a scene to inspect state</div>
        )}
      </div>

    </div>
  );
};

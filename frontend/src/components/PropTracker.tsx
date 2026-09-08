import React, { useState } from 'react';
import { 
  Package, 
  MapPin, 
  User, 
  AlertTriangle, 
  ArrowRight, 
  CheckCircle2,
  Sparkles,
  ShieldAlert
} from 'lucide-react';
import { Prop } from '../types';

interface PropTrackerProps {
  propsList: Prop[];
}

export const PropTracker: React.FC<PropTrackerProps> = ({ propsList }) => {
  const [selectedPropId, setSelectedPropId] = useState<string>(propsList[0]?.id || 'prop_red_notebook');
  const selectedProp = propsList.find((p) => p.id === selectedPropId) || propsList[0];

  return (
    <div className="space-y-6">
      {/* Header & Prop Selector */}
      <div className="bg-[#121622] border border-[#20283b] rounded-xl p-5 shadow-lg">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
          <div>
            <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Package className="w-4 h-4 text-amber-400" />
              Hero Prop Custody & Movement Tracker
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Physical custody tracking and missing retrieval detection across camera units.
            </p>
          </div>
          <span className="text-xs text-slate-400">Total Hero Props: <strong className="text-white">{propsList.length}</strong></span>
        </div>

        {/* Prop Buttons */}
        <div className="flex flex-wrap gap-2 pt-2 border-t border-[#1d2433]">
          {propsList.map((prop) => {
            const isSelected = selectedProp?.id === prop.id;
            return (
              <button
                key={prop.id}
                onClick={() => setSelectedPropId(prop.id)}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer flex items-center gap-2 ${
                  isSelected
                    ? 'bg-amber-500 text-black shadow-md'
                    : 'bg-[#0a0d14] text-slate-300 border border-[#20283b] hover:bg-[#161c29]'
                }`}
              >
                <span>{prop.name}</span>
                <span className={`text-[10px] px-1.5 py-0.2 rounded font-normal ${isSelected ? 'bg-black/20 text-black' : 'bg-slate-800 text-slate-400'}`}>
                  {prop.category}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Selected Prop Card Slate */}
      {selectedProp && (
        <div className="bg-[#121622] border border-[#20283b] rounded-xl p-5 shadow-lg">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="text-[10px] font-mono uppercase text-amber-400 font-bold bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/30 inline-block mb-1">
                {selectedProp.category} PROP
              </div>
              <h1 className="text-xl font-black text-white">{selectedProp.name}</h1>
              <p className="text-xs text-slate-300 mt-1 max-w-2xl">{selectedProp.description}</p>
            </div>

            <div className="bg-[#0a0d14] p-3 rounded-lg border border-[#1e2535] text-xs">
              <div className="text-[10px] text-slate-500 uppercase font-bold">Latest Recorded Location</div>
              <div className="text-amber-300 font-mono font-bold mt-0.5">{selectedProp.current_location}</div>
            </div>
          </div>
        </div>
      )}

      {/* Prop Journey Timeline */}
      <div className="bg-[#121622] border border-[#20283b] rounded-xl p-6 shadow-xl">
        <h2 className="text-xs font-bold text-white uppercase tracking-wider mb-6 flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-amber-400" />
          Custody Trajectory Across Scenes ({selectedProp?.name})
        </h2>

        <div className="space-y-4">
          {selectedProp?.movements.map((move, idx) => {
            const prevMove = idx > 0 ? selectedProp.movements[idx - 1] : null;

            // Detect missing retrieval teleportation (e.g. Car -> Table without transition)
            const isTeleportation = prevMove && 
              prevMove.location.toLowerCase().includes('car') && 
              (move.location.toLowerCase().includes('café') || move.location.toLowerCase().includes('table')) &&
              !move.interaction_event?.toLowerCase().includes('retriev');

            return (
              <React.Fragment key={idx}>
                {/* Missing Transition Warning Alert between steps */}
                {isTeleportation && (
                  <div className="p-3.5 rounded-xl bg-rose-500/15 border-2 border-rose-500/50 shadow-lg shadow-rose-500/10 flex items-start gap-3 my-2">
                    <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
                    <div>
                      <div className="text-xs font-black text-rose-300 uppercase tracking-wide">
                        ⚠️ Missing Transition Detected: Teleportation Error
                      </div>
                      <div className="text-xs text-slate-200 mt-0.5">
                        Prop moved from: <strong className="text-white">'{prevMove.location}'</strong> → to: <strong className="text-white">'{move.location}'</strong>
                      </div>
                      <div className="text-xs text-amber-300 font-mono mt-1">
                        <b>Required Action:</b> Insert "Rahul retrieves {selectedProp.name} from car" before Scene #{move.scene_number}.
                      </div>
                    </div>
                  </div>
                )}

                {/* Move Step Card */}
                <div className={`p-4 rounded-xl border transition-all ${
                  isTeleportation
                    ? 'bg-[#1a1215] border-rose-500/40'
                    : 'bg-[#0a0d14] border-[#1d2535]'
                }`}>
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-black text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/30">
                        SCENE #{move.scene_number.toString().padStart(2, '0')}
                      </span>
                      <span className="text-xs font-bold text-white">{move.scene_title}</span>
                    </div>

                    <span className="text-[11px] font-mono text-slate-400">
                      Holder: <strong className="text-slate-200">{move.holder || 'None / Static'}</strong>
                    </span>
                  </div>

                  <div className="text-xs text-slate-300 mt-2 flex items-center gap-2">
                    <MapPin className="w-3.5 h-3.5 text-amber-400" />
                    <span className="text-slate-400">Location:</span>
                    <span className="font-mono font-bold text-white">{move.location}</span>
                  </div>

                  {move.state_description && (
                    <div className="text-xs text-slate-400 mt-1 pl-5">
                      {move.state_description}
                    </div>
                  )}
                </div>
              </React.Fragment>
            );
          })}

          {(!selectedProp?.movements || selectedProp.movements.length === 0) && (
            <div className="text-center py-8 text-slate-500 text-xs">
              No recorded scene appearances for this prop.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

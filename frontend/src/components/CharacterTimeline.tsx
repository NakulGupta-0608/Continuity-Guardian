import React, { useState } from 'react';
import { 
  Users, 
  AlertTriangle, 
  MapPin, 
  ShieldCheck, 
  HeartPulse, 
  Shirt, 
  ArrowDown,
  Sparkles,
  Info
} from 'lucide-react';
import { Character } from '../types';

interface CharacterTimelineProps {
  characters: Character[];
}

export const CharacterTimeline: React.FC<CharacterTimelineProps> = ({ characters }) => {
  const [selectedCharId, setSelectedCharId] = useState<string>(characters[0]?.id || 'char_rahul');
  const selectedChar = characters.find((c) => c.id === selectedCharId) || characters[0];

  return (
    <div className="space-y-6">
      {/* Header & Character Selection Tabs */}
      <div className="bg-[#121622] border border-[#20283b] rounded-xl p-5 shadow-lg">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
          <div>
            <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Users className="w-4 h-4 text-violet-400" />
              Character Continuity Timeline
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Multi-scene state journey tracking wardrobe, physical conditions, injuries, and location transitions.
            </p>
          </div>

          <div className="text-xs text-slate-400">
            Select character to inspect chronological state transitions:
          </div>
        </div>

        {/* Character Selector Buttons */}
        <div className="flex flex-wrap gap-2 pt-2 border-t border-[#1d2433]">
          {characters.map((char) => {
            const isSelected = selectedChar?.id === char.id;
            return (
              <button
                key={char.id}
                onClick={() => setSelectedCharId(char.id)}
                className={`px-4 py-2 rounded-lg text-xs font-bold transition-all cursor-pointer flex items-center gap-2 ${
                  isSelected
                    ? 'bg-gradient-to-r from-amber-500 to-amber-600 text-black shadow-md'
                    : 'bg-[#0a0d14] text-slate-300 border border-[#20283b] hover:bg-[#161c29]'
                }`}
              >
                <span>{char.name}</span>
                <span className={`text-[10px] px-1.5 py-0.2 rounded font-normal ${isSelected ? 'bg-black/20 text-black' : 'bg-slate-800 text-slate-400'}`}>
                  {char.role}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Selected Character Profile Slate */}
      {selectedChar && (
        <div className="bg-[#121622] border border-[#20283b] rounded-xl p-5 shadow-lg">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs">
            <div className="p-3 rounded-lg bg-[#0a0d14] border border-[#1e2535]">
              <div className="text-[10px] text-slate-500 uppercase tracking-wider font-bold mb-1">Standard Wardrobe</div>
              <div className="text-white font-medium">{selectedChar.default_wardrobe || 'Standard Production Attire'}</div>
            </div>
            <div className="p-3 rounded-lg bg-[#0a0d14] border border-[#1e2535]">
              <div className="text-[10px] text-slate-500 uppercase tracking-wider font-bold mb-1">Baseline Condition</div>
              <div className="text-emerald-400 font-medium">{selectedChar.default_condition}</div>
            </div>
            <div className="p-3 rounded-lg bg-[#0a0d14] border border-[#1e2535]">
              <div className="text-[10px] text-slate-500 uppercase tracking-wider font-bold mb-1">Current Filming Location</div>
              <div className="text-amber-300 font-medium">{selectedChar.current_location}</div>
            </div>
            <div className="p-3 rounded-lg bg-[#0a0d14] border border-[#1e2535]">
              <div className="text-[10px] text-slate-500 uppercase tracking-wider font-bold mb-1">Known Narrative Facts</div>
              <div className="text-slate-300">{selectedChar.known_facts?.length || 0} registered plot facts</div>
            </div>
          </div>
        </div>
      )}

      {/* Visual State Journey (Vertical Timeline with Inconsistency Highlights) */}
      <div className="bg-[#121622] border border-[#20283b] rounded-xl p-6 shadow-xl">
        <h2 className="text-xs font-bold text-white uppercase tracking-wider mb-6 flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-amber-400" />
          Chronological Scene-by-Scene Trajectory ({selectedChar?.name})
        </h2>

        <div className="relative pl-6 sm:pl-8 space-y-6 before:absolute before:left-3 sm:before:left-4 before:top-3 before:bottom-3 before:w-0.5 before:bg-[#252f44]">
          {selectedChar?.timeline.map((step, idx) => {
            const prevStep = idx > 0 ? selectedChar.timeline[idx - 1] : null;
            
            // Detect Wardrobe anomaly
            const isWardrobeSwap = prevStep && step.wardrobe && prevStep.wardrobe && 
              step.wardrobe.toLowerCase().includes('red jacket') && prevStep.wardrobe.toLowerCase().includes('black');

            // Detect Injury healing anomaly
            const isSpontaneousHealing = prevStep && 
              prevStep.condition.toLowerCase().includes('injured') && step.condition.toLowerCase().includes('healthy');

            const hasConflict = isWardrobeSwap || isSpontaneousHealing;

            return (
              <div key={idx} className="relative group">
                {/* Timeline Dot */}
                <div className={`absolute -left-[27px] sm:-left-[35px] top-4 w-4 h-4 rounded-full border-2 transition-transform group-hover:scale-125 ${
                  hasConflict
                    ? 'bg-rose-500 border-rose-300 animate-pulse'
                    : 'bg-amber-500 border-amber-300'
                }`} />

                {/* Step Card */}
                <div className={`p-4 rounded-xl border transition-all ${
                  hasConflict
                    ? 'bg-[#181119] border-rose-500/50 shadow-lg shadow-rose-500/10'
                    : 'bg-[#0a0d14] border-[#1d2535] hover:border-[#2a364d]'
                }`}>
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-black text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/30">
                        SCENE #{step.scene_number.toString().padStart(2, '0')}
                      </span>
                      <span className="text-xs font-bold text-white">{step.scene_title}</span>
                    </div>
                    <div className="flex items-center gap-2 text-[11px] text-slate-400">
                      <span className="flex items-center gap-1">
                        <MapPin className="w-3 h-3 text-slate-400" />
                        {step.location}
                      </span>
                      <span>•</span>
                      <span>{step.time_of_day}</span>
                    </div>
                  </div>

                  {/* Attributes Grid */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs mt-3">
                    <div className={`p-2.5 rounded-lg border ${
                      isWardrobeSwap ? 'bg-rose-500/10 border-rose-500/40' : 'bg-[#121622] border-[#1c2333]'
                    }`}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[10px] text-slate-400 uppercase font-bold flex items-center gap-1">
                          <Shirt className="w-3 h-3" /> Wardrobe
                        </span>
                        {isWardrobeSwap && (
                          <span className="text-[9px] font-bold text-rose-400 uppercase bg-rose-500/20 px-1.5 py-0.2 rounded">
                            Wardrobe Swapped!
                          </span>
                        )}
                      </div>
                      <div className={`font-mono text-xs ${isWardrobeSwap ? 'text-rose-300 font-bold' : 'text-slate-200'}`}>
                        {step.wardrobe || 'Standard Costume'}
                      </div>
                    </div>

                    <div className={`p-2.5 rounded-lg border ${
                      isSpontaneousHealing ? 'bg-rose-500/10 border-rose-500/40' : 'bg-[#121622] border-[#1c2333]'
                    }`}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[10px] text-slate-400 uppercase font-bold flex items-center gap-1">
                          <HeartPulse className="w-3 h-3" /> Physical Condition
                        </span>
                        {isSpontaneousHealing && (
                          <span className="text-[9px] font-bold text-rose-400 uppercase bg-rose-500/20 px-1.5 py-0.2 rounded">
                            Sudden Healing!
                          </span>
                        )}
                      </div>
                      <div className={`font-mono text-xs ${isSpontaneousHealing ? 'text-rose-300 font-bold' : 'text-slate-200'}`}>
                        {step.condition}
                      </div>
                    </div>
                  </div>

                  {/* Warning banner on card */}
                  {hasConflict && (
                    <div className="mt-3 p-2 rounded bg-rose-500/20 border border-rose-500/30 flex items-center gap-2 text-xs text-rose-300">
                      <AlertTriangle className="w-4 h-4 shrink-0" />
                      <span>
                        {isWardrobeSwap && "Continuity Alert: Costume abruptly changed with no wardrobe transition event."}
                        {isSpontaneousHealing && "Continuity Alert: Arm injury disappeared without medical care or stitches."}
                      </span>
                    </div>
                  )}

                  {/* Dialogue Snippet */}
                  {step.dialogue && step.dialogue.length > 0 && (
                    <div className="mt-3 text-[11px] text-slate-400 italic border-l-2 border-slate-700 pl-2">
                      "{step.dialogue[0]}"
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

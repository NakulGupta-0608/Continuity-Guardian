import React, { useState } from 'react';
import { 
  X, 
  Upload, 
  FileText, 
  CheckCircle2, 
  AlertCircle,
  PlusCircle,
  Film,
  Sparkles
} from 'lucide-react';
import { api } from '../services/api';

interface ScriptUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  projectId: string;
  onSuccess: (newProjectId?: string) => void;
}

export const ScriptUploadModal: React.FC<ScriptUploadModalProps> = ({
  isOpen,
  onClose,
  projectId,
  onSuccess
}) => {
  const [scriptText, setScriptText] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [mode, setMode] = useState<'new_project' | 'replace' | 'append'>('new_project');
  const [projectTitle, setProjectTitle] = useState('');
  const [genre, setGenre] = useState('Thriller');
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [resultMessage, setResultMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const loadPreset = (type: 'screenplay' | 'structured') => {
    if (type === 'screenplay') {
      setScriptText(
`INT. COFFEE SHOP - DAY
SARAH sits near the window wearing a bright RED DRESS. She checks her phone anxiously.
MARK enters wearing a dark blue suit, holding a leather briefcase.

SARAH
Did anyone follow you?

MARK
No. We have twenty minutes before the train leaves.

EXT. COFFEE SHOP - CONTINUOUS
SARAH rushes out into the street. She is now wearing a GREEN HOODIE. Mark follows her into the alleyway.

MARK
Wait! You left the briefcase on the table!`
      );
      if (!projectTitle) setProjectTitle('The Downtown Handover');
    } else {
      setScriptText(
`Scene 1
Location: Warehouse
Time: 8:00 PM
Weather: Rain
Characters: Alex, Maya
Alex clothing: Black leather jacket
Alex condition: Healthy
Props: Red notebook, Flashlight
Events: Alex hides the red notebook inside the steel locker.

Scene 2
Location: Warehouse
Time: 8:15 PM
Weather: Rain
Characters: Alex, Maya
Alex clothing: White t-shirt
Alex condition: Healthy
Props: Red notebook
Events: Alex pulls the red notebook from his jacket pocket.`
      );
      if (!projectTitle) setProjectTitle('Shadows in Sector 4');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!scriptText.trim() && !file) {
      setError('Please provide script text or upload a screenplay file.');
      return;
    }

    if (mode === 'new_project' && !projectTitle.trim()) {
      setError('Please provide a Project Title for your new movie.');
      return;
    }

    setIsSubmitting(true);
    setError(null);
    try {
      const res = await api.uploadScript(projectId, scriptText, file || undefined, {
        mode,
        project_title: projectTitle,
        genre
      });

      const flawsFound = res.continuity_analysis?.issues_detected_in_run || 0;
      setResultMessage(
        `✓ Success! Ingested ${res.scenes_imported} scenes, created ${res.characters_created} characters. Continuity scan detected ${flawsFound} flaws.`
      );

      setTimeout(() => {
        onSuccess(res.project_id);
        onClose();
      }, 1500);
    } catch (err: any) {
      setError(err.message || 'Failed to parse script.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-[#121622] border border-[#20283b] rounded-xl max-w-2xl w-full p-6 shadow-2xl relative my-8">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white transition-colors cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Title */}
        <div className="flex items-center gap-2 mb-4">
          <div className="p-2 rounded-lg bg-amber-500/20 text-amber-400 border border-amber-500/30">
            <Upload className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white uppercase tracking-wide">
              Upload Your Own Movie Script / Scenes
            </h2>
            <p className="text-xs text-slate-400">
              Continuity Guardian automatically extracts scenes, characters, wardrobe, props, and runs continuity checks
            </p>
          </div>
        </div>

        {/* Alerts */}
        {error && (
          <div className="p-3 mb-4 rounded-lg bg-rose-500/20 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {resultMessage && (
          <div className="p-3 mb-4 rounded-lg bg-emerald-500/20 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            <span>{resultMessage}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          
          {/* Ingestion Mode Selector */}
          <div>
            <label className="block text-xs font-bold text-slate-300 uppercase mb-1.5">
              Ingestion Mode:
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs">
              {[
                { id: 'new_project', label: 'Create New Movie Project', desc: 'Fresh workspace for your script' },
                { id: 'replace', label: 'Replace Current Scenes', desc: 'Clear demo scenes and load yours' },
                { id: 'append', label: 'Append to Current Movie', desc: 'Add scenes to active project' },
              ].map((m) => (
                <button
                  key={m.id}
                  type="button"
                  onClick={() => setMode(m.id as any)}
                  className={`p-3 rounded-lg border text-left transition-all cursor-pointer ${
                    mode === m.id
                      ? 'bg-amber-500/15 border-amber-400 text-white shadow-md'
                      : 'bg-[#0a0d14] border-[#222a3d] text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <div className="font-bold text-xs text-white">{m.label}</div>
                  <div className="text-[10px] text-slate-400 mt-0.5">{m.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* New Project Fields if mode == 'new_project' */}
          {mode === 'new_project' && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 p-3 rounded-lg bg-[#0a0d14] border border-[#232b3d]">
              <div>
                <label className="block text-[11px] font-bold text-slate-300 uppercase mb-1">
                  Movie / Project Name:
                </label>
                <input
                  type="text"
                  placeholder="e.g. Echoes of Platform 9"
                  value={projectTitle}
                  onChange={(e) => setProjectTitle(e.target.value)}
                  className="w-full bg-[#121622] border border-[#263147] rounded-md px-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-400"
                />
              </div>
              <div>
                <label className="block text-[11px] font-bold text-slate-300 uppercase mb-1">
                  Genre:
                </label>
                <select
                  value={genre}
                  onChange={(e) => setGenre(e.target.value)}
                  className="w-full bg-[#121622] border border-[#263147] rounded-md px-3 py-1.5 text-xs text-white focus:outline-none focus:border-amber-400"
                >
                  <option value="Neo-Noir / Thriller">Neo-Noir / Thriller</option>
                  <option value="Sci-Fi Mystery">Sci-Fi Mystery</option>
                  <option value="Drama">Drama</option>
                  <option value="Crime / Heist">Crime / Heist</option>
                  <option value="Horror">Horror</option>
                  <option value="Action">Action</option>
                </select>
              </div>
            </div>
          )}

          {/* Script Text Input & Preset Buttons */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="block text-xs font-bold text-slate-300 uppercase">
                Paste Screenplay or Structured Scenes:
              </label>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => loadPreset('screenplay')}
                  className="text-[10px] text-amber-400 hover:text-amber-300 underline font-semibold cursor-pointer"
                >
                  Load Screenplay Example
                </button>
                <span className="text-slate-600">|</span>
                <button
                  type="button"
                  onClick={() => loadPreset('structured')}
                  className="text-[10px] text-amber-400 hover:text-amber-300 underline font-semibold cursor-pointer"
                >
                  Load Structured Example
                </button>
              </div>
            </div>

            <textarea
              rows={8}
              value={scriptText}
              onChange={(e) => setScriptText(e.target.value)}
              placeholder={`Supports any format!
Examples:

Option A (Screenplay):
INT. COFFEE SHOP - DAY
SARAH wears a red dress. MARK sits with a leather briefcase...

Option B (Structured):
Scene 1
Location: Café
Time: 8:00 PM
Characters: Rahul, Priya
Rahul clothing: Black jacket
Props: Red notebook

Scene 2
Location: Café
Rahul clothing: Red jacket (Engine flags wardrobe error!)`}
              className="w-full bg-[#0a0d14] border border-[#232b3d] rounded-lg p-3 text-xs font-mono text-slate-200 placeholder-slate-600 focus:outline-none focus:border-amber-400 leading-relaxed"
            />
          </div>

          {/* File Upload Alternative */}
          <div>
            <label className="block text-xs font-bold text-slate-300 uppercase mb-1">
              Or Upload Screenplay File (.txt, .fountain, .pdf):
            </label>
            <input
              type="file"
              accept=".txt,.fountain,.pdf,.md"
              onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)}
              className="text-xs text-slate-400 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-slate-800 file:text-amber-300 hover:file:bg-slate-700 cursor-pointer"
            />
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end gap-3 pt-3 border-t border-[#1d2535]">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-semibold text-slate-400 hover:text-white cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-5 py-2 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-black text-xs font-bold rounded-lg shadow-lg shadow-amber-500/20 transition-all cursor-pointer disabled:opacity-50"
            >
              {isSubmitting ? 'Parsing & Checking Continuity...' : 'Parse & Run Continuity Check'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

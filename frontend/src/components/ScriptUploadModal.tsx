import React, { useState } from 'react';
import { X, Upload, FileText, CheckCircle2, AlertCircle } from 'lucide-react';
import { api } from '../services/api';

interface ScriptUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  projectId: string;
  onSuccess: () => void;
}

export const ScriptUploadModal: React.FC<ScriptUploadModalProps> = ({
  isOpen,
  onClose,
  projectId,
  onSuccess
}) => {
  const [scriptText, setScriptText] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [resultMessage, setResultMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!scriptText.trim() && !file) {
      setError('Please provide screenplay text or upload a screenplay file.');
      return;
    }

    setIsSubmitting(true);
    setError(null);
    try {
      const res = await api.uploadScript(projectId, scriptText, file || undefined);
      setResultMessage(`Successfully imported ${res.scenes_imported} scenes into project!`);
      setTimeout(() => {
        onSuccess();
        onClose();
      }, 1500);
    } catch (err: any) {
      setError(err.message || 'Failed to ingest script');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-[#121622] border border-[#20283b] rounded-xl max-w-xl w-full p-6 shadow-2xl relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2 mb-3">
          <div className="p-2 rounded-lg bg-amber-500/20 text-amber-400">
            <Upload className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white uppercase tracking-wide">
              Ingest Screenplay / Production Scene
            </h2>
            <p className="text-xs text-slate-400">Upload standard Fountain or screenplay text for automated continuity parsing</p>
          </div>
        </div>

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
          <div>
            <label className="block text-xs font-bold text-slate-300 uppercase mb-1">
              Screenplay Excerpt (Standard Sluglines):
            </label>
            <textarea
              rows={6}
              value={scriptText}
              onChange={(e) => setScriptText(e.target.value)}
              placeholder={`INT. STATION CAFÉ - NIGHT\nRAHUL sits at the corner booth wearing his black leather jacket.\n\nPRIYA walks in, holding the red notebook...`}
              className="w-full bg-[#0a0d14] border border-[#232b3d] rounded-lg p-3 text-xs font-mono text-slate-200 placeholder-slate-600 focus:outline-none focus:border-amber-400"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-300 uppercase mb-1">
              Or Upload Screenplay (.txt, .fountain):
            </label>
            <input
              type="file"
              accept=".txt,.fountain,.pdf"
              onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)}
              className="text-xs text-slate-400 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-slate-800 file:text-amber-300 hover:file:bg-slate-700"
            />
          </div>

          <div className="flex justify-end gap-3 pt-3 border-t border-[#1d2535]">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-semibold text-slate-400 hover:text-white"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 bg-amber-500 hover:bg-amber-400 disabled:opacity-40 text-black text-xs font-bold rounded-lg transition-colors cursor-pointer"
            >
              {isSubmitting ? 'Ingesting & Analyzing...' : 'Parse & Run Continuity Check'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

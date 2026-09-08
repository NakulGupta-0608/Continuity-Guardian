import React, { useEffect, useState } from 'react';
import { 
  Header 
} from './components/Header';
import { 
  DashboardOverview 
} from './components/DashboardOverview';
import { 
  IssuesDashboard 
} from './components/IssuesDashboard';
import { 
  SceneExplorer 
} from './components/SceneExplorer';
import { 
  CharacterTimeline 
} from './components/CharacterTimeline';
import { 
  PropTracker 
} from './components/PropTracker';
import { 
  AnalyticsView 
} from './components/AnalyticsView';
import { 
  AIAssistantDrawer 
} from './components/AIAssistantDrawer';
import { 
  ScriptUploadModal 
} from './components/ScriptUploadModal';
import { api } from './services/api';
import { 
  Project, 
  Scene, 
  Character, 
  Prop, 
  ContinuityIssue, 
  SuggestedFix 
} from './types';
import { 
  AlertCircle, 
  CheckCircle2, 
  Upload, 
  Sparkles,
  Bot
} from 'lucide-react';

export const App: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [currentProject, setCurrentProject] = useState<Project | null>(null);
  const [scenes, setScenes] = useState<Scene[]>([]);
  const [characters, setCharacters] = useState<Character[]>([]);
  const [propsList, setPropsList] = useState<Prop[]>([]);
  const [issues, setIssues] = useState<ContinuityIssue[]>([]);
  
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [isAssistantOpen, setIsAssistantOpen] = useState<boolean>(false);
  const [isScriptModalOpen, setIsScriptModalOpen] = useState<boolean>(false);
  const [isChecking, setIsChecking] = useState<boolean>(false);
  const [resolvingId, setResolvingId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [selectedSceneId, setSelectedSceneId] = useState<string | undefined>(undefined);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 4000);
  };

  // Initial Load: Fetch Projects
  useEffect(() => {
    const init = async () => {
      try {
        const projs = await api.getProjects();
        setProjects(projs);
        if (projs.length > 0) {
          setCurrentProject(projs[0]);
        }
      } catch (err) {
        console.error('Failed to load projects:', err);
      }
    };
    init();
  }, []);

  // Load project-specific data
  const loadProjectData = async (projectId: string) => {
    try {
      const [proj, scs, chars, prps, iss] = await Promise.all([
        api.getProject(projectId),
        api.getScenes(projectId),
        api.getCharacters(projectId),
        api.getProps(projectId),
        api.getIssues(projectId)
      ]);
      setCurrentProject(proj);
      setScenes(scs);
      setCharacters(chars);
      setPropsList(prps);
      setIssues(iss);
    } catch (err) {
      console.error('Failed to load project details:', err);
    }
  };

  useEffect(() => {
    if (currentProject?.id) {
      loadProjectData(currentProject.id);
    }
  }, [currentProject?.id]);

  // Handle Run Continuity Check
  const handleRunContinuityCheck = async () => {
    if (!currentProject?.id || isChecking) return;
    setIsChecking(true);
    showToast("Analyzing movie state across 8 dimensions...");

    try {
      const res = await api.runContinuityCheck(currentProject.id);
      await loadProjectData(currentProject.id);
      showToast(`✓ Continuity scan complete. ${res.total_open_issues || 6} issues registered. Health: ${res.health_score}%`);
    } catch (err: any) {
      showToast(`⚠️ Error running check: ${err.message}`);
    } finally {
      setIsChecking(false);
    }
  };

  // Handle Resolving an Issue
  const handleResolveIssue = async (issueId: string, fix: SuggestedFix) => {
    if (!currentProject?.id) return;
    setResolvingId(issueId);
    try {
      const res = await api.resolveIssue(issueId, fix.title, fix.patch);
      await loadProjectData(currentProject.id);
      showToast(`✓ Issue resolved: ${fix.title}. Health score recalculated to ${res.new_health_score}%!`);
    } catch (err: any) {
      showToast(`⚠️ Error resolving issue: ${err.message}`);
    } finally {
      setResolvingId(null);
    }
  };

  const handleSelectSceneFromDashboard = (sceneId: string) => {
    setSelectedSceneId(sceneId);
    setActiveTab('scenes');
  };

  const handleOpenIssueFromDashboard = (issueId: string) => {
    setActiveTab('issues');
  };

  // Filter items if search query is provided
  const filteredScenes = scenes.filter(s => 
    !searchQuery || 
    s.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    s.summary.toLowerCase().includes(searchQuery.toLowerCase()) ||
    s.location_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredIssues = issues.filter(i =>
    !searchQuery ||
    i.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
    i.entity_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    i.issue_type.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-[#0a0c10] text-slate-100 flex flex-col selection:bg-amber-500 selection:text-black">
      
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed top-20 right-6 z-50 bg-[#151b29] border border-amber-500/50 text-amber-200 px-4 py-3 rounded-xl shadow-2xl flex items-center gap-2.5 text-xs font-semibold animate-in fade-in slide-in-from-top-4 duration-300">
          <Sparkles className="w-4 h-4 text-amber-400 shrink-0" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Global Header */}
      <Header
        currentProject={currentProject}
        projects={projects}
        onSelectProject={(id) => {
          const p = projects.find(x => x.id === id);
          if (p) setCurrentProject(p);
        }}
        onRunCheck={handleRunContinuityCheck}
        isChecking={isChecking}
        onOpenAssistant={() => setIsAssistantOpen(true)}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        
        {/* Secondary Bar with Script Upload Button */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <span>Project: <strong className="text-white">{currentProject?.title}</strong></span>
            <span>•</span>
            <span className="font-mono text-amber-400">{scenes.length} Scenes Filmed</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsScriptModalOpen(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#141926] hover:bg-[#1a2133] text-slate-200 border border-[#232d42] text-xs font-semibold transition-all cursor-pointer"
            >
              <Upload className="w-3.5 h-3.5 text-amber-400" />
              <span>Ingest Scene / Script</span>
            </button>
          </div>
        </div>

        {/* View Switcher */}
        {activeTab === 'dashboard' && (
          <DashboardOverview
            project={currentProject}
            scenes={scenes}
            issues={issues}
            onNavigateTab={setActiveTab}
            onSelectScene={handleSelectSceneFromDashboard}
            onOpenIssue={handleOpenIssueFromDashboard}
          />
        )}

        {activeTab === 'issues' && (
          <IssuesDashboard
            issues={filteredIssues}
            onResolveIssue={handleResolveIssue}
            resolvingId={resolvingId}
          />
        )}

        {activeTab === 'scenes' && (
          <SceneExplorer
            scenes={filteredScenes}
            selectedSceneId={selectedSceneId}
          />
        )}

        {activeTab === 'characters' && (
          <CharacterTimeline
            characters={characters}
          />
        )}

        {activeTab === 'props' && (
          <PropTracker
            propsList={propsList}
          />
        )}

        {activeTab === 'analytics' && currentProject && (
          <AnalyticsView
            projectId={currentProject.id}
          />
        )}

      </main>

      {/* Floating Assistant Trigger on Mobile / Bottom Right */}
      <button
        onClick={() => setIsAssistantOpen(true)}
        className="fixed bottom-6 right-6 p-3.5 rounded-full bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-black shadow-2xl shadow-amber-500/30 border border-amber-300 z-30 transition-transform active:scale-90 cursor-pointer flex items-center gap-2 font-bold text-xs"
      >
        <Bot className="w-5 h-5" />
        <span className="hidden sm:inline">Ask AI Copilot</span>
      </button>

      {/* AI Assistant Drawer */}
      <AIAssistantDrawer
        isOpen={isAssistantOpen}
        onClose={() => setIsAssistantOpen(false)}
        projectId={currentProject?.id || 'proj_midnight_7'}
        onStateModified={() => {
          if (currentProject?.id) loadProjectData(currentProject.id);
        }}
      />

      {/* Script Ingestion Modal */}
      <ScriptUploadModal
        isOpen={isScriptModalOpen}
        onClose={() => setIsScriptModalOpen(false)}
        projectId={currentProject?.id || 'proj_midnight_7'}
        onSuccess={() => {
          if (currentProject?.id) loadProjectData(currentProject.id);
          showToast("New script scene parsed and added to movie state!");
        }}
      />

      {/* Footer */}
      <footer className="border-t border-[#181e2b] py-6 text-center text-xs text-slate-500 bg-[#07090e]">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <div className="font-mono text-slate-400">
            Continuity Guardian © 2026 — <span className="text-amber-400 font-semibold">Your movie remembers. Your production doesn't have to.</span>
          </div>
          <div className="flex items-center gap-4 text-slate-500">
            <span>Powered by Google Gemini 2.5 & ClickHouse</span>
          </div>
        </div>
      </footer>

    </div>
  );
};

export default App;

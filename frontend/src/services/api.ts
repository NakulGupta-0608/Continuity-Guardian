import {
  Project,
  Scene,
  Character,
  Prop,
  ContinuityIssue,
  ProjectAnalytics
} from '../types';

const API_BASE = '/api';

export const api = {
  async getProjects(): Promise<Project[]> {
    const res = await fetch(`${API_BASE}/projects`);
    if (!res.ok) throw new Error('Failed to fetch projects');
    return res.json();
  },

  async getProject(id: string): Promise<Project> {
    const res = await fetch(`${API_BASE}/projects/${id}`);
    if (!res.ok) throw new Error('Failed to fetch project');
    return res.json();
  },

  async createProject(data: { title: string; genre?: string; description?: string; image_url?: string }): Promise<any> {
    const res = await fetch(`${API_BASE}/projects`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to create project');
    return res.json();
  },

  async getScenes(projectId: string): Promise<Scene[]> {
    const res = await fetch(`${API_BASE}/projects/${projectId}/scenes`);
    if (!res.ok) throw new Error('Failed to fetch scenes');
    return res.json();
  },

  async getCharacters(projectId: string): Promise<Character[]> {
    const res = await fetch(`${API_BASE}/projects/${projectId}/characters`);
    if (!res.ok) throw new Error('Failed to fetch characters');
    return res.json();
  },

  async getProps(projectId: string): Promise<Prop[]> {
    const res = await fetch(`${API_BASE}/projects/${projectId}/props`);
    if (!res.ok) throw new Error('Failed to fetch props');
    return res.json();
  },

  async getIssues(projectId: string, filters?: { severity?: string; issue_type?: string; status?: string }): Promise<ContinuityIssue[]> {
    const params = new URLSearchParams();
    if (filters?.severity && filters.severity !== 'ALL') params.append('severity', filters.severity);
    if (filters?.issue_type && filters.issue_type !== 'ALL') params.append('issue_type', filters.issue_type);
    if (filters?.status && filters.status !== 'ALL') params.append('status', filters.status);

    const url = `${API_BASE}/projects/${projectId}/issues${params.toString() ? '?' + params.toString() : ''}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch issues');
    return res.json();
  },

  async runContinuityCheck(projectId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/projects/${projectId}/continuity/check`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Failed to run continuity check');
    return res.json();
  },

  async resolveIssue(issueId: string, resolutionText?: string, patchData?: Record<string, any>): Promise<any> {
    const res = await fetch(`${API_BASE}/issues/${issueId}/resolve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        resolution_text: resolutionText || 'Resolved via Continuity Guardian UI',
        patch_data: patchData || {}
      })
    });
    if (!res.ok) throw new Error('Failed to resolve issue');
    return res.json();
  },

  async chatAgent(projectId: string, message: string): Promise<any> {
    const res = await fetch(`${API_BASE}/agent/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project_id: projectId, message })
    });
    if (!res.ok) throw new Error('Failed to talk to agent');
    return res.json();
  },

  async getAnalytics(projectId: string): Promise<ProjectAnalytics> {
    const res = await fetch(`${API_BASE}/projects/${projectId}/analytics`);
    if (!res.ok) throw new Error('Failed to fetch analytics');
    return res.json();
  },

  async uploadScript(projectId: string, scriptText: string, file?: File): Promise<any> {
    const formData = new FormData();
    if (file) {
      formData.append('file', file);
    } else {
      formData.append('script_text', scriptText);
    }
    const res = await fetch(`${API_BASE}/projects/${projectId}/upload-script`, {
      method: 'POST',
      body: formData
    });
    if (!res.ok) throw new Error('Failed to upload script');
    return res.json();
  }
};

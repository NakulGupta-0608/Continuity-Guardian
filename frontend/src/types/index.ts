export interface Project {
  id: string;
  title: string;
  genre: string;
  description: string;
  image_url: string;
  language: string;
  status: string;
  health_score: number;
  scenes_count?: number;
  characters_count?: number;
  props_count?: number;
  issues_count?: number;
  created_at?: string;
}

export interface CharacterAppearance {
  character_id: string;
  name: string;
  wardrobe: string;
  condition: string;
  location: string;
  known_facts?: string[];
  dialogue?: string[];
}

export interface PropAppearance {
  prop_id: string;
  name: string;
  location: string;
  holder: string;
  state_description: string;
  interaction_event?: string;
}

export interface IssueSummary {
  id: string;
  type: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  status: 'OPEN' | 'RESOLVED' | 'IGNORED';
  description: string;
}

export interface Scene {
  id: string;
  scene_number: number;
  title: string;
  location_name: string;
  time_of_day: string;
  weather: string;
  emotional_tone: string;
  summary: string;
  script_content: string;
  events: string[];
  dialogue_facts: string[];
  is_flashback: boolean;
  characters: CharacterAppearance[];
  props: PropAppearance[];
  issues: IssueSummary[];
}

export interface CharacterTimelineEntry {
  scene_number: number;
  scene_id: string;
  scene_title: string;
  time_of_day: string;
  location: string;
  wardrobe: string;
  condition: string;
  dialogue: string[];
}

export interface Character {
  id: string;
  name: string;
  role: string;
  age: string;
  appearance: string;
  default_wardrobe: string;
  default_condition: string;
  current_location: string;
  relationships: Record<string, string>;
  known_facts: string[];
  possessions: string[];
  timeline: CharacterTimelineEntry[];
}

export interface PropMovement {
  scene_number: number;
  scene_id: string;
  scene_title: string;
  location: string;
  holder: string;
  state_description: string;
  interaction_event?: string;
}

export interface Prop {
  id: string;
  name: string;
  description: string;
  category: string;
  current_location: string;
  current_holder: string;
  movements: PropMovement[];
}

export interface SuggestedFix {
  id: string;
  title: string;
  action: string;
  patch: Record<string, any>;
  description?: string;
}

export interface ContinuityIssue {
  id: string;
  project_id: string;
  scene_id?: string;
  issue_type: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  entity_type: string;
  entity_name: string;
  description: string;
  previous_state: string;
  current_state: string;
  suggested_fixes: SuggestedFix[];
  confidence: number;
  status: 'OPEN' | 'RESOLVED' | 'IGNORED';
  resolution_note?: string;
  resolved_at?: string;
  created_at?: string;
}

export interface ClickHouseEvent {
  project_id: string;
  scene_id: string;
  scene_number: number;
  character: string;
  prop: string;
  event_type: string;
  old_value: string;
  new_value: string;
  description: string;
  actor: string;
  metadata: string;
  timestamp: string;
}

export interface ProjectAnalytics {
  project_id: string;
  project_title: string;
  health_score: number;
  total_scenes: number;
  total_characters: number;
  total_props: number;
  total_issues: number;
  open_issues: number;
  resolved_issues: number;
  severity_distribution: Record<string, number>;
  category_distribution: Record<string, number>;
  status_distribution: Record<string, number>;
  scene_defect_density: Record<string, number>;
  problematic_characters: Record<string, number>;
  problematic_props: Record<string, number>;
  clickhouse_telemetry: {
    status: string;
    total_event_records: number;
    recent_stream: ClickHouseEvent[];
  };
}

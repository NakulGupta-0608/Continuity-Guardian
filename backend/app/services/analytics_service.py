import json
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from backend.app.database.models import Project, Scene, Character, Prop, ContinuityIssue, AuditEvent
from backend.app.database.clickhouse import clickhouse_manager

def get_project_analytics(project_id: str, db: Session) -> Dict[str, Any]:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return {"error": "Project not found"}

    scenes = db.query(Scene).filter(Scene.project_id == project_id).all()
    characters = db.query(Character).filter(Character.project_id == project_id).all()
    props = db.query(Prop).filter(Prop.project_id == project_id).all()
    issues = db.query(ContinuityIssue).filter(ContinuityIssue.project_id == project_id).all()

    # Breakdown by severity
    severity_dist = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    # Breakdown by category
    category_dist = {}
    # Breakdown by status
    status_dist = {"OPEN": 0, "RESOLVED": 0, "IGNORED": 0}
    # Breakdown by scene
    scene_defect_counts = {}
    # Breakdown by character
    char_defect_counts = {}
    # Breakdown by prop
    prop_defect_counts = {}

    for iss in issues:
        sev = iss.severity or "MEDIUM"
        severity_dist[sev] = severity_dist.get(sev, 0) + 1

        cat = iss.issue_type or "OTHER"
        category_dist[cat] = category_dist.get(cat, 0) + 1

        stat = iss.status or "OPEN"
        status_dist[stat] = status_dist.get(stat, 0) + 1

        sc_key = f"Scene {iss.scene_id.replace('scene_', '') if iss.scene_id else '?'}"
        scene_defect_counts[sc_key] = scene_defect_counts.get(sc_key, 0) + 1

        if iss.entity_type == "Character" and iss.entity_name:
            char_defect_counts[iss.entity_name] = char_defect_counts.get(iss.entity_name, 0) + 1
        elif iss.entity_type == "Prop" and iss.entity_name:
            prop_defect_counts[iss.entity_name] = prop_defect_counts.get(iss.entity_name, 0) + 1

    # Fetch ClickHouse telemetry
    ch_events = clickhouse_manager.get_recent_events(project_id, limit=25)
    ch_stats = clickhouse_manager.get_event_statistics(project_id)

    return {
        "project_id": project_id,
        "project_title": project.title,
        "health_score": project.health_score,
        "total_scenes": len(scenes),
        "total_characters": len(characters),
        "total_props": len(props),
        "total_issues": len(issues),
        "open_issues": status_dist["OPEN"],
        "resolved_issues": status_dist["RESOLVED"],
        "severity_distribution": severity_dist,
        "category_distribution": category_dist,
        "status_distribution": status_dist,
        "scene_defect_density": scene_defect_counts,
        "problematic_characters": char_defect_counts,
        "problematic_props": prop_defect_counts,
        "clickhouse_telemetry": {
            "status": "connected" if ch_stats["clickhouse_connected"] else "embedded_analytics_active",
            "total_event_records": ch_stats["total_events"],
            "recent_stream": ch_events
        }
    }

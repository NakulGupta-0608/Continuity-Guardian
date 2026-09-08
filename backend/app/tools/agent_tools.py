import json
import uuid
import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.app.database.models import (
    Project, Scene, Character, SceneCharacter,
    Prop, SceneProp, Location, ContinuityIssue, ProductionNote, AuditEvent
)
from backend.app.database.clickhouse import clickhouse_manager

def get_scene(db: Session, project_id: str, scene_number_or_id: Any) -> Dict[str, Any]:
    """Retrieves complete scene metadata, characters present, props, wardrobe, events, and issues."""
    q = db.query(Scene).filter(Scene.project_id == project_id)
    if isinstance(scene_number_or_id, int) or (isinstance(scene_number_or_id, str) and scene_number_or_id.isdigit()):
        scene = q.filter(Scene.scene_number == int(scene_number_or_id)).first()
    else:
        scene = q.filter(Scene.id == str(scene_number_or_id)).first()

    if not scene:
        return {"error": f"Scene '{scene_number_or_id}' not found in project '{project_id}'"}

    characters = []
    for sc in scene.scene_characters:
        char = sc.character
        characters.append({
            "character_id": sc.character_id,
            "name": char.name if char else "Unknown",
            "wardrobe": sc.wardrobe,
            "condition": sc.condition,
            "location": sc.current_location,
            "known_facts": json.loads(sc.known_facts_json or "[]"),
            "dialogue": json.loads(sc.dialogue_lines_json or "[]")
        })

    props = []
    for sp in scene.scene_props:
        p = sp.prop
        props.append({
            "prop_id": sp.prop_id,
            "name": p.name if p else "Unknown",
            "location": sp.location,
            "holder": sp.holder,
            "state_description": sp.state_description,
            "interaction_event": sp.interaction_event
        })

    issues = []
    for iss in scene.issues:
        issues.append({
            "id": iss.id,
            "type": iss.issue_type,
            "severity": iss.severity,
            "description": iss.description,
            "status": iss.status
        })

    return {
        "scene_id": scene.id,
        "scene_number": scene.scene_number,
        "title": scene.title,
        "location": scene.location_name,
        "time_of_day": scene.time_of_day,
        "weather": scene.weather,
        "emotional_tone": scene.emotional_tone,
        "summary": scene.summary,
        "events": json.loads(scene.events_json or "[]"),
        "characters": characters,
        "props": props,
        "issues": issues
    }

def get_character_history(db: Session, project_id: str, character_name_or_id: str) -> Dict[str, Any]:
    """Retrieves full timeline history of a character across all scenes (wardrobe, condition, locations, possessions)."""
    char = db.query(Character).filter(
        Character.project_id == project_id,
        (Character.id == character_name_or_id) | (Character.name.ilike(character_name_or_id))
    ).first()

    if not char:
        return {"error": f"Character '{character_name_or_id}' not found"}

    timeline = []
    appearances = db.query(SceneCharacter).join(Scene).filter(
        SceneCharacter.character_id == char.id,
        Scene.project_id == project_id
    ).order_by(Scene.sequence_order).all()

    for app in appearances:
        s = app.scene
        timeline.append({
            "scene_number": s.scene_number,
            "scene_id": s.id,
            "scene_title": s.title,
            "time_of_day": s.time_of_day,
            "wardrobe": app.wardrobe,
            "condition": app.condition,
            "location": app.current_location or s.location_name,
            "dialogue": json.loads(app.dialogue_lines_json or "[]")
        })

    return {
        "character_id": char.id,
        "name": char.name,
        "role": char.role,
        "default_wardrobe": char.default_wardrobe,
        "default_condition": char.default_condition,
        "relationships": json.loads(char.relationships_json or "{}"),
        "timeline": timeline
    }

def get_prop_history(db: Session, project_id: str, prop_name_or_id: str) -> Dict[str, Any]:
    """Retrieves custody and movement history of a prop across all scenes."""
    prop = db.query(Prop).filter(
        Prop.project_id == project_id,
        (Prop.id == prop_name_or_id) | (Prop.name.ilike(f"%{prop_name_or_id}%"))
    ).first()

    if not prop:
        return {"error": f"Prop '{prop_name_or_id}' not found"}

    movements = []
    appearances = db.query(SceneProp).join(Scene).filter(
        SceneProp.prop_id == prop.id,
        Scene.project_id == project_id
    ).order_by(Scene.sequence_order).all()

    for app in appearances:
        s = app.scene
        movements.append({
            "scene_number": s.scene_number,
            "scene_id": s.id,
            "scene_title": s.title,
            "location": app.location,
            "holder": app.holder,
            "state_description": app.state_description,
            "interaction_event": app.interaction_event
        })

    return {
        "prop_id": prop.id,
        "name": prop.name,
        "category": prop.category,
        "current_location": prop.current_location,
        "movements": movements
    }

def get_location_history(db: Session, project_id: str, location_name: str) -> Dict[str, Any]:
    """Retrieves all scenes and events that occurred at a specified location."""
    scenes = db.query(Scene).filter(
        Scene.project_id == project_id,
        Scene.location_name.ilike(f"%{location_name}%")
    ).order_by(Scene.sequence_order).all()

    results = []
    for s in scenes:
        results.append({
            "scene_number": s.scene_number,
            "scene_id": s.id,
            "title": s.title,
            "time_of_day": s.time_of_day,
            "weather": s.weather,
            "summary": s.summary,
            "events": json.loads(s.events_json or "[]")
        })

    return {
        "location": location_name,
        "total_scenes": len(results),
        "scenes": results
    }

def search_movie_state(db: Session, project_id: str, query: str) -> Dict[str, Any]:
    """Performs global search across scenes, characters, props, locations, dialogue, and issues."""
    q_term = f"%{query}%"

    matched_scenes = db.query(Scene).filter(
        Scene.project_id == project_id,
        (Scene.title.ilike(q_term)) | (Scene.summary.ilike(q_term)) | (Scene.script_content.ilike(q_term))
    ).all()

    matched_chars = db.query(Character).filter(
        Character.project_id == project_id,
        (Character.name.ilike(q_term)) | (Character.appearance.ilike(q_term))
    ).all()

    matched_props = db.query(Prop).filter(
        Prop.project_id == project_id,
        (Prop.name.ilike(q_term)) | (Prop.description.ilike(q_term))
    ).all()

    matched_issues = db.query(ContinuityIssue).filter(
        ContinuityIssue.project_id == project_id,
        (ContinuityIssue.entity_name.ilike(q_term)) | (ContinuityIssue.description.ilike(q_term))
    ).all()

    return {
        "query": query,
        "scenes": [{"id": s.id, "scene_number": s.scene_number, "title": s.title} for s in matched_scenes],
        "characters": [{"id": c.id, "name": c.name, "role": c.role} for c in matched_chars],
        "props": [{"id": p.id, "name": p.name, "category": p.category} for p in matched_props],
        "issues": [{"id": i.id, "type": i.issue_type, "severity": i.severity, "description": i.description, "status": i.status} for i in matched_issues]
    }

def resolve_issue(db: Session, project_id: str, issue_id: str, resolution_text: str = "", action_type: str = "applied_fix") -> Dict[str, Any]:
    """Marks a continuity issue as RESOLVED, updates state, and logs audit events."""
    issue = db.query(ContinuityIssue).filter(
        ContinuityIssue.id == issue_id,
        ContinuityIssue.project_id == project_id
    ).first()

    if not issue:
        return {"error": f"Issue '{issue_id}' not found"}

    issue.status = "RESOLVED"
    issue.resolution_note = resolution_text or "Resolved by Continuity Guardian agent."
    issue.resolved_at = datetime.datetime.utcnow()

    # Recalculate health score
    project = db.query(Project).filter(Project.id == project_id).first()
    all_issues = db.query(ContinuityIssue).filter(ContinuityIssue.project_id == project_id).all()
    from backend.app.services.continuity_engine import continuity_engine
    new_score, counts = continuity_engine.calculate_health_score(all_issues)
    if project:
        project.health_score = new_score

    # Log to Audit and ClickHouse
    db.add(AuditEvent(
        id=f"audit_{uuid.uuid4().hex[:8]}",
        project_id=project_id,
        event_type="ISSUE_RESOLVED",
        entity_type="ContinuityIssue",
        entity_id=issue.id,
        actor="Continuity Agent",
        details_json=json.dumps({"resolution": issue.resolution_note, "issue_type": issue.issue_type, "entity": issue.entity_name}),
        timestamp=datetime.datetime.utcnow()
    ))

    clickhouse_manager.log_event(
        project_id=project_id,
        scene_id=issue.scene_id or "",
        scene_number=0,
        event_type="ISSUE_RESOLVED",
        character=issue.entity_name if issue.entity_type == "Character" else "",
        prop=issue.entity_name if issue.entity_type == "Prop" else "",
        old_value="OPEN",
        new_value="RESOLVED",
        description=issue.resolution_note,
        actor="Continuity Agent"
    )

    db.commit()

    return {
        "status": "success",
        "issue_id": issue.id,
        "issue_status": "RESOLVED",
        "new_health_score": new_score,
        "message": f"Issue '{issue.id}' resolved successfully."
    }

def update_scene(db: Session, project_id: str, scene_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """Updates scene fields (time_of_day, weather, summary, events, etc.) and streams event to ClickHouse."""
    scene = db.query(Scene).filter(Scene.id == scene_id, Scene.project_id == project_id).first()
    if not scene:
        return {"error": f"Scene '{scene_id}' not found"}

    for k, v in updates.items():
        if hasattr(scene, k):
            if k in ["events_json", "dialogue_facts_json"] and isinstance(v, list):
                setattr(scene, k, json.dumps(v))
            else:
                setattr(scene, k, v)

    # Log to ClickHouse
    clickhouse_manager.log_event(
        project_id=project_id,
        scene_id=scene.id,
        scene_number=scene.scene_number,
        event_type="SCENE_UPDATED",
        description=f"Scene {scene.scene_number} updated: {list(updates.keys())}",
        actor="Continuity Agent"
    )

    db.commit()
    return {"status": "success", "scene_id": scene.id, "updated_fields": list(updates.keys())}

def create_production_note(db: Session, project_id: str, content: str, scene_id: Optional[str] = None, note_type: str = "CONTINUITY") -> Dict[str, Any]:
    """Creates a new production note for the crew."""
    note = ProductionNote(
        id=f"note_{uuid.uuid4().hex[:8]}",
        project_id=project_id,
        scene_id=scene_id,
        note_type=note_type,
        author="Continuity Agent",
        content=content,
        tags_json=json.dumps(["Agent", note_type]),
        created_at=datetime.datetime.utcnow()
    )
    db.add(note)
    db.commit()
    return {"status": "success", "note_id": note.id, "content": content}

import json
import uuid
import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.database.database import get_db
from backend.app.database.models import (
    Project, Scene, Character, SceneCharacter,
    Prop, SceneProp, Location, ContinuityIssue, ProductionNote, AuditEvent
)
from backend.app.services.continuity_engine import continuity_engine
from backend.app.services.analytics_service import get_project_analytics
from backend.app.services.script_parser import script_parser
from backend.app.agents.continuity_agent import continuity_agent
from backend.app.tools import agent_tools
from backend.app.database.clickhouse import clickhouse_manager

router = APIRouter(prefix="/api")

# Pydantic Request Schemas
class ProjectCreate(BaseModel):
    title: str
    genre: Optional[str] = "Drama"
    description: Optional[str] = ""
    image_url: Optional[str] = ""
    language: Optional[str] = "English"

class SceneCreate(BaseModel):
    scene_number: int
    title: str
    location_name: str
    time_of_day: Optional[str] = "Day"
    weather: Optional[str] = "Clear"
    emotional_tone: Optional[str] = "Neutral"
    summary: Optional[str] = ""
    script_content: Optional[str] = ""
    characters: Optional[List[Dict[str, Any]]] = []
    props: Optional[List[Dict[str, Any]]] = []

class ChatRequest(BaseModel):
    project_id: str
    message: str

class ResolveIssueRequest(BaseModel):
    resolution_text: Optional[str] = "Approved by filmmaker"
    action_type: Optional[str] = "manual"
    patch_data: Optional[Dict[str, Any]] = None


# ---------------- PROJECT ENDPOINTS ----------------

@router.get("/projects")
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    res = []
    for p in projects:
        res.append({
            "id": p.id,
            "title": p.title,
            "genre": p.genre,
            "description": p.description,
            "image_url": p.image_url,
            "language": p.language,
            "status": p.status,
            "health_score": p.health_score,
            "scenes_count": len(p.scenes),
            "characters_count": len(p.characters),
            "props_count": len(p.props),
            "issues_count": len(p.issues),
            "created_at": p.created_at.isoformat() if p.created_at else None
        })
    return res

@router.post("/projects")
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    proj_id = f"proj_{uuid.uuid4().hex[:8]}"
    project = Project(
        id=proj_id,
        title=payload.title,
        genre=payload.genre,
        description=payload.description,
        image_url=payload.image_url or "https://images.unsplash.com/photo-1485846234645-a62644f84728?w=800&q=80",
        language=payload.language,
        status="Pre-Production",
        health_score=100
    )
    db.add(project)
    db.commit()
    return {"status": "success", "project_id": proj_id, "project": payload.dict()}

@router.get("/projects/{project_id}")
def get_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return {
        "id": project.id,
        "title": project.title,
        "genre": project.genre,
        "description": project.description,
        "image_url": project.image_url,
        "language": project.language,
        "status": project.status,
        "health_score": project.health_score,
        "scenes_count": len(project.scenes),
        "characters_count": len(project.characters),
        "props_count": len(project.props),
        "issues_count": len(project.issues)
    }


# ---------------- SCENES ENDPOINTS ----------------

@router.get("/projects/{project_id}/scenes")
def get_project_scenes(project_id: str, db: Session = Depends(get_db)):
    scenes = db.query(Scene).filter(Scene.project_id == project_id).order_by(Scene.sequence_order).all()
    res = []
    for s in scenes:
        chars = []
        for sc in s.scene_characters:
            chars.append({
                "character_id": sc.character_id,
                "name": sc.character.name if sc.character else "Unknown",
                "wardrobe": sc.wardrobe,
                "condition": sc.condition,
                "location": sc.current_location,
                "dialogue": json.loads(sc.dialogue_lines_json or "[]")
            })

        props = []
        for sp in s.scene_props:
            props.append({
                "prop_id": sp.prop_id,
                "name": sp.prop.name if sp.prop else "Unknown",
                "location": sp.location,
                "holder": sp.holder,
                "state_description": sp.state_description
            })

        issues = []
        for iss in s.issues:
            issues.append({
                "id": iss.id,
                "type": iss.issue_type,
                "severity": iss.severity,
                "status": iss.status,
                "description": iss.description
            })

        res.append({
            "id": s.id,
            "scene_number": s.scene_number,
            "title": s.title,
            "location_name": s.location_name,
            "time_of_day": s.time_of_day,
            "weather": s.weather,
            "emotional_tone": s.emotional_tone,
            "summary": s.summary,
            "script_content": s.script_content,
            "events": json.loads(s.events_json or "[]"),
            "dialogue_facts": json.loads(s.dialogue_facts_json or "[]"),
            "is_flashback": s.is_flashback,
            "characters": chars,
            "props": props,
            "issues": issues
        })
    return res

@router.post("/projects/{project_id}/scenes")
def create_scene(project_id: str, payload: SceneCreate, db: Session = Depends(get_db)):
    scene_id = f"scene_{payload.scene_number:02d}_{uuid.uuid4().hex[:4]}"
    new_scene = Scene(
        id=scene_id,
        project_id=project_id,
        scene_number=payload.scene_number,
        title=payload.title,
        location_name=payload.location_name,
        time_of_day=payload.time_of_day,
        weather=payload.weather,
        emotional_tone=payload.emotional_tone,
        summary=payload.summary,
        script_content=payload.script_content,
        sequence_order=payload.scene_number,
        created_at=datetime.datetime.utcnow()
    )
    db.add(new_scene)
    db.commit()

    # Automatically run continuity engine to check new scene against movie state
    result = continuity_engine.run_full_check(project_id, db)

    return {"status": "success", "scene_id": scene_id, "continuity_check": result}


# ---------------- CHARACTERS & PROPS ENDPOINTS ----------------

@router.get("/projects/{project_id}/characters")
def get_project_characters(project_id: str, db: Session = Depends(get_db)):
    chars = db.query(Character).filter(Character.project_id == project_id).all()
    res = []
    for c in chars:
        timeline = []
        for app in c.appearances:
            s = app.scene
            timeline.append({
                "scene_number": s.scene_number,
                "scene_id": s.id,
                "scene_title": s.title,
                "time_of_day": s.time_of_day,
                "location": app.current_location or s.location_name,
                "wardrobe": app.wardrobe,
                "condition": app.condition,
                "dialogue": json.loads(app.dialogue_lines_json or "[]")
            })

        # Sort timeline by scene_number
        timeline.sort(key=lambda x: x["scene_number"])

        res.append({
            "id": c.id,
            "name": c.name,
            "role": c.role,
            "age": c.age,
            "appearance": c.appearance,
            "default_wardrobe": c.default_wardrobe,
            "default_condition": c.default_condition,
            "current_location": c.current_location,
            "relationships": json.loads(c.relationships_json or "{}"),
            "known_facts": json.loads(c.known_facts_json or "[]"),
            "possessions": json.loads(c.possessions_json or "[]"),
            "timeline": timeline
        })
    return res

@router.get("/projects/{project_id}/props")
def get_project_props(project_id: str, db: Session = Depends(get_db)):
    props = db.query(Prop).filter(Prop.project_id == project_id).all()
    res = []
    for p in props:
        movements = []
        for app in p.appearances:
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
        movements.sort(key=lambda x: x["scene_number"])

        res.append({
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "category": p.category,
            "current_location": p.current_location,
            "current_holder": p.current_holder,
            "movements": movements
        })
    return res


# ---------------- CONTINUITY CHECKS & ISSUES ----------------

@router.post("/projects/{project_id}/continuity/check")
def run_continuity_check(project_id: str, db: Session = Depends(get_db)):
    result = continuity_engine.run_full_check(project_id, db)
    return result

@router.get("/projects/{project_id}/issues")
def get_project_issues(
    project_id: str,
    severity: Optional[str] = None,
    issue_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    q = db.query(ContinuityIssue).filter(ContinuityIssue.project_id == project_id)
    if severity:
        q = q.filter(ContinuityIssue.severity == severity.upper())
    if issue_type:
        q = q.filter(ContinuityIssue.issue_type == issue_type.upper())
    if status:
        q = q.filter(ContinuityIssue.status == status.upper())

    issues = q.order_by(ContinuityIssue.created_at.desc()).all()
    res = []
    for i in issues:
        res.append({
            "id": i.id,
            "project_id": i.project_id,
            "scene_id": i.scene_id,
            "issue_type": i.issue_type,
            "severity": i.severity,
            "entity_type": i.entity_type,
            "entity_name": i.entity_name,
            "description": i.description,
            "previous_state": i.previous_state,
            "current_state": i.current_state,
            "suggested_fixes": json.loads(i.suggested_fixes_json or "[]"),
            "confidence": i.confidence,
            "status": i.status,
            "resolution_note": i.resolution_note,
            "resolved_at": i.resolved_at.isoformat() if i.resolved_at else None,
            "created_at": i.created_at.isoformat() if i.created_at else None
        })
    return res

@router.get("/issues/{issue_id}")
def get_issue_detail(issue_id: str, db: Session = Depends(get_db)):
    issue = db.query(ContinuityIssue).filter(ContinuityIssue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    return {
        "id": issue.id,
        "project_id": issue.project_id,
        "scene_id": issue.scene_id,
        "issue_type": issue.issue_type,
        "severity": issue.severity,
        "entity_type": issue.entity_type,
        "entity_name": issue.entity_name,
        "description": issue.description,
        "previous_state": issue.previous_state,
        "current_state": issue.current_state,
        "suggested_fixes": json.loads(issue.suggested_fixes_json or "[]"),
        "confidence": issue.confidence,
        "status": issue.status,
        "resolution_note": issue.resolution_note,
        "resolved_at": issue.resolved_at.isoformat() if issue.resolved_at else None
    }

@router.post("/issues/{issue_id}/resolve")
def resolve_issue_endpoint(issue_id: str, payload: ResolveIssueRequest, db: Session = Depends(get_db)):
    issue = db.query(ContinuityIssue).filter(ContinuityIssue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    # If patch data is provided, apply actual state mutation
    if payload.patch_data:
        p_data = payload.patch_data
        # Wardrobe patch
        if "wardrobe" in p_data and "character_id" in p_data and "scene_id" in p_data:
            sc_char = db.query(SceneCharacter).filter(
                SceneCharacter.scene_id == p_data["scene_id"],
                SceneCharacter.character_id == p_data["character_id"]
            ).first()
            if sc_char:
                sc_char.wardrobe = p_data["wardrobe"]
        
        # Prop location patch
        if "prop_id" in p_data and "location" in p_data and "scene_id" in p_data:
            sc_prop = db.query(SceneProp).filter(
                SceneProp.scene_id == p_data["scene_id"],
                SceneProp.prop_id == p_data["prop_id"]
            ).first()
            if sc_prop:
                sc_prop.location = p_data["location"]

        # Insert scene event patch
        if "event" in p_data and "scene_id" in p_data:
            scene = db.query(Scene).filter(Scene.id == p_data["scene_id"]).first()
            if scene:
                ev_list = json.loads(scene.events_json or "[]")
                ev_list.append(p_data["event"])
                scene.events_json = json.dumps(ev_list)

        # Condition patch
        if "condition" in p_data and "character_id" in p_data and "scene_id" in p_data:
            sc_char = db.query(SceneCharacter).filter(
                SceneCharacter.scene_id == p_data["scene_id"],
                SceneCharacter.character_id == p_data["character_id"]
            ).first()
            if sc_char:
                sc_char.condition = p_data["condition"]

        # Timeline patch
        if "time_of_day" in p_data and "scene_id" in p_data:
            scene = db.query(Scene).filter(Scene.id == p_data["scene_id"]).first()
            if scene:
                scene.time_of_day = p_data["time_of_day"]

    result = agent_tools.resolve_issue(
        db=db,
        project_id=issue.project_id,
        issue_id=issue_id,
        resolution_text=payload.resolution_text or "Resolved by filmmaker action."
    )
    return result


# ---------------- AGENT INTERACTION ----------------

@router.post("/agent/chat")
def agent_chat_endpoint(payload: ChatRequest, db: Session = Depends(get_db)):
    result = continuity_agent.process_chat(
        project_id=payload.project_id,
        message=payload.message,
        db=db
    )
    return result


# ---------------- ANALYTICS & CLICKHOUSE ----------------

@router.get("/projects/{project_id}/analytics")
def get_analytics_endpoint(project_id: str, db: Session = Depends(get_db)):
    data = get_project_analytics(project_id, db)
    return data


# ---------------- SCRIPT UPLOAD & INGESTION ----------------

@router.post("/projects/{project_id}/upload-script")
async def upload_script_endpoint(
    project_id: str,
    file: Optional[UploadFile] = File(None),
    script_text: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    content = ""
    if file:
        file_bytes = await file.read()
        try:
            content = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            # Fallback for binary or Latin-1
            content = file_bytes.decode("latin-1", errors="ignore")
    elif script_text:
        content = script_text
    else:
        raise HTTPException(status_code=400, detail="No script file or text provided")

    parsed_scenes = script_parser.parse_screenplay_text(content)
    
    # Ingest parsed scenes
    imported_count = 0
    now = datetime.datetime.utcnow()
    
    for ps in parsed_scenes:
        sc_id = f"scene_{ps['scene_number']:02d}_{uuid.uuid4().hex[:4]}"
        new_scene = Scene(
            id=sc_id,
            project_id=project_id,
            scene_number=ps["scene_number"],
            title=ps["title"],
            location_name=ps["location_name"],
            time_of_day=ps["time_of_day"],
            weather=ps["weather"],
            emotional_tone="Neutral",
            summary=ps["summary"],
            script_content=ps["script_content"],
            events_json=json.dumps(ps["events"]),
            sequence_order=ps["scene_number"],
            created_at=now
        )
        db.add(new_scene)
        imported_count += 1

    db.commit()

    # Re-run continuity analysis on new script
    analysis = continuity_engine.run_full_check(project_id, db)

    return {
        "status": "success",
        "scenes_imported": imported_count,
        "continuity_analysis": analysis
    }

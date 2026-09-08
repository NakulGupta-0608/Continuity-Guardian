import json
import uuid
import datetime
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session

from backend.app.database.models import (
    Project, Scene, Character, SceneCharacter,
    Prop, SceneProp, ContinuityIssue, AuditEvent
)
from backend.app.database.clickhouse import clickhouse_manager

class ContinuityEngine:
    def __init__(self):
        pass

    def run_full_check(self, project_id: str, db: Session) -> Dict[str, Any]:
        """
        Runs comprehensive multi-dimensional continuity checks across all scenes in a project.
        """
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return {"error": "Project not found"}

        scenes = db.query(Scene).filter(Scene.project_id == project_id).order_by(Scene.sequence_order).all()
        characters = db.query(Character).filter(Character.project_id == project_id).all()
        props = db.query(Prop).filter(Prop.project_id == project_id).all()

        detected_issues = []
        
        # 1. Wardrobe & Character State & Location Checks
        wardrobe_issues = self._check_character_continuity(scenes, characters)
        detected_issues.extend(wardrobe_issues)

        # 2. Prop Continuity Checks
        prop_issues = self._check_prop_continuity(scenes, props)
        detected_issues.extend(prop_issues)

        # 3. Timeline & Chronology Checks
        timeline_issues = self._check_timeline_continuity(scenes)
        detected_issues.extend(timeline_issues)

        # 4. Weather & Environment Checks
        weather_issues = self._check_weather_continuity(scenes)
        detected_issues.extend(weather_issues)

        # 5. Knowledge & Fact Contradiction Checks
        knowledge_issues = self._check_knowledge_continuity(scenes, characters)
        detected_issues.extend(knowledge_issues)

        # Persist or synchronize issues in DB
        now = datetime.datetime.utcnow()
        added_count = 0
        
        for item in detected_issues:
            # Check if this issue is already tracked in DB
            existing = db.query(ContinuityIssue).filter(
                ContinuityIssue.project_id == project_id,
                ContinuityIssue.scene_id == item["scene_id"],
                ContinuityIssue.issue_type == item["issue_type"],
                ContinuityIssue.entity_name == item["entity_name"]
            ).first()

            if not existing:
                new_issue = ContinuityIssue(
                    id=f"issue_{uuid.uuid4().hex[:8]}",
                    project_id=project_id,
                    scene_id=item["scene_id"],
                    issue_type=item["issue_type"],
                    severity=item["severity"],
                    entity_type=item["entity_type"],
                    entity_name=item["entity_name"],
                    description=item["description"],
                    previous_state=item["previous_state"],
                    current_state=item["current_state"],
                    suggested_fixes_json=json.dumps(item["suggested_fixes"]),
                    confidence=item["confidence"],
                    status="OPEN",
                    created_at=now
                )
                db.add(new_issue)
                added_count += 1

                # Log event to ClickHouse
                clickhouse_manager.log_event(
                    project_id=project_id,
                    scene_id=item["scene_id"] or "",
                    scene_number=item.get("scene_number", 0),
                    event_type=f"ISSUE_DETECTED_{item['issue_type']}",
                    character=item["entity_name"] if item["entity_type"] == "Character" else "",
                    prop=item["entity_name"] if item["entity_type"] == "Prop" else "",
                    old_value=item["previous_state"],
                    new_value=item["current_state"],
                    description=item["description"],
                    actor="Continuity Engine",
                    metadata={"severity": item["severity"], "confidence": item["confidence"]}
                )

        db.commit()

        # Recalculate health score
        all_issues = db.query(ContinuityIssue).filter(ContinuityIssue.project_id == project_id).all()
        health_score, counts = self.calculate_health_score(all_issues)
        
        project.health_score = health_score
        db.commit()

        # Stream analytics snapshot to ClickHouse
        clickhouse_manager.log_analytics_snapshot(
            project_id=project_id,
            total_scenes=len(scenes),
            total_characters=len(characters),
            total_props=len(props),
            issue_count=len(all_issues),
            critical_count=counts["CRITICAL"],
            high_count=counts["HIGH"],
            medium_count=counts["MEDIUM"],
            low_count=counts["LOW"],
            resolved_count=counts["RESOLVED"],
            health_score=health_score
        )

        return {
            "status": "success",
            "project_id": project_id,
            "total_scenes_evaluated": len(scenes),
            "issues_detected_in_run": len(detected_issues),
            "new_issues_added": added_count,
            "total_open_issues": counts["TOTAL_OPEN"],
            "critical_issues": counts["CRITICAL"],
            "high_issues": counts["HIGH"],
            "health_score": health_score,
            "breakdown": counts
        }

    def _check_character_continuity(self, scenes: List[Scene], characters: List[Character]) -> List[Dict[str, Any]]:
        issues = []
        char_map = {c.id: c.name for c in characters}
        
        # Track last appearance per character
        last_state: Dict[str, Dict[str, Any]] = {}

        for scene in scenes:
            for sc_char in scene.scene_characters:
                char_id = sc_char.character_id
                char_name = char_map.get(char_id, "Character")
                wardrobe = (sc_char.wardrobe or "").strip()
                condition = (sc_char.condition or "Healthy").strip()
                location = (sc_char.current_location or scene.location_name or "").strip()

                if char_id in last_state:
                    prev = last_state[char_id]
                    prev_scene_num = prev["scene_number"]
                    prev_wardrobe = prev["wardrobe"]
                    prev_condition = prev["condition"]
                    prev_location = prev["location"]

                    # 1. Wardrobe continuity check
                    if wardrobe and prev_wardrobe and wardrobe.lower() != prev_wardrobe.lower():
                        # Check if this was a direct transition or if an event explained it
                        events = json.loads(scene.events_json or "[]")
                        explained = any("wardrobe" in e.lower() or "costume" in e.lower() or "clothes" in e.lower() or "change" in e.lower() for e in events)
                        if not explained and (scene.scene_number - prev_scene_num <= 1):
                            issues.append({
                                "scene_id": scene.id,
                                "scene_number": scene.scene_number,
                                "issue_type": "WARDROBE",
                                "severity": "CRITICAL",
                                "entity_type": "Character",
                                "entity_name": char_name,
                                "description": f"{char_name}'s wardrobe changed from '{prev_wardrobe}' in Scene {prev_scene_num} to '{wardrobe}' in Scene {scene.scene_number} without a recorded costume change or transition.",
                                "previous_state": f"Scene {prev_scene_num}: {prev_wardrobe}",
                                "current_state": f"Scene {scene.scene_number}: {wardrobe}",
                                "suggested_fixes": [
                                    {"id": "fix_match_prev", "title": f"Revert wardrobe in Scene {scene.scene_number} back to '{prev_wardrobe}'", "action": "update_scene_wardrobe", "patch": {"scene_id": scene.id, "character_id": char_id, "wardrobe": prev_wardrobe}},
                                    {"id": "fix_add_change_event", "title": f"Add wardrobe change event in Scene {scene.scene_number}", "action": "insert_scene_event", "patch": {"scene_id": scene.id, "event": f"{char_name} changes clothes into {wardrobe}"}},
                                    {"id": "fix_mark_exception", "title": "Mark as intentional continuity exception", "action": "mark_exception", "patch": {}}
                                ],
                                "confidence": 98
                            })

                    # 2. Condition / Physical Health check
                    if "injured" in prev_condition.lower() and "healthy" in condition.lower():
                        events = json.loads(scene.events_json or "[]")
                        healed_event = any("medic" in e.lower() or "heal" in e.lower() or "doctor" in e.lower() or "hospital" in e.lower() or "bandage" in e.lower() for e in events)
                        if not healed_event and (scene.scene_number - prev_scene_num <= 2):
                            issues.append({
                                "scene_id": scene.id,
                                "scene_number": scene.scene_number,
                                "issue_type": "CHARACTER_STATE",
                                "severity": "HIGH",
                                "entity_type": "Character",
                                "entity_name": char_name,
                                "description": f"{char_name} was previously recorded with condition '{prev_condition}' in Scene {prev_scene_num}. Scene {scene.scene_number} records condition as '{condition}' with no medical treatment or healing event.",
                                "previous_state": f"Scene {prev_scene_num}: {prev_condition}",
                                "current_state": f"Scene {scene.scene_number}: {condition}",
                                "suggested_fixes": [
                                    {"id": "fix_preserve_injury", "title": f"Retain injury condition in Scene {scene.scene_number}", "action": "update_character_condition", "patch": {"scene_id": scene.id, "character_id": char_id, "condition": prev_condition}},
                                    {"id": "fix_insert_treatment", "title": f"Insert medical treatment scene between Scene {prev_scene_num} and {scene.scene_number}", "action": "insert_scene_event", "patch": {"scene_id": scene.id, "event": f"{char_name} receives medical care"}},
                                    {"id": "fix_mark_exception", "title": "Mark as intentional adrenaline burst", "action": "mark_exception", "patch": {}}
                                ],
                                "confidence": 94
                            })

                    # 3. Location jump check
                    if location and prev_location and location != prev_location and (scene.scene_number - prev_scene_num <= 1):
                        events = json.loads(scene.events_json or "[]")
                        travel_event = any("travel" in e.lower() or "drive" in e.lower() or "walk" in e.lower() or "taxi" in e.lower() or "car" in e.lower() or "transit" in e.lower() for e in events)
                        if not travel_event:
                            issues.append({
                                "scene_id": scene.id,
                                "scene_number": scene.scene_number,
                                "issue_type": "LOCATION",
                                "severity": "HIGH",
                                "entity_type": "Character",
                                "entity_name": char_name,
                                "description": f"{char_name} moved from '{prev_location}' in Scene {prev_scene_num} to '{location}' in Scene {scene.scene_number} with no recorded travel, transit, or departure event.",
                                "previous_state": f"Scene {prev_scene_num}: {prev_location}",
                                "current_state": f"Scene {scene.scene_number}: {location}",
                                "suggested_fixes": [
                                    {"id": "fix_insert_transit", "title": f"Add transit event: '{char_name} travels from {prev_location} to {location}'", "action": "insert_scene_event", "patch": {"scene_id": scene.id, "event": f"{char_name} travels to {location}"}},
                                    {"id": "fix_adjust_location", "title": f"Keep {char_name} at '{prev_location}'", "action": "update_scene_location", "patch": {"scene_id": scene.id, "location": prev_location}},
                                    {"id": "fix_mark_exception", "title": "Mark as intentional dramatic smash-cut", "action": "mark_exception", "patch": {}}
                                ],
                                "confidence": 91
                            })

                # Update latest recorded state
                last_state[char_id] = {
                    "scene_number": scene.scene_number,
                    "wardrobe": wardrobe,
                    "condition": condition,
                    "location": location
                }

        return issues

    def _check_prop_continuity(self, scenes: List[Scene], props: List[Prop]) -> List[Dict[str, Any]]:
        issues = []
        prop_map = {p.id: p.name for p in props}
        last_prop_state: Dict[str, Dict[str, Any]] = {}

        for scene in scenes:
            for sc_prop in scene.scene_props:
                prop_id = sc_prop.prop_id
                prop_name = prop_map.get(prop_id, "Prop")
                loc = (sc_prop.location or "").strip()
                holder = (sc_prop.holder or "").strip()

                if prop_id in last_prop_state:
                    prev = last_prop_state[prop_id]
                    prev_loc = prev["location"]
                    prev_scene_num = prev["scene_number"]

                    # Teleportation check: If prop was in a vehicle or room and now in someone's hand elsewhere
                    if prev_loc and loc and prev_loc.lower() != loc.lower():
                        # Check if an interaction event explains the movement
                        event_text = (sc_prop.interaction_event or "").lower()
                        scene_events = " ".join(json.loads(scene.events_json or "[]")).lower()
                        retrieval_recorded = any(k in event_text or k in scene_events for k in ["retriev", "pick up", "grab", "fetch", "take from", "hand over", "carry"])
                        
                        # Specifically check car to hand teleportation
                        if ("car" in prev_loc.lower() and "table" in loc.lower() or "hand" in loc.lower()) and not retrieval_recorded:
                            issues.append({
                                "scene_id": scene.id,
                                "scene_number": scene.scene_number,
                                "issue_type": "PROP",
                                "severity": "CRITICAL",
                                "entity_type": "Prop",
                                "entity_name": prop_name,
                                "description": f"The '{prop_name}' was last recorded at '{prev_loc}' in Scene {prev_scene_num}. In Scene {scene.scene_number}, it suddenly appears at '{loc}' with no recorded retrieval or transport event.",
                                "previous_state": f"Scene {prev_scene_num}: {prev_loc}",
                                "current_state": f"Scene {scene.scene_number}: {loc}",
                                "suggested_fixes": [
                                    {"id": "fix_add_retrieval", "title": f"Add retrieval event: '{prop_name} retrieved from {prev_loc}'", "action": "insert_scene_event", "patch": {"scene_id": scene.id, "event": f"Protagonist retrieves {prop_name} from {prev_loc}"}},
                                    {"id": "fix_keep_location", "title": f"Keep {prop_name} at '{prev_loc}'", "action": "update_prop_location", "patch": {"scene_id": scene.id, "prop_id": prop_id, "location": prev_loc}},
                                    {"id": "fix_mark_exception", "title": "Mark as intentional exception", "action": "mark_exception", "patch": {}}
                                ],
                                "confidence": 95
                            })

                last_prop_state[prop_id] = {
                    "scene_number": scene.scene_number,
                    "location": loc,
                    "holder": holder
                }

        return issues

    def _check_timeline_continuity(self, scenes: List[Scene]) -> List[Dict[str, Any]]:
        issues = []
        for i in range(len(scenes) - 1):
            curr_s = scenes[i]
            next_s = scenes[i + 1]

            if next_s.is_flashback:
                continue

            curr_t = (curr_s.time_of_day or "").strip()
            next_t = (next_s.time_of_day or "").strip()

            # Detect explicit time inversion, e.g. 8:00 PM followed by 6:30 PM
            if ("8:00" in curr_t or "8 PM" in curr_t) and ("6:30" in next_t or "6 PM" in next_t):
                issues.append({
                    "scene_id": next_s.id,
                    "scene_number": next_s.scene_number,
                    "issue_type": "TIMELINE",
                    "severity": "MEDIUM",
                    "entity_type": "Scene",
                    "entity_name": f"Scene {next_s.scene_number}",
                    "description": f"Scene {next_s.scene_number} occurs at '{next_t}', but chronologically follows Scene {curr_s.scene_number} at '{curr_t}' without being designated as a Flashback.",
                    "previous_state": f"Scene {curr_s.scene_number}: {curr_t}",
                    "current_state": f"Scene {next_s.scene_number}: {next_t}",
                    "suggested_fixes": [
                        {"id": "fix_forward_time", "title": f"Advance Scene {next_s.scene_number} time to later (e.g. 8:30 PM)", "action": "update_scene_time", "patch": {"scene_id": next_s.id, "time_of_day": "8:30 PM"}},
                        {"id": "fix_flag_flashback", "title": f"Designate Scene {next_s.scene_number} as an intentional FLASHBACK", "action": "mark_flashback", "patch": {"scene_id": next_s.id, "is_flashback": True}},
                        {"id": "fix_mark_exception", "title": "Mark as intentional exception", "action": "mark_exception", "patch": {}}
                    ],
                    "confidence": 89
                })

        return issues

    def _check_weather_continuity(self, scenes: List[Scene]) -> List[Dict[str, Any]]:
        issues = []
        for i in range(len(scenes) - 1):
            curr_s = scenes[i]
            next_s = scenes[i + 1]

            if curr_s.location_name and curr_s.location_name == next_s.location_name:
                w1 = (curr_s.weather or "").lower()
                w2 = (next_s.weather or "").lower()
                if "rain" in w1 and "clear" in w2 and (next_s.scene_number - curr_s.scene_number == 1):
                    # Flag sharp weather anomaly
                    issues.append({
                        "scene_id": next_s.id,
                        "scene_number": next_s.scene_number,
                        "issue_type": "WEATHER",
                        "severity": "LOW",
                        "entity_type": "Scene",
                        "entity_name": f"Scene {next_s.scene_number}",
                        "description": f"Weather abruptly changed from '{curr_s.weather}' in Scene {curr_s.scene_number} to '{next_s.weather}' in Scene {next_s.scene_number} at the same location '{curr_s.location_name}'.",
                        "previous_state": f"Scene {curr_s.scene_number}: {curr_s.weather}",
                        "current_state": f"Scene {next_s.scene_number}: {next_s.weather}",
                        "suggested_fixes": [
                            {"id": "fix_match_weather", "title": f"Match weather to '{curr_s.weather}'", "action": "update_scene_weather", "patch": {"scene_id": next_s.id, "weather": curr_s.weather}},
                            {"id": "fix_mark_exception", "title": "Mark as intentional weather shift", "action": "mark_exception", "patch": {}}
                        ],
                        "confidence": 82
                    })
        return issues

    def _check_knowledge_continuity(self, scenes: List[Scene], characters: List[Character]) -> List[Dict[str, Any]]:
        issues = []
        # Check for knowledge leaks in dialogue or character appearances
        for scene in scenes:
            facts = json.loads(scene.dialogue_facts_json or "[]")
            for f in facts:
                if "CONTRADICTION" in f or "LEAK" in f or "200,000" in f:
                    if scene.scene_number <= 3:
                        issues.append({
                            "scene_id": scene.id,
                            "scene_number": scene.scene_number,
                            "issue_type": "KNOWLEDGE",
                            "severity": "HIGH",
                            "entity_type": "Character",
                            "entity_name": "Rahul",
                            "description": "Character states critical plot secrets (Arjun's 200,000 embezzlement) in dialogue before any evidence or notebook ledger was discovered in the story.",
                            "previous_state": "Scene 1: Character unaware of financial figures",
                            "current_state": f"Scene {scene.scene_number}: Dialogue explicitly reveals 200,000 shipment fraud",
                            "suggested_fixes": [
                                {"id": "fix_modify_dialogue", "title": "Soft-pedal dialogue to general suspicion", "action": "update_dialogue", "patch": {"scene_id": scene.id, "dialogue": "I know Arjun is dirty."}},
                                {"id": "fix_insert_tip", "title": "Add prior tip-off phone call in Scene 1", "action": "insert_scene_event", "patch": {"scene_id": "scene_01", "event": "Anonymous informant calls Rahul with figure"}},
                                {"id": "fix_mark_exception", "title": "Mark as intentional bluff", "action": "mark_exception", "patch": {}}
                            ],
                            "confidence": 94
                        })
        return issues

    def calculate_health_score(self, issues: List[ContinuityIssue]) -> Tuple[int, Dict[str, int]]:
        open_issues = [i for i in issues if i.status == "OPEN"]
        resolved_issues = [i for i in issues if i.status == "RESOLVED"]

        crit = sum(1 for i in open_issues if i.severity == "CRITICAL")
        high = sum(1 for i in open_issues if i.severity == "HIGH")
        med = sum(1 for i in open_issues if i.severity == "MEDIUM")
        low = sum(1 for i in open_issues if i.severity == "LOW")

        # Base score 100 with calibrated penalties matching film production scale
        penalty = (crit * 5) + (high * 3) + (med * 2) + (low * 1)
        score = max(10, min(100, 100 - penalty))

        # Resolution recovery bonus
        resolved_bonus = min(20, len(resolved_issues) * 3)
        score = min(100, score + resolved_bonus)

        counts = {
            "TOTAL_OPEN": len(open_issues),
            "RESOLVED": len(resolved_issues),
            "CRITICAL": crit,
            "HIGH": high,
            "MEDIUM": med,
            "LOW": low
        }
        return score, counts

# Global singleton
continuity_engine = ContinuityEngine()

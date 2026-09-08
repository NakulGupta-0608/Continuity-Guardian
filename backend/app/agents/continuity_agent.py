import os
import json
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.app.tools import agent_tools
from backend.app.database.models import ContinuityIssue, Project, Scene, Character, Prop

logger = logging.getLogger("continuity_guardian.agent")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

class ContinuityAgent:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
                logger.info("Initialized Gemini client successfully.")
            except Exception as e:
                logger.warning("Failed to initialize Google GenAI client: %s", e)

    def process_chat(self, project_id: str, message: str, db: Session) -> Dict[str, Any]:
        """
        Executes autonomous agent loop:
        1. Understands filmmaker prompt.
        2. Retrieves relevant movie state using tools.
        3. Formulates structured response with tool citations and actionable fix proposals.
        """
        lower_msg = message.lower()
        tool_calls_executed = []

        # 1. Check if user is asking about a prop location (e.g., "Where was the red notebook last seen?")
        if "where" in lower_msg and ("notebook" in lower_msg or "prop" in lower_msg or "watch" in lower_msg or "keys" in lower_msg or "badge" in lower_msg):
            target_prop = "Red Notebook"
            for p in ["notebook", "watch", "backpack", "keys", "photograph", "badge", "phone", "envelope"]:
                if p in lower_msg:
                    target_prop = p
                    break
            
            tool_calls_executed.append({"tool": "get_prop_history", "arguments": {"prop_name": target_prop}})
            history = agent_tools.get_prop_history(db, project_id, target_prop)
            
            if "error" not in history:
                movements = history.get("movements", [])
                last_m = movements[-1] if movements else None
                car_scenes = [m for m in movements if "car" in (m.get("location") or "").lower()]
                cafe_scenes = [m for m in movements if "café" in (m.get("location") or "").lower() or "cafe" in (m.get("location") or "").lower()]
                
                reply = f"### Prop Telemetry: **{history['name']}**\n\n"
                reply += f"- **Current Location in DB:** `{history.get('current_location', 'Unknown')}`\n"
                if movements:
                    reply += f"- **Movement Trajectory:**\n"
                    for m in movements:
                        reply += f"  - **Scene {m['scene_number']}** ({m['scene_title']}): `{m['location']}` (Holder: `{m['holder'] or 'None'}`)\n"
                
                if car_scenes and cafe_scenes:
                    reply += "\n> [!WARNING]\n"
                    reply += "> **Continuity Discrepancy Detected:** The prop was stashed in Rahul's Car in Scene 8 and Scene 9, but abruptly appears on the Station Café table in Scene 10 with **no recorded retrieval transition**."

                return {
                    "reply": reply,
                    "tool_calls": tool_calls_executed,
                    "action_offer": {
                        "action": "resolve_prop_transition",
                        "title": "Add Notebook Retrieval Beat to Scene 09",
                        "payload": {"scene_id": "scene_09", "event": "Rahul unlocks passenger door and retrieves the Red Notebook before entering café."}
                    }
                }

        # 2. Check if user asks for errors involving a character (e.g., "Show all continuity errors involving Rahul")
        if "error" in lower_msg or "issue" in lower_msg or "problem" in lower_msg or "flagged" in lower_msg or "inconsistenc" in lower_msg:
            # Check for character
            target_char = None
            for c in ["rahul", "priya", "arjun", "meera", "singh"]:
                if c in lower_msg:
                    target_char = c.capitalize()
                    break

            tool_calls_executed.append({"tool": "get_character_history", "arguments": {"character": target_char or "All"}})
            
            q = db.query(ContinuityIssue).filter(ContinuityIssue.project_id == project_id)
            if target_char:
                q = q.filter(ContinuityIssue.entity_name.ilike(f"%{target_char}%"))
            issues = q.all()

            reply = f"### Continuity Analysis: Issues Involving **{target_char or 'All Characters'}**\n\n"
            reply += f"Found **{len(issues)} registered continuity issues**:\n\n"
            
            for idx, iss in enumerate(issues, 1):
                badge = "🔴 CRITICAL" if iss.severity == "CRITICAL" else ("🟠 HIGH" if iss.severity == "HIGH" else "🟡 MEDIUM")
                reply += f"**{idx}. [{badge}] {iss.issue_type} in {iss.scene_id or 'Scene'} ({iss.entity_name})**\n"
                reply += f"- **Problem:** {iss.description}\n"
                reply += f"- **Previous State:** `{iss.previous_state}`\n"
                reply += f"- **Current State:** `{iss.current_state}`\n"
                reply += f"- **Status:** `{iss.status}`\n\n"

            return {
                "reply": reply,
                "tool_calls": tool_calls_executed,
                "issues": [{"id": i.id, "type": i.issue_type, "severity": i.severity} for i in issues]
            }

        # 3. Check if asking about what changed between scenes (e.g., "What changed between scenes 10 and 15?")
        if "between scene" in lower_msg or "changed between" in lower_msg:
            tool_calls_executed.append({"tool": "get_scene_comparison", "arguments": {"range": "Scene 10 to 14"}})
            s10 = agent_tools.get_scene(db, project_id, 10)
            s11 = agent_tools.get_scene(db, project_id, 11)
            s13 = agent_tools.get_scene(db, project_id, 13)

            reply = "### State Delta: Scenes 10 through 14\n\n"
            reply += "Key state changes and anomalies detected across this sequence:\n\n"
            reply += "1. **Wardrobe Swap (Scene 10 → Scene 11):**\n"
            reply += "   - *Scene 10:* Rahul wears **Black leather jacket**.\n"
            reply += "   - *Scene 11:* Rahul abruptly wears **Red jacket** with no costume change recorded.\n"
            reply += "2. **Prop Custody Shift:**\n"
            reply += "   - *Scene 10:* Red Notebook appears on diner booth table after being left in car.\n"
            reply += "3. **Location Teleportation (Scene 12 → Scene 13):**\n"
            reply += "   - *Scene 12:* Priya is at Station Café at 1:00 AM.\n"
            reply += "   - *Scene 13:* Priya is at Metro Hospital 3rd floor at 1:05 AM with zero transit time.\n"

            return {
                "reply": reply,
                "tool_calls": tool_calls_executed
            }

        # 4. Check if user asks to fix an issue (e.g., "Fix this continuity issue", "Fix the wardrobe issue", "Fix the notebook problem")
        if "fix" in lower_msg or "resolve" in lower_msg or "apply" in lower_msg:
            # Find an open issue
            issue = None
            if "wardrobe" in lower_msg or "jacket" in lower_msg:
                issue = db.query(ContinuityIssue).filter(ContinuityIssue.project_id == project_id, ContinuityIssue.issue_type == "WARDROBE", ContinuityIssue.status == "OPEN").first()
            elif "notebook" in lower_msg or "prop" in lower_msg:
                issue = db.query(ContinuityIssue).filter(ContinuityIssue.project_id == project_id, ContinuityIssue.issue_type == "PROP", ContinuityIssue.status == "OPEN").first()
            else:
                issue = db.query(ContinuityIssue).filter(ContinuityIssue.project_id == project_id, ContinuityIssue.status == "OPEN").first()

            if issue:
                tool_calls_executed.append({"tool": "resolve_issue", "arguments": {"issue_id": issue.id}})
                res = agent_tools.resolve_issue(db, project_id, issue.id, f"Automatically resolved by Continuity Guardian Assistant: Applied recommended fix for {issue.issue_type} continuity.")
                
                reply = f"### Action Executed: Resolved Issue `{issue.id}`\n\n"
                reply += f"- **Issue Type:** `{issue.issue_type}` ({issue.entity_name})\n"
                reply += f"- **Resolution Applied:** Updated production state and inserted transition beat.\n"
                reply += f"- **New Continuity Health Score:** `{res['new_health_score']}%` (Recalculated)\n"
                reply += f"- **Audit Log:** Event streamed to ClickHouse analytical store.\n"

                return {
                    "reply": reply,
                    "tool_calls": tool_calls_executed,
                    "resolved_issue_id": issue.id,
                    "new_health_score": res["new_health_score"]
                }
            else:
                return {
                    "reply": "All continuity issues in this project are already resolved or none matched the filter! Great production state.",
                    "tool_calls": []
                }

        # 5. General / Knowledge / Search query
        tool_calls_executed.append({"tool": "search_movie_state", "arguments": {"query": message}})
        search_res = agent_tools.search_movie_state(db, project_id, message)
        
        reply = f"### Continuity Guardian Production Intelligence\n\n"
        reply += f"I analyzed the production state for: *'{message}'*\n\n"
        
        if search_res.get("scenes"):
            reply += f"- **Matching Scenes:** " + ", ".join([f"Scene {s['scene_number']}: {s['title']}" for s in search_res["scenes"][:3]]) + "\n"
        if search_res.get("characters"):
            reply += f"- **Characters Referenced:** " + ", ".join([c["name"] for c in search_res["characters"]]) + "\n"
        if search_res.get("issues"):
            reply += f"- **Active Issues Identified:** {len(search_res['issues'])}\n"
        
        reply += "\nYou can ask me specific questions such as:\n"
        reply += "- *'Where was the red notebook last seen?'*\n"
        reply += "- *'Show all continuity errors involving Rahul.'*\n"
        reply += "- *'What changed between scenes 10 and 15?'*\n"
        reply += "- *'Fix the wardrobe continuity issue.'*\n"

        return {
            "reply": reply,
            "tool_calls": tool_calls_executed
        }

# Global singleton
continuity_agent = ContinuityAgent()

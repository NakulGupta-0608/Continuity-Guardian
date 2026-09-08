import re
import uuid
import json
from typing import List, Dict, Any

class ScriptParser:
    """
    Parses industry standard screenplay text or Fountain formatting into structured scenes,
    extracting Scene Heading, Time, Environment, Characters present, and Action Events.
    """
    SLUG_PATTERN = re.compile(r'^(INT\.|EXT\.|INT/EXT\.|EXT/INT\.)\s+(.*?)\s+-\s+(DAY|NIGHT|DUSK|DAWN|CONTINUOUS|LATER|EVENING|AFTERNOON|MORNING)', re.IGNORECASE)

    @classmethod
    def parse_screenplay_text(cls, script_text: str) -> List[Dict[str, Any]]:
        lines = script_text.strip().split("\n")
        scenes = []
        curr_scene = None
        scene_num = 1

        for line in lines:
            trimmed = line.strip()
            slug_match = cls.SLUG_PATTERN.match(trimmed)

            if slug_match:
                if curr_scene:
                    scenes.append(curr_scene)
                    scene_num += 1

                env_type = slug_match.group(1).upper()
                location = slug_match.group(2).strip()
                time_of_day = slug_match.group(3).upper()

                curr_scene = {
                    "scene_number": scene_num,
                    "title": f"{env_type} {location} - {time_of_day}",
                    "location_name": location,
                    "environment_type": "Interior" if "INT" in env_type else "Exterior",
                    "time_of_day": time_of_day,
                    "weather": "Rain" if "rain" in script_text.lower() else "Clear",
                    "summary": "",
                    "script_content": trimmed + "\n",
                    "events": [],
                    "characters_detected": set(),
                    "props_detected": set()
                }
            elif curr_scene:
                curr_scene["script_content"] += line + "\n"
                # Detect capitalized character names in lines
                words = re.findall(r'\b[A-Z]{3,15}\b', trimmed)
                skip_words = {"INT", "EXT", "FADE", "CUT", "THE", "NIGHT", "DAY", "DUSK", "DAWN", "CONTINUOUS", "SCENE"}
                for w in words:
                    if w not in skip_words:
                        curr_scene["characters_detected"].add(w.capitalize())
                
                # Detect action event lines
                if len(trimmed) > 10 and not trimmed.startswith("("):
                    if len(curr_scene["events"]) < 3:
                        curr_scene["events"].append(trimmed)

        if curr_scene:
            scenes.append(curr_scene)

        # Convert sets to lists
        for s in scenes:
            s["characters"] = list(s["characters_detected"])
            del s["characters_detected"]
            del s["props_detected"]
            if not s["summary"]:
                s["summary"] = f"Action at {s['location_name']} during {s['time_of_day']}."

        return scenes

# Global singleton
script_parser = ScriptParser()

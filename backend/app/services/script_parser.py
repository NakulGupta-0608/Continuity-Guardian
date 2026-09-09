import re
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("continuity_guardian.script_parser")

class ScriptParser:
    """
    Robust multi-format script and screenplay parser.
    Supports:
    1. Standard Screenplay Sluglines (INT./EXT. LOCATION - TIME)
    2. Structured Scene Specs (Scene 1, Location: ..., Characters: ..., Wardrobe: ..., Props: ...)
    3. Natural Language / Freeform Scene Descriptions
    """

    SLUG_PATTERN = re.compile(
        r'^\s*(?:(\d+)[\.\s]+)?(?:(INT\.|EXT\.|INT/EXT\.|EXT/INT\.|I/E\.?)\s+)?(.*?)(?:\s+[-–—]\s*(.*?))?$',
        re.IGNORECASE
    )

    SCENE_HEADER_PATTERN = re.compile(
        r'^\s*(?:#+\s*)?(?:SCENE|Scene)\s*(\d+)[:\s\-–—]*(.*)$',
        re.IGNORECASE
    )

    TIME_KEYWORDS = ["NIGHT", "DAY", "DUSK", "DAWN", "CONTINUOUS", "LATER", "EVENING", "AFTERNOON", "MORNING", "MIDNIGHT", "NOON"]
    WEATHER_KEYWORDS = ["RAIN", "HEAVY RAIN", "STORM", "FOG", "CLEAR", "SNOW", "SUNNY", "DRIZZLE", "OVERCAST"]

    @classmethod
    def parse_screenplay_text(cls, text: str) -> List[Dict[str, Any]]:
        cleaned_text = text.strip()
        if not cleaned_text:
            return []

        # Check if text is structured key-value format (e.g. contains "Location:" or "Scene 1")
        if re.search(r'\bLocation\s*:', cleaned_text, re.IGNORECASE) or re.search(r'\bScene\s+\d+\b', cleaned_text, re.IGNORECASE):
            structured_scenes = cls._parse_structured_format(cleaned_text)
            if structured_scenes:
                return structured_scenes

        # Check for standard sluglines
        slugline_scenes = cls._parse_slugline_format(cleaned_text)
        if slugline_scenes:
            return slugline_scenes

        # Fallback: treat as single scene or double-newline blocks
        return cls._parse_freeform_format(cleaned_text)

    @classmethod
    def _parse_structured_format(cls, text: str) -> List[Dict[str, Any]]:
        """
        Parses structured format:
        Scene 1 / Scene 12
        Location: Café
        Time: 8:00 PM
        Weather: Rain
        Characters: Rahul, Priya
        Rahul clothing: Black jacket
        Rahul condition: Left arm injured
        Props: Red notebook, Coffee cup
        Events: Rahul gives notebook to Priya
        """
        raw_scenes = re.split(r'\n(?=\s*(?:#+\s*)?(?:SCENE|Scene)\s+\d+)', text, flags=re.IGNORECASE)
        if len(raw_scenes) == 1 and not re.match(r'^\s*(?:#+\s*)?(?:SCENE|Scene)\s+\d+', raw_scenes[0], re.IGNORECASE):
            # Try splitting by "Scene:"
            raw_scenes = re.split(r'\n(?=\s*Scene\s*:)', text, flags=re.IGNORECASE)

        parsed_scenes = []
        scene_counter = 1

        for block in raw_scenes:
            block = block.strip()
            if not block:
                continue

            scene_num = scene_counter
            title = f"Scene {scene_num}"
            location = "Main Location"
            time_of_day = "Day"
            weather = "Clear"
            summary = ""
            events = []
            characters_map: Dict[str, Dict[str, Any]] = {}
            props_list: List[Dict[str, Any]] = []

            lines = block.split("\n")
            for line in lines:
                l_str = line.strip()
                if not l_str:
                    continue

                # Header: Scene 1: Title
                h_match = cls.SCENE_HEADER_PATTERN.match(l_str)
                if h_match:
                    try:
                        scene_num = int(h_match.group(1))
                    except ValueError:
                        pass
                    rest = h_match.group(2).strip()
                    if rest:
                        title = rest
                    continue

                # Location:
                loc_match = re.match(r'^Location\s*:\s*(.*)$', l_str, re.IGNORECASE)
                if loc_match:
                    location = loc_match.group(1).strip()
                    continue

                # Time:
                time_match = re.match(r'^Time\s*(?:of\s*day)?\s*:\s*(.*)$', l_str, re.IGNORECASE)
                if time_match:
                    time_of_day = time_match.group(1).strip()
                    continue

                # Weather:
                weather_match = re.match(r'^Weather\s*:\s*(.*)$', l_str, re.IGNORECASE)
                if weather_match:
                    weather = weather_match.group(1).strip()
                    continue

                # Characters: Rahul, Priya
                char_match = re.match(r'^Characters?\s*:\s*(.*)$', l_str, re.IGNORECASE)
                if char_match:
                    names = re.split(r'[,;]+', char_match.group(1))
                    for n in names:
                        n_clean = n.strip()
                        if n_clean and len(n_clean) >= 2:
                            if n_clean not in characters_map:
                                characters_map[n_clean] = {
                                    "name": n_clean,
                                    "wardrobe": "Standard attire",
                                    "condition": "Healthy",
                                    "dialogue": []
                                }
                    continue

                # Character specific clothing: e.g. "Rahul clothing: Black jacket" or "Wardrobe: Black jacket"
                wardrobe_match = re.match(r'^(?:([A-Za-z0-9_\s]+)\s+)?(?:clothing|clothes|wardrobe|costume)\s*:\s*(.*)$', l_str, re.IGNORECASE)
                if wardrobe_match:
                    c_name = (wardrobe_match.group(1) or "").strip()
                    wardrobe_val = wardrobe_match.group(2).strip()
                    if c_name:
                        if c_name not in characters_map:
                            characters_map[c_name] = {"name": c_name, "wardrobe": wardrobe_val, "condition": "Healthy", "dialogue": []}
                        else:
                            characters_map[c_name]["wardrobe"] = wardrobe_val
                    else:
                        for c in characters_map.values():
                            c["wardrobe"] = wardrobe_val
                    continue

                # Character specific condition: e.g. "Rahul condition: Left arm injured" or "Condition: Injured"
                cond_match = re.match(r'^(?:([A-Za-z0-9_\s]+)\s+)?condition\s*:\s*(.*)$', l_str, re.IGNORECASE)
                if cond_match:
                    c_name = (cond_match.group(1) or "").strip()
                    cond_val = cond_match.group(2).strip()
                    if c_name:
                        if c_name not in characters_map:
                            characters_map[c_name] = {"name": c_name, "wardrobe": "Standard attire", "condition": cond_val, "dialogue": []}
                        else:
                            characters_map[c_name]["condition"] = cond_val
                    else:
                        for c in characters_map.values():
                            c["condition"] = cond_val
                    continue

                # Props: Red notebook, Coffee cup
                prop_match = re.match(r'^Props?\s*:\s*(.*)$', l_str, re.IGNORECASE)
                if prop_match:
                    p_names = re.split(r'[,;]+', prop_match.group(1))
                    for p in p_names:
                        p_clean = p.strip()
                        if p_clean:
                            props_list.append({
                                "name": p_clean,
                                "location": location,
                                "holder": ""
                            })
                    continue

                # Events: Rahul gives notebook to Priya
                event_match = re.match(r'^Events?\s*:\s*(.*)$', l_str, re.IGNORECASE)
                if event_match:
                    ev_text = event_match.group(1).strip()
                    if ev_text:
                        events.append(ev_text)
                    continue

                # Narrative action lines
                if len(l_str) > 10 and not l_str.startswith("("):
                    if len(events) < 4:
                        events.append(l_str)

            # Auto-extract mentioned characters and props if not explicitly declared
            cls._enrich_unstructured_elements(block, characters_map, props_list, location)

            parsed_scenes.append({
                "scene_number": scene_num,
                "title": f"Scene {scene_num} - {location}",
                "location_name": location,
                "environment_type": "Interior" if "INT" in location.upper() or any(w in location.lower() for w in ["café", "cafe", "room", "office", "hospital", "house", "bar", "kitchen"]) else "Exterior",
                "time_of_day": time_of_day,
                "weather": weather,
                "summary": summary or f"Events at {location} during {time_of_day}.",
                "script_content": block,
                "events": events or [f"Action at {location}"],
                "dialogue_facts": [],
                "characters": list(characters_map.values()),
                "props": props_list
            })
            scene_counter += 1

        return parsed_scenes

    @classmethod
    def _parse_slugline_format(cls, text: str) -> List[Dict[str, Any]]:
        """
        Parses standard screenplay slugline format (INT./EXT. LOCATION - TIME).
        """
        lines = text.split("\n")
        scenes = []
        curr_scene = None
        scene_num = 1

        slug_regex = re.compile(r'^\s*(INT\.|EXT\.|INT/EXT\.|EXT/INT\.|I/E\.?)\s+([^-\n\r]+)(?:[-–—]\s*(.*))?$', re.IGNORECASE)

        for line in lines:
            trimmed = line.strip()
            match = slug_regex.match(trimmed)

            if match:
                if curr_scene:
                    cls._finalize_scene(curr_scene)
                    scenes.append(curr_scene)
                    scene_num += 1

                env_type = match.group(1).upper()
                location = match.group(2).strip()
                time_part = (match.group(3) or "DAY").strip().upper()

                # Check weather in time part or script text
                weather = "Clear"
                for w in cls.WEATHER_KEYWORDS:
                    if w in text.upper():
                        weather = w.capitalize()
                        break

                curr_scene = {
                    "scene_number": scene_num,
                    "title": f"{env_type} {location} - {time_part}",
                    "location_name": location,
                    "environment_type": "Interior" if "INT" in env_type else "Exterior",
                    "time_of_day": time_part,
                    "weather": weather,
                    "summary": "",
                    "script_content": trimmed + "\n",
                    "events": [],
                    "characters_map": {},
                    "props_list": [],
                    "raw_lines": []
                }
            elif curr_scene:
                curr_scene["script_content"] += line + "\n"
                curr_scene["raw_lines"].append(trimmed)

        if curr_scene:
            cls._finalize_scene(curr_scene)
            scenes.append(curr_scene)

        return scenes

    @classmethod
    def _finalize_scene(cls, scene_dict: Dict[str, Any]):
        raw_text = "\n".join(scene_dict["raw_lines"])
        cls._enrich_unstructured_elements(
            raw_text,
            scene_dict["characters_map"],
            scene_dict["props_list"],
            scene_dict["location_name"]
        )

        for l in scene_dict["raw_lines"]:
            if len(l) > 15 and not l.isupper() and not l.startswith("(") and len(scene_dict["events"]) < 3:
                scene_dict["events"].append(l)

        scene_dict["characters"] = list(scene_dict["characters_map"].values())
        scene_dict["props"] = scene_dict["props_list"]
        del scene_dict["characters_map"]
        del scene_dict["props_list"]
        del scene_dict["raw_lines"]
        if not scene_dict["summary"]:
            scene_dict["summary"] = f"Action at {scene_dict['location_name']} ({scene_dict['time_of_day']})."

    @classmethod
    def _parse_freeform_format(cls, text: str) -> List[Dict[str, Any]]:
        """
        Parses freeform script or paragraph blocks.
        """
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        if not paragraphs:
            paragraphs = [text.strip()]

        scenes = []
        for idx, p in enumerate(paragraphs, 1):
            char_map: Dict[str, Dict[str, Any]] = {}
            props: List[Dict[str, Any]] = []
            cls._enrich_unstructured_elements(p, char_map, props, "Scene Location")

            scenes.append({
                "scene_number": idx,
                "title": f"Scene {idx}",
                "location_name": f"Location {idx}",
                "environment_type": "Interior",
                "time_of_day": "Day",
                "weather": "Clear",
                "summary": p[:140] + ("..." if len(p) > 140 else ""),
                "script_content": p,
                "events": [p[:100]],
                "dialogue_facts": [],
                "characters": list(char_map.values()),
                "props": props
            })
        return scenes

    @classmethod
    def _enrich_unstructured_elements(cls, text: str, characters_map: Dict[str, Dict[str, Any]], props_list: List[Dict[str, Any]], location: str):
        """
        Extracts character names, wardrobe descriptions, injuries, and common props from script text.
        """
        # Detect uppercase character names (e.g. RAHUL, PRIYA, JOHN, ALICE)
        uppercase_names = re.findall(r'\b[A-Z]{3,15}\b', text)
        skip = {"INT", "EXT", "FADE", "CUT", "THE", "NIGHT", "DAY", "DUSK", "DAWN", "CONTINUOUS", "SCENE", "AND", "WITH", "FROM"}
        
        for name in uppercase_names:
            if name not in skip:
                c_name = name.capitalize()
                if c_name not in characters_map:
                    characters_map[c_name] = {
                        "name": c_name,
                        "wardrobe": "Standard costume",
                        "condition": "Healthy",
                        "dialogue": []
                    }

        # Detect wardrobe keywords near character (e.g. "jacket", "shirt", "coat", "dress", "jeans", "suit")
        wardrobe_patterns = [
            r'(black\s+jacket|red\s+jacket|leather\s+jacket|trench\s+coat|blue\s+shirt|white\s+shirt|blue\s+jeans|sweater|hoodie|suit|uniform)',
            r'wearing\s+([a-zA-Z\s]{4,30})(?:,|\.|\n|$)',
            r'dressed\s+in\s+([a-zA-Z\s]{4,30})(?:,|\.|\n|$)'
        ]
        for pat in wardrobe_patterns:
            matches = re.findall(pat, text, re.IGNORECASE)
            for m in matches:
                m_str = m.strip() if isinstance(m, str) else m[0].strip()
                if m_str and len(m_str) > 3:
                    # Assign to first character found if any
                    for c in characters_map.values():
                        if c["wardrobe"] == "Standard costume":
                            c["wardrobe"] = m_str
                            break

        # Detect physical condition / injuries
        injury_patterns = [
            r'(left\s+arm\s+injured|bleeding|lacerated|wounded|unconscious|bandaged|limping|bruised|healthy)'
        ]
        for pat in injury_patterns:
            matches = re.findall(pat, text, re.IGNORECASE)
            for m in matches:
                m_str = m.strip()
                for c in characters_map.values():
                    c["condition"] = m_str.capitalize()
                    break

        # Detect props (notebook, watch, backpack, keys, phone, badge, gun, knife, envelope, letter)
        prop_keywords = ["notebook", "watch", "backpack", "keys", "phone", "badge", "photograph", "envelope", "letter", "briefcase", "laptop", "gun", "knife"]
        for pk in prop_keywords:
            if re.search(rf'\b{pk}\b', text, re.IGNORECASE):
                # Format prop name
                p_name = pk.capitalize()
                if not any(p["name"].lower() == p_name.lower() for p in props_list):
                    props_list.append({
                        "name": p_name,
                        "location": location,
                        "holder": list(characters_map.keys())[0] if characters_map else ""
                    })

# Global singleton
script_parser = ScriptParser()

import json
import datetime
from backend.app.database.models import (
    Project, Scene, Character, SceneCharacter,
    Prop, SceneProp, Location, ContinuityIssue, ProductionNote, AuditEvent
)

DEMO_PROJECT_ID = "proj_midnight_7"

def seed_demo_project(db):
    # Check if already seeded
    existing = db.query(Project).filter(Project.id == DEMO_PROJECT_ID).first()
    if existing:
        return existing

    now = datetime.datetime.utcnow()

    # 1. Create Project
    project = Project(
        id=DEMO_PROJECT_ID,
        title="Midnight at Platform 7",
        genre="Neo-Noir Mystery / Thriller",
        description="An investigative reporter and an estranged railway supervisor unravel a syndicate conspiracy at an abandoned industrial rail terminal during a torrential midnight downpour.",
        image_url="https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?w=1200&q=80",
        language="English / Hindi",
        status="Production",
        health_score=82,
        created_at=now
    )
    db.add(project)

    # 2. Create Locations
    locations_data = [
        {"id": "loc_platform_7", "name": "Platform 7", "description": "Dilapidated outdoor railway platform, rusted iron girders, rain-swept tracks.", "env": "Exterior", "rules": "Constant night rain, cold mist."},
        {"id": "loc_station_cafe", "name": "Station Café", "description": "24-hour diner opposite the freight tracks, yellow vinyl booths, buzzing fluorescent tubes.", "env": "Interior", "rules": "Warm shelter, muffled rain on windows."},
        {"id": "loc_rahul_car", "name": "Rahul's Car", "description": "Old 2008 navy sedan parked on gravel shoulder beside service road.", "env": "Interior / Vehicle", "rules": "Fogged windows, wiper blades scraping."},
        {"id": "loc_metro_hospital", "name": "Metro Hospital", "description": "Stark trauma bay and waiting corridor with bleached tiles and harsh overhead LEDs.", "env": "Interior", "rules": "Sterile lighting, constant distant paging."}
    ]
    for loc in locations_data:
        db.add(Location(
            id=loc["id"],
            project_id=DEMO_PROJECT_ID,
            name=loc["name"],
            description=loc["description"],
            environment_type=loc["env"],
            time_rules=loc["rules"]
        ))

    # 3. Create Characters
    characters_data = [
        {
            "id": "char_rahul",
            "name": "Rahul",
            "role": "Lead Protagonist",
            "age": "32",
            "appearance": "Tall, haggard expression, unkempt dark hair, stubble.",
            "default_wardrobe": "Black leather jacket, white crewneck tee, dark wash jeans.",
            "default_condition": "Healthy",
            "current_location": "Station Café",
            "relationships": {"Priya": "Trusted ally & investigative partner", "Meera": "Protective older brother", "Arjun": "Former coworker turned rival", "Inspector Singh": "Suspicious interrogator"},
            "known_facts": ["Father worked on Platform 7 track records", "Received mysterious midnight rendezvous cipher"],
            "possessions": ["Silver watch", "Car keys"]
        },
        {
            "id": "char_priya",
            "name": "Priya",
            "role": "Investigative Journalist",
            "age": "29",
            "appearance": "Athletic, sharp focused gaze, hair tied back.",
            "default_wardrobe": "Beige belted trench coat, charcoal trousers, waterproof ankle boots.",
            "default_condition": "Healthy",
            "current_location": "Station Café",
            "relationships": {"Rahul": "Collaborator and confidante", "Inspector Singh": "Adversarial source"},
            "known_facts": ["Syndicate is laundering cargo manifests through Platform 7", "Knows informant was silenced"],
            "possessions": ["Black backpack", "Phone"]
        },
        {
            "id": "char_arjun",
            "name": "Arjun",
            "role": "Chief Yard Antagonist",
            "age": "41",
            "appearance": "Broad-shouldered, scar across right eyebrow, predatory posture.",
            "default_wardrobe": "Dark navy industrial windbreaker, reflective utility pants, steel-toe boots.",
            "default_condition": "Healthy",
            "current_location": "Platform 7",
            "relationships": {"Rahul": "Despises his persistence", "Inspector Singh": "Secret financial associate"},
            "known_facts": ["Knows exact contents of sealed freight containers", "Orders midnight train routing"],
            "possessions": ["Car keys", "Phone"]
        },
        {
            "id": "char_meera",
            "name": "Meera",
            "role": "Rahul's Sister",
            "age": "24",
            "appearance": "Expressive eyes, artistic demeanour, wears silver hoop earrings.",
            "default_wardrobe": "Oversized forest green knit sweater, beige corduroy trousers.",
            "default_condition": "Healthy",
            "current_location": "Metro Hospital",
            "relationships": {"Rahul": "Believes in his innocence", "Priya": "Appreciates her support"},
            "known_facts": ["Found father's old journal duplicate in family storage"],
            "possessions": ["Old photograph"]
        },
        {
            "id": "char_singh",
            "name": "Inspector Singh",
            "role": "Senior Police Investigator",
            "age": "49",
            "appearance": "Grizzled mustache, observant posture, heavy smoker.",
            "default_wardrobe": "Brown distressed leather jacket, khaki police slacks, wool scarf.",
            "default_condition": "Healthy",
            "current_location": "Platform 7",
            "relationships": {"Rahul": "Suspect in the cargo breach", "Arjun": "Tense underground dealings"},
            "known_facts": ["Discovered cipher fragments at the train depot"],
            "possessions": ["Police badge", "Phone"]
        }
    ]
    for c in characters_data:
        db.add(Character(
            id=c["id"],
            project_id=DEMO_PROJECT_ID,
            name=c["name"],
            role=c["role"],
            age=c["age"],
            appearance=c["appearance"],
            default_wardrobe=c["default_wardrobe"],
            default_condition=c["default_condition"],
            current_location=c["current_location"],
            relationships_json=json.dumps(c["relationships"]),
            known_facts_json=json.dumps(c["known_facts"]),
            possessions_json=json.dumps(c["possessions"]),
            created_at=now
        ))

    # 4. Create Props
    props_data = [
        {"id": "prop_red_notebook", "name": "Red Notebook", "desc": "Worn moleskine notebook filled with handwritten train arrival times and encrypted freight codes.", "cat": "Document", "loc": "Rahul's Car", "holder": ""},
        {"id": "prop_silver_watch", "name": "Silver Watch", "desc": "Vintage 1974 mechanical chronograph with cracked bezel.", "cat": "Accessory", "loc": "Rahul", "holder": "char_rahul"},
        {"id": "prop_black_backpack", "name": "Black Backpack", "desc": "Cordura ballistic waterproof backpack containing camera lenses and audio recorder.", "cat": "Container", "loc": "Priya", "holder": "char_priya"},
        {"id": "prop_car_keys", "name": "Car Keys", "desc": "Heavy brass key ring with electronic clicker and blue cord fob.", "cat": "Tool", "loc": "Rahul", "holder": "char_rahul"},
        {"id": "prop_old_photograph", "name": "Old Photograph", "desc": "Black and white portrait of 1998 railway crew posing in front of Engine 412.", "cat": "Document", "loc": "Station Café", "holder": ""},
        {"id": "prop_phone", "name": "Burner Phone", "desc": "Rugged black push-button mobile phone with scrambled messaging SIM.", "cat": "Electronics", "loc": "Priya", "holder": "char_priya"},
        {"id": "prop_police_badge", "name": "Police Badge", "desc": "Gold state CID inspector shield in black leather folding wallet.", "cat": "Badge", "loc": "Inspector Singh", "holder": "char_singh"},
        {"id": "prop_envelope", "name": "Sealed Envelope", "desc": "Thick manila envelope stamped 'CONFIDENTIAL / FREIGHT 7' with unbroken red wax seal.", "cat": "Document", "loc": "Station Café", "holder": ""}
    ]
    for p in props_data:
        db.add(Prop(
            id=p["id"],
            project_id=DEMO_PROJECT_ID,
            name=p["name"],
            description=p["desc"],
            category=p["cat"],
            current_location=p["loc"],
            current_holder=p["holder"],
            created_at=now
        ))

    # 5. Create 14 Scenes
    scenes_data = [
        {
            "id": "scene_01",
            "scene_number": 1,
            "title": "Midnight Rendezvous at Platform 7",
            "location_name": "Platform 7",
            "time_of_day": "11:58 PM",
            "weather": "Heavy Rain",
            "emotional_tone": "Tense / Foreboding",
            "summary": "Rahul waits in the lashing rain under the rusted awning of Platform 7. The midnight cargo whistle sounds in the distance.",
            "script": "EXT. PLATFORM 7 - NIGHT\nRain cascades down corrugated tin roofs. RAHUL pulls his black leather jacket collar up against the biting wind. His silver watch ticks past 11:58 PM. Footsteps splash in puddles behind him.",
            "events": ["Rahul arrives at Platform 7", "Checks his silver watch", "Hears mysterious cargo whistle"],
            "dialogue_facts": ["Rahul is meeting an unknown informant", "The 12:05 AM cargo train is unscheduled"],
            "seq": 1,
            "characters": [
                {"char_id": "char_rahul", "wardrobe": "Black leather jacket, white tee, blue jeans", "condition": "Healthy", "location": "Platform 7", "known_facts": ["Meeting informant at midnight"], "dialogue": ["Where are you? It's almost midnight."]}
            ],
            "props": [
                {"prop_id": "prop_silver_watch", "location": "Rahul's wrist", "holder": "char_rahul", "state": "Ticking at 11:58 PM", "event": "Rahul checks the dial"}
            ]
        },
        {
            "id": "scene_02",
            "scene_number": 2,
            "title": "The Cipher Exchange & Premature Knowledge",
            "location_name": "Platform 7",
            "time_of_day": "Monday 8:00 PM",
            "weather": "Heavy Rain",
            "emotional_tone": "Suspicious",
            "summary": "Priya steps out of the steam holding a sealed envelope. Rahul confronts her, mysteriously knowing Arjun's embezzled cargo amount before discovering any files.",
            "script": "EXT. PLATFORM 7 - CONTINUOUS\nPRIYA emerges from the gloom, clutching a yellow courier envelope.\nPRIYA: 'You shouldn't have come alone, Rahul.'\nRAHUL: 'I know Arjun embezzled the entire 200,000 shipment through this freight line.'\nPRIYA: (stunned) 'How could you possibly know that already?'",
            "events": ["Priya hands sealed envelope to Rahul", "Rahul reveals knowledge about Arjun's 200,000 shipment prematurely"],
            "dialogue_facts": ["Rahul claims Arjun embezzled 200,000 shipment (KNOWLEDGE CONTRADICTION: unrevealed at this point)"],
            "seq": 2,
            "characters": [
                {"char_id": "char_rahul", "wardrobe": "Black leather jacket, white tee, blue jeans", "condition": "Healthy", "location": "Platform 7", "known_facts": ["Arjun embezzled 200,000 shipment (LEAK)"], "dialogue": ["I know Arjun embezzled the entire 200,000 shipment."]},
                {"char_id": "char_priya", "wardrobe": "Beige belted trench coat, charcoal trousers", "condition": "Healthy", "location": "Platform 7", "known_facts": ["Has sealed envelope"], "dialogue": ["You shouldn't have come alone, Rahul."]}
            ],
            "props": [
                {"prop_id": "prop_envelope", "location": "Priya's hands", "holder": "char_priya", "state": "Sealed red wax", "event": "Priya holds out envelope to Rahul"}
            ]
        },
        {
            "id": "scene_03",
            "scene_number": 3,
            "title": "Confrontation by the Tracks (Timeline Inversion)",
            "location_name": "Platform 7",
            "time_of_day": "Monday 6:30 PM", # Intentional chronology contradiction: Scene 2 was 8:00 PM
            "weather": "Foggy Rain",
            "emotional_tone": "Hostile",
            "summary": "Arjun and Inspector Singh corner Rahul by the coal siding. An argument breaks out over track access permits.",
            "script": "EXT. PLATFORM 7 - TRACKS\nARJUN steps off the locomotive footplate, flashlight beam blinding Rahul.\nINSPECTOR SINGH steps forward flashing his police shield.\nARJUN: 'Platform 7 is restricted territory tonight.'",
            "events": ["Arjun blocks path", "Singh flashes badge", "Scene timestamp shows 6:30 PM despite following 8:00 PM scene"],
            "dialogue_facts": ["Arjun claims authorization from terminal authorities"],
            "seq": 3,
            "characters": [
                {"char_id": "char_rahul", "wardrobe": "Black leather jacket, white tee, blue jeans", "condition": "Healthy", "location": "Platform 7", "known_facts": [], "dialogue": ["I have clearance to be here."]},
                {"char_id": "char_arjun", "wardrobe": "Dark navy windbreaker, utility pants", "condition": "Healthy", "location": "Platform 7", "known_facts": ["Restricted movement order"], "dialogue": ["Platform 7 is restricted territory tonight."]},
                {"char_id": "char_singh", "wardrobe": "Brown distressed leather jacket, police slacks", "condition": "Healthy", "location": "Platform 7", "known_facts": ["Investigating yard breach"], "dialogue": ["Step back, Rahul."]}
            ],
            "props": [
                {"prop_id": "prop_police_badge", "location": "Singh's coat", "holder": "char_singh", "state": "Flashed at Rahul", "event": "Singh brandishes shield"}
            ]
        },
        {
            "id": "scene_04",
            "scene_number": 4,
            "title": "The Scuffle at Signal Box B",
            "location_name": "Platform 7",
            "time_of_day": "Night",
            "weather": "Heavy Rain",
            "emotional_tone": "Violent / Urgent",
            "summary": "A physical struggle ensues near the switch levers. Rahul is shoved into shattered glass, sustaining a severe laceration to his left arm.",
            "script": "EXT. SIGNAL BOX B - NIGHT\nArjun lunges. Rahul dodges but trips into broken window frames of the derelict signal box. Jagged glass slices deep into Rahul's left forearm. Blood pools on his white shirt sleeve.",
            "events": ["Rahul shoved into broken window", "Left arm severely cut and bleeding heavily", "Priya helps Rahul escape into the fog"],
            "dialogue_facts": ["Rahul is injured in the left arm"],
            "seq": 4,
            "characters": [
                {"char_id": "char_rahul", "wardrobe": "Black leather jacket, white tee (bloodied left sleeve)", "condition": "Left arm injured / bleeding", "location": "Platform 7", "known_facts": [], "dialogue": ["Get off me!"]},
                {"char_id": "char_arjun", "wardrobe": "Dark navy windbreaker", "condition": "Healthy", "location": "Platform 7", "known_facts": [], "dialogue": ["You should have walked away, Rahul."]}
            ],
            "props": [
                {"prop_id": "prop_car_keys", "location": "Rahul's pocket", "holder": "char_rahul", "state": "Intact", "event": "Rahul grabs car keys"}
            ]
        },
        {
            "id": "scene_05",
            "scene_number": 5,
            "title": "Makeshift Bandage in the Service Alley",
            "location_name": "Platform 7",
            "time_of_day": "Night",
            "weather": "Drizzle",
            "emotional_tone": "Painful / Adrenaline",
            "summary": "Priya ties a makeshift tourniquet around Rahul's wounded left arm using her scarf.",
            "script": "EXT. SERVICE ALLEY - NIGHT\nPriya wraps Rahul's bleeding left forearm tightly with her wool scarf. Rahul winces in acute pain.\nPRIYA: 'You need stitches. We need to reach a clinic.'",
            "events": ["Priya bandages Rahul's injured arm", "Rahul winces from left arm injury"],
            "dialogue_facts": ["Rahul's left arm requires medical stitches"],
            "seq": 5,
            "characters": [
                {"char_id": "char_rahul", "wardrobe": "Black leather jacket, bloodied sleeve, makeshift bandage", "condition": "Left arm injured / bandaged", "location": "Platform 7", "known_facts": [], "dialogue": ["Just wrap it tight. We don't have time."]},
                {"char_id": "char_priya", "wardrobe": "Beige belted trench coat", "condition": "Healthy", "location": "Platform 7", "known_facts": [], "dialogue": ["You need stitches."]}
            ],
            "props": []
        },
        {
            "id": "scene_06",
            "scene_number": 6,
            "title": "Inspection of the Outer Perimeter (Spontaneous Healing)",
            "location_name": "Platform 7",
            "time_of_day": "Night",
            "weather": "Clear Sky", # Weather shift
            "emotional_tone": "Inquisitive",
            "summary": "Rahul examines the perimeter gate. Inexplicably, his left arm shows no injury, bandage, or limitation, lifting heavy iron chains with both arms effortlessly.",
            "script": "EXT. PERIMETER GATE - NIGHT\nRahul walks over to the heavy iron chain on Gate 4. He grabs the thick padlock with both bare hands, exerting full force with his left arm. His sleeve is clean, with no trace of wound or bandage.",
            "events": ["Rahul tests the padlocks with both arms", "Left arm suddenly completely healthy without treatment"],
            "dialogue_facts": ["Gate 4 has been chained since last Thursday"],
            "seq": 6,
            "characters": [
                {"char_id": "char_rahul", "wardrobe": "Black leather jacket, pristine white tee", "condition": "Healthy", # Physical state contradiction!
                 "location": "Platform 7", "known_facts": [], "dialogue": ["The lock is rusted shut."]}
            ],
            "props": []
        },
        {
            "id": "scene_07",
            "scene_number": 7,
            "title": "Retreat to the Car",
            "location_name": "Rahul's Car",
            "time_of_day": "Night",
            "weather": "Rain",
            "emotional_tone": "Exhausted",
            "summary": "Rahul and Priya scramble inside Rahul's sedan. Priya pulls out her phone to verify GPS timestamps.",
            "script": "INT. RAHUL'S CAR - NIGHT\nWipers sweep rhythmically. Priya catches her breath while checking signal on her phone.\nPRIYA: 'The dispatch records match the freight number.'",
            "events": ["Rahul and Priya enter vehicle", "Doors locked"],
            "dialogue_facts": ["Dispatch matches freight number 412"],
            "seq": 7,
            "characters": [
                {"char_id": "char_rahul", "wardrobe": "Black leather jacket, white tee", "condition": "Healthy", "location": "Rahul's Car", "known_facts": [], "dialogue": ["We're safe inside for now."]},
                {"char_id": "char_priya", "wardrobe": "Beige trench coat", "condition": "Healthy", "location": "Rahul's Car", "known_facts": [], "dialogue": ["Look at these timestamps."]}
            ],
            "props": [
                {"prop_id": "prop_phone", "location": "Priya's hands", "holder": "char_priya", "state": "Active GPS screen", "event": "Priya checks signal"}
            ]
        },
        {
            "id": "scene_08",
            "scene_number": 8,
            "title": "Stashing the Red Notebook in the Car",
            "location_name": "Rahul's Car",
            "time_of_day": "Night",
            "weather": "Rain",
            "emotional_tone": "Cautious",
            "summary": "Rahul retrieves the Red Notebook from his glove compartment, reviews the cipher entries, and places it securely under the passenger seat inside the car.",
            "script": "INT. RAHUL'S CAR - NIGHT\nRahul opens the glovebox and lifts out the weathered RED NOTEBOOK. He flips through scribbled dates.\nRAHUL: 'If anything happens to me, the answers are here.'\nHe slides the Red Notebook underneath the passenger seat beneath the floor mat.",
            "events": ["Rahul places Red Notebook under passenger seat inside the car", "Locks the vehicle"],
            "dialogue_facts": ["The Red Notebook contains the syndicate ledger"],
            "seq": 8,
            "characters": [
                {"char_id": "char_rahul", "wardrobe": "Black leather jacket, white tee", "condition": "Healthy", "location": "Rahul's Car", "known_facts": ["Ledger is in the red notebook"], "dialogue": ["The answers are inside this notebook."]},
                {"char_id": "char_priya", "wardrobe": "Beige trench coat", "condition": "Healthy", "location": "Rahul's Car", "known_facts": [], "dialogue": ["Keep it hidden."]}
            ],
            "props": [
                {"prop_id": "prop_red_notebook", "location": "Inside Rahul's car (under passenger seat)", "holder": "", "state": "Hidden under seat", "event": "Rahul stashes notebook in car"}
            ]
        },
        {
            "id": "scene_09",
            "scene_number": 9,
            "title": "Walking Across to the Station Café",
            "location_name": "Platform 7",
            "time_of_day": "Night",
            "weather": "Rain",
            "emotional_tone": "Chilly / Watchful",
            "summary": "Leaving the car locked on the access road with the notebook securely inside, Rahul and Priya jog across the asphalt toward the warm glow of Station Café.",
            "script": "EXT. ACCESS ROAD - NIGHT\nRahul clicks the car lock fob. The sedan chirps. Carrying only his keys and Priya with her backpack, they run through puddles toward the diner entrance.",
            "events": ["Rahul locks car with notebook inside", "Rahul and Priya walk to Station Café"],
            "dialogue_facts": ["The car is left locked on the gravel road"],
            "seq": 9,
            "characters": [
                {"char_id": "char_rahul", "wardrobe": "Black leather jacket, white tee", "condition": "Healthy", "location": "Platform 7", "known_facts": [], "dialogue": ["Diner is open. Let's get out of the cold."]},
                {"char_id": "char_priya", "wardrobe": "Beige trench coat", "condition": "Healthy", "location": "Platform 7", "known_facts": [], "dialogue": ["Hurry."]}
            ],
            "props": [
                {"prop_id": "prop_car_keys", "location": "Rahul's hand", "holder": "char_rahul", "state": "Clicking lock", "event": "Rahul locks car"},
                {"prop_id": "prop_red_notebook", "location": "Inside Rahul's car", "holder": "", "state": "Remains in car", "event": "Notebook stays in car"}
            ]
        },
        {
            "id": "scene_10",
            "scene_number": 10,
            "title": "The Booth at Station Café (Prop Teleportation)",
            "location_name": "Station Café",
            "time_of_day": "12:45 AM",
            "weather": "Rain against windows",
            "emotional_tone": "Intense / Investigative",
            "summary": "Inside the diner booth, Rahul is wearing his Black leather jacket. Inexplicably, he pulls the Red Notebook from his jacket pocket and slaps it onto the table, despite leaving it in the car with no retrieval event!",
            "script": "INT. STATION CAFÉ - NIGHT\nSteam rises from two coffee mugs on the laminated table.\nRahul unzips his BLACK LEATHER JACKET. Suddenly, he pulls the RED NOTEBOOK from inside his breast pocket and slams it onto the table.\nRAHUL: 'Look at page twelve.'\nPRIYA: (staring at the red cover) 'Wait, didn't you leave that in the car?'",
            "events": ["Rahul wears Black leather jacket", "Rahul places Red Notebook on table without retrieving it from car"],
            "dialogue_facts": ["Page 12 details the midnight cargo routing"],
            "seq": 10,
            "characters": [
                {"char_id": "char_rahul", "wardrobe": "Black leather jacket, white tee", "condition": "Healthy", "location": "Station Café", "known_facts": [], "dialogue": ["Look at page twelve."]},
                {"char_id": "char_priya", "wardrobe": "Beige trench coat", "condition": "Healthy", "location": "Station Café", "known_facts": [], "dialogue": ["Wait, didn't you leave that in the car?"]}
            ],
            "props": [
                {"prop_id": "prop_red_notebook", "location": "Station Café table", "holder": "char_rahul", "state": "On café table (teleported from car)", "event": "Rahul slams notebook on table"}
            ]
        },
        {
            "id": "scene_11",
            "scene_number": 11,
            "title": "The Heated Discussion (Wardrobe Swap)",
            "location_name": "Station Café",
            "time_of_day": "12:50 AM",
            "weather": "Rain against windows",
            "emotional_tone": "Argumentative",
            "summary": "Continuing directly from Scene 10 at the exact same table, Rahul is now inexplicably wearing a RED JACKET with no costume change recorded.",
            "script": "INT. STATION CAFÉ - MOMENTS LATER\nThe waitress refills the cups. Rahul leans forward over the table. He is now wearing a vibrant RED BOMBER JACKET over his white shirt. There has been no wardrobe change or coat check.",
            "events": ["Rahul is now wearing a Red jacket instead of Black jacket", "No change of clothes was recorded"],
            "dialogue_facts": ["The cargo arrives at Platform 7 precisely at 1:15 AM"],
            "seq": 11,
            "characters": [
                {"char_id": "char_rahul", "wardrobe": "Red jacket, white tee", # Wardrobe contradiction!
                 "condition": "Healthy", "location": "Station Café", "known_facts": [], "dialogue": ["If the train departs at 1:15, we only have twenty minutes."]},
                {"char_id": "char_priya", "wardrobe": "Beige trench coat", "condition": "Healthy", "location": "Station Café", "known_facts": [], "dialogue": ["We need the police report first."]}
            ],
            "props": [
                {"prop_id": "prop_red_notebook", "location": "Station Café table", "holder": "", "state": "Open to page 12", "event": "Open on table"}
            ]
        },
        {
            "id": "scene_12",
            "scene_number": 12,
            "title": "Meera's Phone Call",
            "location_name": "Station Café",
            "time_of_day": "1:00 AM",
            "weather": "Rain against windows",
            "emotional_tone": "Panicked",
            "summary": "Meera calls Rahul from Metro Hospital reporting that Arjun's men were spotted in the lower corridors.",
            "script": "INT. STATION CAFÉ - NIGHT\nRahul's phone vibrates violently on the table. He puts it on speaker.\nMEERA: (over phone) 'Rahul, they're searching the wing. Someone told them I was here.'\nPRIYA: 'Meera, stay in the nursing station. Don't go outside.'",
            "events": ["Meera warns about intruders at hospital", "Priya instructs Meera over phone"],
            "dialogue_facts": ["Arjun's associates are prowling Metro Hospital"],
            "seq": 12,
            "characters": [
                {"char_id": "char_rahul", "wardrobe": "Red jacket, white tee", "condition": "Healthy", "location": "Station Café", "known_facts": ["Meera is in danger at hospital"], "dialogue": ["Meera, lock the room door!"]},
                {"char_id": "char_priya", "wardrobe": "Beige trench coat", "condition": "Healthy", "location": "Station Café", "known_facts": ["Meera is in danger at hospital"], "dialogue": ["Stay in the nursing station."]}
            ],
            "props": [
                {"prop_id": "prop_phone", "location": "Café table", "holder": "", "state": "Speakerphone active", "event": "Call from Meera"}
            ]
        },
        {
            "id": "scene_13",
            "scene_number": 13,
            "title": "The Trauma Ward Corridors (Location Teleportation)",
            "location_name": "Metro Hospital",
            "time_of_day": "1:05 AM",
            "weather": "Interior",
            "emotional_tone": "Panic / Chase",
            "summary": "Suddenly and without any travel, transit, or departure sequence from the diner, Priya is inside Metro Hospital confronting Arjun outside Meera's room!",
            "script": "INT. METRO HOSPITAL - 3RD FLOOR CORRIDOR - NIGHT\nFluorescent tubes hum. Suddenly, PRIYA bursts through the double fire doors of the 3rd floor ward, breathing heavily.\nARJUN turns from Meera's hospital room door, surprised.\nARJUN: 'How did you get here from the station café so fast?'",
            "events": ["Priya teleports from Station Café directly into Metro Hospital 3rd floor", "No transit or travel event was recorded"],
            "dialogue_facts": ["Meera is resting in Room 304"],
            "seq": 13,
            "characters": [
                {"char_id": "char_priya", "wardrobe": "Beige trench coat", "condition": "Healthy", "location": "Metro Hospital", "known_facts": [], "dialogue": ["Step away from that door, Arjun!"]},
                {"char_id": "char_arjun", "wardrobe": "Dark navy windbreaker", "condition": "Healthy", "location": "Metro Hospital", "known_facts": [], "dialogue": ["How did you get here from the café so fast?"]},
                {"char_id": "char_meera", "wardrobe": "Green knit sweater", "condition": "Healthy", "location": "Metro Hospital", "known_facts": [], "dialogue": ["Priya! He tried to take father's photograph!"]}
            ],
            "props": [
                {"prop_id": "prop_old_photograph", "location": "Meera's hands", "holder": "char_meera", "state": "Creased edges", "event": "Meera shields photograph"}
            ]
        },
        {
            "id": "scene_14",
            "scene_number": 14,
            "title": "The Final Stand at Platform 7",
            "location_name": "Platform 7",
            "time_of_day": "1:30 AM",
            "weather": "Thunderstorm",
            "emotional_tone": "Climactic",
            "summary": "Inspector Singh arrives with backup as the freight train approaches. Rahul presents the recovered photographic evidence and the red notebook cipher.",
            "script": "EXT. PLATFORM 7 - TRACKS - NIGHT\nLocomotive 412 grinds to a halt under blinding searchlights. Singh corners Arjun against the freight cars. Rahul hands the red notebook to Singh.\nINSPECTOR SINGH: 'This ledger seals the case.'",
            "events": ["Inspector Singh intercepts Arjun", "Rahul submits notebook and photo evidence", "Syndicate scheme dismantled"],
            "dialogue_facts": ["Train 412 holds contraband freight in Container C-9"],
            "seq": 14,
            "characters": [
                {"char_id": "char_rahul", "wardrobe": "Black leather jacket, white tee", "condition": "Healthy", "location": "Platform 7", "known_facts": ["Container C-9 contains contraband"], "dialogue": ["Check container C-9, Inspector."]},
                {"char_id": "char_singh", "wardrobe": "Brown leather jacket, police badge", "condition": "Healthy", "location": "Platform 7", "known_facts": ["Full syndicate evidence verified"], "dialogue": ["Arjun, step away from the train."]},
                {"char_id": "char_arjun", "wardrobe": "Dark navy windbreaker", "condition": "Healthy", "location": "Platform 7", "known_facts": [], "dialogue": ["You have no idea what you're interfering with."]}
            ],
            "props": [
                {"prop_id": "prop_police_badge", "location": "Singh's coat", "holder": "char_singh", "state": "Displayed", "event": "Official apprehension"}
            ]
        }
    ]

    for sc in scenes_data:
        scene_obj = Scene(
            id=sc["id"],
            project_id=DEMO_PROJECT_ID,
            scene_number=sc["scene_number"],
            title=sc["title"],
            location_name=sc["location_name"],
            time_of_day=sc["time_of_day"],
            weather=sc["weather"],
            emotional_tone=sc["emotional_tone"],
            summary=sc["summary"],
            script_content=sc["script"],
            events_json=json.dumps(sc["events"]),
            dialogue_facts_json=json.dumps(sc["dialogue_facts"]),
            sequence_order=sc["seq"],
            created_at=now
        )
        db.add(scene_obj)

        for c_app in sc["characters"]:
            db.add(SceneCharacter(
                id=f"{sc['id']}_{c_app['char_id']}",
                scene_id=sc["id"],
                character_id=c_app["char_id"],
                wardrobe=c_app["wardrobe"],
                condition=c_app["condition"],
                emotional_state="Active",
                current_location=c_app["location"],
                known_facts_json=json.dumps(c_app.get("known_facts", [])),
                dialogue_lines_json=json.dumps(c_app.get("dialogue", []))
            ))

        for p_app in sc["props"]:
            db.add(SceneProp(
                id=f"{sc['id']}_{p_app['prop_id']}",
                scene_id=sc["id"],
                prop_id=p_app["prop_id"],
                location=p_app["location"],
                holder=p_app["holder"],
                state_description=p_app["state"],
                interaction_event=p_app["event"]
            ))

    # 6. Intentional Continuity Issues for Demonstration
    issues_data = [
        {
            "id": "issue_01_wardrobe",
            "scene_id": "scene_11",
            "type": "WARDROBE",
            "severity": "CRITICAL",
            "entity_type": "Character",
            "entity_name": "Rahul",
            "description": "Rahul's wardrobe changed abruptly from 'Black leather jacket' in Scene 10 to 'Red jacket' in Scene 11 without any change of clothes, departure, or wardrobe transition event recorded.",
            "prev": "Scene 10: Black leather jacket, white tee",
            "curr": "Scene 11: Red jacket, white tee",
            "fixes": [
                {"id": "fix_1", "title": "Change Scene 11 wardrobe back to Black jacket", "action": "update_scene_wardrobe", "patch": {"scene_id": "scene_11", "character_id": "char_rahul", "wardrobe": "Black leather jacket, white tee"}, "description": "Keep Rahul in his signature black leather jacket throughout the café sequence."},
                {"id": "fix_2", "title": "Insert coat change transition in Scene 10", "action": "insert_scene_event", "patch": {"scene_id": "scene_10", "event": "Rahul removes wet leather jacket and borrows diner red bomber jacket"}, "description": "Add narrative justification for wardrobe swap."},
                {"id": "fix_3", "title": "Mark as intentional artistic continuity exception", "action": "mark_exception", "patch": {}, "description": "Director note: symbolic color change representing heightened emotional state."}
            ],
            "confidence": 98,
            "status": "OPEN"
        },
        {
            "id": "issue_02_prop",
            "scene_id": "scene_10",
            "type": "PROP",
            "severity": "CRITICAL",
            "entity_type": "Prop",
            "entity_name": "Red Notebook",
            "description": "The Red Notebook was stashed under the passenger seat inside Rahul's locked car in Scene 08 and Scene 09. In Scene 10, Rahul suddenly produces it inside Station Café with no recorded retrieval from the locked car.",
            "prev": "Scene 08 & 09: Under passenger seat inside Rahul's locked car",
            "curr": "Scene 10: Slapped onto table inside Station Café",
            "fixes": [
                {"id": "fix_1", "title": "Add retrieval event at end of Scene 09", "action": "insert_scene_event", "patch": {"scene_id": "scene_09", "event": "Rahul unlocks passenger door and grabs the Red Notebook before crossing to café."}, "description": "Establish continuity by having Rahul explicitly retrieve the notebook from the vehicle."},
                {"id": "fix_2", "title": "Retain notebook in car during Scene 10", "action": "update_prop_location", "patch": {"scene_id": "scene_10", "prop_id": "prop_red_notebook", "location": "Inside Rahul's car"}, "description": "Rahul refers to the notebook verbally instead of physically possessing it on the diner table."},
                {"id": "fix_3", "title": "Mark as intentional exception", "action": "mark_exception", "patch": {}, "description": "Director note: Acceptable narrative compression."}
            ],
            "confidence": 95,
            "status": "OPEN"
        },
        {
            "id": "issue_03_location",
            "scene_id": "scene_13",
            "type": "LOCATION",
            "severity": "HIGH",
            "entity_type": "Character",
            "entity_name": "Priya",
            "description": "Priya moved from Station Café in Scene 12 directly to Metro Hospital 3rd Floor in Scene 13 within 5 minutes elapsed film time. No transit, vehicle departure, or travel scene was recorded.",
            "prev": "Scene 12 (1:00 AM): Station Café booth",
            "curr": "Scene 13 (1:05 AM): Metro Hospital 3rd floor ward",
            "fixes": [
                {"id": "fix_1", "title": "Insert travel / transit beat between Scene 12 and 13", "action": "insert_scene_event", "patch": {"scene_id": "scene_12", "event": "Priya sprints out of café into taxi speeding to Metro Hospital."}, "description": "Add an explicit travel event bridging the two distant locations."},
                {"id": "fix_2", "title": "Adjust Scene 13 timestamp to 1:40 AM", "action": "update_scene_time", "patch": {"scene_id": "scene_13", "time_of_day": "1:40 AM"}, "description": "Provide realistic travel window for transit between station and trauma hospital."},
                {"id": "fix_3", "title": "Mark as intentional smash-cut transition", "action": "mark_exception", "patch": {}, "description": "Director note: Stylistic smash cut for high dramatic tension."}
            ],
            "confidence": 91,
            "status": "OPEN"
        },
        {
            "id": "issue_04_health",
            "scene_id": "scene_06",
            "type": "CHARACTER_STATE",
            "severity": "HIGH",
            "entity_type": "Character",
            "entity_name": "Rahul",
            "description": "Rahul's left arm was severely cut with deep lacerations and heavy bleeding in Scene 04 and bandaged in Scene 05. In Scene 06, he has clean sleeves and exerts full two-handed force on rusted chains with no injury or recovery event recorded.",
            "prev": "Scene 05: Left arm injured / bleeding, bandaged with wool scarf",
            "curr": "Scene 06: Left arm completely healthy, lifting rusted chain",
            "fixes": [
                {"id": "fix_1", "title": "Maintain left arm bandage in Scene 06", "action": "update_character_condition", "patch": {"scene_id": "scene_06", "character_id": "char_rahul", "condition": "Left arm bandaged / favoring right hand"}, "description": "Preserve wound continuity by having Rahul favor his uninjured right arm."},
                {"id": "fix_2", "title": "Downgrade Scene 04 injury to minor bruise", "action": "update_character_condition", "patch": {"scene_id": "scene_04", "character_id": "char_rahul", "condition": "Left arm bruised"}, "description": "Reduce original injury severity so spontaneous physical exertion is plausible."},
                {"id": "fix_3", "title": "Mark as intentional adrenaline burst", "action": "mark_exception", "patch": {}, "description": "Director note: Rahul ignores extreme physical pain due to fight-or-flight reflex."}
            ],
            "confidence": 93,
            "status": "OPEN"
        },
        {
            "id": "issue_05_timeline",
            "scene_id": "scene_03",
            "type": "TIMELINE",
            "severity": "MEDIUM",
            "entity_type": "Scene",
            "entity_name": "Scene 03",
            "description": "Scene 03 occurs at Monday 6:30 PM, but chronologically follows Scene 02 which was set at Monday 8:00 PM. No flashback or non-linear title card is specified.",
            "prev": "Scene 02: Monday 8:00 PM",
            "curr": "Scene 03: Monday 6:30 PM",
            "fixes": [
                {"id": "fix_1", "title": "Adjust Scene 03 time to Monday 8:30 PM", "action": "update_scene_time", "patch": {"scene_id": "scene_03", "time_of_day": "Monday 8:30 PM"}, "description": "Restore forward chronological time progression."},
                {"id": "fix_2", "title": "Mark Scene 03 as deliberate FLASHBACK", "action": "mark_flashback", "patch": {"scene_id": "scene_03", "is_flashback": True}, "description": "Designate Scene 03 as an intentional dramatic flashback sequence."},
                {"id": "fix_3", "title": "Mark as intentional exception", "action": "mark_exception", "patch": {}, "description": "Director note: Subjective psychological time distortion."}
            ],
            "confidence": 89,
            "status": "OPEN"
        },
        {
            "id": "issue_06_knowledge",
            "scene_id": "scene_02",
            "type": "KNOWLEDGE",
            "severity": "HIGH",
            "entity_type": "Character",
            "entity_name": "Rahul",
            "description": "In Scene 02, Rahul tells Priya: 'I know Arjun embezzled the entire 200,000 shipment.' In established story state, this financial ledger information is only discovered in the Red Notebook in Scene 08/10. Rahul has no recorded discovery event for this secret.",
            "prev": "Scene 01: Rahul is unaware of cargo contents or embezzled amounts",
            "curr": "Scene 02: Rahul explicitly quotes exact 200,000 embezzlement figure",
            "fixes": [
                {"id": "fix_1", "title": "Alter Rahul's dialogue in Scene 02 to suspicion instead of certainty", "action": "update_dialogue", "patch": {"scene_id": "scene_02", "dialogue": "I suspect Arjun is moving illegal freight through this line."}, "description": "Replace specific leaked numerical secret with general intuition."},
                {"id": "fix_2", "title": "Add prior phone tip in Scene 01", "action": "insert_scene_event", "patch": {"scene_id": "scene_01", "event": "Rahul receives anonymous SMS stating: 'Arjun took 200,000 shipment.'"}, "description": "Provide a legitimate discovery channel for Rahul's prior knowledge."},
                {"id": "fix_3", "title": "Mark as intentional bluff", "action": "mark_exception", "patch": {}, "description": "Director note: Rahul is bluffing to provoke Priya into revealing confirmation."}
            ],
            "confidence": 94,
            "status": "OPEN"
        }
    ]

    for iss in issues_data:
        db.add(ContinuityIssue(
            id=iss["id"],
            project_id=DEMO_PROJECT_ID,
            scene_id=iss["scene_id"],
            issue_type=iss["type"],
            severity=iss["severity"],
            entity_type=iss["entity_type"],
            entity_name=iss["entity_name"],
            description=iss["description"],
            previous_state=iss["prev"],
            current_state=iss["curr"],
            suggested_fixes_json=json.dumps(iss["fixes"]),
            confidence=iss["confidence"],
            status=iss["status"],
            created_at=now
        ))

    # 7. Production Notes
    notes_data = [
        {"id": "note_01", "scene_id": "scene_10", "type": "WARDROBE", "author": "Script Supervisor Maya", "content": "Camera B operator flagged Rahul's jacket color difference in café setup. Reshoot or insert color grade patch."},
        {"id": "note_02", "scene_id": "scene_08", "type": "PROPS", "author": "Prop Master Kabir", "content": "Red notebook hero prop has duplicate stunt copy with water-resistant plastic sleeve."},
        {"id": "note_03", "scene_id": "scene_04", "type": "DIRECTOR", "author": "Director Kabir S.", "content": "Rain intensity on Platform 7 must stay consistent with sound design mix in Scene 01 and 02."}
    ]
    for n in notes_data:
        db.add(ProductionNote(
            id=n["id"],
            project_id=DEMO_PROJECT_ID,
            scene_id=n["scene_id"],
            note_type=n["type"],
            author=n["author"],
            content=n["content"],
            tags_json=json.dumps(["Production", "Continuity"]),
            created_at=now
        ))

    # 8. Initial Audit Event
    db.add(AuditEvent(
        id="audit_init_01",
        project_id=DEMO_PROJECT_ID,
        event_type="PROJECT_SEEDED",
        entity_type="Project",
        entity_id=DEMO_PROJECT_ID,
        actor="System",
        details_json=json.dumps({"scenes": 14, "characters": 5, "props": 8, "intentional_issues": 6}),
        timestamp=now
    ))

    db.commit()
    return project

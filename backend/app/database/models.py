import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from backend.app.database.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    genre = Column(String, default="Drama")
    description = Column(Text, default="")
    image_url = Column(String, default="")
    language = Column(String, default="English")
    status = Column(String, default="Production")
    health_score = Column(Integer, default=87)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    scenes = relationship("Scene", back_populates="project", cascade="all, delete-orphan", order_by="Scene.sequence_order")
    characters = relationship("Character", back_populates="project", cascade="all, delete-orphan")
    props = relationship("Prop", back_populates="project", cascade="all, delete-orphan")
    locations = relationship("Location", back_populates="project", cascade="all, delete-orphan")
    issues = relationship("ContinuityIssue", back_populates="project", cascade="all, delete-orphan")
    notes = relationship("ProductionNote", back_populates="project", cascade="all, delete-orphan")
    audit_events = relationship("AuditEvent", back_populates="project", cascade="all, delete-orphan")


class Scene(Base):
    __tablename__ = "scenes"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    scene_number = Column(Integer, nullable=False, index=True)
    title = Column(String, nullable=False)
    location_name = Column(String, default="")
    time_of_day = Column(String, default="Day")
    weather = Column(String, default="Clear")
    emotional_tone = Column(String, default="Neutral")
    summary = Column(Text, default="")
    script_content = Column(Text, default="")
    events_json = Column(Text, default="[]")
    dialogue_facts_json = Column(Text, default="[]")
    sequence_order = Column(Integer, default=1)
    is_flashback = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="scenes")
    scene_characters = relationship("SceneCharacter", back_populates="scene", cascade="all, delete-orphan")
    scene_props = relationship("SceneProp", back_populates="scene", cascade="all, delete-orphan")
    issues = relationship("ContinuityIssue", back_populates="scene", cascade="all, delete-orphan")


class Character(Base):
    __tablename__ = "characters"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    role = Column(String, default="Supporting")
    age = Column(String, default="30s")
    appearance = Column(Text, default="")
    default_wardrobe = Column(String, default="")
    default_condition = Column(String, default="Healthy")
    current_location = Column(String, default="")
    relationships_json = Column(Text, default="{}")
    known_facts_json = Column(Text, default="[]")
    possessions_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="characters")
    appearances = relationship("SceneCharacter", back_populates="character", cascade="all, delete-orphan")


class SceneCharacter(Base):
    __tablename__ = "scene_characters"

    id = Column(String, primary_key=True, index=True)
    scene_id = Column(String, ForeignKey("scenes.id"), nullable=False, index=True)
    character_id = Column(String, ForeignKey("characters.id"), nullable=False, index=True)
    wardrobe = Column(String, default="")
    condition = Column(String, default="Healthy")
    emotional_state = Column(String, default="Neutral")
    current_location = Column(String, default="")
    known_facts_json = Column(Text, default="[]")
    dialogue_lines_json = Column(Text, default="[]")

    scene = relationship("Scene", back_populates="scene_characters")
    character = relationship("Character", back_populates="appearances")


class Prop(Base):
    __tablename__ = "props"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    category = Column(String, default="Prop")
    current_location = Column(String, default="")
    current_holder = Column(String, default="")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="props")
    appearances = relationship("SceneProp", back_populates="prop", cascade="all, delete-orphan")


class SceneProp(Base):
    __tablename__ = "scene_props"

    id = Column(String, primary_key=True, index=True)
    scene_id = Column(String, ForeignKey("scenes.id"), nullable=False, index=True)
    prop_id = Column(String, ForeignKey("props.id"), nullable=False, index=True)
    location = Column(String, default="")
    holder = Column(String, default="")
    state_description = Column(Text, default="")
    interaction_event = Column(Text, default="")

    scene = relationship("Scene", back_populates="scene_props")
    prop = relationship("Prop", back_populates="appearances")


class Location(Base):
    __tablename__ = "locations"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    environment_type = Column(String, default="Interior")
    time_rules = Column(String, default="")

    project = relationship("Project", back_populates="locations")


class ContinuityIssue(Base):
    __tablename__ = "continuity_issues"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    scene_id = Column(String, ForeignKey("scenes.id"), nullable=True, index=True)
    issue_type = Column(String, nullable=False) # WARDROBE, PROP, LOCATION, CHARACTER_STATE, TIMELINE, WEATHER, DIALOGUE_FACT, KNOWLEDGE
    severity = Column(String, default="MEDIUM") # CRITICAL, HIGH, MEDIUM, LOW
    entity_type = Column(String, default="Character")
    entity_name = Column(String, default="")
    description = Column(Text, nullable=False)
    previous_state = Column(Text, default="")
    current_state = Column(Text, default="")
    suggested_fixes_json = Column(Text, default="[]")
    confidence = Column(Integer, default=90)
    status = Column(String, default="OPEN") # OPEN, RESOLVED, IGNORED
    resolution_note = Column(Text, default="")
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="issues")
    scene = relationship("Scene", back_populates="issues")


class ProductionNote(Base):
    __tablename__ = "production_notes"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    scene_id = Column(String, ForeignKey("scenes.id"), nullable=True, index=True)
    note_type = Column(String, default="CONTINUITY")
    author = Column(String, default="Script Supervisor")
    content = Column(Text, nullable=False)
    tags_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="notes")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    event_type = Column(String, nullable=False)
    entity_type = Column(String, default="")
    entity_id = Column(String, default="")
    actor = Column(String, default="Continuity Agent")
    details_json = Column(Text, default="{}")
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="audit_events")

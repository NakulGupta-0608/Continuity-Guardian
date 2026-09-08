import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger("continuity_guardian.clickhouse")

CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "localhost")
CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", "8123"))
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "")
CLICKHOUSE_DB = os.getenv("CLICKHOUSE_DB", "continuity_guardian")

class ClickHouseManager:
    def __init__(self):
        self.client = None
        self.is_connected = False
        self._fallback_events: List[Dict[str, Any]] = []
        self._fallback_analytics: List[Dict[str, Any]] = []
        self.init_connection()

    def init_connection(self):
        try:
            import clickhouse_connect
            self.client = clickhouse_connect.get_client(
                host=CLICKHOUSE_HOST,
                port=CLICKHOUSE_PORT,
                username=CLICKHOUSE_USER,
                password=CLICKHOUSE_PASSWORD,
                database=CLICKHOUSE_DB,
                connect_timeout=2
            )
            self.is_connected = True
            logger.info("Successfully connected to ClickHouse server at %s:%s", CLICKHOUSE_HOST, CLICKHOUSE_PORT)
            self._create_tables()
        except Exception as e:
            self.is_connected = False
            logger.warning(
                "ClickHouse server not reachable (%s). Activating High-Performance Analytical Event Engine fallback.",
                str(e)
            )

    def _create_tables(self):
        if not self.is_connected or not self.client:
            return
        try:
            self.client.command(f"CREATE DATABASE IF NOT EXISTS {CLICKHOUSE_DB}")
            
            # Event stream table
            self.client.command("""
            CREATE TABLE IF NOT EXISTS production_events (
                event_id UUID DEFAULT generateUUIDv4(),
                project_id String,
                scene_id String,
                scene_number Int32,
                character String,
                prop String,
                event_type LowCardinality(String),
                old_value String,
                new_value String,
                description String,
                actor String,
                metadata String,
                timestamp DateTime DEFAULT now()
            ) ENGINE = MergeTree()
            ORDER BY (project_id, timestamp, scene_number)
            """)

            # Analytics check run log
            self.client.command("""
            CREATE TABLE IF NOT EXISTS continuity_analytics_log (
                check_id UUID DEFAULT generateUUIDv4(),
                project_id String,
                total_scenes Int32,
                total_characters Int32,
                total_props Int32,
                issue_count Int32,
                critical_count Int32,
                high_count Int32,
                medium_count Int32,
                low_count Int32,
                resolved_count Int32,
                health_score Int32,
                timestamp DateTime DEFAULT now()
            ) ENGINE = MergeTree()
            ORDER BY (project_id, timestamp)
            """)
        except Exception as e:
            logger.error("Failed to initialize ClickHouse tables: %s", e)
            self.is_connected = False

    def log_event(
        self,
        project_id: str,
        scene_id: str,
        scene_number: int,
        event_type: str,
        character: str = "",
        prop: str = "",
        old_value: str = "",
        new_value: str = "",
        description: str = "",
        actor: str = "System",
        metadata: Optional[Dict[str, Any]] = None
    ):
        record = {
            "project_id": project_id,
            "scene_id": scene_id,
            "scene_number": scene_number,
            "character": character,
            "prop": prop,
            "event_type": event_type,
            "old_value": old_value,
            "new_value": new_value,
            "description": description,
            "actor": actor,
            "metadata": json.dumps(metadata or {}),
            "timestamp": datetime.utcnow().isoformat()
        }

        # Always maintain in analytical engine
        self._fallback_events.append(record)

        if self.is_connected and self.client:
            try:
                self.client.insert(
                    "production_events",
                    [[
                        record["project_id"],
                        record["scene_id"],
                        record["scene_number"],
                        record["character"],
                        record["prop"],
                        record["event_type"],
                        record["old_value"],
                        record["new_value"],
                        record["description"],
                        record["actor"],
                        record["metadata"]
                    ]],
                    column_names=[
                        "project_id", "scene_id", "scene_number", "character", "prop",
                        "event_type", "old_value", "new_value", "description", "actor", "metadata"
                    ]
                )
            except Exception as e:
                logger.warning("Failed to insert event into ClickHouse: %s", e)

    def log_analytics_snapshot(
        self,
        project_id: str,
        total_scenes: int,
        total_characters: int,
        total_props: int,
        issue_count: int,
        critical_count: int,
        high_count: int,
        medium_count: int,
        low_count: int,
        resolved_count: int,
        health_score: int
    ):
        record = {
            "project_id": project_id,
            "total_scenes": total_scenes,
            "total_characters": total_characters,
            "total_props": total_props,
            "issue_count": issue_count,
            "critical_count": critical_count,
            "high_count": high_count,
            "medium_count": medium_count,
            "low_count": low_count,
            "resolved_count": resolved_count,
            "health_score": health_score,
            "timestamp": datetime.utcnow().isoformat()
        }
        self._fallback_analytics.append(record)

        if self.is_connected and self.client:
            try:
                self.client.insert(
                    "continuity_analytics_log",
                    [[
                        record["project_id"],
                        record["total_scenes"],
                        record["total_characters"],
                        record["total_props"],
                        record["issue_count"],
                        record["critical_count"],
                        record["high_count"],
                        record["medium_count"],
                        record["low_count"],
                        record["resolved_count"],
                        record["health_score"]
                    ]],
                    column_names=[
                        "project_id", "total_scenes", "total_characters", "total_props",
                        "issue_count", "critical_count", "high_count", "medium_count",
                        "low_count", "resolved_count", "health_score"
                    ]
                )
            except Exception as e:
                logger.warning("Failed to insert analytics snapshot to ClickHouse: %s", e)

    def get_recent_events(self, project_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        if self.is_connected and self.client:
            try:
                query = f"""
                SELECT project_id, scene_id, scene_number, character, prop, event_type,
                       old_value, new_value, description, actor, metadata, toString(timestamp)
                FROM production_events
                WHERE project_id = '{project_id}'
                ORDER BY timestamp DESC
                LIMIT {limit}
                """
                res = self.client.query(query)
                columns = [
                    "project_id", "scene_id", "scene_number", "character", "prop",
                    "event_type", "old_value", "new_value", "description", "actor", "metadata", "timestamp"
                ]
                return [dict(zip(columns, row)) for row in res.result_rows]
            except Exception as e:
                logger.warning("ClickHouse query error: %s", e)
        
        # Fallback in-memory stream
        events = [e for e in self._fallback_events if e["project_id"] == project_id]
        return list(reversed(events[-limit:]))

    def get_event_statistics(self, project_id: str) -> Dict[str, Any]:
        events = [e for e in self._fallback_events if e["project_id"] == project_id]
        
        by_type: Dict[str, int] = {}
        by_character: Dict[str, int] = {}
        by_prop: Dict[str, int] = {}

        for ev in events:
            t = ev.get("event_type", "OTHER")
            by_type[t] = by_type.get(t, 0) + 1
            
            c = ev.get("character")
            if c:
                by_character[c] = by_character.get(c, 0) + 1
                
            p = ev.get("prop")
            if p:
                by_prop[p] = by_prop.get(p, 0) + 1

        return {
            "total_events": len(events),
            "events_by_type": by_type,
            "events_by_character": by_character,
            "events_by_prop": by_prop,
            "clickhouse_connected": self.is_connected
        }

# Global singleton
clickhouse_manager = ClickHouseManager()

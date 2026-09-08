import unittest
import json
from backend.app.database.database import SessionLocal, Base, engine
import backend.app.database.models as models
from backend.app.data.demo_project import seed_demo_project, DEMO_PROJECT_ID
from backend.app.services.continuity_engine import continuity_engine
from backend.app.agents.continuity_agent import continuity_agent
from backend.app.services.analytics_service import get_project_analytics
from backend.app.services.script_parser import script_parser
from backend.app.tools import agent_tools
from backend.app.database.clickhouse import clickhouse_manager

class TestContinuity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.db = SessionLocal()
        seed_demo_project(cls.db)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_demo_project_seeded(self):
        project = self.db.query(models.Project).filter(models.Project.id == DEMO_PROJECT_ID).first()
        self.assertIsNotNone(project)
        self.assertEqual(project.title, "Midnight at Platform 7")
        self.assertEqual(len(project.scenes), 14)
        self.assertEqual(len(project.characters), 5)
        self.assertEqual(len(project.props), 8)
        self.assertEqual(len(project.locations), 4)

    def test_continuity_engine_execution(self):
        res = continuity_engine.run_full_check(DEMO_PROJECT_ID, self.db)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["total_scenes_evaluated"], 14)
        self.assertGreater(res["total_open_issues"], 0)
        self.assertTrue(0 <= res["health_score"] <= 100)

    def test_agent_prop_inquiry(self):
        chat_res = continuity_agent.process_chat(DEMO_PROJECT_ID, "Where was the red notebook last seen?", self.db)
        self.assertIn("Red Notebook", chat_res["reply"])
        self.assertGreater(len(chat_res["tool_calls"]), 0)
        self.assertEqual(chat_res["tool_calls"][0]["tool"], "get_prop_history")

    def test_agent_error_inquiry(self):
        chat_res = continuity_agent.process_chat(DEMO_PROJECT_ID, "Show all continuity errors involving Rahul", self.db)
        self.assertIn("Rahul", chat_res["reply"])
        self.assertGreater(len(chat_res["tool_calls"]), 0)

    def test_issue_resolution_and_health_score(self):
        issue = self.db.query(models.ContinuityIssue).filter(
            models.ContinuityIssue.project_id == DEMO_PROJECT_ID,
            models.ContinuityIssue.status == "OPEN"
        ).first()
        self.assertIsNotNone(issue)

        initial_score = self.db.query(models.Project).filter(models.Project.id == DEMO_PROJECT_ID).first().health_score
        
        res = agent_tools.resolve_issue(self.db, DEMO_PROJECT_ID, issue.id, "Test resolution applied")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["issue_status"], "RESOLVED")
        self.assertGreaterEqual(res["new_health_score"], initial_score)

    def test_script_parser(self):
        script_text = """
        EXT. PLATFORM 7 - NIGHT
        Rain pours down the platform roof.
        RAHUL waits by the vending machines clutching a yellow folder.
        
        INT. STATION CAFÉ - CONTINUOUS
        PRIYA orders black coffee while checking her watch.
        """
        scenes = script_parser.parse_screenplay_text(script_text)
        self.assertEqual(len(scenes), 2)
        self.assertEqual(scenes[0]["location_name"], "PLATFORM 7")
        self.assertEqual(scenes[0]["time_of_day"], "NIGHT")
        self.assertIn("Rahul", scenes[0]["characters"])
        self.assertEqual(scenes[1]["location_name"], "STATION CAFÉ")

    def test_clickhouse_event_logging(self):
        clickhouse_manager.log_event(
            project_id=DEMO_PROJECT_ID,
            scene_id="scene_01",
            scene_number=1,
            event_type="TEST_EVENT",
            description="Automated unit test event",
            actor="Unittest"
        )
        stats = clickhouse_manager.get_event_statistics(DEMO_PROJECT_ID)
        self.assertGreater(stats["total_events"], 0)

if __name__ == "__main__":
    unittest.main()

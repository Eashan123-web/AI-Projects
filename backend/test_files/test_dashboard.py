
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api import dashboard as dashboard_api

client = TestClient(app)

class FakeCursor:

    def __init__(self):
        self.fetchone_results = [(3,), (2,), (4, 72.5, 95), (5,),]

        self.fetchall_results = [
            [("Good", 2), ("Excellent", 1),],
            [
                {
                    "matching_skills": {"Backend": ["Java", "SQL", "Java"],},
                    "missing_skills": {"Backend": ["Spring Boot", "Docker"],},
                }
            ],
            [
                (101, "resume.pdf", "Java Developer", 75, "2026-11-09"),
            ],
        ]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def execute(self, query):
        pass

    def fetchone(self):
        return self.fetchone_results.pop(0)

    def fetchall(self):
        return self.fetchall_results.pop(0)

class FakeConnection:

    def __init__(self):
        self.fake_cursor = FakeCursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def cursor(self):
        return self.fake_cursor

@pytest.fixture(autouse=True)
def mock_database(monkeypatch):

    monkeypatch.setattr(dashboard_api, "get_connection", lambda: FakeConnection(),)

def test_dashboard_stats_success():

    response = client.get("/api/dashboard/stats")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"

    summary = data["summary"]

    assert summary["total_resumes"] == 3
    assert summary["total_jobs"] == 2
    assert summary["total_analyses"] == 4
    assert summary["total_recommendations"] == 5
    assert summary["average_match_score"] == 72.5
    assert summary["highest_match_score"] == 95.0


def test_dashboard_score_distribution():

    response = client.get("/api/dashboard/stats")

    assert response.status_code == 200

    distribution = response.json()["score_distribution"]

    assert distribution["Low"] == 0
    assert distribution["Moderate"] == 0
    assert distribution["Good"] == 2
    assert distribution["Excellent"] == 1

def test_dashboard_skill_analytics():

    response = client.get("/api/dashboard/stats")

    assert response.status_code == 200

    analytics = response.json()["skill_analytics"]

    assert analytics["total_matched_skills"] == 3
    assert analytics["total_missing_skills"] == 2

    assert analytics["most_matched_skills"][0] == {"skill": "Java", "count": 2,}

def test_dashboard_recent_analyses():

    response = client.get("/api/dashboard/stats")

    assert response.status_code == 200

    recent = response.json()["recent_analyses"]

    assert len(recent) == 1
    assert recent[0]["analysis_id"] == 101
    assert recent[0]["resume_filename"] == "resume.pdf"
    assert recent[0]["job_title"] == "Java Developer"
    assert recent[0]["match_score"] == 75.0


def test_count_skills():

    result = dashboard_api.count_skills({
        "Backend": ["Java", "SQL", "Java", "  Python  "], "Frontend": ["React"],})

    assert result["Java"] == 2
    assert result["SQL"] == 1
    assert result["Python"] == 1
    assert result["React"] == 1


def test_count_skills_invalid_input():

    result = dashboard_api.count_skills(["Java", "Python"])

    assert len(result) == 0

def test_dashboard_database_error(monkeypatch):

    def raise_database_error():
        raise RuntimeError("Simulated database failure")

    monkeypatch.setattr(dashboard_api, "get_connection", raise_database_error,)

    response = client.get("/api/dashboard/stats")

    assert response.status_code == 500
    assert response.json()["detail"] == ("Unable to retrieve dashboard statistics.")
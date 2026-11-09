import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api import history as history_api

client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_history_repository(monkeypatch):

    monkeypatch.setattr(history_api, "get_all_resumes", lambda **kwargs: [
            {"id": 1, "filename": "resume1.pdf"}, {"id": 2, "filename": "resume2.pdf"},
        ],
    )

    monkeypatch.setattr(history_api, "get_all_analyses",
        lambda **kwargs: [
            {"analysis_id": 101, "match_score": 75}, {"analysis_id": 102, "match_score": 85},
        ],
    )

    monkeypatch.setattr(history_api, "get_analysis_details",
        lambda analysis_id: {
            "analysis_id": analysis_id, "match_score": 75, "matched_skills": ["Java", "SQL"],
            "missing_skills": ["Spring Boot"],
        },
    )

def test_get_resume_history():

    response = client.get("/api/history/resumes")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert data["total_returned"] == 2
    assert len(data["resumes"]) == 2

def test_get_analysis_history():

    response = client.get("/api/history/analyses")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert data["total_returned"] == 2
    assert len(data["analyses"]) == 2

def test_get_resume_history_with_pagination():

    response = client.get("/api/history/resumes?limit=1&offset=5")

    assert response.status_code == 200

    data = response.json()

    assert data["limit"] == 1
    assert data["offset"] == 5

def test_get_analysis_details():

    response = client.get("/api/history/analyses/101")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert data["analysis"]["analysis_id"] == 101
    assert data["analysis"]["match_score"] == 75

def test_get_nonexistent_analysis(monkeypatch):

    monkeypatch.setattr(history_api, "get_analysis_details", lambda analysis_id: None,)

    response = client.get("/api/history/analyses/999")

    assert response.status_code == 404

def test_reject_invalid_analysis_id():

    response = client.get("/api/history/analyses/0")

    assert response.status_code == 422

def test_reject_invalid_pagination():

    response = client.get("/api/history/resumes?limit=200")

    assert response.status_code == 422
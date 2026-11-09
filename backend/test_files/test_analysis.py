
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api import analysis as analysis_api

client = TestClient(app)

VALID_FILENAME = "a" * 32 + ".pdf"

VALID_JOB_DESCRIPTION = (
    "Looking for a Java developer with Spring Boot, SQL, "
    "REST API development and backend experience."
)

@pytest.fixture(autouse=True)
def mock_analysis_dependencies(tmp_path, monkeypatch):
    """Mock services and database operations for isolated API tests."""

    resume_file = tmp_path / VALID_FILENAME
    resume_file.write_bytes(b"%PDF-1.4 test resume")

    monkeypatch.setattr(analysis_api, "UPLOAD_DIR", tmp_path)

    monkeypatch.setattr(analysis_api, "extract_resume_text", lambda path: "Java Python SQL Spring Boot REST API",)

    monkeypatch.setattr(analysis_api, "extract_skills", lambda text: ["Java", "Python", "SQL"],)

    monkeypatch.setattr(analysis_api, "analyze_job_description", lambda description: {
            "skills": ["Java", "Spring Boot", "SQL"],
            "total_skills": 3,
        },
    )

    monkeypatch.setattr(analysis_api, "calculate_match",
        lambda resume_skills, job_skills: {
            "match_score": 75, "matched_skills": ["Java", "SQL"], "missing_skills": ["Spring Boot"],
        },
    )

    monkeypatch.setattr(analysis_api, "get_resume_by_filename", lambda filename: {"resume_id": 101},)

    monkeypatch.setattr(analysis_api, "build_resume_rag_context",
        lambda *args: {
            "relevant_chunks": [], "context": "", "status": "success",
        },
    )

    monkeypatch.setattr(analysis_api, "generate_ai_match_analysis",
        lambda *args: "Candidate has a good technical match.",)

    monkeypatch.setattr(analysis_api, "generate_resume_recommendations",
        lambda *args: {"recommendations": ["Learn Spring Boot"],},)

    monkeypatch.setattr(analysis_api, "generate_resume_improvements",
        lambda *args: {"suggestions": ["Add measurable project achievements"],},)

    monkeypatch.setattr(analysis_api, "save_job_description", lambda *args: 201,)

    monkeypatch.setattr(analysis_api, "save_analysis_result", lambda *args: 301,)

    monkeypatch.setattr(analysis_api, "save_recommendations", lambda *args: 401,)

def test_successful_resume_job_matching():
    response = client.post("/api/analysis/match",
        json={"filename": VALID_FILENAME, "job_description": VALID_JOB_DESCRIPTION,},)

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert data["resume_id"] == 101
    assert data["job_id"] == 201
    assert data["analysis_id"] == 301
    assert data["matching_analysis"]["match_score"] == 75

def test_successful_resume_recommendations():
    response = client.post("/api/analysis/recommendations",
        json={
            "filename": VALID_FILENAME, "job_description": VALID_JOB_DESCRIPTION,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert data["recommendation_id"] == 401
    assert "recommendations" in data

def test_successful_resume_improvement():
    response = client.post(
        "/api/analysis/improve",
        json={
            "filename": VALID_FILENAME, "job_description": VALID_JOB_DESCRIPTION,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert data["resume_id"] == 101
    assert data["match_score"] == 75
    assert "improvements" in data

def test_analysis_rejects_invalid_filename():
    response = client.post(
        "/api/analysis/match",
        json={
            "filename": "invalid.pdf", "job_description": VALID_JOB_DESCRIPTION,
        },
    )

    assert response.status_code == 422

def test_analysis_rejects_missing_resume():
    response = client.post("/api/analysis/match",
        json={
            "filename": "b" * 32 + ".pdf", "job_description": VALID_JOB_DESCRIPTION,
        },
    )

    assert response.status_code == 404
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api import jobs as jobs_api

client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_job_analysis(monkeypatch):
    """Mock the job analysis service to avoid external dependencies."""

    monkeypatch.setattr(jobs_api, "analyze_job_description",
        lambda description: {
            "skills": ["Java", "Spring Boot", "SQL"], "total_skills": 3,
        },
    )

def test_analyze_valid_job_description():
    """A valid job description should be analyzed successfully."""

    description = ("Java backend developer with Spring Boot and SQL experience.")

    response = client.post("/api/jobs/analyze", json={"job_description": description},)

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert data["analysis"]["total_skills"] == 3
    assert data["analysis"]["skills"] == ["Java", "Spring Boot", "SQL",]
    assert data["job_description_length"] == len(description)


def test_analyze_short_job_description():
    """Descriptions shorter than 30 characters should be rejected."""

    response = client.post("/api/jobs/analyze", json={"job_description": "Java developer"},)

    assert response.status_code == 422

def test_analyze_empty_job_description():
    """An empty description should be rejected."""

    response = client.post("/api/jobs/analyze", json={"job_description": ""},)

    assert response.status_code == 422

def test_analyze_whitespace_job_description():
    """A description containing only whitespace should be rejected."""

    response = client.post("/api/jobs/analyze", json={"job_description": " " * 40},)

    assert response.status_code == 422

def test_analyze_oversized_job_description():
    """Descriptions exceeding 30,000 characters should be rejected."""

    response = client.post("/api/jobs/analyze", json={"job_description": "A" * 30001},)

    assert response.status_code == 422
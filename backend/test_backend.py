import json
import uuid
import urllib.request
import urllib.error
from pathlib import Path
from zipfile import ZipFile
from docx import Document

BASE_URL = "http://127.0.0.1:8000"

TEST_DIR = Path(__file__).resolve().parent / "test_files"
TEST_DIR.mkdir(parents=True, exist_ok=True)

RESUME_PATH = TEST_DIR / "random_test_resume.docx"

# Helper: Make HTTP requests

def api_request(endpoint, method="GET", data=None, headers=None, expected_status=200):
    url = BASE_URL + endpoint

    request_headers = headers or {}

    body = None

    if data is not None:
        body = json.dumps(data).encode("utf-8")
        request_headers["Content-Type"] = "application/json"

    request = urllib.request.Request(url, data=body, headers=request_headers, method=method)

    try:
        with urllib.request.urlopen(request, timeout=60) as response:

            response_body = response.read().decode("utf-8")

            if response.status != expected_status:
                raise RuntimeError(f"Unexpected status: {response.status}")

            if response_body:
                return json.loads(response_body)

            return {}

    except urllib.error.HTTPError as error:
        error_body = error.read().decode("utf-8")

        raise RuntimeError(
            f"API failed: {method} {endpoint}\n"
            f"Status: {error.code}\n"
            f"Response: {error_body}"
        )

# Helper: Print test results

passed_tests = []

def test_passed(name):
    passed_tests.append(name)
    print(f"[PASS] {name}")

# Step 1: Generate random resume

def generate_random_resume():

    candidate_id = uuid.uuid4().hex[:6].upper()

    document = Document()
    document.add_heading("Rahul Sharma", level=1)
    document.add_paragraph(f"Email: rahul.test.{candidate_id}@example.com")
    document.add_paragraph("Phone: 9000000000")

    document.add_heading("Professional Summary", level=2)
    document.add_paragraph("Software Developer with experience in " "Java, Python, backend development, REST APIs "
        "and database management.")
    
    document.add_heading("Technical Skills", level=2)
    document.add_paragraph("Java, Python, JavaScript, SQL, Spring Boot, " "Hibernate, FastAPI, PostgreSQL, MySQL, "
        "REST API, Microservices, Git, GitHub, " "Docker, Linux, Selenium, HTML, CSS, React.")
    
    document.add_heading("Work Experience", level=2)
    document.add_paragraph("Software Developer | ABC Technologies | 2023-2025")

    document.add_paragraph(
        "Developed backend applications using Java " "and Spring Boot. Created REST APIs, integrated "
        "PostgreSQL databases and implemented business logic.")

    document.add_heading("Education", level=2)
    document.add_paragraph("Bachelor of Technology in Computer Science.")

    document.add_heading("Projects", level=2)
    document.add_paragraph("Employee Management System using Spring Boot, " "PostgreSQL, React and REST APIs.")

    document.save(RESUME_PATH)

    # Basic DOCX archive verification
    with ZipFile(RESUME_PATH) as archive:
        assert "word/document.xml" in archive.namelist()

    test_passed("Random DOCX resume generated")

    return RESUME_PATH

# Step 2: Upload resume

def upload_resume(file_path):

    boundary = "----Boundary" + uuid.uuid4().hex

    file_bytes = file_path.read_bytes()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; '
        f'filename="{file_path.name}"\r\n'
        f"Content-Type: application/vnd.openxmlformats-officedocument."
        f"wordprocessingml.document\r\n\r\n"
    ).encode("utf-8")

    body += file_bytes

    body += f"\r\n--{boundary}--\r\n".encode("utf-8")

    request = urllib.request.Request(BASE_URL + "/api/resumes/upload",
        data=body, headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:

            result = json.loads(response.read().decode("utf-8"))

    except urllib.error.HTTPError as error:
        raise RuntimeError("Resume upload failed: " + error.read().decode("utf-8"))

    filename = result["filename"]

    assert filename
    assert result["status"] == "success"

    test_passed("Resume upload API")

    return filename, result

# Step 3: Run complete backend tests

def run_tests():

    print("\n====================================")
    print(" AI RESUME ANALYZER BACKEND TEST")
    print("====================================\n")

    # Test 1: Health
    health = api_request("/health")

    assert health["status"] == "healthy"

    test_passed("Backend health check")

    # Test 2: Resume generation
    resume_path = generate_random_resume()

    # Test 3: Upload
    filename, upload_result = upload_resume(resume_path)

    print("Uploaded filename:", filename)

    # Test 4: Resume text extraction
    text_result = api_request(f"/api/resumes/{filename}/text")

    assert text_result["character_count"] > 0

    test_passed("Resume text extraction")

    # Test 5: Skill extraction
    skill_result = api_request(f"/api/skills/extract/{filename}")

    assert "skills" in skill_result

    test_passed("Resume skill extraction")

    # Test 6: Job description analysis
    job_description = ("We are looking for a Java Backend Developer " "with experience in Java, Spring Boot, "
        "Hibernate, PostgreSQL, REST API and Microservices. " "Candidates should understand SQL, Git, "
        "Docker and backend application development.")

    job_result = api_request("/api/jobs/analyze", method="POST", data={
            "job_description": job_description
        }
    )

    test_passed("Job description analysis")

    # Test 7: Resume-job matching
    request_data = {
        "filename": filename, "job_description": job_description
    }

    match_result = api_request("/api/analysis/match", method="POST", data=request_data)

    assert match_result["status"] == "success"
    assert match_result["database_status"] == "saved"

    analysis_id = match_result["analysis_id"]

    test_passed("Resume-job matching")
    test_passed("Match result saved in PostgreSQL")

    # Test 8: Recommendations
    recommendation_result = api_request("/api/analysis/recommendations", method="POST", data=request_data)

    assert recommendation_result["status"] == "success"
    assert recommendation_result["database_status"] == "saved"

    test_passed("Recommendation generation")
    test_passed("Recommendations saved in PostgreSQL")

    # Test 9: Resume history
    resume_history = api_request("/api/history/resumes")

    assert resume_history["total_returned"] >= 1

    test_passed("Resume history API")

    # Test 10: Analysis history
    analysis_history = api_request("/api/history/analyses")

    assert analysis_history["total_returned"] >= 1

    test_passed("Analysis history API")

    # Test 11: Individual analysis details
    details = api_request(f"/api/history/analyses/{analysis_id}")

    assert details["status"] == "success"

    test_passed("Individual analysis details API")

    # Test 12: Recommendations retrieval
    analysis_data = details["analysis"]

    assert "recommendations" in analysis_data

    test_passed("Saved recommendations retrieval")

    # Final report

    print("\n====================================")
    print(" BACKEND TEST SUMMARY")
    print("====================================")

    for test in passed_tests:
        print(f"[PASS] {test}")

    print("\nTotal passed:", len(passed_tests))
    print("Failed: 0")

    print("\nResume ID:", upload_result.get("resume_id"))
    print("Analysis ID:", analysis_id)

    print("Match Score:",
        match_result["matching_analysis"]["match_score"])

    print("\nALL BACKEND TESTS COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":

    try:
        run_tests()

    except Exception as error:

        print("\n[FAILED] Backend testing stopped.")
        print("Reason:", repr(error))
        print("\nCheck the Uvicorn terminal for the corresponding " "backend error.")
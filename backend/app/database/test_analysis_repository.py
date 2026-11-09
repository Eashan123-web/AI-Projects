from app.database.resume_repository import get_resume_by_filename
from app.database.job_repository import save_job_description
from app.database.analysis_repository import (save_analysis_result, get_analysis_result)

if __name__ == "__main__":

    # Replace this with an actual filename already uploaded through the API.
    resume_filename = "YOUR_UPLOADED_RESUME_FILENAME.pdf"

    resume = get_resume_by_filename(resume_filename)

    if not resume:
        print("Resume not found in database.")
        raise SystemExit(1)

    job = save_job_description(title="Java Backend Developer",
        description=("Java, Spring Boot, PostgreSQL, " "REST API and Microservices experience required."))

    sample_matching_analysis = {
        "match_score": 75.0, "total_required_skills": 4, "total_matched_skills": 3, "total_missing_skills": 1,
        "matching_skills": ["Java", "Spring Boot", "PostgreSQL"], "missing_skills": ["Microservices"],
        "additional_skills": ["Python"]
    }

    analysis = save_analysis_result(resume_id=resume["id"], job_id=job["id"], match_score=75.0,
        matching_analysis=sample_matching_analysis
    )

    print("\nANALYSIS SAVED SUCCESSFULLY!")
    print(analysis)

    retrieved_analysis = get_analysis_result(analysis["id"])

    print("\nRETRIEVED ANALYSIS:")
    print(retrieved_analysis)
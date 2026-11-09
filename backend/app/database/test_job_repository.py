from app.database.job_repository import (save_job_description, get_job_description)

if __name__ == "__main__":

    job = save_job_description(title="Java Backend Developer",
        description=("Looking for a Java developer with " "Spring Boot, REST API, PostgreSQL "
            "and Microservices experience."))

    print("JOB DESCRIPTION SAVED SUCCESSFULLY!")
    print(job)

    saved_job = get_job_description(job["id"])

    print("\nRETRIEVED JOB DESCRIPTION:")
    print(saved_job)

import json
import re
from pathlib import Path

from app.services.skill_service import extract_skills

BASE_DIR = Path(__file__).resolve().parents[1]
PATTERNS_FILE = BASE_DIR / "data" / "job_patterns.json"

def load_job_patterns():
    if not PATTERNS_FILE.exists():
        raise FileNotFoundError("Job patterns configuration file not found.")

    with PATTERNS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)

def extract_requirements(job_description: str):

    if not job_description or not job_description.strip():
        raise ValueError("Job description cannot be empty.")

    patterns = load_job_patterns()

    result = {}

    for category, expressions in patterns.items():

        matches = set()

        for expression in expressions:

            found = re.finditer(expression, job_description, flags=re.IGNORECASE)

            for match in found:
                matches.add(match.group(0))

        result[category] = sorted(matches, key=str.lower)

    return result

def analyze_job_description(job_description: str):

    if not job_description or not job_description.strip():
        raise ValueError("Job description cannot be empty.")

    skills = extract_skills(job_description)

    total_skills = sum(
        len(category_skills)
        for category_skills in skills.values()
    )

    requirements = extract_requirements(job_description)

    return {
        "skills": skills, "total_skills": total_skills,
        "experience_requirements": requirements.get("experience", []),
        "education_requirements": requirements.get("education", [])
    }

import re

def generate_skill_recommendations(missing_skills: dict):
    """Generate recommendations for missing job skills."""

    recommendations = []

    for category, skills in missing_skills.items():

        for skill in skills:

            recommendations.append({
                "category": category, "skill": skill, "priority": "High",
                "recommendation": (f"If you have practical experience with {skill}, "
                    "include a relevant project or work example in " "your resume. Otherwise, consider learning it.")
            })

    return recommendations

def extract_missing_keywords(resume_text: str, job_description: str):
    """Identify meaningful job-description terms that are not present in the resume.
    This is a simple keyword-gap detector, not an AI understanding or semantic similarity model."""

    stop_words = {
        "the", "and", "for", "with", "from", "this", "that", "are", "was", "were", "will", "have", "from", "its",
        "has", "had", "you", "your", "our", "their", "they", "them", "who", "what", "when", "where", "also", "such",
        "how", "why", "all", "any", "can", "should", "must", "would", "could", "into", "about",
        "using", "use", "work", "working", "experience", "knowledge", "strong", "good", "ability",
        "required", "requirements", "responsibilities", "developer", "development", "years", "year", "other"
    }

    resume_normalized = resume_text.casefold()

    job_words = re.findall(r"\b[a-zA-Z][a-zA-Z+#.-]{2,}\b", job_description.casefold())

    missing_keywords = []
    seen = set()

    for word in job_words:

        if word in stop_words or word in seen:
            continue

        seen.add(word)

        # Check whole-word presence
        pattern = r"(?<!\w)" + re.escape(word) + r"(?!\w)"

        if not re.search(pattern, resume_normalized):
            missing_keywords.append(word)

    return missing_keywords[:20]

def generate_resume_recommendations(resume_text: str, job_description: str, matching_analysis: dict):
    """Generate a complete resume improvement report."""

    if not resume_text.strip():
        raise ValueError("Resume text cannot be empty.")

    if not job_description.strip():
        raise ValueError("Job description cannot be empty.")

    if not isinstance(matching_analysis, dict):
        raise ValueError("Invalid matching analysis.")

    missing_skills = matching_analysis.get("missing_skills", {})

    matching_skills = matching_analysis.get("matching_skills", {})

    skill_recommendations = generate_skill_recommendations(missing_skills)

    missing_keywords = extract_missing_keywords(resume_text, job_description)

    general_recommendations = []

    if missing_skills:

        general_recommendations.append("Review the missing technical skills and add "
            "relevant evidence only where supported by " "your actual experience.")

    if missing_keywords:

        general_recommendations.append("Review the missing job-description keywords. "
            "Include relevant terminology naturally where " "it accurately describes your experience.")

    if matching_skills:

        general_recommendations.append("Highlight your matching technical skills in "
            "your professional summary and relevant project " "or employment descriptions.")

    if not general_recommendations:

        general_recommendations.append(
            "Your resume covers the detected job skills. " "Review your project descriptions and achievements "
            "to improve clarity and relevance.")

    return {
        "skill_recommendations": skill_recommendations, "missing_keywords": missing_keywords,
        "general_recommendations": general_recommendations,
        "summary_improvement_tip": (
            "Write a concise professional summary highlighting " "your verified experience, relevant technical skills "
            "and projects that align with this job description. " "Do not claim skills or experience you do not have.")
    }
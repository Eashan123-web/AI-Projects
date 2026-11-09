
import json

from app.services.ollama_service import generate_ai_response

def generate_resume_improvements(resume_text: str, job_description: str, matching_analysis: dict,
    rag_context: list = None):
    """Generate practical, job-specific resume improvement suggestions using Ollama and retrieved resume context."""

    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text cannot be empty.")

    if not job_description or not job_description.strip():
        raise ValueError("Job description cannot be empty.")

    system_prompt = """You are an expert resume writer, career coach, and technical recruiter.

    Your task is to improve a candidate's resume for a specific job.

    Follow these rules strictly:

    1. Use only information supported by the supplied resume.
    2. Never invent skills, qualifications, projects, or work experience.
    3. Never fabricate achievements, metrics, or responsibilities.
    4. Identify missing job-related skills honestly.
    5. Improve wording while preserving the candidate's actual experience.
    6. Use relevant retrieved resume sections as supporting context.
    7. Make suggestions practical, professional, and ATS-friendly.
    8. Do not claim the candidate has a missing skill.
    9. Clearly distinguish suggested changes from verified experience.

    Return your response using these headings:

    1. Resume Improvement Summary
    2. Professional Summary - Improved Version
    3. Experience and Project Improvements
    4. Missing Skills and Keywords
    5. ATS Optimization Suggestions
    6. Recommended Next Actions

    If information is unavailable, explicitly mention that it is unavailable."""

    analysis_data = {
        "resume_text": resume_text, "job_description": job_description, "matching_analysis": matching_analysis,
        "retrieved_resume_context": rag_context or []
    }

    prompt = f"""
    Improve the following resume for the supplied job description.

    CANDIDATE AND JOB INFORMATION:

    {json.dumps(analysis_data, indent=2, ensure_ascii=False)}

    Provide specific, actionable improvements.

    For the professional summary, write an improved version based
    only on verified information from the resume.

    For experience and projects, suggest stronger wording without
    adding responsibilities or achievements that are not supported.

    Identify missing keywords separately. Do not insert missing
    skills into the candidate's experience as if they already
    possess those skills.

    Make the recommendations relevant to the target job."""

    return generate_ai_response(prompt=prompt, system_prompt=system_prompt)
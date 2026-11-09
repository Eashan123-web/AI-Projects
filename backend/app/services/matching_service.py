
def calculate_match(resume_skills: dict, job_skills: dict):
    """Compare resume skills against job-required skills. The score represents technical skill coverage."""

    if not isinstance(resume_skills, dict):
        raise ValueError("Invalid resume skills.")

    if not isinstance(job_skills, dict):
        raise ValueError("Invalid job skills.")

    matching_skills = {}
    missing_skills = {}
    additional_skills = {}

    total_required = 0
    total_matched = 0

    # Process every category required by the job
    for category, required_skills in job_skills.items():

        candidate_skills = resume_skills.get(category, [])

        # Compare without case sensitivity
        candidate_lookup = {
            skill.casefold(): skill
            for skill in candidate_skills
        }

        matched = []
        missing = []

        for skill in required_skills:

            total_required += 1

            if skill.casefold() in candidate_lookup:
                matched.append(skill)
                total_matched += 1
            else:
                missing.append(skill)

        if matched:
            matching_skills[category] = matched

        if missing:
            missing_skills[category] = missing

    # Identify resume skills not required by the job
    for category, candidate_skills in resume_skills.items():

        required_lookup = {
            skill.casefold()
            for skill in job_skills.get(category, [])
        }

        extra = [
            skill
            for skill in candidate_skills
            if skill.casefold() not in required_lookup
        ]

        if extra:
            additional_skills[category] = extra

    # Calculate technical skill coverage
    if total_required > 0:
        match_score = round((total_matched / total_required) * 100, 2)
    else:
        match_score = 0.0
    return {
        "match_score": match_score, "total_required_skills": total_required, "total_matched_skills": total_matched,
        "total_missing_skills": total_required - total_matched, "matching_skills": matching_skills,
        "missing_skills": missing_skills, "additional_skills": additional_skills
    }
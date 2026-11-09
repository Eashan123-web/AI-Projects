
import logging
from collections import Counter

from fastapi import APIRouter, HTTPException

from app.database.db import get_connection


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"],
)


def count_skills(skill_data):
    """
    Count skills grouped by category.

    Expected structure:
    {
        "Backend Development": ["Java", "Spring Boot"]
    }
    """

    skills = Counter()

    if not isinstance(skill_data, dict):
        return skills

    for category_skills in skill_data.values():

        if isinstance(category_skills, list):

            for skill in category_skills:

                if isinstance(skill, str) and skill.strip():
                    skills[skill.strip()] += 1

    return skills


@router.get("/stats")
def get_dashboard_stats():
    """
    Retrieve dashboard statistics and analytics.
    """

    try:

        with get_connection() as conn:

            with conn.cursor() as cursor:

                # 1. Total resumes
                cursor.execute(
                    "SELECT COUNT(*) FROM resumes"
                )

                total_resumes = cursor.fetchone()[0]

                # 2. Total job descriptions
                cursor.execute(
                    "SELECT COUNT(*) FROM job_descriptions"
                )

                total_jobs = cursor.fetchone()[0]

                # 3. Analysis statistics
                cursor.execute(
                    """
                    SELECT
                        COUNT(*),
                        COALESCE(AVG(match_score), 0),
                        COALESCE(MAX(match_score), 0)
                    FROM analysis_results
                    """
                )

                analysis_stats = cursor.fetchone()

                total_analyses = analysis_stats[0]
                average_score = float(analysis_stats[1] or 0)
                highest_score = float(analysis_stats[2] or 0)

                # 4. Total recommendations
                cursor.execute(
                    "SELECT COUNT(*) FROM recommendations"
                )

                total_recommendations = cursor.fetchone()[0]

                # 5. Match score distribution
                cursor.execute(
                    """
                    SELECT
                        CASE
                            WHEN match_score < 40 THEN 'Low'
                            WHEN match_score < 60 THEN 'Moderate'
                            WHEN match_score < 80 THEN 'Good'
                            ELSE 'Excellent'
                        END AS score_category,
                        COUNT(*)
                    FROM analysis_results
                    WHERE match_score IS NOT NULL
                    GROUP BY score_category
                    """
                )

                score_rows = cursor.fetchall()

                score_distribution = {
                    "Low": 0,
                    "Moderate": 0,
                    "Good": 0,
                    "Excellent": 0,
                }

                for category, count in score_rows:

                    if category in score_distribution:
                        score_distribution[category] = count

                # 6. Skill analytics
                cursor.execute(
                    """
                    SELECT matching_analysis
                    FROM analysis_results
                    WHERE matching_analysis IS NOT NULL
                    """
                )

                analysis_rows = cursor.fetchall()

                matched_skills = Counter()
                missing_skills = Counter()

                total_matched_skills = 0
                total_missing_skills = 0

                for row in analysis_rows:

                    matching_analysis = row[0]

                    if not isinstance(matching_analysis, dict):
                        continue

                    matching = matching_analysis.get(
                        "matching_skills", {}
                    )

                    missing = matching_analysis.get(
                        "missing_skills", {}
                    )

                    matched_count = count_skills(matching)
                    missing_count = count_skills(missing)

                    matched_skills.update(matched_count)
                    missing_skills.update(missing_count)

                    total_matched_skills += sum(
                        matched_count.values()
                    )

                    total_missing_skills += sum(
                        missing_count.values()
                    )

                # 7. Recent analysis activity
                cursor.execute(
                    """
                    SELECT
                        a.id,
                        r.original_filename,
                        j.title,
                        a.match_score,
                        a.created_at
                    FROM analysis_results a
                    LEFT JOIN resumes r
                        ON a.resume_id = r.id
                    LEFT JOIN job_descriptions j
                        ON a.job_id = j.id
                    ORDER BY a.created_at DESC
                    LIMIT 10
                    """
                )

                recent_rows = cursor.fetchall()

                recent_analyses = []

                for row in recent_rows:

                    recent_analyses.append(
                        {
                            "analysis_id": row[0],
                            "resume_filename": row[1],
                            "job_title": row[2],
                            "match_score": (
                                float(row[3])
                                if row[3] is not None
                                else 0.0
                            ),
                            "created_at": row[4],
                        }
                    )

                # 8. Final dashboard response
                return {
                    "message": (
                        "Dashboard statistics retrieved successfully."
                    ),

                    "summary": {
                        "total_resumes": total_resumes,
                        "total_jobs": total_jobs,
                        "total_analyses": total_analyses,
                        "total_recommendations": total_recommendations,
                        "average_match_score": round(
                            average_score, 2
                        ),
                        "highest_match_score": round(
                            highest_score, 2
                        ),
                    },

                    "score_distribution": score_distribution,

                    "skill_analytics": {
                        "total_matched_skills": total_matched_skills,
                        "total_missing_skills": total_missing_skills,

                        "most_matched_skills": [
                            {
                                "skill": skill,
                                "count": count,
                            }
                            for skill, count in matched_skills.most_common(10)
                        ],

                        "most_missing_skills": [
                            {
                                "skill": skill,
                                "count": count,
                            }
                            for skill, count in missing_skills.most_common(10)
                        ],
                    },

                    "recent_analyses": recent_analyses,
                    "status": "success",
                }

    except Exception:
        logger.exception("Dashboard statistics retrieval failed.")

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve dashboard statistics.",
        )

function RecommendationResults({ result }) {
  if (!result || !result.recommendations) {
    return null;
  }

  const {
    skill_recommendations = [], missing_keywords = [], general_recommendations = [], summary_improvement_tip = "",
  } = result.recommendations;

  // Exclude generic words that do not provide useful resume guidance.
  const genericKeywords = ["looking", "candidate"];

  const usefulKeywords = missing_keywords.filter((keyword) => !genericKeywords.includes(keyword.toLowerCase()));

  const getPriorityClass = (priority) => {
    switch (priority?.toLowerCase()) {
      case "high":
        return "priority-high";
      case "medium":
        return "priority-medium";
      case "low":
        return "priority-low";
      default:
        return "priority-default";
    }
  };

  return (
    <section className="recommendations-container">
      <div className="recommendations-heading">
        <div>
          <span className="section-eyebrow">CAREER IMPROVEMENT</span>
          <h2>Resume Recommendations</h2>
          <p>Practical suggestions based on your resume and the selected job description.</p>
        </div>

        <div className="recommendation-score">
          <span>Current Match</span>
          <strong>{result.match_score ?? 0}%</strong>
        </div>
      </div>

      <div className="recommendation-section">
        <h3>Skill Gap Recommendations</h3>
        <p className="section-description">Review these job requirements and add evidence only if you genuinely
          have the relevant experience.</p>

        {skill_recommendations.length > 0 ? (
          <div className="skill-recommendation-list">
            {skill_recommendations.map((item, index) => (
              <article
                className="skill-recommendation-card"
                key={`${item.category}-${item.skill}-${index}`}
              >
                <div className="recommendation-card-top">
                  <div>
                    <h4>{item.skill}</h4>
                    <span className="recommendation-category">{item.category}</span>
                  </div>

                  <span className={`priority-badge ${getPriorityClass(item.priority)}`}>
                    {item.priority || "Normal"} Priority</span>
                </div>

                <p>{item.recommendation}</p>
              </article>
            ))}
          </div>
        ) : (
          <p>No skill gap recommendations available.</p>
        )}
      </div>

      <div className="recommendation-section">
        <h3>Missing Job Description Keywords</h3>
        <p className="section-description">Check whether these terms accurately describe your existing skills
          and experience.
        </p>

        {usefulKeywords.length > 0 ? (
          <div className="keyword-list">
            {usefulKeywords.map((keyword, index) => (
              <span className="keyword-chip" key={`${keyword}-${index}`}>{keyword}</span>
            ))}
          </div>
        ) : (
          <p>No additional keywords identified.</p>
        )}
      </div>

      <div className="recommendation-section">
        <h3>General Recommendations</h3>

        {general_recommendations.length > 0 ? (
          <ul className="general-recommendation-list">
            {general_recommendations.map((recommendation, index) => (
              <li key={index}>{recommendation}</li>
            ))}
          </ul>
        ) : (
          <p>No general recommendations available.</p>
        )}
      </div>

      <div className="summary-tip-card">
        <div className="summary-tip-icon">✦</div>
        <div>
          <h3>Professional Summary Improvement</h3>
          <p>{summary_improvement_tip || "No summary tip available."}</p>
        </div>
      </div>

      <p className="recommendation-disclaimer">
        These are resume-improvement suggestions, not claims about your qualifications or a prediction of hiring success. 
        Only include skills and experience you can verify.</p>
    </section>
  );
}

export default RecommendationResults;
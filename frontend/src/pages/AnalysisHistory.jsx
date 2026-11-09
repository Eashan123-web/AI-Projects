import { useCallback, useEffect, useMemo, useState } from "react";
import {
  getAnalysisHistory,
  getAnalysisDetails,
} from "../services/api";

function formatDate(dateString) {
  if (!dateString) return "Date unavailable";

  const date = new Date(dateString);

  if (Number.isNaN(date.getTime())) {
    return "Date unavailable";
  }

  return date.toLocaleString("en-IN", {
    day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit",
  });
}

function getScoreClass(score) {
  if (score >= 75) return "history-score-high";
  if (score >= 50) return "history-score-medium";
  return "history-score-low";
}

function SkillCategory({ title, skills, type }) {
  const categories = Object.entries(skills || {});

  return (
    <div className={`history-skill-card ${type}`}>
      <h4>{title}</h4>

      {categories.length === 0 ? (
        <p>No skills available.</p>
      ) : (
        categories.map(([category, items]) => (
          <div className="history-skill-category" key={category}>
            <strong>{category}</strong>

            <div className="history-skill-tags">
              {(items || []).map((skill) => (
                <span key={skill}>{skill}</span>
              ))}
            </div>
          </div>
        ))
      )}
    </div>
  );
}

function AnalysisDetails({ analysis, onBack }) {
  const matching = analysis.matching_analysis || {};
  const recommendations = analysis.recommendations || [];

  return (
    <div className="history-detail-page">
      <button type="button"
        className="history-back-button"
        onClick={onBack}>← Back to Analysis History
      </button>

      <div className="history-detail-heading">
        <div>
          <span className="welcome-label">ANALYSIS DETAILS</span>
          <h2>Analysis #{analysis.analysis_id}</h2>
          <p>{analysis.resume_filename}</p>
          <small>{formatDate(analysis.created_at)}</small>
        </div>

        <div className="history-detail-score">
          <span>Match Score</span>
          <strong>{analysis.match_score ?? 0}%</strong>
        </div>
      </div>

      <div className="history-detail-stats">
        <div>
          <span>Required Skills</span>
          <strong>{matching.total_required_skills ?? 0}</strong>
        </div>

        <div>
          <span>Matched Skills</span>
          <strong>{matching.total_matched_skills ?? 0}</strong>
        </div>

        <div>
          <span>Missing Skills</span>
          <strong>{matching.total_missing_skills ?? 0}</strong>
        </div>
      </div>

      <div className="history-job-description">
        <h3>Job Description</h3>
        <p>{analysis.job_description || "No job description available."}</p>
      </div>

      <div className="history-skills-grid">
        <SkillCategory title="Matched Skills"
          skills={matching.matching_skills}
          type="matched"/>

        <SkillCategory title="Missing Skills"
          skills={matching.missing_skills}
          type="missing"/>

        <SkillCategory title="Additional Skills"
          skills={matching.additional_skills}
          type="additional"/>
      </div>

      <div className="history-saved-recommendations">
        <h3>Saved Recommendations</h3>

        {recommendations.length === 0 ? (
          <p>No recommendations were saved for this analysis.</p>
        ) : (
          recommendations.map((record) => {
            const data = record.recommendation_data || {};

            return (
              <div className="history-recommendation-record"
                key={record.id}>
                <p className="history-recommendation-date">
                  Generated: {formatDate(record.created_at)}</p>

                <h4>Skill Recommendations</h4>

                {data.skill_recommendations?.length > 0 ? (
                  data.skill_recommendations.map((item, index) => (
                    <div
                      className="history-recommendation-item"
                      key={`${item.skill}-${index}`}>
                      <div>
                        <strong>{item.skill}</strong>
                        <span>{item.category}</span>
                      </div>

                      <span className="history-priority">
                        {item.priority || "Normal"} Priority
                      </span>

                      <p>{item.recommendation}</p>
                    </div>
                  ))
                ) : (
                  <p>No skill recommendations available.</p>
                )}

                <h4>Missing Keywords</h4>

                <div className="history-skill-tags">
                  {(data.missing_keywords || [])
                    .filter((keyword) =>
                        !["looking", "candidate"].includes(
                          keyword.toLowerCase()
                        ))
                    .map((keyword, index) => (
                      <span key={`${keyword}-${index}`}>
                        {keyword}
                      </span>
                    ))}
                </div>

                <h4>General Recommendations</h4>

                <ul>
                  {(data.general_recommendations || []).map(
                    (item, index) => (
                      <li key={index}>{item}</li>
                    )
                  )}
                </ul>

                <h4>Professional Summary Tip</h4>
                <p>
                  {data.summary_improvement_tip || "No summary tip available."}
                </p>
              </div>
            );
          })
        )}
      </div>

      <p className="history-disclaimer">
        Match scores represent detected skill overlap. They do not predict hiring probability.
      </p>
    </div>
  );
}

function AnalysisHistory() {
  const [analyses, setAnalyses] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);

  const loadHistory = useCallback(async () => {
  setLoading(true);
  setError("");

    try {
      const data = await getAnalysisHistory();

      if (data.status !== "success") {
        throw new Error(data.message || "Unable to retrieve analysis history.");
      }

    setAnalyses(data.analyses || []);
    } catch (err) {
      setError(err.message || "Failed to load analysis history.");
    } finally {
      setLoading(false);
    }}, []);

useEffect(() => {
  const timer = setTimeout(() => {
    loadHistory();
  }, 0);

  return () => clearTimeout(timer);
}, [loadHistory]);

  const filteredAnalyses = useMemo(() => {
    const search = searchTerm.trim().toLowerCase();

    if (!search)
      return analyses;

    return analyses.filter((item) =>
      [
        item.resume_filename, item.job_title, String(item.analysis_id),
      ].filter(Boolean).some((value) => String(value).toLowerCase().includes(search))
    );
  }, [analyses, searchTerm]);

  const handleViewDetails = async (analysisId) => {
    setLoadingDetails(true);
    setError("");

    try {
      const data = await getAnalysisDetails(analysisId);

      if (data.status !== "success" || !data.analysis) {
        throw new Error(
          data.message || "Unable to retrieve analysis details."
        );
      }

      setSelectedAnalysis(data.analysis);
    } catch (err) {
      setError(err.message || "Failed to load analysis details.");
    } finally {
      setLoadingDetails(false);
    }
  };

  if (selectedAnalysis) {
    return (
      <AnalysisDetails analysis={selectedAnalysis} onBack={() => setSelectedAnalysis(null)}/>
    );
  }

  return (
    <div className="analysis-history-page">
      <div className="upload-page-heading">
        <span className="welcome-label">CAREER INTELLIGENCE</span>
        <h1>Analysis History</h1>
        <p>View your previous resume analyses, match scores and saved recommendations.</p>
      </div>

      <div className="history-summary">
        <div>
          <span>Total Analyses</span>
          <strong>{analyses.length}</strong>
        </div>

        <div>
          <span>Average Match Score</span>
          <strong>
            {analyses.length ? (
                  analyses.reduce((total, item) => total + Number(item.match_score || 0), 0) / analyses.length
                ).toFixed(2) : "0.00"} %
          </strong>
        </div>
      </div>

      <div className="history-table-card">
        <div className="history-table-heading">
          <div>
            <h2>Previous Analyses</h2>
            <p>Review your saved resume matching activity.</p>
          </div>

          <button type="button"
            className="history-refresh-button"
            onClick={loadHistory}
            disabled={loading}>
            {loading ? "Refreshing..." : "↻ Refresh"}
          </button>
        </div>

        <div className="history-search">
          <input type="text"
            placeholder="Search resume filename or analysis ID..."
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.target.value)}/>
        </div>

        {error && (
          <div className="upload-error">{error}</div>
        )}

        {loading ? (
          <div className="history-empty-state">Loading analysis history...</div>
        ) : filteredAnalyses.length === 0 ? (
          <div className="history-empty-state">
            {analyses.length === 0 ? "No analysis history found."  : "No matching records found."}
          </div>
        ) : (
          <div className="history-table-wrapper">
            <table className="history-table">
              <thead>
                <tr>
                  <th>Analysis ID</th>
                  <th>Resume</th>
                  <th>Job</th>
                  <th>Match Score</th>
                  <th>Date</th>
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>
                {filteredAnalyses.map((item) => (
                  <tr key={item.analysis_id}>
                    <td>#{item.analysis_id}</td>

                    <td className="history-filename">{item.resume_filename}</td>

                    <td>{item.job_title || "Job #" + item.job_id}</td>

                    <td>
                      <span
                        className={`history-score ${getScoreClass(Number(item.match_score || 0))}`}>
                        {Number(item.match_score || 0).toFixed(2)}%
                      </span>
                    </td>

                    <td>{formatDate(item.created_at)}</td>

                    <td>
                      <button type="button"
                        className="history-view-button"
                        onClick={() => handleViewDetails(item.analysis_id)
                        }
                        disabled={loadingDetails}>View Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {loadingDetails && (
          <p className="history-loading-details">Loading analysis details...</p>
        )}

        <div className="history-table-footer">Showing {filteredAnalyses.length} of {analyses.length} records</div>
      </div>
    </div>
  );
}

export default AnalysisHistory;
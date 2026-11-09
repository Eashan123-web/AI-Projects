
import { useEffect, useState } from "react";
import { getDashboardStats } from "../services/api";

function formatDate(dateValue) {
  if (!dateValue)
    return "Date unavailable";

  return new Date(dateValue).toLocaleString("en-IN", {
    day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit",
  });
}

function getScoreLabel(score) {
  if (score < 40)
    return "Low";
  if (score < 60)
    return "Moderate";
  if (score < 80)
    return "Good";
  return "Excellent";
}

function Dashboard({ onNavigate }) {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [refreshCount, setRefreshCount] = useState(0);

  useEffect(() => {
    let isActive = true;

    getDashboardStats().then((data) => {
        if (isActive) {
          setDashboardData(data);
          setError("");
        }
      })
      .catch((err) => {
        if (isActive) {
          setError(err.message || "Unable to load dashboard data.");
        }
      })
      .finally(() => {
        if (isActive) {
          setLoading(false);
        }
      });

    return () => {
      isActive = false;
    };
  }, [refreshCount]);

  const summary = dashboardData?.summary || {};
  const scoreDistribution = dashboardData?.score_distribution || {};
  const skillAnalytics = dashboardData?.skill_analytics || {};
  const recentAnalyses = dashboardData?.recent_analyses || [];
  const statistics = [
    {
      title: "Resumes Uploaded",
      value: summary.total_resumes ?? "—",
      description: "Total resumes stored",
      icon: "📄",
      color: "blue",
    },
    {
      title: "Jobs Analyzed",
      value: summary.total_jobs ?? "—",
      description: "Job descriptions stored",
      icon: "💼",
      color: "purple",
    },
    {
      title: "Average Match Score",
      value: summary.average_match_score !== undefined ? `${summary.average_match_score}%` : "—",
      description: "Across all analyses",
      icon: "📊",
      color: "green",
    },
    {
      title: "Recommendations",
      value: summary.total_recommendations ?? "—",
      description: "Suggestions generated",
      icon: "✨",
      color: "orange",
    },
  ];

  const scoreCategories = [
    { name: "Low", value: scoreDistribution.Low || 0 },
    { name: "Moderate", value: scoreDistribution.Moderate || 0 },
    { name: "Good", value: scoreDistribution.Good || 0 },
    { name: "Excellent", value: scoreDistribution.Excellent || 0 },
  ];

  const maxScoreCount = Math.max(...scoreCategories.map((item) => item.value), 1);
  const matchedSkills = skillAnalytics.most_matched_skills || [];
  const missingSkills = skillAnalytics.most_missing_skills || [];
  const maxMatchedCount = Math.max(...matchedSkills.map((item) => item.count), 1);
  const maxMissingCount = Math.max(...missingSkills.map((item) => item.count), 1);

  function refreshDashboard() {
    setLoading(true);
    setError("");
    setRefreshCount((count) => count + 1);
  }

  if (loading && !dashboardData) {
    return (
      <div className="dashboard">
        <div className="dashboard-loading">
          <div className="loading-spinner"></div>
          <h2>Loading Dashboard...</h2>
          <p>Fetching your latest analytics from PostgreSQL.</p>
        </div>
      </div>
    );
  }

  if (error && !dashboardData) {
    return (
      <div className="dashboard">
        <div className="dashboard-error">
          <h2>Unable to Load Dashboard</h2>
          <p>{error}</p>
          <button className="primary-button"
            onClick={refreshDashboard}>Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      {/* Welcome Section */}
      <section className="welcome-section">
        <div>
          <span className="welcome-label">YOUR CAREER WORKSPACE</span>

          <h1>Welcome to ResumeAI</h1>

          <p>Analyze your resume, discover skill gaps, and understand how well your profile matches a job description.
          </p>
        </div>

        <div className="dashboard-header-actions">
          <button className="secondary-button"
            onClick={refreshDashboard}
            disabled={loading}>
            {loading ? "Refreshing..." : "↻ Refresh"}
          </button>

          <button className="primary-button"
            onClick={() => onNavigate("Resume Analysis")}>+ Analyze a Resume
          </button>
        </div>
      </section>

      {error && (
        <div className="dashboard-inline-error">{error} Previous dashboard data is still displayed.</div>
      )}

      {/* Statistics Cards */}
      <section className="stats-grid">
        {statistics.map((stat) => (
          <article
            className={`stat-card dashboard-stat-card ${stat.color}`}
            key={stat.title}>
            <div className="dashboard-stat-top">
              <p className="stat-title">{stat.title}</p>
              <span className="dashboard-stat-icon">{stat.icon}</span>
            </div>

            <h2>{stat.value}</h2>

            <span>{stat.description}</span>
          </article>
        ))}
      </section>

      {/* Additional Statistics */}
      <section className="dashboard-mini-stats">
        <article className="dashboard-mini-card">
          <span>Highest Match Score</span>
          <strong>{summary.highest_match_score !== undefined ? `${summary.highest_match_score}%` : "—"}</strong>
        </article>

        <article className="dashboard-mini-card">
          <span>Total Analyses</span>
          <strong>{summary.total_analyses ?? "—"}</strong>
        </article>

        <article className="dashboard-mini-card">
          <span>Matched Skill Occurrences</span>
          <strong>{skillAnalytics.total_matched_skills ?? 0}</strong>
        </article>

        <article className="dashboard-mini-card">
          <span>Missing Skill Occurrences</span>
          <strong>{skillAnalytics.total_missing_skills ?? 0}</strong>
        </article>
      </section>

      {/* Analytics */}
      <section className="dashboard-analytics-grid">

        {/* Score Distribution */}
        <article className="dashboard-card analytics-card">
          <div className="section-heading">
            <div>
              <h2>Match Score Distribution</h2>
              <p>Number of analyses in each score range</p>
            </div>
          </div>

          <div className="score-distribution">
            {scoreCategories.map((item) => (
              <div className="score-bar-item" key={item.name}>
                <div className="score-bar-heading">
                  <span>{item.name}</span>
                  <strong>{item.value}</strong>
                </div>

                <div className="score-bar-track">
                  <div className={`score-bar-fill ${item.name.toLowerCase()}`}
                    style={{
                      width: `${(item.value / maxScoreCount) * 100}%`,
                    }}
                  ></div>
                </div>
              </div>
            ))}
          </div>

          <div className="analytics-footer">Total completed analyses: {summary.total_analyses ?? 0}</div>
        </article>

        {/* Skill Overview */}
        <article className="dashboard-card analytics-card">
          <div className="section-heading">
            <div>
              <h2>Skills Overview</h2>
              <p>Matched versus missing skill occurrences</p>
            </div>
          </div>

          <div className="skill-overview">
            <div className="skill-overview-item matched-overview">
              <span>Matched Skills</span>
              <strong>{skillAnalytics.total_matched_skills ?? 0}</strong>
            </div>

            <div className="skill-overview-item missing-overview">
              <span>Missing Skills</span>
              <strong>{skillAnalytics.total_missing_skills ?? 0}</strong>
            </div>
          </div>

          <div className="analytics-footer">These are skill occurrences across saved analyses, not unique skills.</div>
        </article>
      </section>

      {/* Skill Analytics */}
      <section className="dashboard-analytics-grid">

        <article className="dashboard-card analytics-card">
          <div className="section-heading">
            <div>
              <h2>Most Matched Skills</h2>
              <p>Skills frequently found in resumes</p>
            </div>
          </div>

          {matchedSkills.length > 0 ? (
            <div className="skill-ranking-list">
              {matchedSkills.map((item, index) => (
                <div className="skill-ranking-item" key={item.skill}>
                  <div className="skill-ranking-heading">
                    <span><b>{index + 1}.</b> {item.skill}</span>
                    <strong>{item.count}</strong>
                  </div>

                  <div className="skill-ranking-track">
                    <div className="skill-ranking-fill matched-fill"
                      style={{
                        width: `${(item.count / maxMatchedCount) * 100}%`,
                      }}></div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="dashboard-no-data">No matched skill data available.</p>
          )}
        </article>

        <article className="dashboard-card analytics-card">
          <div className="section-heading">
            <div>
              <h2>Most Missing Skills</h2>
              <p>Skills frequently absent from resumes</p>
            </div>
          </div>

          {missingSkills.length > 0 ? (
            <div className="skill-ranking-list">
              {missingSkills.map((item, index) => (
                <div className="skill-ranking-item" key={item.skill}>
                  <div className="skill-ranking-heading">
                    <span>
                      <b>{index + 1}.</b> {item.skill}
                    </span>
                    <strong>{item.count}</strong>
                  </div>

                  <div className="skill-ranking-track">
                    <div className="skill-ranking-fill missing-fill"
                      style={{
                        width: `${(item.count / maxMissingCount) * 100}%`,
                      }}></div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="dashboard-no-data">No missing skill data available.</p>
          )}
        </article>
      </section>

      {/* Recent Activity */}
      <section className="dashboard-card recent-activity">
        <div className="section-heading">
          <div>
            <h2>Recent Activity</h2>
            <p>Your latest resume and job analysis records</p>
          </div>

          <button className="text-button"
            onClick={() => onNavigate("Analysis History")}>View History →</button>
        </div>

        {recentAnalyses.length > 0 ? (
          <div className="recent-activity-table-wrapper">
            <table className="recent-activity-table">
              <thead>
                <tr>
                  <th>Analysis ID</th>
                  <th>Resume</th>
                  <th>Job Title</th>
                  <th>Match Score</th>
                  <th>Category</th>
                  <th>Date</th>
                </tr>
              </thead>

              <tbody>
                {recentAnalyses.map((analysis) => (
                  <tr key={analysis.analysis_id}>
                    <td>#{analysis.analysis_id}</td>

                    <td className="recent-resume-name">{analysis.resume_filename || "Unknown resume"}</td>

                    <td>{analysis.job_title || "Not specified"}</td>

                    <td><strong>{analysis.match_score}%</strong></td>

                    <td>
                      <span className={`score-category-badge ${getScoreLabel(analysis.match_score).toLowerCase()}`}>
                        {getScoreLabel(analysis.match_score)}
                      </span>
                    </td>

                    <td>{formatDate(analysis.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-state-icon">◷</div>
            <h3>No analysis activity yet</h3>
            <p>Your completed resume analyses will appear here.</p>
            <button className="secondary-button"
              onClick={() => onNavigate("Resume Analysis")}> Analyze Your First Resume
            </button>
          </div>
        )}
      </section>
    </div>
  );
}

export default Dashboard;
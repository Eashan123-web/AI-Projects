import "./ResumeImprovementResults.css";

function ResumeImprovementResults({ result }) {
  if (!result) {
    return null;
  }

  return (
    <div className="resume-improvement-results">

      <div className="results-heading">
        <span className="welcome-label">AI CAREER ASSISTANT</span>
        <h2>AI Resume Improvement Results</h2>
        <p>
          Personalized suggestions to improve your resume for the target job.
        </p>
      </div>

      <div className="improvement-summary-grid">

        <div className="improvement-summary-card">
          <span>Resume Match Score</span>
          <h3>{result.match_score ?? "N/A"}{result.match_score != null ? "%" : ""}</h3>
        </div>

        <div className="improvement-summary-card">
          <span>RAG Context Retrieved</span>
          <h3>{result.rag_analysis?.chunks_retrieved ?? 0}</h3>
        </div>

      </div>

      <div className="improvement-content-card">
        <h3>AI-Generated Improvements</h3>

        {typeof result.improvements === "string" ? (
          <div className="improvement-text">
            {result.improvements}
          </div>
        ) : (
          <pre className="improvement-text">
            {JSON.stringify(result.improvements, null, 2)}
          </pre>
        )}
      </div>

      <div className="improvement-footer">
        <span>✓ AI improvement analysis generated successfully.</span>
      </div>

    </div>
  );
}

export default ResumeImprovementResults;
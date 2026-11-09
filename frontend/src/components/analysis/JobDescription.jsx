import { useState } from "react";
import { analyzeJobDescription } from "../../services/api";

function JobDescription() {
  const [jobDescription, setJobDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [analysisResult, setAnalysisResult] = useState(null);

  const handleAnalyze = async () => {
    setError("");
    setAnalysisResult(null);

    if (!jobDescription.trim()) {
      setError("Please enter a job description.");
      return;
    }

    if (jobDescription.trim().length < 30) {
      setError("Please enter a more detailed job description.");
      return;
    }

    setLoading(true);

    try {
      const result = await analyzeJobDescription(jobDescription);
      setAnalysisResult(result);
    } catch (err) {
      setError(err.message || "Unable to analyze the job description.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="job-description-page">
      <div className="upload-page-heading">
        <span className="welcome-label">JOB REQUIREMENTS</span>
        <h1>Analyze a Job Description</h1>
        <p> Paste a job description to identify required skills, technologies, and important keywords.</p>
      </div>

      <div className="job-description-card">
        <label htmlFor="job-description">Job Description</label>

        <textarea id="job-description"
          className="job-description-input"
          placeholder="Paste the complete job description here...

Example:
We are looking for a Java Developer with experience in Spring Boot, REST APIs, SQL, and Microservices..."
          value={jobDescription}
          onChange={(event) => {
            setJobDescription(event.target.value);
            setError("");
            setAnalysisResult(null);
          }}
          rows={12}/>

        <div className="description-footer">
          <span>{jobDescription.length} characters</span>
          <span>Paste the complete job requirements for better results.</span>
        </div>

        <button className="primary-button analyze-job-button" onClick={handleAnalyze} disabled={loading}>
          {loading ? "Analyzing..." : "Analyze Job Description"}
        </button>

        {error && (
          <div className="upload-error">{error}</div>
        )}

        {analysisResult !== null && (
          <div className="job-analysis-result">
            <div className="section-heading">
              <div>
                <h2>Job Analysis Results</h2>
                <p>Analysis returned by your FastAPI backend</p>
              </div>
            </div>

            <pre className="analysis-output">
              {typeof analysisResult === "string" ? analysisResult : JSON.stringify(analysisResult, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}

export default JobDescription;
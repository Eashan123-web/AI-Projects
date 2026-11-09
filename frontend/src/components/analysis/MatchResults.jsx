
function SkillGroup({ title, skills, color }) {
  if (!skills || Object.keys(skills).length === 0) {
    return (<p className="results-description"> No skills available.</p>);
  }

  return (
    <div className="skill-group">
      <h4>{title}</h4>

      {Object.entries(skills).map(([category, items]) => (
        <div className="skill-category" key={category}>
          <strong>{category}</strong>

          <div className="skill-tags">{items.map((skill) => (
              <span className={`skill-tag ${color}`} key={skill}>{skill}</span>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

function MatchResults({ result }) {
  console.log("MatchResults component received:", result);

  if (!result) {
    console.log("No matching result received.");
    return null;
  }

  const analysis = result.matching_analysis || {};
  const score = Number(analysis.match_score ?? 0);
  const matched = analysis.matching_skills || {};
  const missing = analysis.missing_skills || {};
  const additional = analysis.additional_skills || {};
  const jobSkills = result.job_analysis?.skills || {};

  const formatSkills = (groups) =>
    Object.values(groups).reduce((total, skills) => total + skills.length, 0);

  return (
    <section className="match-results">
      <div className="results-heading">
        <span className="section-label">ANALYSIS COMPLETE</span>
        <h2>Resume Matching Results</h2>
        <p>Your resume has been compared with the supplied job description.</p>
      </div>

      <div className="results-overview">
        <div className="score-card">
          <span className="result-label">Resume Match Score</span>
          <div className="score-value">{score.toFixed(2)}%</div>

          <div className="score-track">
            <div className="score-fill"
              style={{
                width: `${Math.min(100, Math.max(0, score))}%`,
              }}/>
          </div>

          <span className="score-caption">Based on detected required skills</span>
        </div>

        <div className="stat-card">
          <span className="result-label">Required Skills</span>
          <strong>{analysis.total_required_skills ?? 0}</strong>
        </div>

        <div className="stat-card">
          <span className="result-label">Matched Skills</span>
          <strong className="matched-number">{analysis.total_matched_skills ?? 0}</strong>
        </div>

        <div className="stat-card">
          <span className="result-label">Missing Skills</span>
          <strong className="missing-number">{analysis.total_missing_skills ?? 0}</strong>
        </div>

        <div className="stat-card">
          <span className="result-label">Additional Skills</span>
          <strong>{formatSkills(additional)}</strong>
        </div>
      </div>

      <div className="results-section">
        <h3>Matched Skills</h3>
        <p className="results-description">Skills detected in your resume that match the job requirements.</p>

        <SkillGroup title="Matching Skills by Category" skills={matched} color="matched"/>
      </div>

      <div className="results-section">
        <h3>Missing Skills</h3>
        <p className="results-description"> These requirements were not detected in your resume.</p>

        <SkillGroup title="Skills to Review" skills={missing} color="missing"/>
      </div>

      <div className="results-section">
        <h3>Additional Skills"
        </h3>
        <p className="results-description">Other skills detected in your resume.</p>

        <SkillGroup title="Other Detected Skills" skills={additional} color="additional"/>
      </div>

      <div className="results-section">
        <h3>Job Description Requirements</h3>
        <p className="results-description">{result.job_analysis?.total_skills ?? 0} skills extracted.</p>

        <SkillGroup title="Required Skills by Category" skills={jobSkills} color="required"/>
      </div>

      <div className="database-status">
        <span>{result.database_status === "saved" ? "✓" : "!"}</span>
        Analysis database status: {result.database_status || "Unknown"}
      </div>

      <p className="results-note">
        The match score represents detected skill overlap. It is not a prediction of interview selection or hiring
         probability.</p>
    </section>
  );
}

export default MatchResults;
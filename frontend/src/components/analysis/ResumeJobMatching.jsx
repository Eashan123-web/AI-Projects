
import { useState } from "react";
import { uploadResume, matchResumeWithJob, getResumeRecommendations, improveResume,} from "../../services/api";
import MatchResults from "./MatchResults";
import RecommendationResults from "./RecommendationResults";
import ResumeImprovementResults from "./ResumeImprovementAnalysis";

function ResumeJobMatching() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadedFilename, setUploadedFilename] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [uploading, setUploading] = useState(false);
  const [matching, setMatching] = useState(false);
  const [generatingRecommendations, setGeneratingRecommendations] = useState(false);
  const [improvingResume, setImprovingResume] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [matchResult, setMatchResult] = useState(null);
  const [recommendationResult, setRecommendationResult] = useState(null);
  const [improvementResult, setImprovementResult] = useState(null);

  // Handle resume selection
  const handleFileChange = (event) => {
    const file = event.target.files?.[0];

    setError("");
    setSuccess("");
    setUploadedFilename("");
    setMatchResult(null);
    setRecommendationResult(null);
    setImprovementResult(null);

    if (!file) {
      setSelectedFile(null);
      return;
    }

    const extension = file.name.split(".").pop().toLowerCase();

    if (!["pdf", "docx"].includes(extension)) {
      setSelectedFile(null);
      setError("Only PDF and DOCX files are supported.");
      event.target.value = "";
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setSelectedFile(null);
      setError("Resume file size must not exceed 10 MB.");
      event.target.value = "";
      return;
    }

    setSelectedFile(file);
  };

  // Upload resume
  const handleUpload = async () => {
    if (!selectedFile) {
      setError("Please select your resume first.");
      return;
    }

    setUploading(true);
    setError("");
    setSuccess("");
    setUploadedFilename("");
    setMatchResult(null);
    setRecommendationResult(null);
    setImprovementResult(null);

    try {
      const response = await uploadResume(selectedFile);

      const filename =
        response.filename || response.stored_filename || response.saved_filename || response.file_name;

      if (!filename) {
        console.error("Upload response:", response);
        throw new Error("Upload response did not contain a stored filename.");
      }

      setUploadedFilename(filename);
      setSuccess("Resume uploaded successfully!");

      console.log("Uploaded filename:", filename);
    } catch (err) {
      console.error("Resume upload error:", err);
      setError(err.message || "Resume upload failed.");
    } finally {
      setUploading(false);
    }
  };

  // Match resume with job description
  const handleMatch = async () => {
    setError("");
    setSuccess("");
    setMatchResult(null);
    setRecommendationResult(null);
    setImprovementResult(null);

    if (!uploadedFilename) {
      setError("Please upload your resume first.");
      return;
    }

    if (!jobDescription.trim()) {
      setError("Please enter a job description.");
      return;
    }

    setMatching(true);

    try {
      const result = await matchResumeWithJob(uploadedFilename, jobDescription.trim());

      console.log("Matching API response:", result);

      if (!result || result.status !== "success") {
        throw new Error(result?.message || "Resume matching could not be completed.");
      }

      setMatchResult(result);
      setSuccess("Resume analysis completed successfully!");
    } catch (err) {
      console.error("Matching error:", err);
      setError(err.message || "Resume matching failed.");
    } finally {
      setMatching(false);
    }
  };

  // Generate resume recommendations
  const handleRecommendations = async () => {
    setError("");
    setSuccess("");
    setRecommendationResult(null);

    if (!uploadedFilename) {
      setError("Please upload your resume first.");
      return;
    }

    if (!jobDescription.trim()) {
      setError("Please enter a job description first.");
      return;
    }

    setGeneratingRecommendations(true);

    try {
      const result = await getResumeRecommendations(uploadedFilename, jobDescription.trim());

      console.log("Recommendations API response:", result);

      if (!result || result.status !== "success") {
        throw new Error(result?.message || "Resume recommendations could not be generated.");
      }

      setRecommendationResult(result);
      setSuccess("Resume recommendations generated successfully!");
    } catch (err) {
      console.error("Recommendation error:", err);
      setError(err.message || "Unable to generate resume recommendations.");
    } finally {
      setGeneratingRecommendations(false);
    }
  };

  // Generate AI resume improvements
  const handleImproveResume = async () => {
    setError("");
    setSuccess("");
    setImprovementResult(null);

    if (!uploadedFilename) {
      setError("Please upload your resume first.");
      return;
    }

    if (!jobDescription.trim()) {
      setError("Please enter a job description first.");
      return;
    }

    setImprovingResume(true);

    try {
      const result = await improveResume(uploadedFilename, jobDescription.trim());

      console.log("Resume improvement API response:", result);

      if (!result || result.status !== "success") {
        throw new Error(result?.message || "AI resume improvements could not be generated.");
      }

      setImprovementResult(result);
      setSuccess("AI resume improvements generated successfully!");
    } catch (err) {
      console.error("Resume improvement error:", err);
      setError(err.message || "Unable to generate resume improvements.");
    } finally {
      setImprovingResume(false);
    }
  };

  // Check whether any operation is running
  const isProcessing = uploading || matching || generatingRecommendations || improvingResume;

  return (
    <div className="resume-matching-page">

      {/* Page Heading */}
      <div className="upload-page-heading">
        <span className="welcome-label"> CAREER INTELLIGENCE </span>

        <h1>Resume and Job Matching</h1>

        <p> Upload your resume and paste a job description to discover how well your profile matches the job requirements.
        </p>
      </div>

      <div className="matching-card">

        {/* Resume Upload */}
        <div className="matching-form-section">
          <label>Upload Your Resume</label>

          <div className="matching-upload-area">
            <div className="matching-upload-icon">📄</div>

            <h3>Select your resume</h3>

            <p> Upload a PDF or DOCX file from your computer. </p>

            <label className="matching-browse-button"> Browse Files
              <input type="file" accept=".pdf,.docx" onChange={handleFileChange}/>
            </label>

            {selectedFile && (
              <div className="matching-selected-file">
                <span>📎</span>

                <div>
                  <strong>{selectedFile.name}</strong>

                  <small>
                    {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                  </small>
                </div>
              </div>
            )}

            <button type="button" className="primary-button matching-upload-button" onClick={handleUpload}
              disabled={!selectedFile || isProcessing}>
              {uploading ? "Uploading..." : "Upload Resume"}
            </button>

            {uploadedFilename && (
              <div className="upload-success"> Resume uploaded and ready for analysis.</div>
            )}
          </div>
        </div>

        {/* Job Description */}
        <div className="matching-form-section">
          <label htmlFor="matching-job-description"> Job Description </label>

          <textarea id="matching-job-description" className="job-description-input" rows={12}
            placeholder="Paste the complete job description here..." value={jobDescription}
            onChange={(event) => {
              setJobDescription(event.target.value);
              setMatchResult(null);
              setRecommendationResult(null);
              setImprovementResult(null);
              setError("");
              setSuccess("");
            }}/>

          <div className="description-footer">
            <span>{jobDescription.length} characters</span>

            <span> Include job skills and responsibilities.</span>
          </div>
        </div>

        {/* Analyze Resume Button */}
        <button type="button" className="primary-button analyze-job-button" onClick={handleMatch} disabled={isProcessing}>
          {matching
            ? "Analyzing Resume..."
            : "Analyze Resume Match"}
        </button>

        {/* Recommendations Button */}
        <button type="button" className="recommendation-button" onClick={handleRecommendations}
          disabled={
            !uploadedFilename || !jobDescription.trim() || isProcessing
          }>
          {generatingRecommendations ? "Generating Recommendations..." : "Generate Resume Recommendations"}
        </button>

        {/* AI Resume Improvement Button */}
        <button type="button" className="recommendation-button" onClick={handleImproveResume}
          disabled={
            !uploadedFilename || !jobDescription.trim() || isProcessing
          }>
          {improvingResume ? "Generating AI Improvements..." : "Improve My Resume with AI"}
        </button>

        {/* Error Message */}
        {error && (
          <div className="upload-error">{error}</div>
        )}

        {/* Success Message */}
        {success && (
          <div className="upload-success">{success}</div>
        )}

        {/* Matching Results */}
        {matchResult && (<MatchResults result={matchResult} />)}

        {/* Recommendation Results */}
        {recommendationResult && (<RecommendationResults result={recommendationResult} />)}

        {/* AI Resume Improvement Results */}
        {improvementResult && (<ResumeImprovementResults result={improvementResult} />)}

      </div>
    </div>
  );
}

export default ResumeJobMatching;
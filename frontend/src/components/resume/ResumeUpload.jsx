
import { useState } from "react";
import { uploadResume } from "../../services/api";

function ResumeUpload() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [uploadedResume, setUploadedResume] = useState(null);

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];

    setMessage("");
    setError("");
    setUploadedResume(null);

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

    const maxSize = 10 * 1024 * 1024;

    if (file.size > maxSize) {
      setSelectedFile(null);
      setError("File size must not exceed 10 MB.");
      event.target.value = "";
      return;
    }

    setSelectedFile(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError("Please select a resume first.");
      return;
    }

    setLoading(true);
    setError("");
    setMessage("");

    try {
      const response = await uploadResume(selectedFile);

      setUploadedResume(response);
      setMessage("Resume uploaded successfully!");
      setSelectedFile(null);
    } catch (err) {
      setError(err.message || "Resume upload failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="resume-upload-page">
      <div className="upload-page-heading">
        <span className="welcome-label">RESUME MANAGEMENT</span>
        <h1>Upload Your Resume</h1>
        <p> Upload your resume to extract skills, analyze experience, and match it with job opportunities.</p>
      </div>

      <div className="upload-card">
        <div className="upload-icon">📄</div>

        <h2>Choose your resume</h2>

        <p className="upload-description">Select a PDF or DOCX file from your computer.</p>

        <label className="file-select-button">
          Browse Files
          <input type="file"
            accept=".pdf,.docx"
            onChange={handleFileChange}/>
        </label>

        {selectedFile && (
          <div className="selected-file">
            <span>📎</span>
            <div>
              <strong>{selectedFile.name}</strong>
              <small>{(selectedFile.size / (1024 * 1024)).toFixed(2)} MB</small>
            </div>
          </div>
        )}

        <button className="primary-button upload-submit-button"
          onClick={handleUpload}
          disabled={!selectedFile || loading}>
          {loading ? "Uploading..." : "Upload Resume"}
        </button>

        {message && (
          <div className="upload-success">{message}</div>
        )}

        {error && (
          <div className="upload-error">{error}</div>
        )}

        {uploadedResume && (
          <div className="uploaded-result">
            <h3>Upload Details</h3>
            <p>Filename:{" "}
              <strong>{uploadedResume.filename || uploadedResume.original_filename || "Uploaded successfully"}</strong>
            </p>
            <p>
              Database status:{" "}
              {uploadedResume.database_status || "See backend response"}
            </p>
          </div>
        )}

        <div className="upload-guidelines">
          <span>Supported formats: PDF, DOCX</span>
          <span>Maximum file size: 10 MB</span>
          <span>Your resume is sent to your local backend for processing.</span>
        </div>
      </div>
    </div>
  );
}

export default ResumeUpload;

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export async function uploadResume(file) {
  const formData = new FormData();

  formData.append("file", file);

  const response = await fetch(
    `${API_BASE_URL}/api/resumes/upload`,
    {
      method: "POST", body: formData,
    }
  );

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.detail || data.message || "Unable to upload resume.");
  }

  return data;
}

export async function analyzeJobDescription(jobDescription) {
  const response = await fetch(`${API_BASE_URL}/api/jobs/analyze`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        job_description: jobDescription,
      }),
    }
  );

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(data?.detail || "Unable to analyze job description.");
  }

  return data;
}

export async function getResumeHistory() {
  const response = await fetch(`${API_BASE_URL}/api/history/resumes`);

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(data?.detail || "Unable to load uploaded resumes.");
  }

  return data;
}

export async function matchResumeWithJob(filename, jobDescription) {
  const response = await fetch(`${API_BASE_URL}/api/analysis/match`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        filename: filename, job_description: jobDescription,
      }),
    }
  );

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(data?.detail || "Resume matching failed.");
  }

  return data;
}


export async function getResumeRecommendations(filename, jobDescription) {
  const response = await fetch(`${API_BASE_URL}/api/analysis/recommendations`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        filename, job_description: jobDescription,
      }),
    }
  );

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.detail || data.message || "Failed to generate recommendations.");
  }

  return data;
}

export async function getAnalysisHistory() {
  const response = await fetch(`${API_BASE_URL}/api/history/analyses`);

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.detail || data.message || "Failed to load analysis history.");
  }

  return data;
}

export async function getAnalysisDetails(analysisId) {
  const response = await fetch(`${API_BASE_URL}/api/history/analyses/${analysisId}`);

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.detail || data.message || "Failed to load analysis details.");
  }

  return data;
}


export async function getDashboardStats() {
  const response = await fetch(`${API_BASE_URL}/api/dashboard/stats`);

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.detail || data.message || "Failed to load dashboard statistics.");
  }

  return data;
}


export async function improveResume(filename, jobDescription) {
  const response = await fetch(`${API_BASE_URL}/api/analysis/improve`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      filename,
      job_description: jobDescription,
    }),
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      data.detail || data.message || "Failed to generate resume improvements."
    );
  }

  return data;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

async function request(path: string, options: RequestInit = {}) {
  const token = getToken();

  const headers: Record<string, string> = {
    ...(options.body instanceof FormData
      ? {}
      : { "Content-Type": "application/json" }),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...((options.headers as Record<string, string>) || {}),
  };

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorBody = await response
      .json()
      .catch(() => ({ detail: "Something went wrong" }));
    throw new Error(errorBody.detail || "Request failed");
  }

  return response.json();
}

export const api = {
  signup: (name: string, email: string, password: string) =>
    request("/auth/signup", {
      method: "POST",
      body: JSON.stringify({ name, email, password }),
    }),

  login: (email: string, password: string) =>
    request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  getMe: () => request("/auth/me"),

  uploadResume: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return request("/resumes/upload", { method: "POST", body: formData });
  },

  listResumes: () => request("/resumes/"),

  getJobMatches: (resumeId: number) => request(`/jobs/match/${resumeId}`),

  startInterview: (jobId?: number) =>
    request("/interviews/start", { method: "POST", body: JSON.stringify({ job_id: jobId ?? null }) }),

  submitAnswer: (sessionId: number, answer: string) =>
    request(`/interviews/${sessionId}/answer`, { method: "POST", body: JSON.stringify({ answer }) }),

  generateFeedback: (sessionId: number) =>
    request(`/feedback/${sessionId}/generate`, { method: "POST" }),

  logFlag: (sessionId: number, flagType: string, message: string) =>
    request(`/interviews/${sessionId}/flag`, {
      method: "POST",
      body: JSON.stringify({ flag_type: flagType, message }),
    }),
};

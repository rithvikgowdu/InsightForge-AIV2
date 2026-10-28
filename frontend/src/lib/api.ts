import {
  AnalysisDetail,
  AnalysisRun,
  AnalysisStatusResponse,
  AuthToken,
  User,
} from "./types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

class ApiError extends Error {
  statusCode: number;
  code?: string;
  details?: Record<string, unknown>;

  constructor(
    message: string,
    statusCode: number,
    code?: string,
    details?: Record<string, unknown>
  ) {
    super(message);
    this.name = "ApiError";
    this.statusCode = statusCode;
    this.code = code;
    this.details = details;
  }
}

function getStoredToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("insightforge_token");
}

export function setStoredToken(token: string | null): void {
  if (typeof window === "undefined") return;
  if (token) {
    localStorage.setItem("insightforge_token", token);
  } else {
    localStorage.removeItem("insightforge_token");
  }
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getStoredToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const url = `${API_BASE_URL}${endpoint}`;

  let response: Response;
  try {
    response = await fetch(url, {
      ...options,
      headers,
    });
  } catch {
    throw new ApiError(
      "Unable to connect to the InsightForge API server. Please check your backend connection.",
      0,
      "NETWORK_ERROR"
    );
  }

  if (response.status === 401) {
    setStoredToken(null);
    if (typeof window !== "undefined" && !window.location.pathname.startsWith("/login")) {
      window.dispatchEvent(new CustomEvent("insightforge_unauthorized"));
    }
  }

  if (!response.ok) {
    let errorData: { detail?: string; code?: string; details?: Record<string, unknown> } = {};
    try {
      errorData = await response.json();
    } catch {
      errorData = { detail: response.statusText };
    }

    throw new ApiError(
      errorData.detail || `Request failed with status ${response.status}`,
      response.status,
      errorData.code,
      errorData.details
    );
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

export const api = {
  auth: {
    register: (data: {
      email: string;
      username: string;
      password: string;
      full_name?: string;
    }) => request<User>("/auth/register", { method: "POST", body: JSON.stringify(data) }),

    login: (data: { username_or_email: string; password: string }) =>
      request<AuthToken>("/auth/login", { method: "POST", body: JSON.stringify(data) }),

    me: () => request<User>("/auth/me"),
  },

  analysis: {
    create: (data: {
      repo_url?: string;
      repo_owner?: string;
      repo_name?: string;
      issue_limit?: number;
      include_closed?: boolean;
    }) => request<AnalysisRun>("/analysis", { method: "POST", body: JSON.stringify(data) }),

    list: (skip = 0, limit = 50) =>
      request<AnalysisRun[]>(`/analysis/history?skip=${skip}&limit=${limit}`),

    get: (id: string) => request<AnalysisDetail>(`/analysis/${id}`),

    getStatus: (id: string) =>
      request<AnalysisStatusResponse>(`/analysis/${id}/status`),

    delete: (id: string) =>
      request<void>(`/analysis/${id}`, { method: "DELETE" }),
  },

  health: {
    check: () => request<{ status: string; version: string }>("/health"),
    ready: () =>
      request<{ status: string; database: boolean; ai_pipeline: boolean }>("/health/ready"),
  },
};

export { ApiError };

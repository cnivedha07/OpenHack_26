import { DashboardSummary } from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("trustfed_jwt_token");
}

export function getAuthUser(): { username: string; role: string; hospital_id: string | null } | null {
  if (typeof window === "undefined") return null;
  const userStr = localStorage.getItem("trustfed_user");
  if (!userStr) return null;
  try {
    return JSON.parse(userStr);
  } catch {
    return null;
  }
}

export function logout() {
  if (typeof window !== "undefined") {
    localStorage.removeItem("trustfed_jwt_token");
    localStorage.removeItem("trustfed_user");
    window.location.href = "/login";
  }
}

export async function ensureDefaultAuthToken(): Promise<string | null> {
  let token = getAuthToken();
  if (!token && typeof window !== "undefined") {
    try {
      const loginRes = await fetch(`${API_BASE_URL}/auth/admin/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: "admin", password: "admin123" }),
      });
      if (loginRes.ok) {
        const data = await loginRes.json();
        if (data.access_token) {
          localStorage.setItem("trustfed_jwt_token", data.access_token);
          localStorage.setItem("trustfed_user", JSON.stringify({
            username: data.username,
            role: data.role,
            hospital_id: data.hospital_id,
          }));
          return data.access_token;
        }
      }
    } catch {
      // Auto login fallback failed
    }
  }
  return token;
}

async function apiFetch<T = any>(endpoint: string, options?: RequestInit, isRetry: boolean = false): Promise<T> {
  const headers: Record<string, string> = {};
  if (options?.body && !(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  // Ensure an auth token is present for non-auth endpoints
  let token = getAuthToken();
  if (!token && !endpoint.startsWith("/auth/")) {
    token = await ensureDefaultAuthToken();
  }

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const doFetch = async (baseUrl: string) => {
    const res = await fetch(`${baseUrl}${endpoint}`, {
      ...options,
      headers: {
        ...headers,
        ...(options?.headers || {}),
      },
    });

    if (!res.ok) {
      // Handle 401 Unauthorized by auto-renewing default token once
      if (res.status === 401 && !isRetry && !endpoint.startsWith("/auth/")) {
        if (typeof window !== "undefined") {
          localStorage.removeItem("trustfed_jwt_token");
        }
        const newToken = await ensureDefaultAuthToken();
        if (newToken) {
          return await apiFetch<T>(endpoint, options, true);
        }
      }

      let errorMessage = `HTTP ${res.status}: ${res.statusText}`;
      try {
        const errorData = await res.json();
        if (errorData.detail) {
          errorMessage = typeof errorData.detail === "string" ? errorData.detail : JSON.stringify(errorData.detail);
        } else if (errorData.message) {
          errorMessage = errorData.message;
        }
      } catch {
        // Response was not JSON
      }
      throw new Error(errorMessage);
    }

    return await res.json();
  };

  try {
    return await doFetch(API_BASE_URL);
  } catch (error: any) {
    if (error instanceof TypeError && (error.message === "Failed to fetch" || error.message.includes("fetch"))) {
      // Try fallback between localhost and 127.0.0.1 (IPv4 vs IPv6 resolution mismatch fix)
      const altUrl = API_BASE_URL.includes("localhost")
        ? API_BASE_URL.replace("localhost", "127.0.0.1")
        : API_BASE_URL.replace("127.0.0.1", "localhost");
      try {
        return await doFetch(altUrl);
      } catch {
        // Fallback also failed
      }
      throw new Error(`Unable to connect to backend server at ${API_BASE_URL}. Please ensure the backend server is running.`);
    }
    throw error;
  }
}

export async function fetchDashboardMetrics(): Promise<DashboardSummary> {
  return apiFetch<DashboardSummary>("/metrics");
}

export async function startFederatedRound() {
  return apiFetch("/train/start", { method: "POST" });
}

export async function stopFederatedRound() {
  return apiFetch("/train/stop", { method: "POST" });
}

export async function pauseFederatedRound() {
  return apiFetch("/train/pause", { method: "POST" });
}

export async function resumeFederatedRound() {
  return apiFetch("/train/resume", { method: "POST" });
}

export async function resetFederatedTraining() {
  return apiFetch("/train/reset", { method: "POST" });
}

export async function toggleDifferentialPrivacy(enabled: boolean) {
  return apiFetch("/train/dp/toggle", {
    method: "POST",
    body: JSON.stringify({ enabled }),
  });
}

export async function fetchFitReport() {
  return apiFetch("/train/fit-report");
}

export async function fetchSystemLogs() {
  return apiFetch("/logs");
}

export async function fetchValidationReport() {
  return apiFetch("/validation");
}

export async function toggleAttack(hospital_id: string, attack_type: string, intensity: number = 1.0) {
  return apiFetch("/attack/toggle", {
    method: "POST",
    body: JSON.stringify({ hospital_id, attack_type, intensity }),
  });
}

export async function anonymizeSampleText(text: string) {
  return apiFetch("/privacy/anonymize", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}

export async function loginAdmin(username: string, password: string) {
  const data = await apiFetch("/auth/admin/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
  if (typeof window !== "undefined" && data.access_token) {
    localStorage.setItem("trustfed_jwt_token", data.access_token);
    localStorage.setItem("trustfed_user", JSON.stringify({
      username: data.username,
      role: data.role,
      hospital_id: data.hospital_id,
    }));
  }
  return data;
}

export async function loginHospital(username: string, password: string) {
  const data = await apiFetch("/auth/hospital/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
  if (typeof window !== "undefined" && data.access_token) {
    localStorage.setItem("trustfed_jwt_token", data.access_token);
    localStorage.setItem("trustfed_user", JSON.stringify({
      username: data.username,
      role: data.role,
      hospital_id: data.hospital_id,
    }));
  }

  return data;
}

export async function uploadHospitalDataset(hospitalId: string, file: File) {

  const formData = new FormData();
  formData.append("file", file);
  formData.append("hospital_id", hospitalId);

  return apiFetch("/upload", {
    method: "POST",
    body: formData,
  });
}

export async function fetchHospitalDatasets(hospitalId: string) {
  return apiFetch(`/datasets/${hospitalId}`);
}

export async function fetchTrainingRuns(hospitalId: string) {
  return apiFetch(`/training/runs/${hospitalId}`);
}


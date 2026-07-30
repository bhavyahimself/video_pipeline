/**
 * ClipEngine — API Client
 * Axios wrapper with JWT interceptor for backend communication.
 */

import axios, { AxiosInstance, AxiosError } from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE,
      headers: { "Content-Type": "application/json" },
    });

    // Request interceptor: attach JWT
    this.client.interceptors.request.use((config) => {
      if (typeof window !== "undefined") {
        const token = localStorage.getItem("access_token");
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
      }
      return config;
    });

    // Response interceptor: handle 401
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Try refresh token
          const refreshToken = localStorage.getItem("refresh_token");
          if (refreshToken) {
            try {
              const res = await axios.post(`${API_BASE}/auth/refresh`, null, {
                headers: { Authorization: `Bearer ${refreshToken}` },
              });
              localStorage.setItem("access_token", res.data.access_token);
              localStorage.setItem("refresh_token", res.data.refresh_token);
              // Retry original request
              if (error.config) {
                error.config.headers.Authorization = `Bearer ${res.data.access_token}`;
                return this.client.request(error.config);
              }
            } catch {
              localStorage.removeItem("access_token");
              localStorage.removeItem("refresh_token");
              window.location.href = "/login";
            }
          }
        }
        return Promise.reject(error);
      }
    );
  }

  // ── Auth ──────────────────────────────────────────────────────
  async register(email: string, password: string, name: string) {
    const res = await this.client.post("/auth/register", { email, password, name });
    this.setTokens(res.data);
    return res.data;
  }

  async login(email: string, password: string) {
    const res = await this.client.post("/auth/login", { email, password });
    this.setTokens(res.data);
    return res.data;
  }

  async getMe() {
    const res = await this.client.get("/auth/me");
    return res.data;
  }

  logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  }

  private setTokens(data: { access_token: string; refresh_token: string }) {
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
  }

  // ── Videos ────────────────────────────────────────────────────
  async createVideo(data: {
    topic: string;
    channel_type: string;
    project_id?: string;
    skip_research?: boolean;
    skip_voice?: boolean;
    custom_script?: string;
  }) {
    const res = await this.client.post("/videos", data);
    return res.data;
  }

  async listVideos(params?: { page?: number; per_page?: number; channel_type?: string; status_filter?: string }) {
    const res = await this.client.get("/videos", { params });
    return res.data;
  }

  async getVideo(id: string) {
    const res = await this.client.get(`/videos/${id}`);
    return res.data;
  }

  async deleteVideo(id: string) {
    await this.client.delete(`/videos/${id}`);
  }

  async batchCreateVideos(topics: string[], channel_type: string) {
    const res = await this.client.post("/videos/batch", { topics, channel_type });
    return res.data;
  }

  // ── Scripts ───────────────────────────────────────────────────
  async getScript(id: string) {
    const res = await this.client.get(`/scripts/${id}`);
    return res.data;
  }

  async updateScript(id: string, content: string) {
    const res = await this.client.put(`/scripts/${id}`, { content });
    return res.data;
  }

  async getScriptVersions(id: string) {
    const res = await this.client.get(`/scripts/${id}/versions`);
    return res.data;
  }

  async regenerateScript(id: string) {
    const res = await this.client.post(`/scripts/${id}/regenerate`);
    return res.data;
  }

  // ── Jobs ──────────────────────────────────────────────────────
  async getJob(id: string) {
    const res = await this.client.get(`/jobs/${id}`);
    return res.data;
  }

  async cancelJob(id: string) {
    const res = await this.client.post(`/jobs/${id}/cancel`);
    return res.data;
  }

  async retryJob(id: string) {
    const res = await this.client.post(`/jobs/${id}/retry`);
    return res.data;
  }

  // ── Channels ──────────────────────────────────────────────────
  async listChannels() {
    const res = await this.client.get("/channels");
    return res.data;
  }

  async createCustomChannel(data: any) {
    const res = await this.client.post("/channels/custom", data);
    return res.data;
  }

  // ── Billing ───────────────────────────────────────────────────
  async getPlans() {
    const res = await this.client.get("/billing/plans");
    return res.data;
  }

  async createCheckout(plan: string, successUrl: string, cancelUrl: string) {
    const res = await this.client.post("/billing/checkout", {
      plan,
      success_url: successUrl,
      cancel_url: cancelUrl,
    });
    return res.data;
  }

  async getUsage() {
    const res = await this.client.get("/billing/usage");
    return res.data;
  }

  // ── Analytics ─────────────────────────────────────────────────
  async getAnalyticsOverview() {
    const res = await this.client.get("/analytics/overview");
    return res.data;
  }
}

export const api = new ApiClient();
export default api;


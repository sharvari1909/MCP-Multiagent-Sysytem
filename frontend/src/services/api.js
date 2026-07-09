import axios from "axios";

const localBackendUrl = "http://localhost:8000";
const defaultBackendUrl = localBackendUrl;
const configuredApiUrl = import.meta.env.VITE_API_BASE_URL || defaultBackendUrl;
const apiBaseUrl = configuredApiUrl.endsWith("/api")
  ? configuredApiUrl
  : `${configuredApiUrl.replace(/\/$/, "")}/api`;

const api = axios.create({
  baseURL: apiBaseUrl,
});

export default api;

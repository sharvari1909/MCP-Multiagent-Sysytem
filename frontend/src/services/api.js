import axios from "axios";

const renderBackendUrl = "https://mcp-multiagent-sysytem.onrender.com";
const railwayBackendUrl = "https://mcp-multiagent-sysytem-production.up.railway.app";
const localBackendUrl = "http://localhost:8000";
const defaultBackendUrl = window.location.hostname.endsWith(".onrender.com")
  ? renderBackendUrl
  : window.location.hostname.endsWith(".up.railway.app")
    ? railwayBackendUrl
    : localBackendUrl;
const configuredApiUrl = import.meta.env.VITE_API_BASE_URL || defaultBackendUrl;
const apiBaseUrl = configuredApiUrl.endsWith("/api")
  ? configuredApiUrl
  : `${configuredApiUrl.replace(/\/$/, "")}/api`;

const api = axios.create({
  baseURL: apiBaseUrl,
});

export default api;

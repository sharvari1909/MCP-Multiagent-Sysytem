import axios from "axios";

const renderBackendUrl = "https://mcp-multiagent-sysytem.onrender.com";
const localBackendUrl = "http://localhost:8000";
const defaultBackendUrl = window.location.hostname.endsWith(".onrender.com")
  ? renderBackendUrl
  : localBackendUrl;

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || `${defaultBackendUrl}/api`,
});

export default api;

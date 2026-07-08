class WebSocketService {
  constructor() {
    this.socket = null;
  }

  connect(onMessage) {
    const renderWsUrl = "wss://mcp-multiagent-sysytem.onrender.com/ws";
    const railwayWsUrl = "wss://mcp-multiagent-sysytem-production.up.railway.app/ws";
    const localWsUrl = "ws://localhost:8000/ws";
    const defaultWsUrl = window.location.hostname.endsWith(".onrender.com")
      ? renderWsUrl
      : window.location.hostname.endsWith(".up.railway.app")
        ? railwayWsUrl
        : localWsUrl;
    const wsUrl = import.meta.env.VITE_WS_URL || defaultWsUrl;
    this.socket = new WebSocket(wsUrl);

    this.socket.onopen = () => {
      console.log("WebSocket connected");
    };

    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };

    this.socket.onerror = (error) => {
      console.error("WebSocket error", error);
    };
  }
}

export default new WebSocketService();

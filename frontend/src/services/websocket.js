class WebSocketService {
  constructor() {
    this.socket = null;
  }

  connect(onMessage) {
    const localWsUrl = "ws://localhost:8000/ws";
    const defaultWsUrl = localWsUrl;
    const wsUrl = import.meta.env.VITE_WS_URL || defaultWsUrl;
    try {
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
    } catch (error) {
      console.error("Failed to establish WebSocket connection:", error);
    }
  }
}

export default new WebSocketService();

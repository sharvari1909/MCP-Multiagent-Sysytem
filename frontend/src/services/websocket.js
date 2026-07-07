class WebSocketService {
  constructor() {
    this.socket = null;
  }

  connect(onMessage) {
    const wsUrl = import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws";
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

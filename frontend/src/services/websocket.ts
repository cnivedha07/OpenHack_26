const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://127.0.0.1:8000/ws";

export function createWebSocketConnection(onMessage: (data: any) => void) {
  let ws: WebSocket;
  try {
    ws = new WebSocket(WS_URL);
  } catch {
    ws = new WebSocket("ws://localhost:8000/ws");
  }

  ws.onopen = () => {
    console.log("WebSocket connected to TrustFed 2.0 Backend");
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (e) {
      console.error("Error parsing WS message", e);
    }
  };

  ws.onclose = () => {
    console.log("WebSocket connection closed");
  };

  return ws;
}


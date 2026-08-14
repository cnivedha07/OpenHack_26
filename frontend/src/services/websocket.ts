/**
 * TrustFed 2.0 Resilient WebSocket Client with Exponential Backoff Reconnect.
 * Recovers seamlessly from network drops or backend reboots.
 */

const getWsUrl = (): string => {
  if (process.env.NEXT_PUBLIC_WS_URL) {
    return process.env.NEXT_PUBLIC_WS_URL;
  }
  if (typeof window !== "undefined") {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    return `${protocol}//${window.location.hostname}:8000/ws`;
  }
  return "ws://127.0.0.1:8000/ws";
};

export function createWebSocketConnection(onMessage: (data: any) => void) {
  let ws: WebSocket | null = null;
  let isClosedIntentionally = false;
  let reconnectAttempts = 0;
  let reconnectTimer: NodeJS.Timeout | null = null;

  const connect = () => {
    const wsUrl = getWsUrl();
    try {
      ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log(`WebSocket connected to TrustFed 2.0 Backend (${wsUrl})`);
        reconnectAttempts = 0; // Reset backoff counter on successful connection
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessage(data);
        } catch (e) {
          console.error("Error parsing WS message", e);
        }
      };

      ws.onerror = (err) => {
        console.warn("WebSocket error occurred:", err);
      };

      ws.onclose = () => {
        if (!isClosedIntentionally) {
          reconnectAttempts += 1;
          // Exponential backoff: 1s, 2s, 4s, 8s, 16s, max 30s
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts - 1), 30000);
          console.log(`WebSocket closed. Reconnecting attempt #${reconnectAttempts} in ${delay / 1000}s...`);
          
          if (reconnectTimer) clearTimeout(reconnectTimer);
          reconnectTimer = setTimeout(connect, delay);
        } else {
          console.log("WebSocket connection closed intentionally.");
        }
      };
    } catch (err) {
      console.error("Failed to establish WebSocket connection:", err);
      reconnectAttempts += 1;
      const delay = Math.min(1000 * Math.pow(2, reconnectAttempts - 1), 30000);
      reconnectTimer = setTimeout(connect, delay);
    }
  };

  connect();

  return {
    close: () => {
      isClosedIntentionally = true;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      if (ws) ws.close();
    },
    getSocket: () => ws
  };
}

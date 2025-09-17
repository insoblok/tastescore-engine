type MessageHandler = (data: any) => void;

class WebSocketConnection {
  socket: WebSocket;
  private listeners: MessageHandler[] = [];

  constructor(public url: string) {
    this.socket = new WebSocket(url);

    this.socket.onopen = () => {
      console.log(`✅ Connected to ${url}`);
    };

    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.listeners.forEach((cb) => cb(data));
    };

    this.socket.onclose = () => {
      console.log(`❌ Disconnected from ${url}`);
    };

    this.socket.onerror = (err) => {
      console.error(`⚠️ Error in ${url}:`, err);
    };
  }

  send(message: any) {
    if (this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
    } else {
      console.warn(`WebSocket to ${this.url} is not open`);
    }
  }

  onMessage(callback: MessageHandler) {
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter((cb) => cb !== callback);
    };
  }
}

class WebSocketManager {
  public connections: Map<string, WebSocketConnection> = new Map();

  connectAll(urls: string[]) {
    urls.forEach((url) => {
      if (!this.connections.has(url)) {
        this.connections.set(url, new WebSocketConnection(url));
      }
    });
  }

  get(url: string) {
    return this.connections.get(url) || null;
  }

}

export const websocketManager = new WebSocketManager();
export default WebSocketConnection;

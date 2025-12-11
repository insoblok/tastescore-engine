export interface TransactionMessage {
  x: {
    hash: string;
    out: { value: number }[];
  };
}

export function handleWebSocket(
  address: string,
  onMessage?: (data: TransactionMessage) => void,
  onOpen?: () => void,
  onClose?: () => void,
  onError?: (err: Event) => void
): WebSocket {
  if (!address) {
    throw new Error("Wallet address is required");
  }
  const socket = new WebSocket(`wss://ws.blockchain.info/inv`);

  socket.onopen = () => {
    console.log(`✅ Connected to WS for ${address}`);
    onOpen?.();
  };

  socket.onmessage = (event: MessageEvent) => {
    try {
      const data: TransactionMessage = JSON.parse(event.data);
      onMessage?.(data);
    } catch (err) {
      console.error("Error parsing WS message:", err);
    }
  };

  socket.onclose = () => {
    console.log(`🔌 WS closed for ${address}`);
    onClose?.();
  };

  socket.onerror = (err: Event) => {
    console.error("❌ WS error:", err);
    onError?.(err);
  };

  return socket; // allow manual control (close, send, etc.)
}

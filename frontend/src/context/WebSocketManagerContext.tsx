import React, { createContext, useContext, useEffect } from "react";
import { websocketManager } from "../services/websocketManager";
import { BNB_SOCKET_URL, BTC_SOCKET_URL, ETH_SOCKET_URL, SOL_SOCKET_URL } from "../Constants";

const WebSocketManagerContext = createContext(websocketManager);

export const WebSocketManagerProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  useEffect(() => {
    // Connect to all servers at app start
    

    // websocketManager.connectAll([
    //   BTC_SOCKET_URL,
    //   ETH_SOCKET_URL,
    //   BNB_SOCKET_URL,
    //   SOL_SOCKET_URL,
    // ]);
  }, []);

  return (
    <WebSocketManagerContext.Provider value={websocketManager}>
      {children}
    </WebSocketManagerContext.Provider>
  );
};

export const useWebSocketManager = () => useContext(WebSocketManagerContext);

export const ETHER_IN_WEI = 100000000;
export const BTC_SOCKET_URL = import.meta.env.VITE_BTC_WS_URL;
export const ETH_SOCKET_URL = `${import.meta.env.VITE_ETHER_WS_URL}/${import.meta.env.VITE_META_MASK_API_KEY}` ;
export const BNB_SOCKET_URL = `${import.meta.env.VITE_BNB_WS_URL}/${import.meta.env.VITE_META_MASK_API_KEY}`;
export const SOL_SOCKET_URL = import.meta.env.VITE_SOL_WS_URL;
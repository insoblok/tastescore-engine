
export interface IETHTransaction {
  hash: string;
  src: string;
  dst: string;
  blockNumber: number | string;
  time: number;
  amount: string | number;
  fee: string | number;
}

export interface INewPendingTransaction {
  jsonrpc: string;
  method: string;
  params?: {
    subscription: string;
    result: string;
  }
  result?: string;
}

export interface IETHTransactionRPC {
  id: number;
  jsonrpc: string;
  result: {
    blockHash: string;
    blockNumber: string;
    from: string;
    to: string;
    gas: string;
    gasPrice: string,
    hash: string;
    value: string;
  }
}
export interface ILogSubscriptionResponse {
  jsonrpc: string;
  method: string;
  params: {
    subscription: string;
    result: {
      address: string;
      blockHash: string;
      blockNumber: string;
      transactionHash: string;
      transactionIndex: string;
    }
  }
}

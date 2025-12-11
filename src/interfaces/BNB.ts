export interface IBNBTransaction {
  hash: string;
  src: string;
  dst: string;
  blockNumber: string;
  blockHash: string;
  time: string;
  value: string;
  gas: string;
  gasPrice: string;
  gasUsed: string;

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
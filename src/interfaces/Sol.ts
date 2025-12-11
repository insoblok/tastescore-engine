export interface ISOLTransaction {
  description: string;
  type: string;
  source: string;
  fee: number,
  feePayer: string;
  signature: string;
  slot: number;
  timestamp: number;
  nativeTransfers: [ISOLTransfer];
}

export interface ISOLTransfer {
  fromUserAccount: string;
  toUserAccount: string;
  amount: number;
}

export interface ISOLTransactionDTO {
  description: string;
  type: string;
  source: string;
  fee: number,
  signature: string;
  slot: number;
  timestamp: number;
  from: string;
  to: string;
  amount: number;
}

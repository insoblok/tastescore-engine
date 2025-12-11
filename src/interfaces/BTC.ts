export interface ITransactionInput {
  sequence: number;
  prev_out?: {
    addr: string;
    value: number

  }
  script: string;
  // Add other input properties as needed
}

export interface ITransactionOutput {
  addr: string
  value: number
  // Add other output properties as needed
}

export interface IBTCTransaction {
  txid: string;
  hash: string
  time: number
  inputs: ITransactionInput[]
  outputs: ITransactionOutput[]
  result: number | string
  fee: number
  index: number
  openStates: any[]
  toggleItem: (index: number) => void
}

export interface IBTCTransactionRaw {
  op: string; // Operation type ("utx" for unspent transaction)
  x: {
    lock_time: number;
    ver: number; // Transaction version
    size: number; // Transaction size in bytes
    inputs: ITransactionInput[];
    time: number; // Unix timestamp
    tx_index: number;
    vin_sz: number; // Number of inputs
    hash: string; // Transaction hash
    vout_sz: number; // Number of outputs
    relayed_by: string; // IP address that relayed the transaction
    out: ITransactionOutput[];
  };
}

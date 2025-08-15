export interface TransactionInput {
  sequence: number;
  prev_out?: {
    addr: string;
    value: number

  }
  script: string;
  // Add other input properties as needed
}

export interface TransactionOutput {
  addr: string
  value: number
  // Add other output properties as needed
}

export interface BTCTransaction {
  txid: string;
  hash: string
  time: number
  inputs: TransactionInput[]
  outputs: TransactionOutput[]
  result: number | string
  fee: number
  index: number
  openStates: boolean[]
  toggleItem: (index: number) => void
}

export interface BTCTransactionRaw {
  op: string; // Operation type ("utx" for unspent transaction)
  x: {
    lock_time: number;
    ver: number; // Transaction version
    size: number; // Transaction size in bytes
    inputs: TransactionInput[];
    time: number; // Unix timestamp
    tx_index: number;
    vin_sz: number; // Number of inputs
    hash: string; // Transaction hash
    vout_sz: number; // Number of outputs
    relayed_by: string; // IP address that relayed the transaction
    out: TransactionOutput[];
  };
}

// export interface BitcoinTransactionRaw {
//   op: string; // Operation type ("utx" for unspent transaction)
//   x: {
//     lock_time: number;
//     ver: number; // Transaction version
//     size: number; // Transaction size in bytes
//     inputs: {
//       sequence: number;
//       prev_out: {
//         spent: boolean;
//         tx_index: number;
//         type: number;
//         addr: string; // Bitcoin address
//         value: number; // Satoshi value
//         n: number; // Output index
//         script: string; // Hex-encoded script
//       };
//       script: string; // Input script
//     }[];
//     time: number; // Unix timestamp
//     tx_index: number;
//     vin_sz: number; // Number of inputs
//     hash: string; // Transaction hash
//     vout_sz: number; // Number of outputs
//     relayed_by: string; // IP address that relayed the transaction
//     out: {
//       spent: boolean;
//       tx_index: number;
//       type: number;
//       addr: string; // Recipient address
//       value: number; // Satoshi value
//       n: number; // Output index
//       script: string; // Output script
//     }[];
//   };
// }

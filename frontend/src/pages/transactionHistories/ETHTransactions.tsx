import React from "react";
import Navbar from "../../layout/Navbar";
import { useLocation } from "react-router-dom";
import ETHTransactionView from "../../components/transactionHistories/eth/ETHTransactionView";
import ETHSummary from "../../components/transactionHistories/eth/ETHSummary";
import { useWebSocketManager } from "../../context/WebSocketManagerContext";
interface EthereumTransaction {
  hash: string;
  from: string;
  to: string;
  value: string;
  timeStamp: string;
  gasUsed: string;
  // Add other transaction properties as needed
}

interface WalletData {
  address: string;
  balance?: string;
  // Add other wallet properties as needed
}

interface SummaryData {
  totalTransactions?: number;
  totalValue?: string;
  // Add other summary properties as needed
}

interface LocationState {
  results: {
    transactions: EthereumTransaction[];
    // Add other results properties if needed
  };
  wallet: WalletData;
  summary: SummaryData;
}

export default function ETHTransactions(): React.ReactElement {
  const location = useLocation();
  const { results: data, wallet, summary } = location.state as LocationState;

  const wsManager = useWebSocketManager();

  return (
    <>
      <Navbar />
      <div className="w-full h-full flex flex-col justify-center content items-center">
        <ETHSummary summary={summary} />
        <div className="flex flex-col w-full">
          <ETHTransactionView
            wallet={wallet}
            transactions={data.transactions}
            summary={summary}
          />
        </div>
      </div>
    </>
  );
}
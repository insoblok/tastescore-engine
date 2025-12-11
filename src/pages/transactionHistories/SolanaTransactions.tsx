import React, { useEffect, useRef, useState } from "react";
import Navbar from "../../layout/Navbar";
import { useLocation } from "react-router-dom";
import { toast } from "react-toastify";
import axios from "axios";
import apiClient from "../../api/client";
import SOLTransactionView from '../../components/transactionHistories/sol/SolTransactionView';
import SummaryView from "../../components/transactionHistories/sol/SolSummary";
import { ISOLTransaction, ISOLTransfer, ISOLTransactionDTO } from "../../interfaces/Sol";
import { IApiResponse } from "../../interfaces/Common";
import { ClipLoader } from "react-spinners";

export default function SolanaTransactions(): React.ReactElement {
  const location = useLocation();
  const { network, wallet } = location.state;
  const [transactions, setTransactions] = useState<ISOLTransactionDTO[]>([]);
  const [summary, setSummary] = useState<any>();
  const [loading, setLoading] = useState<boolean>(false);
  
  useEffect(() => {
		doRequest(wallet, network);
	}, [network, wallet]);

  const doRequest = async (address: string, type: number) => {
    setLoading(true);
		try {
			const response = await apiClient.get<IApiResponse>(
				`/explore?wallet=${address}&network=${type}`
			);

			if (response.status !== 200) {
				throw new Error(response.statusText);
			}

			if (response.data?.status_code === 400) {
				toast.warning("Please enter a valid wallet address");
				return;
			}
			try {
				const data = JSON.parse(response.data?.data?.histories || "{}");
        console.log(data);
        const summaryResponse = JSON.parse(response.data?.data?.summary || "{}");
				const processedTransactions = processTransactions(data.transactions);
        setTransactions(processedTransactions);
				setSummary(summaryResponse);
			} catch (error) {
				console.error(
					"Exception raised while parsing response: ",
					error
				);
				toast.error("Failed to parse the response data.");
			} finally {
        
      }
		} catch (err) {
			console.error(err);
			toast.error(
				"Unexpected error! Please try again with valid wallet address."
			);
		}
    setLoading(false);
	};

  const processTransactions = (txs: ISOLTransaction[]): ISOLTransactionDTO[] => {
    
    let results: ISOLTransactionDTO[] = [];
    for (const tx of txs) {
      const transfers: ISOLTransfer[] = tx.nativeTransfers;
      for (const tr of transfers) {
        const newTx: ISOLTransactionDTO = {
          description: tx.description,
          timestamp: tx.timestamp,
          type: tx.type,
          fee: tx.fee,
          signature: tx.signature,
          slot: tx.slot,
          from: tr.fromUserAccount,
          to: tr.toUserAccount,
          amount: tr.amount 
        }; 
        results.push(newTx);
      }
      
    }
    return results;
  }
  return (
    <>
      <Navbar />
      {loading ? (
        <div className="w-full h-full flex items-center justify-center min-h-screen">
          <ClipLoader color="#36d7b7" size={50} />
        </div>
      ) : (
        <div className="w-full h-full flex flex-col items-center mt-10">
          <SummaryView {...summary} />

          <div className="flex flex-col w-full px-5">
            <SOLTransactionView wallet={wallet} transactions={transactions} />
          </div>
        </div>
      )}
    </>
  )
}
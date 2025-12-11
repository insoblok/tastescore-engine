import React, { useEffect, useRef, useState } from "react";
import Navbar from "../../layout/Navbar";
import { useLocation } from "react-router-dom";
import ETHTransactionView from "../../components/transactionHistories/eth/ETHTransactionView";
import ETHSummary from "../../components/transactionHistories/eth/ETHSummary";
import { ETH_HTTPS_URL, ETH_SOCKET_URL } from "../../Constants";
import { toast } from "react-toastify";
import axios from "axios";
import {
	IETHTransaction,
	IETHTransactionRPC,
	ILogSubscriptionResponse,
} from "../../interfaces/Ethereum";
import { ILocationState, IApiResponse } from "../../interfaces/Common";
import { convertRawToEthereumTransaction } from "../../utils/transactions";
import apiClient from "../../api/client";

export default function ETHTransactions(): React.ReactElement {
	const location = useLocation();
	const { network, wallet } = location.state as ILocationState;
	const wsRef = useRef<WebSocket | null>(null);
	const [transactions, setTransactions] = useState<IETHTransaction[]>([]);
	const [wsTransactionIds, setWSTransactionIds] = useState<String[]>([]);
	const [summary, setSummary] = useState<any>();


  useEffect(() => {
		doRequest(wallet, network);
	}, [network, wallet]);

	useEffect(() => {
		const ws = new WebSocket(`${ETH_SOCKET_URL}`);
		wsRef.current = ws;
		ws.onopen = () => {
			console.log("✅ WebSocket connected");
			toast.success("Subscription to Ethereum Network succeeded.");

			if (wallet) {
				ws.send(
					JSON.stringify({
						jsonrpc: "2.0",
						id: 1,
						method: "eth_subscribe",
						params: [
							"logs",
							{
								address: wallet,
								topics: [
									"0xd78a0cb8bb633d06981248b816e7bd33c2a35a6089241d099fa519e361cab902",
								],
							},
						],
					})
				);
			}
		};

		ws.onmessage = (event) => {
			const data = JSON.parse(event.data);
			console.log("Message:", data);
			if (!data.params) {
				return;
			}
			messageHandler(data);
		};

		ws.onclose = () => console.log("❌ WebSocket closed");
		return () => {
			if (ws.readyState == WebSocket.OPEN) {
				ws.close();
				wsRef.current = null;
			}
		};
	}, [wallet]);
  
  const messageHandler = async (msg: ILogSubscriptionResponse) => {
		const transactionId: any = msg.params.result.transactionHash || null;
		if (!transactionId || wsTransactionIds.includes(transactionId)) {
			return;
		}
		wsTransactionIds.push(transactionId);
		await fetchTransaction(transactionId);
	};

	const fetchTransaction = async (id: string) => {
		const response = await axios.post(ETH_HTTPS_URL, {
			jsonrpc: "2.0",
			method: "eth_getTransactionByHash",
			params: [id],
			id: 1,
		});
		if (response.status === 200) {
			const data: IETHTransactionRPC = response.data;
			const converted: IETHTransaction =
				convertRawToEthereumTransaction(data);
			setTransactions((prev) => [...prev, converted]);
		}
	};

  const doRequest = async (address: string, type: number) => {
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
        const summaryResponse = JSON.parse(response.data?.data?.summary || "{}");
				setTransactions(data.transactions);
				setSummary(summaryResponse);
			} catch (error) {
				console.error(
					"Exception raised while parsing response: ",
					error
				);
				toast.error("Failed to parse the response data.");
			}
		} catch (err) {
			console.error(err);
			toast.error(
				"Unexpected error! Please try again with valid wallet address."
			);
		}
	};

	

	return (
		<>
			<Navbar />
			<div className="w-full h-full flex flex-col justify-center content items-center">
				<ETHSummary { ...summary} />
				<div className="flex flex-col w-full px-5">
					<ETHTransactionView
						wallet={wallet}
						transactions={transactions}
					/>
				</div>
			</div>
		</>
	);
}

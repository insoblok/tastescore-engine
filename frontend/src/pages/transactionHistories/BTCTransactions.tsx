import React, { useEffect, useRef, useState } from "react";
import BTCSummary from "../../components/transactionHistories/btc/BTCSummary";
import BTCTransactionView from "../../components/transactionHistories/btc/BTCTransactionView";
import Navbar from "../../layout/Navbar";
import { useLocation } from "react-router-dom";
import { BTC_SOCKET_URL } from "../../Constants";
import { IBTCTransaction, IBTCTransactionRaw } from "../../interfaces/BTC";
import { convertRawToBTCTransaction } from "../../utils/transactions";
import { toast } from "react-toastify";
import apiClient from "../../api/client";
import { IApiResponse, ILocationState } from "../../interfaces/Common";

export default function BTCTransactions(): React.ReactElement {
	const location = useLocation();
	const { network, wallet } = location.state as ILocationState;
	const [openStates, setOpenStates] = useState<boolean[]>();
	const wsRef = useRef<WebSocket | null>(null);
	const [transactions, setTransactions] = useState<IBTCTransaction[]>([]);
	const [summary, setSummary] = useState<any>();

	useEffect(() => {
		doRequest(wallet, network);
	}, [network, wallet]);

	useEffect(() => {
		const ws = new WebSocket(BTC_SOCKET_URL);
		wsRef.current = ws;
		ws.onopen = () => {
			console.log("✅ WebSocket connected");
			if (wallet) {
				ws.send(JSON.stringify({ op: "addr_sub", addr: wallet }));
			}
		};

		ws.onmessage = (event) => {
			const data = JSON.parse(event.data);
			console.log("Message:", data);
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

	const messageHandler = (msg: IBTCTransactionRaw): void => {
		toast.info("New Transaction Occurred.");
		const transaction: IBTCTransaction = convertRawToBTCTransaction(msg);
		setTransactions((prevTransactions) => [
			...prevTransactions,
			transaction,
		]);
	};

	const toggleItem = (index: number): void => {
		setOpenStates((prev) => {
			const newStates = [...prev];
			newStates[index] = !newStates[index];
			return newStates;
		});
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
				const data = JSON.parse(response.data?.data?.histories || "");
				const { txs, ...summaryResponse } = data;
				setTransactions(data.txs);
				setOpenStates(data.txs.map(() => false));
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
				<BTCSummary {...summary} />
				<div className="size-9/10 mx-auto space-y-1 mx-10">
					{(() => {
						const txs = transactions.map(
							(one: IBTCTransaction, index: number) => ({
								...one,
								index,
							})
						);
						return txs.map(
							(one: IBTCTransaction, index: number) => (
								<BTCTransactionView
									key={index} // Better to use txid instead of index as key
									{...one}
									toggleItem={toggleItem}
									openStates={openStates}
								/>
							)
						);
					})()}
				</div>
			</div>
		</>
	);
}

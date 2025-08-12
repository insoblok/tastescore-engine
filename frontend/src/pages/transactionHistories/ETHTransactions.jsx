import React from "react";
import Navbar from "../../layout/Navbar";
import { useLocation } from "react-router-dom";
import ETHTransactionView from "../../components/transactionHistories/eth/ETHTransactionView";
import ETHSummary from "../../components/transactionHistories/eth/ETHSummary";

export default function ETHTransactions() {
	const location = useLocation();
	const data = location.state.results;
	const wallet = location.state.wallet;
	const summary = location.state.summary;

	return (
		<>
			<Navbar />
			<div className="w-full h-full flex flex-col justify-center content items-center">
				<ETHSummary summary={summary} />
				<div className="flex flex-col w-full">
					{
						<ETHTransactionView
							wallet={wallet}
							transactions={data.transactions}
							summary={summary}
						/>
					}
				</div>
			</div>
		</>
	);
}

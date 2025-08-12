import React from "react";
import BTCSummary from "../../components/transactionHistories/btc/BTCSummary";
import BTCTransactionView from "../../components/transactionHistories/btc/BTCTransactionView";
import Navbar from "../../layout/Navbar";

import { useLocation } from "react-router-dom";

export default function BTCTransactions() {
	const location = useLocation();
	const data = location.state.results;

	return (
		<>
			<Navbar />
			<div className="w-full h-full flex flex-col justify-center content items-center">
				<BTCSummary {...data} />
				<div className="flex flex-col">
					{data.txs.map((one) => (
						<BTCTransactionView {...one} />
					))}
				</div>
			</div>
		</>
	);
}

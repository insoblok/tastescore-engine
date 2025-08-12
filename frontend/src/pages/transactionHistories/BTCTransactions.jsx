import React, { useState } from "react";
import BTCSummary from "../../components/transactionHistories/btc/BTCSummary";
import BTCTransactionView from "../../components/transactionHistories/btc/BTCTransactionView";
import Navbar from "../../layout/Navbar";

import { useLocation } from "react-router-dom";

export default function BTCTransactions() {
	const location = useLocation();
	const data = location.state.results;

	const [openStates, setOpenStates] = useState(data.txs.map(() => false));

	const toggleItem = (index) => {
		setOpenStates((prev) => {
			const newStates = [...prev];
			newStates[index] = !newStates[index];
			return newStates;
		});
	};

	return (
		<>
			<Navbar />
			<div className="w-full h-full flex flex-col justify-center content items-center">
				<BTCSummary {...data} />
				<div className="size-9/10 mx-auto space-y-1 mx-10">
					{data.txs.map((one, index) => (
						<BTCTransactionView
							key={index}
							index={index}
							{...one}
							toggleItem={toggleItem}
							openStates={openStates}
						/>
					))}
				</div>
			</div>
		</>
	);
}

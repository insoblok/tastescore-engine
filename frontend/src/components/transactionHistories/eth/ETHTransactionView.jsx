import React from "react";
import {
	getFormattedDateTimeString,
	AbstractHashComponent,
} from "../../../utils/transactions";
import DataTable from "react-data-table-component";

export default function ETHTransactionView({ transactions, wallet }) {
	const checkDepositOrTransfer = (src, wlt) => {
		return src.toLowerCase() == wlt.toLowerCase() ? "Transfer" : "Deposit";
	};

	const columns = [
		{
			name: "Transaction Hash",
			selector: (row) => <AbstractHashComponent content={row.hash} />,
		},
		{
			name: "Method",
			selector: (row) => checkDepositOrTransfer(row.src, wallet),
		},
		{ name: "Block", selector: (row) => row.blockNumber },
		{
			name: "Time",
			selector: (row) => getFormattedDateTimeString(row.time),
		},
		{
			name: "From",
			selector: (row) => <AbstractHashComponent content={row.src} />,
		},
		{
			name: "To",
			selector: (row) => <AbstractHashComponent content={row.dst} />,
		},
		{ name: "Amount", selector: (row) => row.amount },
		{ name: "Txn Fee", selector: (row) => row.fee },
	];

	return (
		<DataTable title="" columns={columns} data={transactions} pagination />
	);
}

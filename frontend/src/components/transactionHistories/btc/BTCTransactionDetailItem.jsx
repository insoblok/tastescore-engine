import React from "react";
import { FaCopy } from "react-icons/fa";
import { ETHER_IN_WEI } from "../../../Constants";
import { handleClickCopyClipboard } from "../../../utils/transactions";

export default function BTCTransactionDetailItem(props) {
	const tx = props.type == 0 ? props.prev_out : props;

	return (
		<div className="flex my-1 text-sm">
			<p className="font-bold text-black flex items-center">
				{props.index + 1}
			</p>
			<div className="flex flex-col mx-3 w-[-webkit-fill-available]">
				<div className="flex items-center w-full">
					<p className="text-orange-400 truncate" title={tx.addr}>
						{tx.addr}
					</p>
					<button
						className="p-1 rounded hover:bg-orange-200 transition"
						onClick={(e) => handleClickCopyClipboard(tx.addr, e)}
					>
						<FaCopy className="h-4 w-4 text-orange-400" />
					</button>
				</div>
				<div className="flex">
					<p className="text-black text-start">
						{tx.value / ETHER_IN_WEI} BTC
					</p>
				</div>
			</div>
		</div>
	);
}

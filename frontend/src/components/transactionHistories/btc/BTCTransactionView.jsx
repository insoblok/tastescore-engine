import React from "react";
import { abstractHash, getFormattedDateTimeString } from "../../../utils/transactions";

export default function BTCTransactionView(tx) {
	return (
		<div>
			<div className="flex gap-3 border border-gray-200 p-2">
				<div className="flex1 flex flex-col w-100 items-start">
					<div >ID: <span className="text-lime-700">{abstractHash(tx.hash)}</span></div>
					<div>{ getFormattedDateTimeString(tx.time) } </div>
				</div>
				<div className="flex1 flex flex-col w-100">
						<div>From <span className="text-lime-700">{tx.inputs.length == 1 ? abstractHash(tx.inputs[0]) : `${tx.inputs.length} Inputs`}</span></div>
						<div>To <span className="text-lime-700">{tx.outputs.length == 1 ? abstractHash(tx.outputs[0]) : `${tx.outputs.length} Outputs`}</span></div>
				</div>
				<div className="flex1 flex flex-col w-100 items-end">
					<div>{ tx.result } BTC</div>
					<div><span className="text-red-500"> Fee </span> {tx.fee.toLocaleString()} </div>
				</div>
			</div>	
		</div>
	);
}

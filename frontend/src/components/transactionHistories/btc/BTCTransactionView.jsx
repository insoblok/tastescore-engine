import React from "react";
import {
	abstractHash,
	getFormattedDateTimeString,
} from "../../../utils/transactions";
import BTCTransactionDetailItem from "./BTCTransactionDetailItem";
import { handleClickCopyClipboard } from "../../../utils/transactions";
import { FaCopy } from "react-icons/fa";

export default function BTCTransactionView(tx) {
	const inputs = new Set();
	let outputs = new Set();
	for (const input of tx.inputs) {
		inputs.add(input?.prev_out?.addr);
	}

	for (const output of tx.outputs) {
		outputs.add(output?.addr);
	}
	return (
		<div className="rounded-lg overflow-hidden shadow-sm w-full">
			<div
				htmlFor="info-section"
				className="w-full flex justify-between items-center p-4 bg-primary-100 hover:bg-primary-200 active:bg-primary-300 text-primary-900 font-medium cursor-pointer transition-colors duration-200 ease-in-out select-none"
				onClick={() => tx.toggleItem(tx.index)}
			>
				<div className="flex flex-1">
					<div className="flex-1 flex flex-col w-100 items-start">
						<div>
							ID:{" "}
							<span className="text-lime-700">
								{abstractHash(tx.hash)}
							</span>
							<button
								title="Copy address"
								className="p-2 mx-1 hover:bg-blue-200 text-gray rounded-full"
								onClick={(e) => {
									handleClickCopyClipboard(tx.hash, e);
								}}
							>
								<FaCopy size={12} />
							</button>
						</div>
						<div>{getFormattedDateTimeString(tx.time)} </div>
					</div>
					<div className="flex-1 flex flex-col w-100">
						<div>
							From{" "}
							<span className="text-lime-700">
								{inputs.size == 1
									? abstractHash(inputs.values().next().value)
									: `${inputs.size} Inputs`}
							</span>
              {
                inputs.size == 1 &&
                <button
								title="Copy address"
								className="p-2 mx-1 hover:bg-blue-200 text-gray rounded-full"
								onClick={(e) => {
									handleClickCopyClipboard(inputs.values().next().value, e);
								}}
							>
								<FaCopy size={12} />
							</button>
              }
						</div>
						<div>
							To{" "}
							<span className="text-lime-700">
								{outputs.size == 1
									? abstractHash(
											outputs.values().next().value
									  )
									: `${outputs.size} Outputs`}
							</span>
						</div>
					</div>
					<div className="flex-1 flex w-100 justify-end">
						<div className="flex flex-col">
							<div>{tx.result} BTC</div>
							<div>
								<span className="text-red-500"> Fee </span>{" "}
								{tx.fee.toLocaleString()}{" "}
							</div>
						</div>
						<span
							className={`flex items-center mx-3 transform transition-transform duration-300 ${
								tx.openStates[tx.index]
									? "rotate-180"
									: "rotate-0"
							}`}
						>
							▼
						</span>
					</div>
				</div>
			</div>
			<div
				className={`bg-neutral-100 text-neutral-900 transition-all duration-300 ease-in-out overflow-hidden border-gray-300 border-1 ${
					tx.openStates[tx.index]
						? "max-h-[300px] overflow-y-auto p-4"
						: "max-h-0"
				}`}
			>
				<div className="w-full flex">
					<div className={`size-1/2 flex flex-col p-4 ${outputs.size <= inputs.size ? "border-gray-300 border-e-1" : ""}`}>
						<p className="font-bold text-black "> From </p>
						<div className="flex flex-col">
							{tx.inputs.map((one, index) => (
								<BTCTransactionDetailItem
									{...one}
									index={index}
									key={index}
									type={0}
								/>
							))}
						</div>
					</div>
					<div className={`size-1/2 flex flex-col p-4 ${outputs.size > inputs.size ? "border-gray-300 border-s-1" : ""}`}>
						<p className="font-bold text-black "> TO </p>
						<div className="flex flex-col">
							{tx.outputs.map((one, index) => (
								<BTCTransactionDetailItem
									{...one}
									index={index}
									key={index}
									type={1}
								/>
							))}
						</div>
					</div>
				</div>
			</div>
		</div>
	);
}

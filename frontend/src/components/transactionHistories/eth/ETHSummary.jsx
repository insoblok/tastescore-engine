import React from "react";
import { abstractHash } from "../../../utils/transactions";
import { FaCopy } from "react-icons/fa";
import { handleClickCopyClipboard } from "../../../utils/transactions";

export default function ETHSummary({ summary }) {
	return (
		<div className="max-w-md mx-auto bg-white shadow rounded-xl overflow-hidden md:max-w-2xl mb-3">
			<div className="p-8">
				<p className="mb-3 font-bold text-lime-500">Overview</p>
				<div className="flex justify-center uppercase tracking-wide text-sm text-gray-500 font-semibold">
					<span title={summary.hash} className="flex items-center">
						{abstractHash(summary.hash)}{" "}
					</span>
					<button
						title="Copy address"
						className="p-2 mx-1 hover:bg-blue-200 text-gray rounded-full flex items-center justify-center"
						onClick={(e) => {
							handleClickCopyClipboard(summary.hash, e);
						}}
					>
						<FaCopy size={12} />
					</button>
				</div>

				<div className="mt-6 pt-6 border-t border-gray-200">
					<h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
						ETH Balance
					</h3>
					<div className="mt-2 flex items-baseline justify-center bg-amber-100">
						<p className="text-2xl font-semibold text-gray-900">
							{summary.balance} ETH
						</p>
						<span className="ml-2 text-lg text-gray-500"></span>
					</div>
				</div>

				<div className="mt-6 pt-6 border-t border-gray-200">
					<p className="flex items-center text-xs font-semibold text-gray-500 tracking-wide">
						Totally Received:{" "}
						<span className="mx-4 px-4 py-1 rounded-md border border-teal-300 bg-teal-50 text-teal-600 font-semibold text-sm p-1">
							{summary.totalReceived}{" "}
						</span>
					</p>

					<p className="flex items-center text-xs font-semibold text-gray-500 tracking-wide my-3">
						Totally Sent:{" "}
						<span className="mx-10 px-4 py-1 rounded-md border border-teal-300 bg-teal-50 text-teal-600 font-semibold text-sm p-1">
							{summary.totalSent}{" "}
						</span>
					</p>

					<p className="flex items-center text-xs font-semibold text-gray-500 tracking-wide my-3">
						Number of Txs:{" "}
						<span className="mx-6 px-4 py-1 rounded-md border border-teal-300 bg-teal-50 text-teal-600 font-semibold text-sm p-1">
							{summary.transactionCount}{" "}
						</span>
					</p>
				</div>
			</div>
		</div>
	);
}
import React from "react";
import { abstractHash } from "../../../utils/transactions";
import { FaCopy } from "react-icons/fa";
import { handleClickCopyClipboard } from "../../../utils/transactions";
import { MouseEvent, JSX } from "react";

interface SOLSummaryData {
	address: string;
  balance: number;
	price: number;
	transactionCount: number;
	// Add other summary properties if needed
}

export default function SummaryView(summary : SOLSummaryData): JSX.Element {
  
  console.log(`Summary is ${JSON.stringify(summary)}`);
  const handleCopyClick = (e: MouseEvent<HTMLButtonElement>) => {
		e.stopPropagation();
		handleClickCopyClipboard(summary.address, e);
	};


  return (
    <>
  	<div className="max-w-md mx-auto bg-white shadow rounded-xl overflow-hidden md:max-w-2xl mb-3">
			<div className="p-8">
				<p className="mb-3 font-bold text-lime-500">Overview</p>
				<div className="flex justify-center uppercase tracking-wide text-sm text-gray-500 font-semibold">
					<span title={summary.address} className="flex items-center">
						{abstractHash(summary.address)}
					</span>
					<button
						title="Copy address"
						className="p-2 mx-1 hover:bg-blue-200 text-gray rounded-full flex items-center justify-center"
						onClick={handleCopyClick}
						aria-label="Copy Ethereum address"
					>
						<FaCopy size={12} />
					</button>
				</div>

				<div className="mt-6 pt-6 border-t border-gray-200">
					<h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
					</h3>
					<div className="mt-2 flex items-baseline justify-center">
						<span className="text-2xl font-semibold text-gray-900">
            ${((summary.balance || 0) * ( summary.price || 0)).toLocaleString()} 
						</span>
						<span className="ml-2 text-lg text-gray-500"></span>
					</div>
				</div>

				<div className="flex mt-6 pt-6 border-t border-gray-200">
        <div className="flex items-center text-xs font-semibold text-gray-500 tracking-wide my-3">
						Balance: {" "}
						<span className="mx-6 px-4 py-1 rounded-md border border-teal-300 bg-teal-50 text-teal-600 font-semibold text-sm p-1">
							{(summary.balance || 0).toLocaleString()} SOL
						</span>
					</div>
          
          <div className="flex items-center text-xs font-semibold text-gray-500 tracking-wide my-3">
						Number of Txs:{" "}
						<span className="mx-6 px-4 py-1 rounded-md border border-teal-300 bg-teal-50 text-teal-600 font-semibold text-sm p-1">
							{summary.transactionCount}
						</span>
					</div>

				</div>
			</div>
		</div>
    </>
  );
}

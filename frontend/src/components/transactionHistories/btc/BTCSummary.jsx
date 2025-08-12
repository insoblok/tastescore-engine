import React from "react";
import { abstractHash } from "../../../utils/transactions";

export default function BTCSummary({ address, final_balance }) {
	return (
		<div className="max-w-md mx-auto bg-white rounded-xl overflow-hidden md:max-w-2xl">
			<div className="p-8">
				<div className="uppercase tracking-wide text-sm text-gray-500 font-semibold">
					{abstractHash(address)}
				</div>

				<div className="mt-6 pt-6 border-t border-gray-200">
					<h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
						Bitcoin Balance
					</h3>
					<div className="mt-2 flex items-baseline justify-center bg-amber-100">
						<p className="text-2xl font-semibold text-gray-900">
							{final_balance } BTC
						</p>
						<span className="ml-2 text-lg text-gray-500"></span>
					</div>
				</div>
			</div>
		</div>
	);
}

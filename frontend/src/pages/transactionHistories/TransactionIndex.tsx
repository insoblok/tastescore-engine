import React from "react";
import Navbar from "../../layout/Navbar";

export default function TransactionIndex(): React.ReactElement  {
	return (
		<>
			<Navbar />
			<div className="w-full h-full flex justify-center content items-center">
				<div className="bg-white p-6 rounded-lg shadow-lg max-w-sm text-center h-50">
					<h2 className="text-2xl font-bold text-gray-800">
						Wallet Tracker
					</h2>
					<p className="text-gray-600 mt-3">
						Please enter the wallet address on the search bar.
					</p>
					<button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mt-4">
						Learn More
					</button>
				</div>
			</div>
		</>
	);
}

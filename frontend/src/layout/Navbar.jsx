import { Search, Settings, User } from "lucide-react";
import apiClient from "../api/client";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
export default function Navbar() {
	const [search, setSearch] = useState("");
	const navigate = useNavigate();

	const handleSearch = async (e) => {
		e.preventDefault();
		e.stopPropagation();
		if (!search) {
			toast.warning("Please enter the wallet address!");
			return;
		}
		try {
			const response = await apiClient.get(`/explore?wallet=${search}`);
			if (response.status != 200) {
				throw new Error(response.statusText);
			}
			let target, summary;
			try {
        if (response.data.status_code == 400) {
          toast.warning("Please enter a valid wallet address");
          return;
        }
				let data = JSON.parse(response.data.data.histories);
				if (response.data.data.summary)
					summary = JSON.parse(response.data.data.summary);
				if (data.token == "BTC") target = "/btc-transactions";
				else if (data.token == "ETH") target = "/eth-transactions";

				navigate(target, {
					state: { results: data, wallet: search, summary },
				});
			} catch (error) {
				console.log("Exception raised while parsing response: ", error);
        toast.error("Failed to parse the response data.")
			}
		} catch (err) {
			console.log(err);
      toast.error("Unexpected error! Please try again with valid wallet address.")
			return;
		}
	};

	return (
		<nav className="navbar w-full border-b bg-white px-4 py-3 flex items-center ">
			{/* Search bar */}
			<div className="navbar-left flex-1"></div>
			<div className="navbar-center flex-1">
				<div className="flex items-center flex-1 max-w-xl">
					<form onSubmit={handleSearch} className="w-full">
						<div className="flex items-center w-full bg-gray-100 rounded-full overflow-hidden">
							<input
								type="text"
								value={search}
								onChange={(e) => setSearch(e.target.value)}
								placeholder="Search Blockchain, Transactions, Addresses and Blocks"
								className="flex-1 bg-transparent px-4 py-2 text-sm text-gray-700 focus:outline-none"
							/>
							<button
								className="px-3 text-gray-500 hover:text-gray-700 text-end"
								type="submit"
							>
								<Search size={18} />
							</button>
						</div>
					</form>
				</div>
			</div>
			<div className="flex-1 flex justify-end">
				{/* Sign in */}
				<button className="ml-4 flex items-center gap-1 bg-black text-white px-4 py-1.5 rounded-full hover:bg-gray-900 transition">
					<User size={16} />
					<span className="text-sm">Sign In</span>
				</button>
			</div>
		</nav>
	);
}

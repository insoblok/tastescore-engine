import { Search, User } from "lucide-react";
import apiClient from "../api/client";
import { useState, FormEvent, ChangeEvent, JSX } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

interface ApiResponse {
	status_code?: number;
	data?: {
		histories: string;
		summary?: string;
	};
	statusText?: string;
}

interface NavigationState {
	results: any; // Replace 'any' with a proper interface for your results
	wallet: string;
	summary?: any; // Replace 'any' with a proper interface for your summary
}

export default function Navbar(): JSX.Element {
	const [search, setSearch] = useState<string>("");

	const navigate = useNavigate();

	const handleSearch = async (e: FormEvent): Promise<void> => {
		e.preventDefault();
		e.stopPropagation();

		if (!search) {
			toast.warning("Please enter the wallet address!");
			return;
		}

		try {
			const response = await apiClient.get<ApiResponse>(
				`/explore?wallet=${search}`
			);

			if (response.status !== 200) {
				throw new Error(response.statusText);
			}

			if (response.data?.status_code === 400) {
				toast.warning("Please enter a valid wallet address");
				return;
			}

			try {
				const data = JSON.parse(response.data?.data?.histories || "");
				const summary = response.data?.data?.summary
					? JSON.parse(response.data.data.summary)
					: undefined;

				let target: string;
				if (data.token === "BTC") {
					target = "/btc-transactions";
				} else if (data.token === "ETH") {
					target = "/eth-transactions";
				} else {
					throw new Error("Unsupported token type");
				}

				navigate(target, {
					state: {
						results: data,
						wallet: search,
						summary,
					} as NavigationState,
				});
			} catch (error) {
				console.error(
					"Exception raised while parsing response: ",
					error
				);
				toast.error("Failed to parse the response data.");
			}
		} catch (err) {
			console.error(err);
			toast.error(
				"Unexpected error! Please try again with valid wallet address."
			);
		}
	};

	const handleInputChange = (e: ChangeEvent<HTMLInputElement>): void => {
		setSearch(e.target.value);
	};

	return (
		<nav className="navbar w-full border-b bg-white px-4 py-3 flex items-center">
			{/* Search bar */}
			<div className="navbar-left flex-1"></div>
			<div className="navbar-center flex-1">
				<div className="flex items-center flex-1 max-w-xl">
					<form onSubmit={handleSearch} className="w-full">
						<div className="relative items-center w-full bg-gray-100 rounded-full overflow-hidden">
							<input
								type="text"
								value={search}
								onChange={handleInputChange}
								placeholder="Search Blockchain, Transactions, Addresses and Blocks"
								className="block w-full px-4 py-2 text-sm text-gray-700 border-0 focus:outline-none"
							/>
							<button
								className="absolute top-0 end-0 p-2.5 px-3 text-gray-500 bg-gray-300 text-end cursor-pointer hover:bg-gray-400"
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

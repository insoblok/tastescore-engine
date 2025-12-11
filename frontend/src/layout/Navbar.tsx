import { Search, User } from "lucide-react";
import apiClient from "../api/client";
import { useState, FormEvent, ChangeEvent, JSX } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import { detectBlockchain } from "../utils/transactions";
import ConfirmAlert from "../components/common/ConfirmAlert";
interface NavigationState {
	network: number;
	wallet: string;
}

export default function Navbar(): JSX.Element {
	const [search, setSearch] = useState<string>("");
  const [showConfirmAlert, setShowConfirmAlert] = useState<boolean>(false);
	const navigate = useNavigate();

  const handleConfirm = () => {
    setShowConfirmAlert(false);
    navigate("/eth-track", {
      state: {
        network: 2,
        wallet: search,
      } as NavigationState,
    });
  }


  const handleCancel = () => {
    setShowConfirmAlert(false);
    navigate("/bnb-track", {
      state: {
        network: 3,
        wallet: search,
      } as NavigationState,
    });
  }

	const handleSearch = async (e: FormEvent): Promise<void> => {
		e.preventDefault();
		e.stopPropagation();

		if (!search) {
			toast.warning("Please enter the wallet address!");
			return;
		}

    const network: number = detectBlockchain(search);
    if (network === 0) {
      setShowConfirmAlert(true)
      return;
    }
    let target: string = ""
    if (network == 1) {
      target = "/btc-track"
    }
    else if (network == 4) {
      target = "/sol-track"
    }

    navigate(target, {
      state: {
        wallet: search,
        network
      } as NavigationState
    });    
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
			<div className="flex-1 flex justify-end items-center gap-2">
				{/* Protocol Checker Link */}
				<button 
					onClick={() => navigate("/protocol-checker")}
					className="ml-4 flex items-center gap-1 bg-purple-600 text-white px-4 py-1.5 rounded-full hover:bg-purple-700 transition"
				>
					<span className="text-sm">Protocol Check</span>
				</button>
				{/* Sanctions Checker Link */}
				<button 
					onClick={() => navigate("/sanctions-checker")}
					className="ml-4 flex items-center gap-1 bg-teal-600 text-white px-4 py-1.5 rounded-full hover:bg-teal-700 transition"
				>
					<span className="text-sm">Sanctions Check</span>
				</button>
				{/* Sign in */}
				<button className="ml-4 flex items-center gap-1 bg-black text-white px-4 py-1.5 rounded-full hover:bg-gray-900 transition">
					<User size={16} />
					<span className="text-sm">Sign In</span>
				</button>
			</div>
      {showConfirmAlert && (
        <ConfirmAlert
          message="Is this address Ethereum or BNB?"
          confirmText="Ethereum"
          cancelText="BNB"
          onConfirm={handleConfirm}
          onCancel={handleCancel}
        />
      )}
		</nav>
	);
}

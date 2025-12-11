import "./App.css";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import BTCTransactions from "./pages/transactionHistories/BTCTransactions";
import TransactionIndex from "./pages/transactionHistories/TransactionIndex";
import ETHTransactions from "./pages/transactionHistories/ETHTransactions";
import SolanaTransactions from "./pages/transactionHistories/SolanaTransactions";
import { WebSocketManagerProvider } from "./context/WebSocketManagerContext";


import { ToastContainer } from "react-toastify";
import BNBTransactions from "./pages/transactionHistories/BNBTransactions";
import SanctionsChecker from "./pages/sanctions/SanctionsChecker";
import ProtocolChecker from "./pages/protocols/ProtocolChecker";

const router = createBrowserRouter([
	{
		path: "/",
		element: <TransactionIndex />,
	},
	{
		path: "/btc-track",
		element: <BTCTransactions />,
	},
	{
		path: "/eth-track",
		element: <ETHTransactions />,
	},
  {
    path: "/bnb-track",
    element: <BNBTransactions />
  }, {
    path: "/sol-track",
    element: <SolanaTransactions />
  },
  {
    path: "/sanctions-checker",
    element: <SanctionsChecker />
  },
  {
    path: "/protocol-checker",
    element: <ProtocolChecker />
  }
]);

function App() {
	return (
    <WebSocketManagerProvider>
      <div className="min-h-screen flex flex-col">
          <RouterProvider router={router} />
          <ToastContainer />
      </div>
    </WebSocketManagerProvider>
	);
}

export default App;

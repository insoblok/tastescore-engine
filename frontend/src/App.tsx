import "./App.css";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import BTCTransactions from "./pages/transactionHistories/BTCTransactions";
import TransactionIndex from "./pages/transactionHistories/TransactionIndex";
import ETHTransactions from "./pages/transactionHistories/ETHTransactions";
import { WebSocketManagerProvider } from "./context/WebSocketManagerContext";


import { ToastContainer } from "react-toastify";

const router = createBrowserRouter([
	{
		path: "/",
		element: <TransactionIndex />,
	},
	{
		path: "/btc-transactions",
		element: <BTCTransactions />,
	},
	{
		path: "/eth-transactions",
		element: <ETHTransactions />,
	},
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

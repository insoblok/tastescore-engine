import "./App.css";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import BTCTransactions from "./pages/transactionHistories/BTCTransactions";
import TransactionIndex from "./pages/transactionHistories/TransactionIndex";
import ETHTransactions from "./pages/transactionHistories/ETHTransactions";
import AccordionTest from "./pages/transactionHistories/AccordionTest";

import { ToastContainer } from "react-toastify";

const router = createBrowserRouter([
	{
		path: "/",
		element: <TransactionIndex />,
	},
  {
    path: "/test",
    element: <AccordionTest />,
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
		<div className="min-h-screen flex flex-col">
			<RouterProvider router={router} />
			<ToastContainer />
		</div>
	);
}

export default App;

import { JSX } from "react";
import {
  getFormattedDateTimeString,
  AbstractHashComponent,
} from "../../../utils/transactions";
import DataTable, { TableColumn } from "react-data-table-component";
import { IETHTransaction } from "../../../interfaces/Ethereum";


interface ETHTransactionViewProps {
  transactions: IETHTransaction[];
  wallet: string;
}

export default function ETHTransactionView({
  transactions,
  wallet,
}: ETHTransactionViewProps): JSX.Element {
  const checkDepositOrTransfer = (src: string, wlt: string): string => {
    return src.toLowerCase() === wlt.toLowerCase() ? "Transfer" : "Deposit";
  };

  const columns: TableColumn<any>[] = [
    {
      name: "Transaction Hash",
      selector: (row) => <AbstractHashComponent content={row.hash} />,
      cell: (row) => <AbstractHashComponent content={row.hash} />,
    },
    {
      name: "Method",
      selector: (row) => checkDepositOrTransfer(row.src, wallet),
      cell: (row) => checkDepositOrTransfer(row.src, wallet),
    },
    { 
      name: "Block", 
      selector: (row) => row.blockNumber.toString(),
      cell: (row) => row.blockNumber.toString(),
    },
    {
      name: "Time",
      selector: (row) => getFormattedDateTimeString(row.time),
      cell: (row) => getFormattedDateTimeString(row.time),
    },
    {
      name: "From",
      selector: (row) => <AbstractHashComponent content={row.src} />,
      cell: (row) => <AbstractHashComponent content={row.src} />,
    },
    {
      name: "To",
      selector: (row) => <AbstractHashComponent content={row.dst} />,
      cell: (row) => <AbstractHashComponent content={row.dst} />,
    },
    { 
      name: "Amount", 
      selector: (row) => <TruncateSpan text={row.amount.toString()} />,
      cell: (row) => <TruncateSpan text={row.amount.toString()} />,
    },
    { 
      name: "Txn Fee", 
      selector: (row) => row.fee.toString(),
      cell: (row) => row.fee.toString(),
    },
  ];

  const customStyles = {
    headCells: {
      style: {
        fontWeight: "bold",
        fontSize: "14px",
      },
    },
  };

  return (
    <DataTable 
      title={<span className="text-xl font-bold text-blue-500 uppercase tracking-5">Transactions</span>}
      className="border-1 border-gray-200" 
      customStyles={customStyles}
      columns={columns} 
      data={transactions} 
      pagination
      highlightOnHover
      pointerOnHover 
    />
  );
}

function TruncateSpan ({ text } : { text: string }) {
  return (
    <span title={text} className="truncate">{text}</span>
  )
}
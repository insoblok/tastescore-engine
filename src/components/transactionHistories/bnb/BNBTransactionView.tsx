import { JSX } from "react";
import {
  getFormattedDateTimeString,
  AbstractHashComponent,
} from "../../../utils/transactions";
import DataTable, { TableColumn } from "react-data-table-component";
import { IBNBTransaction } from "../../../interfaces/BNB";
import { ETHER_IN_WEI } from "../../../Constants";
interface Props {
  transactions: IBNBTransaction[];
  wallet: string;
}

export default function BNBTransactionView({ transactions, wallet}: Props) : JSX.Element {

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
      selector: (row) => <TruncateSpan text={(parseFloat(row.value) / ETHER_IN_WEI).toString()} />,
      cell: (row) => <TruncateSpan text={(parseFloat(row.value) / ETHER_IN_WEI).toString()} />,
    },
    { 
      name: "Txn Fee", 
      selector: (row) => row.gasUsed.toString(),
      cell: (row) => row.gasUsed.toString(),
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
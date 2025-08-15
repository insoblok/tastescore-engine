import { JSX } from "react";
import {
  getFormattedDateTimeString,
  AbstractHashComponent,
} from "../../../utils/transactions";
import DataTable, { TableColumn } from "react-data-table-component";

interface ETHTransaction {
  hash: string;
  src: string;
  dst: string;
  blockNumber: number | string;
  time: number;
  amount: string | number;
  fee: string | number;
  // Add other transaction properties as needed
}

interface ETHTransactionViewProps {
  transactions: ETHTransaction[];
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
      selector: (row) => row.amount.toString(),
      cell: (row) => row.amount.toString(),
    },
    { 
      name: "Txn Fee", 
      selector: (row) => row.fee.toString(),
      cell: (row) => row.fee.toString(),
    },
  ];

  return (
    <DataTable 
      title="" 
      columns={columns} 
      data={transactions} 
      pagination 
    />
  );
}
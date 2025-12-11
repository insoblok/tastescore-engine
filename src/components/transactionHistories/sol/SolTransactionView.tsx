import React, { JSX } from 'react';
import { ISOLTransaction, ISOLTransactionDTO } from '../../../interfaces/Sol';
import DataTable, { TableColumn } from "react-data-table-component";
import { AbstractHashComponent, getFormattedDateTimeString } from "../../../utils/transactions";

interface SOLTransactionViewProps {
  transactions: ISOLTransactionDTO[];
  wallet: string;
}

export default function SOLTransactionView({transactions, wallet}: SOLTransactionViewProps): JSX.Element {
  
  console.log(transactions);



  const columns: TableColumn<any>[] = [
    {
      name: "Signature",
      selector: (row) => <AbstractHashComponent content={row.signature} />,
      cell: (row) => <AbstractHashComponent content={row.signature} />,
    }, {
      name: "Block",
      selector: row => row.slot.toString(),
      cell: row => row.slot.toString()
    }, {
      name: "Time",
      selector: row => getFormattedDateTimeString(row.timestamp),
      cell: row => getFormattedDateTimeString(row.timestamp)
    }, {
      name: "From",
      selector: row =>  <AbstractHashComponent content={row.from} />,
      cell: row => <AbstractHashComponent content={row.from} />,
    },{
      name: "To",
      selector: row => <AbstractHashComponent content={row.to} />,
      cell: row => <AbstractHashComponent content={row.to} />,
    }, {
      name: "Value(SOL)",
      selector: row => (row.amount / (10 ** 9)).toLocaleString(),
      cell: row => (row.amount / (10 ** 9)).toLocaleString()
    }
  ]
  
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
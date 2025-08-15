import React, { useEffect, useState } from 'react'
import BTCSummary from '../../components/transactionHistories/btc/BTCSummary'
import BTCTransactionView from '../../components/transactionHistories/btc/BTCTransactionView'
import Navbar from '../../layout/Navbar'
import { useLocation } from 'react-router-dom'
import { useWebSocketManager } from '../../context/WebSocketManagerContext'
import { BTC_SOCKET_URL } from '../../Constants'
import { BTCTransaction, BTCTransactionRaw } from '../../interfaces/btc'
import { convertRawToBTCTransaction } from '../../utils/transactions'
import { toast } from 'react-toastify';

interface LocationState {
  results: {
    txs: BTCTransaction[]
    address?: string
    balance?: number
  }
  wallet: string
}

export default function BTCTransactions (): React.ReactElement {
  const location = useLocation()
  const { results: data, wallet } = location.state as LocationState
  const [openStates, setOpenStates] = useState<boolean[]>(
    data.txs.map(() => false)
  )

  const [transactions, setTransactions] = useState<BTCTransaction[]>([])

  const wsManager = useWebSocketManager()
  const btcWSManager = wsManager.get(BTC_SOCKET_URL)

  useEffect(() => {
    setOpenStates(data.txs.map(() => false))
    setTransactions([...data.txs])
  }, [data])

  useEffect(() => {
    if (!wallet) {
      return
    }
    btcWSManager?.onMessage(messageHandler)
    btcWSManager?.send({
      op: 'addr_sub',
      addr: wallet
    })
  }, [btcWSManager])

  const messageHandler = (msg: BTCTransactionRaw): void => {
    toast.info("New Transaction Occurred.");
    const transaction: BTCTransaction = convertRawToBTCTransaction(msg)
    setTransactions(prevTransactions => [...prevTransactions, transaction])
  }

  const toggleItem = (index: number): void => {
    setOpenStates(prev => {
      const newStates = [...prev]
      newStates[index] = !newStates[index]
      return newStates
    })
  }

  return (
    <>
      <Navbar />
      <div className='w-full h-full flex flex-col justify-center content items-center'>
        <BTCSummary {...data} />
        <div className='size-9/10 mx-auto space-y-1 mx-10'>
          {(() => {
            const txs = transactions.map(
              (one: BTCTransaction, index: number) => ({ ...one, index })
            )
            return txs.map((one: BTCTransaction, index: number) => (
              <BTCTransactionView
                key={one.txid} // Better to use txid instead of index as key
                {...one}
                toggleItem={toggleItem}
                openStates={openStates}
              />
            ))
          })()}
        </div>
      </div>
    </>
  )
}

import { FaCopy } from 'react-icons/fa'
import { ETHER_IN_WEI } from '../../../Constants'
import { handleClickCopyClipboard } from '../../../utils/transactions'
import { MouseEvent } from 'react'
import { JSX } from 'react'

interface TransactionDetail {
  addr: string
  value: number
}

interface BTCTransactionDetailItemProps {
  type?: number
  prev_out?: TransactionDetail
  index: number
  addr?: string
  value?: number
}

export default function BTCTransactionDetailItem (
  props: BTCTransactionDetailItemProps
): JSX.Element {
  const tx: TransactionDetail =
    props.type === 0
      ? (props.prev_out as TransactionDetail)
      : {
          addr: props.addr || '',
          value: props.value || 0
        }

  const handleCopyClick = (e: MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation()
    handleClickCopyClipboard(tx.addr, e)
  }

  return (
    <div className='flex my-1 text-sm'>
      <p className='font-bold text-black flex items-center'>
        {props.index + 1}
      </p>
      <div className='flex flex-col mx-3 w-[fill-available]'>
        <div className='flex items-center w-full'>
          <p className='text-orange-400 truncate' title={tx.addr}>
            {tx.addr}
          </p>
          <button
            className='p-1 rounded hover:bg-orange-200 transition'
            onClick={handleCopyClick}
            aria-label='Copy address'
          >
            <FaCopy className='h-4 w-4 text-orange-400' />
          </button>
        </div>
        <div className='flex'>
          <p className='text-black text-start'>
            {(tx.value / ETHER_IN_WEI).toFixed(8)} BTC
          </p>
        </div>
      </div>
    </div>
  )
}

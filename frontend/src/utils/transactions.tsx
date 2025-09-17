import { toast } from "react-toastify";
import { FaCopy } from "react-icons/fa";
import { ReactElement, MouseEvent } from "react";
import { BTCTransaction, BTCTransactionRaw } from "../interfaces/BTC";
import { ETHTransaction, EthereumTransactionRPC } from "../interfaces/Ethereum";


interface HashComponentProps {
  original: string;
  after: string;
}

export function HashComponent({ original, after }: HashComponentProps): ReactElement {
  return (
    <div className="flex">
      <span title={original} className="flex items-center font-bold text-slate-500">
        {after}
      </span>
      <button
        title="Copy address"
        className="p-2 mx-1 hover:bg-blue-200 text-gray rounded-full flex items-center justify-center text-slate-500"
        onClick={(e: MouseEvent) => handleClickCopyClipboard(original, e)}
      >
        <FaCopy size={12} />
      </button>
    </div>
  );
}

interface AbstractHashComponentProps {
  content: string;
}

export const AbstractHashComponent = ({ content }: AbstractHashComponentProps): ReactElement => {
  const text = `${content.slice(0, 5)}-${content.slice(-5)}`;
  return <HashComponent original={content} after={text} />;
};

export const abstractHash = (content?: string): string => {
  const DEFAULT_HASH_LENGTH = 5;
  
  if (!content?.trim()) {
    return "";
  }

  // Handle case where string is shorter than the required hash length
  if (content.length <= DEFAULT_HASH_LENGTH * 2) {
    return content; // Return original if too short to split meaningfully
  }

  const firstPart = content.slice(0, DEFAULT_HASH_LENGTH);
  const lastPart = content.slice(-DEFAULT_HASH_LENGTH);
  
  return `${firstPart}-${lastPart}`;
};

export const getFormattedDateTimeString = (sec: number): string => {
  return new Date(sec * 1000).toLocaleString();
};

export const handleClickCopyClipboard = (text: string, event: MouseEvent): void => {
  event.stopPropagation();
  navigator.clipboard
    .writeText(text)
    .then(() => {
      toast.success("Copied to Clipboard");
    })
    .catch((err) => {
      toast.error(`Failed to copy: ${err}`);
    });
};


export function convertRawToBTCTransaction(raw: BTCTransactionRaw): BTCTransaction {
  return {
    hash: raw.x.hash,
    time: raw.x.time,
    inputs: raw.x.inputs.map(input => ({
      sequence: input.sequence,
      prev_out: input.prev_out ? {
        addr: input.prev_out.addr,
        value: input.prev_out.value,
      } : undefined,
      script: input.script
    })),
    outputs: raw.x.out.map(output => ({
      addr: output.addr,
      value: output.value,
    })),
    result: 0,
    fee: 0,
    index: 0,
    openStates: [],
    toggleItem: () => {},
    // Additional fields
  };
}

export function convertRawToEthereumTransaction(raw: EthereumTransactionRPC): ETHTransaction {
  return {
    hash: raw.result.hash,
    src: raw.result.from,
    dst: raw.result.to,
    amount: raw.result.value,
    time: Date.now(),
    fee: raw.result.gasPrice,
    blockNumber: raw.result.blockNumber,
  }
}

export const detectBlockchain = (address: string): number => {
  const addr = address.trim();

  // Ethereum / BSC (EVM-based)
  const evmRegex = /^0x[a-fA-F0-9]{40}$/;
  if (evmRegex.test(addr)) {
    return 0;
  }

  // Bitcoin Legacy (starts with 1 or 3)
  const btcLegacyRegex = /^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$/;
  if (btcLegacyRegex.test(addr)) {
    return 1;
  }

  // Bitcoin Bech32 (starts with bc1)
  if (addr.toLowerCase().startsWith("bc1") && addr.length >= 39 && addr.length <= 59) {
    return 1;
  }

  // Solana (Base58, 32-44 chars)
  const solRegex = /^[1-9A-HJ-NP-Za-km-z]{32,44}$/;
  if (solRegex.test(addr)) {
    return 4;
  }

  return -1;
}
import { toast } from "react-toastify";
import { FaCopy } from "react-icons/fa";
import { ReactElement, MouseEvent } from "react";
import { BTCTransaction, BTCTransactionRaw } from "../interfaces/btc";


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
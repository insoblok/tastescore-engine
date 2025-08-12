import { toast } from "react-toastify";
import { FaCopy } from "react-icons/fa";

export function HashComponent ({ original, after }) {
	return (
		<div className="flex">
			<span title={original} className="flex items-center font-bold text-slate-500">{ after } </span>
			<button
				title="Copy address"
				className="p-2 mx-1 hover:bg-blue-200 text-gray rounded-full flex items-center justify-center text-slate-500"
				onClick={e =>{ handleClickCopyClipboard(original, e)}}
			>
			<FaCopy size={12} />
			</button>
		</div>
	)
}

export const AbstractHashComponent = ({ content }) => {
	const text = `${content.slice(0, 5)}-${content.slice(-5)}`;
	return <HashComponent original={content} after={text}  />
};

export const abstractHash = content => {
	return `${content.slice(0, 5)}-${content.slice(-5)}`;
}

export const getFormattedDateTimeString = (sec) => {
	return new Date(sec * 1000).toLocaleString();
};

export const handleClickCopyClipboard = (text, event) => {
  event.stopPropagation();
	navigator.clipboard.writeText(text)
	.then(() => {
		toast.success("Copied to Clipboard");
	})
	.catch(err => {
		toast.error("Failed to copy: ", err)
	})
}

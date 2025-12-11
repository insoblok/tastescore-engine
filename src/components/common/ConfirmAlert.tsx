import React from "react";

interface ConfirmAlertProps {
  message: string;
  confirmText: string;
  cancelText: string;
  onConfirm: () => void;
  onCancel: () => void;
}

const ConfirmAlert: React.FC<ConfirmAlertProps> = ({ message, confirmText, cancelText, onConfirm, onCancel }) => {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black z-50">
      <div className="bg-white rounded-lg shadow-lg p-6 w-96">
        <p className="text-gray-800 text-lg mb-6">{message}</p>
        <div className="flex justify-center gap-4">
          <button
            className="px-4 py-2 rounded bg-gray-200 hover:bg-gray-300 text-gray-700"
            onClick={onCancel}
          >
            { cancelText }
          </button>
          <button
            className="px-4 py-2 rounded bg-blue-600 hover:bg-blue-700 text-white"
            onClick={onConfirm}
          >
            { confirmText }
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmAlert;

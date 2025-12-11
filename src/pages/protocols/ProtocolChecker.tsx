import React, { useState } from "react";
import Navbar from "../../layout/Navbar";
import { toast } from "react-toastify";
import { useProtocolCheck } from "../../hooks/useProtocol";
import ProtocolSafetyCard from "../../components/protocols/ProtocolSafetyCard";
import { ClipLoader } from "react-spinners";
import { Search, AlertCircle } from "lucide-react";

export default function ProtocolChecker(): React.ReactElement {
  const [contractAddress, setContractAddress] = useState("");
  const [chain, setChain] = useState<string>("");
  const { data, loading, error, checkProtocol } = useProtocolCheck();

  const handleCheck = async () => {
    if (!contractAddress.trim()) {
      toast.error("Please enter a contract address");
      return;
    }

    // Basic address validation (Ethereum-style)
    if (!/^0x[a-fA-F0-9]{40}$/.test(contractAddress.trim())) {
      toast.warning("Please enter a valid contract address (0x followed by 40 hex characters)");
      return;
    }

    await checkProtocol(contractAddress.trim(), chain || undefined);
  };

  return (
    <>
      <Navbar />
      <div className="w-full h-full flex flex-col items-center mt-10 px-4">
        <div className="w-full max-w-2xl">
          <h1 className="text-3xl font-bold text-gray-800 mb-6 text-center">
            Protocol Safety Checker
          </h1>

          {/* Search Form */}
          <div className="bg-white shadow rounded-xl p-6 mb-6">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Contract Address
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={contractAddress}
                    onChange={(e) => setContractAddress(e.target.value)}
                    placeholder="0x..."
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    onKeyPress={(e) => {
                      if (e.key === "Enter") {
                        handleCheck();
                      }
                    }}
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Blockchain (Optional)
                </label>
                <select
                  value={chain}
                  onChange={(e) => setChain(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">All Chains</option>
                  <option value="ETH">Ethereum</option>
                  <option value="BNB">BNB Chain</option>
                  <option value="ARB">Arbitrum</option>
                  <option value="OP">Optimism</option>
                  <option value="POLYGON">Polygon</option>
                  <option value="BASE">Base</option>
                </select>
              </div>

              <button
                onClick={handleCheck}
                disabled={loading}
                className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <ClipLoader size={20} color="#ffffff" />
                    <span>Checking...</span>
                  </>
                ) : (
                  <>
                    <Search size={20} />
                    <span>Check Protocol Safety</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6">
              <div className="flex items-start">
                <AlertCircle className="text-red-600 mr-2 mt-0.5" size={20} />
                <div>
                  <h3 className="text-red-800 font-semibold mb-1">Error</h3>
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              </div>
            </div>
          )}

          {/* Results */}
          {data && !loading && (
            <ProtocolSafetyCard safetyCheck={data} />
          )}

          {/* Info Section */}
          {!data && !loading && (
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
              <h3 className="text-blue-800 font-semibold mb-2">How It Works</h3>
              <ul className="text-sm text-blue-700 space-y-2 list-disc list-inside">
                <li>Enter a smart contract address to check its protocol reputation</li>
                <li>Our system analyzes TVL, age, audits, incidents, and Layer 2 risks</li>
                <li>Protocols with scores ≥ 0.8 receive bonus rewards</li>
                <li>Protocols with scores &lt; 0.3 may incur penalty fees</li>
                <li>Unknown contracts receive a neutral score of 0.5</li>
              </ul>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

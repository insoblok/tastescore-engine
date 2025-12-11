import React, { useState } from "react";
import Navbar from "../../layout/Navbar";
import { toast } from "react-toastify";
import apiClient from "../../api/client";
import RiskFlagsCard from "../../components/sanctions/RiskFlagsCard";
import ExposureMetricsCard from "../../components/sanctions/ExposureMetricsCard";
import { ClipLoader } from "react-spinners";
import {
  ISanctionsCheckResponse,
  ISanctionsMetricsResponse,
  IRiskFlagsResponse,
  IExposureMetrics,
  IRiskFlags,
} from "../../interfaces/Sanctions";

export default function SanctionsChecker(): React.ReactElement {
  const [address, setAddress] = useState("");
  const [loading, setLoading] = useState(false);
  const [ingesting, setIngesting] = useState(false);
  const [addressLabel, setAddressLabel] = useState<any>(null);
  const [metrics, setMetrics] = useState<IExposureMetrics | null>(null);
  const [riskFlags, setRiskFlags] = useState<IRiskFlags | null>(null);

  const triggerIngestion = async () => {
    try {
      setIngesting(true);
      const response = await apiClient.post("/sanctions/ingest");
      if (response.data.success) {
        toast.success("Sanctions data updated successfully", { autoClose: 2000 });
      } else {
        toast.warning("Sanctions data update completed with warnings", { autoClose: 2000 });
      }
    } catch (error: any) {
      console.error("Ingestion error:", error);
      // Don't show error toast for ingestion failures - it's non-critical
      // The check will still work with existing data
    } finally {
      setIngesting(false);
    }
  };

  const handleCheck = async () => {
    if (!address.trim()) {
      toast.error("Please enter a wallet address");
      return;
    }

    setLoading(true);
    try {
      // Trigger OFAC ingestion in the background (non-blocking)
      // This ensures we have the latest sanctions data before checking
      triggerIngestion().catch(() => {
        // Silently handle ingestion errors - check will proceed with existing data
      });

      // Check address label (runs in parallel with ingestion) - search across all chains
      // URL encode the address to handle special characters
      const encodedAddress = encodeURIComponent(address.trim());
      const checkResponse = await apiClient.get<ISanctionsCheckResponse>(
        `/sanctions/check?address=${encodedAddress}`
      );
      setAddressLabel(checkResponse.data.data);

      // Get risk flags - search across all chains
      const flagsResponse = await apiClient.get<IRiskFlagsResponse>(
        `/sanctions/risk-flags?address=${encodedAddress}`
      );
      setRiskFlags(flagsResponse.data.data);

      // Get metrics - use chain from label if found, otherwise skip
      if (checkResponse.data.data?.chain) {
        try {
          const metricsResponse = await apiClient.get<ISanctionsMetricsResponse>(
            `/sanctions/metrics?address=${address}&chain=${checkResponse.data.data.chain}`
          );
          if (metricsResponse.data.data && "address" in metricsResponse.data.data) {
            setMetrics(metricsResponse.data.data as IExposureMetrics);
          } else {
            toast.info("No metrics available yet. Metrics are calculated when transactions are scanned.");
          }
        } catch (error) {
          // Metrics not available for this chain, that's okay
          toast.info("No metrics available yet. Metrics are calculated when transactions are scanned.");
        }
      } else {
        // Address not found in database, no metrics available
        setMetrics(null);
      }
    } catch (error: any) {
      console.error(error);
      toast.error(error.response?.data?.detail || "Failed to check address");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />
      <div className="w-full h-full flex flex-col items-center mt-10 px-4">
        <div className="w-full max-w-2xl">
          <h1 className="text-3xl font-bold text-gray-800 mb-6 text-center">
            Sanctions & Mixer Checker
          </h1>

          {/* Search Form */}
          <div className="bg-white shadow rounded-xl p-6 mb-6">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Wallet Address
                </label>
                <input
                  type="text"
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  placeholder="Enter any blockchain address (BTC, ETH, BNB, SOL, etc.)"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Searches across all blockchains automatically
                </p>
              </div>

              <button
                onClick={handleCheck}
                disabled={loading}
                className="w-full bg-teal-600 hover:bg-teal-700 text-white font-bold py-3 px-4 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {loading ? (
                  <>
                    <ClipLoader color="#ffffff" size={20} className="mr-2" />
                    Checking...
                  </>
                ) : (
                  "Check Address"
                )}
              </button>
              {ingesting && (
                <div className="mt-2 text-xs text-teal-600 flex items-center justify-center">
                  <ClipLoader color="#14b8a6" size={12} className="mr-2" />
                  Updating sanctions data in background...
                </div>
              )}
            </div>
          </div>

          {/* Results */}
          {loading ? (
            <div className="w-full flex items-center justify-center min-h-[400px]">
              <ClipLoader color="#36d7b7" size={50} />
            </div>
          ) : (
            <>
              {addressLabel && (
                <div className="mb-4 flex items-center justify-center min-h-[200px]">
                  {addressLabel.is_blacklisted || addressLabel.label ? (
                    <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4 w-full max-w-md">
                      <div className="flex items-center justify-center">
                        <div className="text-center">
                          <span className="text-red-800 font-bold text-lg mr-2">⚠️</span>
                          <p className="text-red-800 font-semibold">
                            Address is {addressLabel.label}
                          </p>
                          {addressLabel.program && (
                            <p className="text-red-600 text-sm">Program: {addressLabel.program}</p>
                          )}
                          {addressLabel.source && (
                            <p className="text-red-600 text-sm">Source: {addressLabel.source}</p>
                          )}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="bg-green-50 border-2 border-green-300 rounded-lg p-4 w-full max-w-md">
                      <div className="flex items-center justify-center">
                        <div className="text-center">
                          <span className="text-green-800 font-bold text-lg mr-2">✓</span>
                          <p className="text-green-800 font-semibold">
                            Address not found in sanctions or mixer lists
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {riskFlags && (
                <RiskFlagsCard 
                  riskFlags={riskFlags} 
                  address={address} 
                  chain={addressLabel?.chain || "ALL"} 
                />
              )}

              {/* {metrics && <ExposureMetricsCard metrics={metrics} />} */}
            </>
          )}
        </div>
      </div>
    </>
  );
}


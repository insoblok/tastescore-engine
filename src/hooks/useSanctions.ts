import { useState, useEffect } from "react";
import apiClient from "../api/client";
import {
  ISanctionsCheckResponse,
  ISanctionsMetricsResponse,
  IRiskFlagsResponse,
  IExposureMetrics,
  IRiskFlags,
  IAddressLabel,
} from "../interfaces/Sanctions";
import { toast } from "react-toastify";

interface UseSanctionsResult {
  addressLabel: IAddressLabel | null;
  metrics: IExposureMetrics | null;
  riskFlags: IRiskFlags | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useSanctions(address: string, chain: string): UseSanctionsResult {
  const [addressLabel, setAddressLabel] = useState<IAddressLabel | null>(null);
  const [metrics, setMetrics] = useState<IExposureMetrics | null>(null);
  const [riskFlags, setRiskFlags] = useState<IRiskFlags | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSanctionsData = async () => {
    if (!address || !chain) return;

    setLoading(true);
    setError(null);

    try {
      // Check address label
      const checkResponse = await apiClient.get<ISanctionsCheckResponse>(
        `/sanctions/check?address=${address}&chain=${chain}`
      );
      setAddressLabel(checkResponse.data.data);

      // Get risk flags
      const flagsResponse = await apiClient.get<IRiskFlagsResponse>(
        `/sanctions/risk-flags?address=${address}&chain=${chain}`
      );
      setRiskFlags(flagsResponse.data.data);

      // Get metrics
      try {
        const metricsResponse = await apiClient.get<ISanctionsMetricsResponse>(
          `/sanctions/metrics?address=${address}&chain=${chain}`
        );
        if (metricsResponse.data.data && "address" in metricsResponse.data.data) {
          setMetrics(metricsResponse.data.data as IExposureMetrics);
        }
      } catch (metricsError) {
        // Metrics might not be available yet, that's okay
        console.log("Metrics not available yet");
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || "Failed to fetch sanctions data";
      setError(errorMessage);
      console.error("Sanctions data fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSanctionsData();
  }, [address, chain]);

  return {
    addressLabel,
    metrics,
    riskFlags,
    loading,
    error,
    refetch: fetchSanctionsData,
  };
}


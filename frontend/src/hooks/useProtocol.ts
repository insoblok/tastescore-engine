import { useState, useEffect } from "react";
import apiClient from "../api/client";
import { ProtocolSafetyCheck, ProtocolListResponse, ProtocolCheckResponse } from "../interfaces/Protocol";

interface UseProtocolCheckResult {
  data: ProtocolSafetyCheck | null;
  loading: boolean;
  error: string | null;
  checkProtocol: (contractAddress: string, chain?: string) => Promise<void>;
}

export function useProtocolCheck(): UseProtocolCheckResult {
  const [data, setData] = useState<ProtocolSafetyCheck | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const checkProtocol = async (contractAddress: string, chain?: string) => {
    setLoading(true);
    setError(null);
    setData(null);
    
    try {
      const params = new URLSearchParams({ contract_address: contractAddress });
      if (chain) {
        params.append("chain", chain);
      }
      
      const url = `/protocols/check?${params.toString()}`;
      console.log("Checking protocol:", url);
      
      const response = await apiClient.get<ProtocolCheckResponse>(url);
      
      console.log("Protocol check response:", response.data);
      
      if (response.data && response.data.success) {
        setData(response.data.data);
      } else {
        setError("Failed to check protocol: Invalid response");
      }
    } catch (err: any) {
      console.error("Protocol check error:", err);
      const errorMessage = err.response?.data?.detail || err.response?.data?.message || err.message || "Failed to check protocol";
      setError(errorMessage);
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  return { data, loading, error, checkProtocol };
}

interface UseProtocolListResult {
  protocols: ProtocolListResponse["data"];
  loading: boolean;
  error: string | null;
  fetchProtocols: (limit?: number, category?: string, minScore?: number) => Promise<void>;
}

export function useProtocolList(): UseProtocolListResult {
  const [protocols, setProtocols] = useState<ProtocolListResponse["data"]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProtocols = async (limit = 100, category?: string, minScore?: number) => {
    setLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams({ limit: limit.toString() });
      if (category) {
        params.append("category", category);
      }
      if (minScore !== undefined) {
        params.append("min_score", minScore.toString());
      }
      
      const response = await apiClient.get<ProtocolListResponse>(
        `/api/protocols?${params.toString()}`
      );
      
      if (response.data.success) {
        setProtocols(response.data.data);
      } else {
        setError("Failed to fetch protocols");
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || "Failed to fetch protocols");
      setProtocols([]);
    } finally {
      setLoading(false);
    }
  };

  return { protocols, loading, error, fetchProtocols };
}

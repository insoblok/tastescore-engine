import React from "react";
import { IExposureMetrics } from "../../interfaces/Sanctions";
import { TrendingDown, TrendingUp, BarChart3 } from "lucide-react";

interface ExposureMetricsCardProps {
  metrics: IExposureMetrics;
}

export default function ExposureMetricsCard({ metrics }: ExposureMetricsCardProps): JSX.Element {
  const getCleanTxRatioColor = (ratio: number): string => {
    if (ratio >= 0.9) return "text-green-600";
    if (ratio >= 0.7) return "text-yellow-600";
    return "text-red-600";
  };

  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 0.8) return "text-green-600";
    if (confidence >= 0.5) return "text-yellow-600";
    return "text-red-600";
  };

  return (
    <div className="max-w-md mx-auto bg-white shadow rounded-xl overflow-hidden md:max-w-2xl mb-3">
      <div className="p-6">
        <div className="flex items-center mb-4">
          <BarChart3 className="text-teal-600 mr-2" size={24} />
          <h3 className="text-lg font-bold text-gray-800">Exposure Metrics</h3>
        </div>

        {metrics.sanctions_data_unknown && (
          <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm text-yellow-800">
              ⚠️ Sanctions data unavailable. Metrics may be incomplete.
            </p>
          </div>
        )}

        {/* Clean Transaction Ratio */}
        {metrics.clean_tx_ratio !== undefined && metrics.clean_tx_ratio !== null && (
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-semibold text-gray-600">Clean Transaction Ratio</span>
              <span className={`text-xl font-bold ${getCleanTxRatioColor(metrics.clean_tx_ratio)}`}>
                {(metrics.clean_tx_ratio * 100).toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${
                  metrics.clean_tx_ratio >= 0.9
                    ? "bg-green-500"
                    : metrics.clean_tx_ratio >= 0.7
                    ? "bg-yellow-500"
                    : "bg-red-500"
                }`}
                style={{ width: `${metrics.clean_tx_ratio * 100}%` }}
              />
            </div>
          </div>
        )}

        {/* Confidence Score */}
        {metrics.confidence !== undefined && metrics.confidence !== null && (
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-semibold text-gray-600">Confidence Score</span>
              <span className={`text-xl font-bold ${getConfidenceColor(metrics.confidence)}`}>
                {(metrics.confidence * 100).toFixed(0)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${
                  metrics.confidence >= 0.8
                    ? "bg-green-500"
                    : metrics.confidence >= 0.5
                    ? "bg-yellow-500"
                    : "bg-red-500"
                }`}
                style={{ width: `${metrics.confidence * 100}%` }}
              />
            </div>
          </div>
        )}

        {/* Direct Blacklist Hits */}
        <div className="mb-4">
          <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
            <TrendingDown className="mr-2" size={16} />
            Direct Blacklist Hits
          </h4>
          <div className="grid grid-cols-3 gap-2">
            <div className="p-2 bg-red-50 rounded text-center">
              <p className="text-xs text-gray-600">30 Days</p>
              <p className="text-sm font-bold text-red-700">
                {metrics.direct_blacklist_hits_30 ?? 0}
              </p>
            </div>
            <div className="p-2 bg-red-50 rounded text-center">
              <p className="text-xs text-gray-600">90 Days</p>
              <p className="text-sm font-bold text-red-700">
                {metrics.direct_blacklist_hits_90 ?? 0}
              </p>
            </div>
            <div className="p-2 bg-red-50 rounded text-center">
              <p className="text-xs text-gray-600">All Time</p>
              <p className="text-sm font-bold text-red-700">
                {metrics.direct_blacklist_hits_all ?? 0}
              </p>
            </div>
          </div>
        </div>

        {/* Mixer Transaction Share */}
        <div className="mb-4">
          <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
            <TrendingUp className="mr-2" size={16} />
            Mixer Transaction Share
          </h4>
          <div className="grid grid-cols-3 gap-2">
            <div className="p-2 bg-yellow-50 rounded text-center">
              <p className="text-xs text-gray-600">7 Days</p>
              <p className="text-sm font-bold text-yellow-700">
                {(metrics.mixer_tx_share_7 ?? 0).toFixed(1)}%
              </p>
            </div>
            <div className="p-2 bg-yellow-50 rounded text-center">
              <p className="text-xs text-gray-600">30 Days</p>
              <p className="text-sm font-bold text-yellow-700">
                {(metrics.mixer_tx_share_30 ?? 0).toFixed(1)}%
              </p>
            </div>
            <div className="p-2 bg-yellow-50 rounded text-center">
              <p className="text-xs text-gray-600">90 Days</p>
              <p className="text-sm font-bold text-yellow-700">
                {(metrics.mixer_tx_share_90 ?? 0).toFixed(1)}%
              </p>
            </div>
          </div>
        </div>

        {/* Blacklist Value (if available) */}
        {metrics.direct_blacklist_value_all !== undefined && 
         metrics.direct_blacklist_value_all !== null && 
         metrics.direct_blacklist_value_all > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <h4 className="text-sm font-semibold text-gray-700 mb-2">Blacklist Transaction Value</h4>
            <div className="text-sm text-gray-600">
              <p>All Time: ${(metrics.direct_blacklist_value_all ?? 0).toFixed(2)}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}


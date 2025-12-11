import React from "react";
import { IRiskFlags } from "../../interfaces/Sanctions";
import { AlertTriangle, Shield, AlertCircle, CheckCircle } from "lucide-react";

interface RiskFlagsCardProps {
  riskFlags: IRiskFlags;
  address: string;
  chain: string;
}

export default function RiskFlagsCard({ riskFlags, address, chain }: RiskFlagsCardProps): JSX.Element {
  const getRiskLevel = (): "high" | "medium" | "low" | "unknown" => {
    if (riskFlags.sanctions_data_unknown) return "unknown";
    if (riskFlags.has_sanctioned_exposure) return "high";
    if (riskFlags.has_mixer_exposure) return "medium";
    if (riskFlags.has_watchlist_exposure) return "medium";
    return "low";
  };

  const riskLevel = getRiskLevel();

  const riskConfig = {
    high: {
      bg: "bg-red-50",
      border: "border-red-300",
      text: "text-red-800",
      icon: AlertTriangle,
      label: "High Risk",
    },
    medium: {
      bg: "bg-yellow-50",
      border: "border-yellow-300",
      text: "text-yellow-800",
      icon: AlertCircle,
      label: "Medium Risk",
    },
    low: {
      bg: "bg-green-50",
      border: "border-green-300",
      text: "text-green-800",
      icon: CheckCircle,
      label: "Low Risk",
    },
    unknown: {
      bg: "bg-gray-50",
      border: "border-gray-300",
      text: "text-gray-800",
      icon: Shield,
      label: "Unknown Risk",
    },
  };

  const config = riskConfig[riskLevel];
  const Icon = config.icon;

  return (
    <div className={`max-w-md mx-auto bg-white shadow rounded-xl overflow-hidden md:max-w-2xl mb-3 ${config.bg} ${config.border} border-2`}>
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <Icon className={`${config.text} mr-2`} size={24} />
            <h3 className={`text-lg font-bold ${config.text}`}>Risk Assessment</h3>
          </div>
          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${config.bg} ${config.text} ${config.border} border`}>
            {config.label}
          </span>
        </div>

        {riskFlags.sanctions_data_unknown && (
          <div className="mb-4 p-3 bg-gray-100 rounded-lg">
            <p className="text-sm text-gray-600">
              ⚠️ Sanctions data unavailable. Risk assessment may be incomplete.
            </p>
          </div>
        )}

        <div className="space-y-3">
          {riskFlags.has_sanctioned_exposure && (
            <div className="flex items-center p-2 bg-red-100 rounded">
              <AlertTriangle className="text-red-600 mr-2" size={16} />
              <span className="text-sm font-semibold text-red-800">Sanctioned Entity Exposure</span>
            </div>
          )}

          {riskFlags.has_mixer_exposure && (
            <div className="flex items-center p-2 bg-yellow-100 rounded">
              <AlertCircle className="text-yellow-600 mr-2" size={16} />
              <span className="text-sm font-semibold text-yellow-800">Mixer Exposure</span>
            </div>
          )}

          {riskFlags.has_watchlist_exposure && (
            <div className="flex items-center p-2 bg-orange-100 rounded">
              <AlertCircle className="text-orange-600 mr-2" size={16} />
              <span className="text-sm font-semibold text-orange-800">Watchlist Exposure</span>
            </div>
          )}

          {riskLevel === "low" && !riskFlags.sanctions_data_unknown && (
            <div className="flex items-center p-2 bg-green-100 rounded">
              <CheckCircle className="text-green-600 mr-2" size={16} />
              <span className="text-sm font-semibold text-green-800">No Known Risk Factors</span>
            </div>
          )}
        </div>

        {riskFlags.flags.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Risk Flags</p>
            <div className="flex flex-wrap gap-2">
              {riskFlags.flags.map((flag, index) => (
                <span
                  key={index}
                  className="px-2 py-1 text-xs rounded-md bg-gray-200 text-gray-700"
                >
                  {flag.replace(/_/g, " ")}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}


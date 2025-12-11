import React from "react";
import { ProtocolSafetyCheck } from "../../interfaces/Protocol";
import { Shield, AlertTriangle, CheckCircle, AlertCircle, HelpCircle, TrendingUp, TrendingDown } from "lucide-react";

interface ProtocolSafetyCardProps {
  safetyCheck: ProtocolSafetyCheck;
}

export default function ProtocolSafetyCard({ safetyCheck }: ProtocolSafetyCardProps): JSX.Element {
  const getQualityConfig = (quality: string) => {
    switch (quality) {
      case "excellent":
        return {
          bg: "bg-green-50",
          border: "border-green-300",
          text: "text-green-800",
          icon: CheckCircle,
          label: "Excellent",
          badgeColor: "bg-green-500",
        };
      case "good":
        return {
          bg: "bg-blue-50",
          border: "border-blue-300",
          text: "text-blue-800",
          icon: Shield,
          label: "Good",
          badgeColor: "bg-blue-500",
        };
      case "fair":
        return {
          bg: "bg-yellow-50",
          border: "border-yellow-300",
          text: "text-yellow-800",
          icon: AlertCircle,
          label: "Fair",
          badgeColor: "bg-yellow-500",
        };
      case "poor":
        return {
          bg: "bg-orange-50",
          border: "border-orange-300",
          text: "text-orange-800",
          icon: AlertTriangle,
          label: "Poor",
          badgeColor: "bg-orange-500",
        };
      default:
        return {
          bg: "bg-gray-50",
          border: "border-gray-300",
          text: "text-gray-800",
          icon: HelpCircle,
          label: "Unknown",
          badgeColor: "bg-gray-500",
        };
    }
  };

  const config = getQualityConfig(safetyCheck.quality);
  const Icon = config.icon;

  const scorePercentage = Math.round(safetyCheck.protocol_score * 100);
  const confidencePercentage = Math.round(safetyCheck.confidence * 100);

  return (
    <div className={`max-w-2xl mx-auto bg-white shadow rounded-xl overflow-hidden mb-6 ${config.bg} ${config.border} border-2`}>
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <Icon className={`${config.text} mr-2`} size={28} />
            <h3 className={`text-xl font-bold ${config.text}`}>Protocol Safety Assessment</h3>
          </div>
          <span className={`px-4 py-2 rounded-full text-sm font-semibold text-white ${config.badgeColor}`}>
            {config.label}
          </span>
        </div>

        {/* Protocol Info */}
        {safetyCheck.protocol && (
          <div className="mb-4 p-4 bg-white rounded-lg border border-gray-200">
            <h4 className="font-semibold text-gray-800 mb-2">{safetyCheck.protocol.name}</h4>
            <div className="flex flex-wrap gap-2 text-sm text-gray-600">
              {safetyCheck.protocol.category && (
                <span className="px-2 py-1 bg-gray-100 rounded">Category: {safetyCheck.protocol.category}</span>
              )}
              {safetyCheck.protocol.chain && (
                <span className="px-2 py-1 bg-gray-100 rounded">Chain: {safetyCheck.protocol.chain}</span>
              )}
            </div>
          </div>
        )}

        {/* Score Display */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-semibold text-gray-700">Protocol Score</span>
            <span className={`text-lg font-bold ${config.text}`}>{scorePercentage}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className={`h-3 rounded-full ${config.badgeColor}`}
              style={{ width: `${scorePercentage}%` }}
            />
          </div>
        </div>

        {/* Confidence */}
        {safetyCheck.confidence > 0 && (
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-semibold text-gray-700">Confidence</span>
              <span className="text-sm text-gray-600">{confidencePercentage}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="h-2 rounded-full bg-gray-400"
                style={{ width: `${confidencePercentage}%` }}
              />
            </div>
          </div>
        )}

        {/* Rewards/Penalties */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          {safetyCheck.reward_multiplier > 1.0 && (
            <div className="p-3 bg-green-100 rounded-lg">
              <div className="flex items-center text-green-800">
                <TrendingUp className="mr-2" size={18} />
                <span className="text-sm font-semibold">Reward Multiplier</span>
              </div>
              <div className="text-lg font-bold text-green-900 mt-1">
                {safetyCheck.reward_multiplier}x
              </div>
            </div>
          )}
          {safetyCheck.penalty_fee > 0 && (
            <div className="p-3 bg-red-100 rounded-lg">
              <div className="flex items-center text-red-800">
                <TrendingDown className="mr-2" size={18} />
                <span className="text-sm font-semibold">Penalty Fee</span>
              </div>
              <div className="text-lg font-bold text-red-900 mt-1">
                +{Math.round(safetyCheck.penalty_fee * 100)}%
              </div>
            </div>
          )}
        </div>

        {/* Messages */}
        {safetyCheck.message && (
          <div className="mb-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-800">{safetyCheck.message}</p>
          </div>
        )}

        {safetyCheck.warning && (
          <div className="mb-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex items-start">
              <AlertTriangle className="text-yellow-600 mr-2 mt-0.5" size={18} />
              <p className="text-sm text-yellow-800">{safetyCheck.warning}</p>
            </div>
          </div>
        )}

        {/* Details */}
        {safetyCheck.details && Object.keys(safetyCheck.details).length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <h4 className="text-sm font-semibold text-gray-700 mb-2">Details</h4>
            <div className="grid grid-cols-2 gap-2 text-sm text-gray-600">
              {safetyCheck.details.tvl !== undefined && (
                <div>
                  <span className="font-medium">TVL: </span>
                  <span>${(safetyCheck.details.tvl / 1e9).toFixed(2)}B</span>
                </div>
              )}
              {safetyCheck.details.age_days !== undefined && (
                <div>
                  <span className="font-medium">Age: </span>
                  <span>{Math.floor(safetyCheck.details.age_days / 365)} years</span>
                </div>
              )}
              {safetyCheck.details.audit_count !== undefined && (
                <div>
                  <span className="font-medium">Audits: </span>
                  <span>{safetyCheck.details.audit_count}</span>
                </div>
              )}
              {safetyCheck.details.incident_count !== undefined && (
                <div>
                  <span className="font-medium">Incidents: </span>
                  <span>{safetyCheck.details.incident_count}</span>
                </div>
              )}
              {safetyCheck.details.bounty_present !== undefined && (
                <div className="col-span-2">
                  <span className="font-medium">Bug Bounty: </span>
                  <span>{safetyCheck.details.bounty_present ? "Yes" : "No"}</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

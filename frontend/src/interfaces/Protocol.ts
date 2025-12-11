/** Protocol Reputation System TypeScript Interfaces */

export interface ProtocolIncident {
  date: string;
  description: string;
  amount_lost_usd: number | null;
  severity: "critical" | "high" | "medium" | "low";
  source: string | null;
}

export interface ProtocolRegistry {
  protocol_id: string;
  name: string;
  slug: string | null;
  category: string | null;
  chain: string | null;
  contract_addresses: string[];
  tvl: number;
  tvl_normalized: number;
  age_days: number;
  longevity_score: number;
  launch_date: string | null;
  audit_score: number;
  audit_count: number;
  audit_firms: string[];
  last_audit_date: string | null;
  bounty_present: boolean;
  incidents: ProtocolIncident[];
  incident_penalty: number;
  l2_risk_score: number;
  l2_technology: string | null;
  protocol_score: number;
  quality: "excellent" | "good" | "fair" | "poor" | "unknown";
  confidence: number;
  last_updated: number | null;
  data_sources: string[];
}

export interface ProtocolSafetyCheck {
  contract_address: string;
  protocol: {
    protocol_id: string;
    name: string;
    category: string | null;
    chain: string | null;
  } | null;
  protocol_score: number;
  quality: "excellent" | "good" | "fair" | "poor" | "unknown";
  safe: boolean;
  reward_multiplier: number;
  penalty_fee: number;
  warning: string | null;
  message: string | null;
  confidence: number;
  details: {
    tvl?: number;
    age_days?: number;
    audit_count?: number;
    incident_count?: number;
    bounty_present?: boolean;
  };
}

export interface ProtocolListResponse {
  success: boolean;
  data: Array<{
    protocol_id: string;
    name: string;
    category: string | null;
    chain: string | null;
    tvl: number;
    protocol_score: number;
    quality: string;
    confidence: number;
  }>;
  count: number;
}

export interface ProtocolCheckResponse {
  success: boolean;
  data: ProtocolSafetyCheck;
}

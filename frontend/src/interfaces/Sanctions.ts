export interface IAddressLabel {
  address: string;
  chain: string;
  label: string | null;
  program?: string;
  source?: string;
  first_seen?: number;
  metadata?: Record<string, any>;
  is_blacklisted?: boolean;
}

export interface IExposureMetrics {
  address: string;
  chain: string;
  direct_blacklist_hits_30: number;
  direct_blacklist_hits_90: number;
  direct_blacklist_hits_all: number;
  direct_blacklist_value_30: number;
  direct_blacklist_value_90: number;
  direct_blacklist_value_all: number;
  mixer_tx_share_7: number;
  mixer_tx_share_30: number;
  mixer_tx_share_90: number;
  indirect_exposure_1_hop?: number | null;
  indirect_exposure_2_hops?: number | null;
  indirect_exposure_3_hops?: number | null;
  clean_tx_ratio: number;
  sanctions_data_unknown: boolean;
  confidence: number;
  last_updated?: number;
}

export interface IRiskFlags {
  has_sanctioned_exposure: boolean;
  has_mixer_exposure: boolean;
  has_watchlist_exposure: boolean;
  sanctions_data_unknown: boolean;
  flags: string[];
}

export interface ISanctionsCheckResponse {
  success: boolean;
  data: IAddressLabel;
}

export interface ISanctionsMetricsResponse {
  success: boolean;
  data: IExposureMetrics | { message?: string };
}

export interface IRiskFlagsResponse {
  success: boolean;
  data: IRiskFlags;
}


"""Protocol scoring calculator based on comprehensive factors."""
import math
import numpy as np
from typing import Optional, List, Dict, Any
from datetime import datetime
from service.models import ProtocolRegistry
from service.utils import logger

# Scoring weights (as per deepseek specification)
SCORING_WEIGHTS = {
    'tvl_score': 0.25,           # Total Value Locked
    'longevity_score': 0.20,     # Time since listing
    'growth_stability_score': 0.15,  # Consistent growth
    'multi_chain_score': 0.15,   # Multi-chain presence
    'audit_score': 0.10,         # Audit status
    'category_safety_score': 0.10,  # Protocol category risk
    'concentration_score': 0.05, # TVL concentration across chains
}

# Category risk levels (higher = safer)
CATEGORY_RISK_LEVELS = {
    'Dexes': 0.9,                # Lower risk
    'Lending': 0.8,
    'Yield': 0.7,
    'CDP': 0.6,
    'Liquid Staking': 0.9,
    'RWA': 0.5,
    'Derivatives': 0.4,          # Higher risk
    'Yield Aggregator': 0.5,
    'Cross Chain': 0.6,
    'Insurance': 0.8,
    'Gaming': 0.3,
    'NFT Marketplace': 0.4,
    'Options': 0.4,
    'Farm': 0.3,
    'Algo-Stables': 0.2,         # Highest risk
    'Bridge': 0.7,
    'DEX': 0.9,  # Alternative naming
    'Lending': 0.8,
}

MIN_SAFE_TVL = 1000000  # $1M minimum for established protocols
MIN_LONGEVITY_DAYS = 180  # 6 months minimum


class ProtocolScoringCalculator:
    """Calculates protocol reputation scores based on comprehensive factors."""
    
    def __init__(self):
        self.tvl_history_cache = {}  # Cache for TVL history
    
    def calculate_tvl_score(self, current_tvl: float) -> float:
        """
        Score based on TVL size (logarithmic scaling).
        Scale: $1k = 0.1, $1M = 0.5, $100M = 0.8, $1B = 1.0
        """
        if current_tvl < 1000:  # Less than $1k
            return 0.0
        
        # Logarithmic scaling: log10(TVL) with caps
        log_tvl = math.log10(max(current_tvl, 1000))
        
        # Scale: $1k = 0.1, $1M = 0.5, $100M = 0.8, $1B = 1.0
        if log_tvl >= 9:  # $1B+
            return 1.0
        elif log_tvl >= 8:  # $100M - $1B
            return 0.7 + (log_tvl - 8) * 0.3
        elif log_tvl >= 6:  # $1M - $100M
            return 0.4 + (log_tvl - 6) * 0.15
        elif log_tvl >= 3:  # $1k - $1M
            return 0.1 + (log_tvl - 3) * 0.1
        else:
            return 0.0
    
    def calculate_longevity_score(self, listed_at_timestamp: Optional[int] = None, age_days: Optional[int] = None) -> float:
        """
        Score based on how long protocol has been tracked.
        """
        if age_days is not None and age_days > 0:
            days_since_listing = age_days
        elif listed_at_timestamp:
            listed_date = datetime.fromtimestamp(listed_at_timestamp)
            days_since_listing = (datetime.now() - listed_date).days
        else:
            return 0.3  # Unknown listing date
        
        if days_since_listing >= 365:  # 1+ years
            return 1.0
        elif days_since_listing >= 180:  # 6-12 months
            return 0.7 + (days_since_listing - 180) / 185 * 0.3
        elif days_since_listing >= 90:  # 3-6 months
            return 0.4 + (days_since_listing - 90) / 90 * 0.3
        elif days_since_listing >= 30:  # 1-3 months
            return 0.2 + (days_since_listing - 30) / 60 * 0.2
        else:
            return 0.1
    
    def calculate_growth_stability_score(self, tvl_history: List[Dict[str, Any]]) -> float:
        """
        Score based on TVL growth stability.
        Requires TVL history data.
        """
        if not tvl_history or len(tvl_history) < 30:  # Not enough history
            return 0.3
        
        # Convert to daily changes
        tvl_values = []
        for entry in tvl_history[-90:]:  # Last 90 days
            if isinstance(entry, dict):
                tvl = entry.get('totalLiquidityUSD') or entry.get('tvl') or 0
            else:
                tvl = float(entry) if entry else 0
            if tvl > 0:
                tvl_values.append(tvl)
        
        if len(tvl_values) < 7:
            return 0.3
        
        # Calculate daily percentage changes
        changes = []
        for i in range(1, len(tvl_values)):
            if tvl_values[i-1] > 0:
                change = (tvl_values[i] - tvl_values[i-1]) / tvl_values[i-1]
                changes.append(change)
        
        if not changes:
            return 0.5
        
        # Calculate volatility (standard deviation of daily changes)
        try:
            volatility = np.std(changes) if len(changes) > 1 else 0.0
        except:
            volatility = 0.0
        
        # Calculate positive growth ratio
        positive_days = sum(1 for change in changes if change > 0)
        growth_ratio = positive_days / len(changes) if changes else 0.0
        
        # Low volatility and consistent growth gets high score
        if volatility < 0.05 and growth_ratio > 0.6:  # <5% daily volatility, >60% positive days
            return 1.0
        elif volatility < 0.1 and growth_ratio > 0.5:
            return 0.8
        elif volatility < 0.2:
            return 0.6
        else:
            return 0.3
    
    def calculate_multi_chain_score(self, chains: List[str]) -> float:
        """
        Score based on multi-chain presence.
        """
        if not chains:
            return 0.1
        
        chain_count = len(chains)
        
        # High weight for Ethereum/L2s presence
        established_chains = {'Ethereum', 'Arbitrum', 'Optimism', 'Polygon', 'Base', 'Avalanche', 'BNB', 'BSC'}
        present_established = len([c for c in chains if c in established_chains])
        
        if chain_count >= 5 and present_established >= 3:
            return 1.0
        elif chain_count >= 3 and present_established >= 2:
            return 0.8
        elif chain_count >= 2 and 'Ethereum' in chains:
            return 0.6
        elif chain_count >= 2:
            return 0.4
        elif chain_count == 1 and chains[0] in established_chains:
            return 0.3
        else:
            return 0.1
    
    def calculate_audit_score(self, audit_count: int, audit_firms: List[str], 
                             last_audit_date: Optional[str] = None) -> float:
        """
        Score based on audit information.
        """
        # Check for audit mentions
        has_audits = audit_count > 0
        
        # Check for major auditor mentions
        major_auditors = ['certik', 'quantstamp', 'trail of bits', 'consensys diligence', 'halborn', 
                         'openzeppelin', 'least authority', 'slowmist', 'peckshield', 'chainsecurity']
        has_major_auditor = False
        if audit_firms:
            for firm in audit_firms:
                if any(auditor in str(firm).lower() for auditor in major_auditors):
                    has_major_auditor = True
                    break
        
        if has_major_auditor and audit_count >= 2:
            return 1.0
        elif has_major_auditor:
            return 0.8
        elif has_audits:
            return 0.6
        else:
            return 0.2
    
    def calculate_category_safety_score(self, category: Optional[str]) -> float:
        """
        Score based on protocol category risk.
        """
        if not category:
            return 0.5  # Default neutral
        
        # Try exact match first
        score = CATEGORY_RISK_LEVELS.get(category, None)
        if score is not None:
            return score
        
        # Try case-insensitive match
        category_lower = category.lower()
        for cat, risk_score in CATEGORY_RISK_LEVELS.items():
            if cat.lower() == category_lower:
                return risk_score
        
        # Default for unknown categories
        return 0.5
    
    def calculate_concentration_score(self, chain_tvls: Dict[str, float]) -> float:
        """
        Score based on TVL concentration across chains.
        Lower concentration (more diversification) = higher score.
        """
        if not chain_tvls or len(chain_tvls) == 1:
            return 0.3  # Single chain or no data
        
        total_tvl = sum(chain_tvls.values())
        if total_tvl == 0:
            return 0.3
        
        # Calculate Herfindahl-Hirschman Index (HHI) for concentration
        market_shares = [tvl / total_tvl for tvl in chain_tvls.values()]
        hhi = sum(share ** 2 for share in market_shares)
        
        # Convert HHI to score: lower concentration (more diversification) = higher score
        if hhi < 0.25:  # Highly diversified
            return 1.0
        elif hhi < 0.5:
            return 0.8
        elif hhi < 0.75:
            return 0.5
        else:
            return 0.3
    
    def calculate_risk_flags(self, protocol: ProtocolRegistry) -> List[str]:
        """
        Identify specific risk flags.
        """
        flags = []
        
        # TVL too low
        if protocol.tvl < 100000:
            flags.append("LOW_TVL")
        
        # New protocol
        if protocol.age_days > 0 and protocol.age_days < 30:
            flags.append("NEW_PROTOCOL")
        elif protocol.age_days == 0:
            flags.append("UNKNOWN_AGE")
        
        # High-risk category
        category = protocol.category or ''
        if category in ['Algo-Stables', 'Farm', 'Gaming']:
            flags.append("HIGH_RISK_CATEGORY")
        
        # Single chain (if we have chain info)
        # Note: This would need chain data from protocol
        
        # No audits
        if protocol.audit_count == 0:
            flags.append("NO_AUDITS")
        
        # Has incidents
        if protocol.incidents and len(protocol.incidents) > 0:
            flags.append("HAS_INCIDENTS")
        
        return flags
    
    def calculate_protocol_score(self, protocol: ProtocolRegistry, tvl_history: Optional[List[Dict[str, Any]]] = None) -> ProtocolRegistry:
        """
        Calculate overall protocol quality score using comprehensive factors.
        """
        # Individual scores
        tvl_score = self.calculate_tvl_score(protocol.tvl)
        protocol.tvl_normalized = tvl_score
        
        longevity_score = self.calculate_longevity_score(
            listed_at_timestamp=None, 
            age_days=protocol.age_days
        )
        protocol.longevity_score = longevity_score
        
        # Growth stability (requires TVL history)
        growth_stability_score = self.calculate_growth_stability_score(tvl_history or [])
        
        # Multi-chain score
        chains = getattr(protocol, 'chains', []) or []
        if not chains and protocol.chain:
            chains = [protocol.chain]
        multi_chain_score = self.calculate_multi_chain_score(chains)
        
        audit_score = self.calculate_audit_score(
            protocol.audit_count,
            protocol.audit_firms,
            protocol.last_audit_date
        )
        protocol.audit_score = audit_score
        
        category_safety_score = self.calculate_category_safety_score(protocol.category)
        
        # Concentration score (would need chain TVL breakdown)
        concentration_score = 0.3  # Default
        # TODO: Extract chain TVL breakdown if available
        
        # Weighted composite score
        composite_score = (
            SCORING_WEIGHTS['tvl_score'] * tvl_score +
            SCORING_WEIGHTS['longevity_score'] * longevity_score +
            SCORING_WEIGHTS['growth_stability_score'] * growth_stability_score +
            SCORING_WEIGHTS['multi_chain_score'] * multi_chain_score +
            SCORING_WEIGHTS['audit_score'] * audit_score +
            SCORING_WEIGHTS['category_safety_score'] * category_safety_score +
            SCORING_WEIGHTS['concentration_score'] * concentration_score
        )
        
        # Apply risk penalties
        risk_flags = self.calculate_risk_flags(protocol)
        penalty_multiplier = 1.0 - (len(risk_flags) * 0.05)  # 5% penalty per flag
        final_score = max(0.0, min(1.0, composite_score * penalty_multiplier))
        
        # Apply incident penalty
        if protocol.incidents:
            incident_penalty = self.calculate_incident_penalty(protocol.incidents)
            protocol.incident_penalty = incident_penalty
            final_score = max(0.0, final_score - (incident_penalty * 0.2))  # 20% max penalty
        else:
            protocol.incident_penalty = 0.0
        
        # Apply L2 risk penalty if available
        if protocol.l2_risk_score:
            final_score = max(0.0, final_score - (protocol.l2_risk_score * 0.1))  # 10% max penalty
        
        protocol.protocol_score = max(0.0, min(1.0, final_score))
        
        # Calculate confidence
        protocol.confidence = self.calculate_confidence(protocol)
        
        # Set last updated timestamp
        protocol.last_updated = int(datetime.now().timestamp())
        
        return protocol
    
    def calculate_incident_penalty(self, incidents: List) -> float:
        """
        Calculate penalty score based on past incidents/hacks.
        Returns 0-1, where 1 is maximum penalty.
        """
        if not incidents:
            return 0.0
        
        total_penalty = 0.0
        
        for incident in incidents:
            # Base penalty based on severity
            severity_weights = {
                "critical": 0.5,
                "high": 0.3,
                "medium": 0.15,
                "low": 0.05
            }
            
            severity = incident.severity if hasattr(incident, 'severity') else "medium"
            base_penalty = severity_weights.get(severity.lower(), 0.15)
            
            # Additional penalty for large losses (>$1M)
            amount = incident.amount_lost_usd if hasattr(incident, 'amount_lost_usd') else 0
            if amount and amount > 1000000:
                base_penalty *= 1.5
            
            total_penalty += base_penalty
        
        # Cap at 1.0 and apply diminishing returns for multiple incidents
        penalty = min(1.0, total_penalty)
        # Diminishing returns: 2 incidents = 0.8x, 3+ = 0.6x
        if len(incidents) >= 3:
            penalty *= 0.6
        elif len(incidents) >= 2:
            penalty *= 0.8
        
        return penalty
    
    def calculate_confidence(self, protocol: ProtocolRegistry) -> float:
        """
        Calculate confidence score (0-1) based on data availability.
        """
        confidence = 0.0
        
        # TVL data available
        if protocol.tvl > 0:
            confidence += 0.3
        
        # Age data available
        if protocol.age_days > 0:
            confidence += 0.2
        
        # Audit data available
        if protocol.audit_count > 0:
            confidence += 0.2
        
        # Incident data available (even if empty, it's data)
        if protocol.incidents is not None:
            confidence += 0.1
        
        # L2 risk data available
        if protocol.l2_risk_score is not None:
            confidence += 0.1
        
        # Data sources count
        if len(protocol.data_sources) > 1:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def get_protocol_quality(self, score: float) -> str:
        """Get quality classification from score."""
        if score >= 0.8:
            return "excellent"
        elif score >= 0.6:
            return "good"
        elif score >= 0.4:
            return "fair"
        elif score > 0.0:
            return "poor"
        else:
            return "unknown"

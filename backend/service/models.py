from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class PrevOut(BaseModel):
    """Previous output data structure"""
    spent: Optional[bool] = False
    tx_index: Optional[int] = 0
    type: Optional[int] = 0
    addr: Optional[str] = ""
    value: Optional[int] = 0
    n: Optional[int] = 0
    script: Optional[str] = ""

class Input(BaseModel):
    """Transaction input data structure"""
    sequence: Optional[int] = 0
    script: Optional[str] = ""
    prev_out: PrevOut
    witness: Optional[str] = ""
    index: Optional[int] = 0

class Out(BaseModel):
    """Transaction output data structure"""
    spent: Optional[bool] = False
    tx_index: Optional[int] = 0
    type: Optional[int] = 0
    addr: Optional[str] = ""
    value: Optional[int] = 0
    n: Optional[int] = 0
    script: Optional[str] = ""

class Tx(BaseModel):
    """Bitcoin transaction data structure"""
    balance: int
    result: int
    ver: int
    size: int
    inputs: List[Input]
    time: int
    weight: int
    fee: int
    lock_time: int
    double_spend: bool
    block_index: int
    block_height: int
    tx_index: int
    vin_sz: int
    hash: str
    vout_sz: int
    relayed_by: str
    out: List[Out]

class TxDTO(BaseModel):
    """ Transaction Data Structure which will be consumed in the frontend """
    balance: float
    result: float
    time: int
    hash: str
    fee: int
    inputs: List[Input]
    outputs: List[Out]

class Address(BaseModel):
    """Bitcoin address data structure"""
    hash160: str
    address: str
    n_tx: int
    total_received: int
    total_sent: int
    final_balance: int
    txs: List[Tx]

class AddressDTO(BaseModel):
    """Bitcoin address data structure"""
    hash160: Optional[str] = ""
    token: Optional[str] = ""
    address: Optional[str] = ""
    n_tx: Optional[int] = 0
    total_received: Optional[int] = 0
    total_sent: Optional[int] = 0
    final_balance: Optional[float] = 0
    txs: Optional[List[TxDTO]]=[]



class ETHAddressSummary(BaseModel):
    """Ethereum address summary data structure"""
    hash: str
    nonce: str
    balance: float
    transactionCount: int
    internalTransactionCount: int
    totalSent: float
    totalReceived: float
    totalFees: float
    lastUpdatedAtNumber: str
    tokenTransferCount: str
    
class ETHAddress(BaseModel):
    """ Ethereum Address Data Structure """
    hash: str
    blockHash: str
    blockNumber: str
    to: str
    from_address: str = Field(..., alias="from")
    value: int
    nonce: int
    gasPrice: int
    gasLimit: int
    gasUsed: int
    data: str
    transactionIndex: int
    success: bool
    state: str
    timestamp: int
    internalTransactions: List[str]

class ETHAddressDTO(BaseModel):
    """ Ethereum Address Data Structure which will be consumed in frontend """
    hash: str
    success: bool
    state: str
    time: int
    blockNumber: str
    src: str
    dst: str
    amount: float
    fee: float

class ETHResponse(BaseModel):
    """Full Ethereum address response with transactions"""
    transactions: List[ETHAddressDTO]
    token: str
    page: str
    size: int

class BNBTransactionDTO(BaseModel):
    blockNumber: Optional[str] = ""
    blockHash: Optional[str] = ""
    time: Optional[str] = ""
    hash: Optional[str] = ""
    transactionIndex: Optional[str] = ""
    src: Optional[str] = ""
    dst: Optional[str] = ""
    value: Optional[str] = ""
    gas: Optional[str] = ""
    gasPrice: Optional[str] = ""
    input: Optional[str] = ""
    contractAddress: Optional[str] = ""
    gasUsed: Optional[str] = ""
    isError: Optional[str] = ""
    
    
    
class SOLTransfer(BaseModel):
    fromUserAccount: str
    toUserAccount: str
    amount: float
    
class SOLTransactionDTO(BaseModel):
    """Data transfer object for Solana transactions."""
    description: str
    direction: str
    type: str
    source: str
    fee: int
    feePayer: str
    signature: str
    slot: float
    timestamp: float
    nativeTransfers: List[SOLTransfer]
class SOLResponse(BaseModel):
    """Response model for Solana address transactions."""
    transactions: List[SOLTransactionDTO]
    token: str
    page: int
    size: int

class SOLAddressSummary(BaseModel):
    """Summary model for Solana address."""
    address: str
    price: float
    balance: float
    balanceLamports: int
    transactionCount: int
    executable: bool
    owner: str


# Sanctions and Mixer Detection Models
class AddressLabel(BaseModel):
    """Address label model for sanctions, mixers, and watchlists."""
    address: str
    chain: str  # 'BTC', 'ETH', 'BNB', 'SOL', etc.
    label: str  # 'sanctioned', 'mixer', 'watchlist'
    program: Optional[str] = None  # e.g., 'OFAC', 'Tornado Cash'
    first_seen: Optional[int] = None  # Unix timestamp
    source: Optional[str] = None  # Source of the label
    metadata: Optional[dict] = None  # Additional metadata


class ExposureMetrics(BaseModel):
    """Exposure metrics for a wallet address."""
    address: str
    chain: str
    direct_blacklist_hits_30: int = 0
    direct_blacklist_hits_90: int = 0
    direct_blacklist_hits_all: int = 0
    direct_blacklist_value_30: float = 0.0  # USD value
    direct_blacklist_value_90: float = 0.0
    direct_blacklist_value_all: float = 0.0
    mixer_tx_share_7: float = 0.0  # Percentage
    mixer_tx_share_30: float = 0.0
    mixer_tx_share_90: float = 0.0
    indirect_exposure_1_hop: Optional[int] = None
    indirect_exposure_2_hops: Optional[int] = None
    indirect_exposure_3_hops: Optional[int] = None
    clean_tx_ratio: float = 0.90  # Default neutral-conservative
    sanctions_data_unknown: bool = False
    confidence: float = 0.0  # Will be adjusted by -0.15 if data unknown
    last_updated: Optional[int] = None  # Unix timestamp


class RiskFlags(BaseModel):
    """Risk flags for an address."""
    has_sanctioned_exposure: bool = False
    has_mixer_exposure: bool = False
    has_watchlist_exposure: bool = False
    sanctions_data_unknown: bool = False
    flags: List[str] = []  # List of specific risk flags


# Protocol Reputation System Models
class ProtocolIncident(BaseModel):
    """Incident/hack information for a protocol."""
    date: str  # ISO date string
    description: str
    amount_lost_usd: Optional[float] = None
    severity: str  # 'critical', 'high', 'medium', 'low'
    source: Optional[str] = None


class ProtocolRegistry(BaseModel):
    """Protocol registry entry with reputation score."""
    protocol_id: str  # Unique identifier (e.g., "uniswap", "aave")
    name: str  # Display name (e.g., "Uniswap V3")
    slug: Optional[str] = None  # DeFiLlama slug
    category: Optional[str] = None  # "DEX", "Lending", "Yield", etc.
    chain: Optional[str] = None  # "Ethereum", "Arbitrum", etc. (primary chain)
    chains: List[str] = []  # List of all chains the protocol operates on
    
    # Contract addresses
    contract_addresses: List[str] = []  # List of contract addresses
    
    # Data from sources
    tvl: float = 0.0  # Total Value Locked in USD
    tvl_normalized: float = 0.0  # 0-1 score based on TVL
    age_days: int = 0  # How old the protocol is
    longevity_score: float = 0.0  # 0-1 based on age
    launch_date: Optional[str] = None  # ISO date string
    
    # Audit and security
    audit_score: float = 0.0  # 0-1 based on audits
    audit_count: int = 0
    audit_firms: List[str] = []  # List of audit firm names
    last_audit_date: Optional[str] = None
    bounty_present: bool = False  # Has bug bounty program?
    
    # Incidents
    incidents: List[ProtocolIncident] = []
    incident_penalty: float = 0.0  # 0-1 penalty score
    
    # Layer 2 risk
    l2_risk_score: float = 0.0  # 0-1 risk from L2BEAT
    l2_technology: Optional[str] = None  # L2 technology type
    
    # Final scores
    protocol_score: float = 0.5  # 0-1 final protocol score (default 0.5 for unknown)
    confidence: float = 0.0  # Confidence in the score (0-1)
    
    # Metadata
    last_updated: Optional[int] = None  # Unix timestamp
    data_sources: List[str] = []  # Which sources provided data


class ProtocolQuality(str, Enum):
    """Protocol quality classification."""
    EXCELLENT = "excellent"  # score >= 0.8
    GOOD = "good"  # score >= 0.6
    FAIR = "fair"  # score >= 0.4
    POOR = "poor"  # score < 0.4
    UNKNOWN = "unknown"  # no data or score = 0.5


class ProtocolSafetyCheck(BaseModel):
    """Result of checking a contract address against protocol registry."""
    contract_address: str
    protocol: Optional[ProtocolRegistry] = None
    protocol_score: float = 0.5  # Default neutral for unknown
    quality: str = "unknown"
    safe: bool = True  # True if score >= 0.5
    reward_multiplier: float = 1.0  # Multiplier for rewards
    penalty_fee: float = 0.0  # Extra fee percentage if risky
    warning: Optional[str] = None
    message: Optional[str] = None
    confidence: float = 0.0
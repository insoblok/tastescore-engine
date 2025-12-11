# Protocol Reputation System

## Overview

The Protocol Reputation System provides a safety scoring mechanism for DeFi protocols, similar to a "credit score" for crypto protocols. It helps users identify safe, established protocols and avoid risky or unknown ones.

## Architecture

### Backend Components

1. **Data Models** (`service/models.py`)
   - `ProtocolRegistry`: Main model storing protocol data and scores
   - `ProtocolIncident`: Tracks hacks/exploits
   - `ProtocolSafetyCheck`: Result of checking a contract address

2. **Data Fetchers**
   - `DeFiLlamaFetcher` (`service/protocols/defillama_fetcher.py`): Fetches TVL, age, and basic protocol data
   - `L2BEATFetcher` (`service/protocols/l2beat_fetcher.py`): Fetches Layer 2 risk assessments

3. **Scoring Calculator** (`service/protocols/scoring_calculator.py`)
   - Implements the weighted scoring formula
   - Calculates component scores (TVL, longevity, audits, etc.)

4. **Sync Job** (`service/protocols/protocol_sync.py`)
   - Nightly job to fetch and update protocol data
   - Runs at 3 AM UTC (after OFAC ingestion)

5. **API Endpoints** (`routers/protocols.py`)
   - `GET /api/protocols/check`: Check contract address safety
   - `GET /api/protocols/{protocol_id}`: Get protocol details
   - `GET /api/protocols/`: List all protocols
   - `POST /api/protocols/sync`: Manually trigger sync

### Frontend Components

1. **Interfaces** (`interfaces/Protocol.ts`)
   - TypeScript types for protocol data

2. **Hooks** (`hooks/useProtocol.ts`)
   - `useProtocolCheck`: Hook for checking contract addresses
   - `useProtocolList`: Hook for listing protocols

3. **Components**
   - `ProtocolSafetyCard`: Displays safety assessment with score, quality, rewards/penalties

4. **Pages**
   - `ProtocolChecker`: Main page for checking contract addresses
   - Accessible at `/protocol-checker`

## Scoring Formula

```
Score = 35% TVL + 25% Longevity + 20% Audits + 10% Bounty
        - 20% Incident Penalty - 10% L2 Risk
```

### Component Details

- **TVL Score (35%)**: Normalized based on category thresholds, logarithmic scaling
- **Longevity Score (25%)**: Based on protocol age (1 year = 1.0)
- **Audit Score (20%)**: Based on audit count, reputable firms, and recency
- **Bounty Score (10%)**: Binary (1.0 if present, 0.0 if not)
- **Incident Penalty (20%)**: Based on severity and amount lost
- **L2 Risk Penalty (10%)**: From L2BEAT risk assessment

### Quality Classifications

- **Excellent**: score ≥ 0.8 → 1.5x reward multiplier
- **Good**: score ≥ 0.6 → 1.2x reward multiplier
- **Fair**: score ≥ 0.4 → 1.0x reward multiplier
- **Poor**: score < 0.4 → 5-10% penalty fee
- **Unknown**: no data → neutral 0.5 score

## Database Schema

Protocols are stored in Firestore `protocol_registry` collection with the following fields:

- `protocol_id`: Unique identifier
- `name`, `slug`, `category`, `chain`
- `contract_addresses`: Array of contract addresses
- `tvl`, `tvl_normalized`
- `age_days`, `longevity_score`
- `audit_score`, `audit_count`, `audit_firms`
- `bounty_present`
- `incidents`: Array of incident objects
- `incident_penalty`
- `l2_risk_score`
- `protocol_score`: Final score (0-1)
- `confidence`: Confidence in score (0-1)
- `last_updated`: Timestamp
- `data_sources`: Array of source names

## Usage

### Checking a Contract Address

```python
# Backend
GET /api/protocols/check?contract_address=0x...&chain=ETH

# Frontend
const { data, checkProtocol } = useProtocolCheck();
await checkProtocol("0x...", "ETH");
```

### Manual Sync

```python
# Sync all protocols
POST /api/protocols/sync

# Sync specific protocol
POST /api/protocols/sync?protocol_slug=uniswap
```

## Scheduled Jobs

- **Protocol Sync**: Runs nightly at 3 AM UTC
- Fetches all protocols from DeFiLlama
- Calculates scores and saves to database
- Updates L2 risk scores from L2BEAT

## Future Enhancements

1. **DeFiSafety Integration**: Add paid audit data (requires API key)
2. **Rekt.news Integration**: Automated incident tracking
3. **Contract Address Mapping**: Better contract-to-protocol identification
4. **Historical Score Tracking**: Track score changes over time
5. **User Notifications**: Alert users when protocol scores change significantly

## Configuration

No additional environment variables required. The system uses public APIs:
- DeFiLlama: https://api.llama.fi (free, public)
- L2BEAT: https://api.l2beat.com (free, public)

## Testing

To test the system:

1. **Manual Sync**: `POST /api/protocols/sync`
2. **Check Known Protocol**: `GET /api/protocols/check?contract_address=0x...`
3. **List Protocols**: `GET /api/protocols/?limit=10&min_score=0.7`

## Notes

- Unknown contracts receive a neutral score of 0.5 (not penalized)
- Protocols are identified by contract addresses stored in `contract_addresses` array
- Scores are recalculated nightly, but can be manually triggered
- Confidence score indicates data quality (higher = more reliable)

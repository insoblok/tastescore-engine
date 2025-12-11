# Mixers & Sanctions/Blacklists Detection Feature

## Overview

This feature detects direct or indirect exposure to sanctioned entities or mixers (e.g., Tornado Cash). It drives `CleanTxRatio` and `risk_flags` for wallet addresses.

## Components

### 1. OFAC Sanctions Ingester (`service/sanctions/ofac_ingester.py`)

- **Purpose**: Downloads and parses OFAC SDN (Specially Designated Nationals) CSV
- **Schedule**: Runs nightly at 2 AM UTC
- **Data Source**: https://www.treasury.gov/ofac/downloads/sdn.csv
- **Functionality**:
  - Downloads SDN CSV from OFAC
  - Extracts digital currency addresses (BTC, ETH, BNB, SOL)
  - Adds known mixer addresses (Tornado Cash)
  - Stores addresses in ClickHouse `address_labels` table

### 2. Metrics Calculator (`service/sanctions/metrics_calculator.py`)

- **Purpose**: Calculates exposure metrics for wallet addresses
- **Metrics Calculated**:
  - `direct_blacklist_hits_{30,90,all}`: Count and USD value of transactions with blacklisted addresses
  - `mixer_tx_share_{7,30,90}`: Percentage of transactions involving mixers
  - `indirect_exposure_{1,2,3_hops}`: Indirect exposure (requires graph data)
  - `clean_tx_ratio`: Ratio of clean transactions (0.0 to 1.0)
  - `confidence`: Confidence score (reduced by -0.15 if data unavailable)

### 3. Database (`service/database.py`)

- **Database**: ClickHouse
- **Tables**:
  - `address_labels`: Stores sanctioned, mixer, and watchlist addresses
  - `exposure_metrics`: Stores calculated exposure metrics per address

### 4. API Endpoints (`routers/sanctions.py`)

- `GET /api/sanctions/check?address={addr}&chain={chain}`: Check if address is blacklisted
- `GET /api/sanctions/metrics?address={addr}&chain={chain}`: Get exposure metrics
- `GET /api/sanctions/risk-flags?address={addr}&chain={chain}`: Get risk flags
- `POST /api/sanctions/ingest`: Manually trigger OFAC ingestion
- `POST /api/sanctions/calculate-metrics`: Calculate metrics for an address

## Configuration

### Environment Variables

Add these to your `.env` file:

```env
# ClickHouse Configuration
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=9000
CLICKHOUSE_DATABASE=tastescore
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=
```

### ClickHouse Setup

1. Install ClickHouse: https://clickhouse.com/docs/en/install
2. Start ClickHouse server
3. The application will automatically create tables on first connection

## Usage

### Automatic Operation

- **Nightly Ingestion**: OFAC data is automatically ingested at 2 AM UTC
- **Metrics Calculation**: Metrics are calculated when addresses are scanned via `/api/explore`

### Manual Operations

#### Check if an address is blacklisted:

```bash
curl "http://localhost:8080/api/sanctions/check?address=0x123...&chain=ETH"
```

#### Get exposure metrics:

```bash
curl "http://localhost:8080/api/sanctions/metrics?address=0x123...&chain=ETH"
```

#### Get risk flags:

```bash
curl "http://localhost:8080/api/sanctions/risk-flags?address=0x123...&chain=ETH"
```

#### Manually trigger ingestion:

```bash
curl -X POST "http://localhost:8080/api/sanctions/ingest"
```

## Defaults/SLA

- **If OFAC feeds unavailable**: 
  - `sanctions_data_unknown=true`
  - `CleanTxRatio=0.90` (neutral-conservative)
  - `confidence -= 0.15`

## Data Sources

1. **OFAC SDN List**: https://www.treasury.gov/ofac/downloads/sdn.csv
2. **Known Mixers**: Hardcoded list of Tornado Cash addresses
3. **Optional**: 0xB10C OFAC-sanctioned crypto addresses extraction tool (GitHub)

## Integration with Existing Code

The metrics calculation can be integrated into the existing `/api/explore` endpoint to automatically calculate exposure metrics when addresses are scanned. This is done by:

1. Parsing transaction data from blockchain scans
2. Calling `MetricsCalculator.calculate_exposure_metrics()`
3. Storing results in ClickHouse
4. Including metrics in API responses

## Testing

1. Start ClickHouse server
2. Start the FastAPI application
3. Trigger manual ingestion: `POST /api/sanctions/ingest`
4. Check an address: `GET /api/sanctions/check?address={addr}&chain=ETH`
5. Verify metrics are calculated and stored

## Notes

- The system gracefully degrades if ClickHouse is unavailable
- Address matching is case-insensitive for Ethereum addresses
- Mixer addresses include known Tornado Cash contracts
- Indirect exposure calculation requires graph data (not yet implemented)


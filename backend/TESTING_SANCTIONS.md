# Testing the Sanctions & Mixers Feature

## Prerequisites

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Up ClickHouse Database

#### Option A: Using Docker (Recommended)

```bash
docker run -d \
  --name clickhouse-server \
  -p 8123:8123 \
  -p 9000:9000 \
  clickhouse/clickhouse-server
```

#### Option B: Local Installation

Follow instructions at: https://clickhouse.com/docs/en/install

### 3. Configure Environment Variables

Create or update `.env` file in the `backend` directory:

```env
# ClickHouse Configuration
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=9000
CLICKHOUSE_DATABASE=tastescore
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=

# Existing app config
APP_NAME=Wallet Tracker
APP_VERSION=1.0.0
```

## Starting the Application

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port=8080 --reload
```

The application will:
- Connect to ClickHouse on startup
- Create necessary tables automatically
- Start the scheduler for nightly ingestion

## Testing Steps

### Step 1: Test Database Connection

Check if ClickHouse is accessible:

```bash
# Using curl
curl http://localhost:8080/api

# Should return: {"message":"Welcome to Wallet Tracker"}
```

### Step 2: Manually Trigger OFAC Ingestion

This downloads and parses the OFAC SDN list:

```bash
curl -X POST "http://localhost:8080/api/sanctions/ingest"
```

**Expected Response:**
```json
{
  "success": true,
  "message": "OFAC ingestion completed successfully"
}
```

**What happens:**
- Downloads SDN CSV from https://www.treasury.gov/ofac/downloads/sdn.csv
- Parses digital currency addresses
- Adds known mixer addresses (Tornado Cash)
- Stores in ClickHouse `address_labels` table

**Check logs** for ingestion progress and any errors.

### Step 3: Check if a Known Sanctioned Address is Detected

Test with a known Tornado Cash address:

```bash
# Tornado Cash 0.1 ETH mixer
curl "http://localhost:8080/api/sanctions/check?address=0x12d66f87a04a9e220743712ce6d9bb1b5616b8fc&chain=ETH"
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "address": "0x12d66f87a04a9e220743712ce6d9bb1b5616b8fc",
    "chain": "ETH",
    "label": "mixer",
    "program": "Tornado Cash",
    "source": "known-mixer-list",
    "first_seen": 1234567890,
    "metadata": {
      "mixer_name": "Tornado Cash"
    }
  }
}
```

### Step 4: Check a Clean Address

Test with a regular address (should not be blacklisted):

```bash
curl "http://localhost:8080/api/sanctions/check?address=0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb&chain=ETH"
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "chain": "ETH",
    "label": null,
    "is_blacklisted": false
  }
}
```

### Step 5: Calculate Exposure Metrics

Calculate metrics for an address with transaction history:

```bash
curl -X POST "http://localhost:8080/api/sanctions/calculate-metrics?address=0x12d66f87a04a9e220743712ce6d9bb1b5616b8fc&chain=ETH" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "time": 1704067200,
      "src": "0x12d66f87a04a9e220743712ce6d9bb1b5616b8fc",
      "dst": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
      "amount": 0.1,
      "value": 0.1
    }
  ]'
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "address": "0x12d66f87a04a9e220743712ce6d9bb1b5616b8fc",
    "chain": "ETH",
    "direct_blacklist_hits_30": 1,
    "direct_blacklist_hits_90": 1,
    "direct_blacklist_hits_all": 1,
    "mixer_tx_share_7": 100.0,
    "mixer_tx_share_30": 100.0,
    "mixer_tx_share_90": 100.0,
    "clean_tx_ratio": 0.0,
    "confidence": 0.5,
    "sanctions_data_unknown": false
  }
}
```

### Step 6: Get Exposure Metrics

Retrieve stored metrics:

```bash
curl "http://localhost:8080/api/sanctions/metrics?address=0x12d66f87a04a9e220743712ce6d9bb1b5616b8fc&chain=ETH"
```

### Step 7: Get Risk Flags

Get risk flags for an address:

```bash
curl "http://localhost:8080/api/sanctions/risk-flags?address=0x12d66f87a04a9e220743712ce6d9bb1b5616b8fc&chain=ETH"
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "has_sanctioned_exposure": false,
    "has_mixer_exposure": true,
    "has_watchlist_exposure": false,
    "sanctions_data_unknown": false,
    "flags": ["mixer_exposure"]
  }
}
```

## Integration Testing with Existing Scan Endpoint

You can also test by scanning a wallet address through the existing endpoint:

```bash
# Scan an Ethereum address
curl "http://localhost:8080/api/explore?wallet=0x12d66f87a04a9e220743712ce6d9bb1b5616b8fc&network=2"
```

Then check the metrics:

```bash
curl "http://localhost:8080/api/sanctions/metrics?address=0x12d66f87a04a9e220743712ce6d9bb1b5616b8fc&chain=ETH"
```

## Testing Scheduler

The scheduler runs OFAC ingestion nightly at 2 AM UTC. To test it immediately:

1. **Check if scheduler is running:**
   - Look for log message: "Scheduler started"
   - Check logs for "Scheduled jobs configured"

2. **Manually test the ingestion function:**
   ```python
   # In Python shell or test script
   from service.sanctions.ofac_ingester import OFACIngester
   ingester = OFACIngester()
   ingester.ingest()
   ```

## Troubleshooting

### ClickHouse Connection Issues

**Error:** `Failed to connect to ClickHouse`

**Solutions:**
1. Verify ClickHouse is running: `docker ps` (if using Docker)
2. Check connection: `curl http://localhost:8123`
3. Verify environment variables in `.env`
4. Check firewall/network settings

### No Addresses Found in Ingestion

**Possible causes:**
1. OFAC CSV format may have changed
2. Network issues downloading CSV
3. No digital currency addresses in current SDN list

**Check logs** for detailed error messages.

### Metrics Not Calculating

**Possible causes:**
1. No transactions provided
2. Transaction format doesn't match expected structure
3. ClickHouse not connected

**Solution:** Check transaction format matches expected structure (see `metrics_calculator.py`)

## Using Python Test Script

See `test_sanctions.py` for an automated test script.

## Expected Database State

After successful ingestion, you should see:

1. **address_labels table** with entries:
   - Label: `sanctioned` (from OFAC)
   - Label: `mixer` (Tornado Cash addresses)

2. **exposure_metrics table** with entries:
   - Metrics for addresses that have been scanned

## Next Steps

1. Integrate metrics calculation into the existing `/api/explore` endpoint
2. Add frontend UI to display risk flags and metrics
3. Set up monitoring/alerts for ingestion failures
4. Add more mixer addresses to the known list


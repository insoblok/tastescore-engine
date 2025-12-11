# Frontend UI for Sanctions & Mixers Feature

## Overview

The frontend UI provides a comprehensive interface for checking wallet addresses against sanctions lists and mixers, displaying risk assessments, and viewing exposure metrics.

## Components

### 1. **SanctionsChecker Page** (`/sanctions-checker`)

A standalone page for checking any wallet address.

**Features:**
- Address input field
- Blockchain selector (BTC, ETH, BNB, SOL)
- Real-time address checking
- Risk flags display
- Exposure metrics visualization

**Access:** Navigate to `/sanctions-checker` or click "Sanctions Check" button in navbar

### 2. **RiskFlagsCard Component**

Displays risk assessment for an address.

**Shows:**
- Overall risk level (High/Medium/Low/Unknown)
- Sanctioned entity exposure
- Mixer exposure
- Watchlist exposure
- Individual risk flags

**Visual Indicators:**
- Color-coded risk levels (Red/Yellow/Green/Gray)
- Icons for different risk types
- Flag badges

### 3. **ExposureMetricsCard Component**

Displays detailed exposure metrics.

**Shows:**
- Clean Transaction Ratio (with progress bar)
- Confidence Score (with progress bar)
- Direct Blacklist Hits (30/90/all time)
- Mixer Transaction Share (7/30/90 days)
- Blacklist Transaction Value

**Visual Features:**
- Progress bars for ratios
- Color-coded metrics (Green/Yellow/Red)
- Grid layout for time periods

## Integration

### Using the Hook

You can integrate sanctions checking into existing transaction pages using the `useSanctions` hook:

```typescript
import { useSanctions } from "../hooks/useSanctions";
import RiskFlagsCard from "../components/sanctions/RiskFlagsCard";

function YourTransactionPage() {
  const { wallet, network } = location.state;
  const chain = network === 1 ? "BTC" : network === 2 ? "ETH" : network === 3 ? "BNB" : "SOL";
  
  const { riskFlags, metrics, loading } = useSanctions(wallet, chain);

  return (
    <>
      <Navbar />
      {riskFlags && <RiskFlagsCard riskFlags={riskFlags} address={wallet} chain={chain} />}
      {/* Your existing transaction view */}
    </>
  );
}
```

### Adding to Existing Pages

To add risk flags to existing transaction pages (BTC, ETH, BNB, SOL):

1. Import the hook and component:
```typescript
import { useSanctions } from "../../hooks/useSanctions";
import RiskFlagsCard from "../../components/sanctions/RiskFlagsCard";
```

2. Use the hook in your component:
```typescript
const chain = network === 1 ? "BTC" : network === 2 ? "ETH" : network === 3 ? "BNB" : "SOL";
const { riskFlags, metrics } = useSanctions(wallet, chain);
```

3. Render the component:
```typescript
{riskFlags && (
  <RiskFlagsCard riskFlags={riskFlags} address={wallet} chain={chain} />
)}
```

## API Integration

The frontend communicates with these endpoints:

- `GET /api/sanctions/check?address={addr}&chain={chain}` - Check address label
- `GET /api/sanctions/metrics?address={addr}&chain={chain}` - Get exposure metrics
- `GET /api/sanctions/risk-flags?address={addr}&chain={chain}` - Get risk flags

## Styling

Components use:
- **Tailwind CSS** for styling
- **Lucide React** for icons
- **React Spinners** for loading states
- Color-coded risk indicators:
  - Red: High risk / Sanctioned
  - Yellow: Medium risk / Mixer
  - Green: Low risk / Clean
  - Gray: Unknown

## Example Usage

### Standalone Checker

1. Navigate to `/sanctions-checker`
2. Enter wallet address
3. Select blockchain
4. Click "Check Address"
5. View results:
   - Address label (if blacklisted)
   - Risk flags
   - Exposure metrics

### Integration Example

```typescript
// In SolanaTransactions.tsx or similar
import { useSanctions } from "../../hooks/useSanctions";
import RiskFlagsCard from "../../components/sanctions/RiskFlagsCard";

export default function SolanaTransactions() {
  const { wallet, network } = location.state;
  const chain = "SOL";
  
  const { riskFlags, metrics } = useSanctions(wallet, chain);

  return (
    <>
      <Navbar />
      {riskFlags && (
        <RiskFlagsCard riskFlags={riskFlags} address={wallet} chain={chain} />
      )}
      {/* Existing summary and transaction views */}
    </>
  );
}
```

## Testing

1. Start the frontend: `npm run dev`
2. Navigate to `http://localhost:5173/sanctions-checker`
3. Test with known addresses:
   - Tornado Cash: `0x12d66f87a04a9e220743712ce6d9bb1b5616b8fc` (ETH)
   - Regular address: Any clean address

## Future Enhancements

- [ ] Add risk flags to all transaction history pages
- [ ] Show risk indicators in transaction lists
- [ ] Add export functionality for reports
- [ ] Add historical risk tracking
- [ ] Add alerts for high-risk addresses


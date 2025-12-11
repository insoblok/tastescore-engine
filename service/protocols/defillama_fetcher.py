"""DeFiLlama API integration for fetching protocol data."""
import requests
from typing import List, Dict, Optional, Any
from datetime import datetime
from service.utils import logger
from service.models import ProtocolRegistry, ProtocolIncident


class DeFiLlamaFetcher:
    """Fetches protocol data from DeFiLlama API."""
    
    BASE_URL = "https://api.llama.fi"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "TasteScore-Engine/1.0"
        })
    
    def get_all_protocols(self) -> List[Dict[str, Any]]:
        """Fetch all protocols from DeFiLlama."""
        try:
            url = f"{self.BASE_URL}/protocols"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Fetched {len(data)} protocols from DeFiLlama")
            return data
        except Exception as e:
            logger.error(f"Failed to fetch protocols from DeFiLlama: {e}")
            return []
    
    def get_protocol_tvl(self, protocol_slug: str, timeout: int = 10) -> Optional[float]:
        """Get current TVL for a specific protocol."""
        try:
            url = f"{self.BASE_URL}/tvl/{protocol_slug}"
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            data = response.json()
            
            # TVL is usually the latest value
            if isinstance(data, list) and len(data) > 0:
                return float(data[-1].get("totalLiquidityUSD", 0))
            elif isinstance(data, dict):
                return float(data.get("totalLiquidityUSD", 0))
            return None
        except requests.Timeout:
            logger.warning(f"Timeout fetching TVL for {protocol_slug}")
            return None
        except Exception as e:
            logger.warning(f"Failed to fetch TVL for {protocol_slug}: {e}")
            return None
    
    def get_protocol_tvl_history(self, protocol_slug: str, timeout: int = 10) -> List[Dict[str, Any]]:
        """Get TVL history for a specific protocol (for growth stability calculation)."""
        try:
            url = f"{self.BASE_URL}/tvl/{protocol_slug}"
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            data = response.json()
            
            # Return the full history
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # If it's a single data point, wrap it in a list
                return [data] if data.get("totalLiquidityUSD") else []
            return []
        except requests.Timeout:
            logger.warning(f"Timeout fetching TVL history for {protocol_slug}")
            return []
        except Exception as e:
            logger.warning(f"Failed to fetch TVL history for {protocol_slug}: {e}")
            return []
    
    def get_protocol_details(self, protocol_slug: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
        """Get detailed information about a protocol."""
        try:
            url = f"{self.BASE_URL}/protocol/{protocol_slug}"
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.Timeout:
            logger.warning(f"Timeout fetching details for {protocol_slug}")
            return None
        except Exception as e:
            logger.warning(f"Failed to fetch details for {protocol_slug}: {e}")
            return None
    
    def parse_protocol_data(self, protocol_data: Dict[str, Any]) -> Optional[ProtocolRegistry]:
        """Parse DeFiLlama protocol data into ProtocolRegistry model."""
        try:
            protocol_id = protocol_data.get("slug", "").lower()
            if not protocol_id:
                return None
            
            name = protocol_data.get("name", "")
            category = protocol_data.get("category", "")
            chain = protocol_data.get("chain", "")
            
            # Get TVL
            tvl = float(protocol_data.get("tvl", 0) or 0)
            
            # Get launch date
            launch_date = protocol_data.get("listedAt") or protocol_data.get("launchDate")
            age_days = 0
            if launch_date:
                try:
                    # Handle Unix timestamp or ISO date string
                    if isinstance(launch_date, (int, float)):
                        launch_dt = datetime.fromtimestamp(launch_date)
                    else:
                        launch_dt = datetime.fromisoformat(str(launch_date).replace("Z", "+00:00"))
                    age_days = (datetime.now() - launch_dt.replace(tzinfo=None)).days
                except Exception:
                    pass
            
            # Get contract addresses if available
            contract_addresses = []
            addresses = protocol_data.get("address", "")
            if addresses:
                if isinstance(addresses, str):
                    contract_addresses = [addr.strip() for addr in addresses.split(",") if addr.strip()]
                elif isinstance(addresses, list):
                    contract_addresses = [str(addr) for addr in addresses]
            
            # Get chains information (for multi-chain scoring)
            chains = protocol_data.get("chains", [])
            if isinstance(chains, str):
                chains = [c.strip() for c in chains.split(",") if c.strip()]
            elif not isinstance(chains, list):
                chains = []
            # If no chains list but we have a chain field, use that
            if not chains and chain:
                chains = [chain]
            
            # Get audit information (if available in metadata)
            audit_info = protocol_data.get("audit_links", []) or []
            audit_count = len(audit_info) if isinstance(audit_info, list) else 0
            
            # Get bug bounty info
            bounty_present = bool(protocol_data.get("bounty", False) or protocol_data.get("bugBounty", False))
            
            # Get incidents/hacks (if available)
            incidents = []
            hacks = protocol_data.get("hacks", []) or []
            if isinstance(hacks, list):
                for hack in hacks:
                    incidents.append(ProtocolIncident(
                        date=str(hack.get("date", "")),
                        description=hack.get("description", "Unknown hack"),
                        amount_lost_usd=float(hack.get("amount", 0) or 0),
                        severity="high" if float(hack.get("amount", 0) or 0) > 1000000 else "medium",
                        source="DeFiLlama"
                    ))
            
            return ProtocolRegistry(
                protocol_id=protocol_id,
                name=name,
                slug=protocol_data.get("slug"),
                category=category,
                chain=chain,
                chains=chains,
                contract_addresses=contract_addresses,
                tvl=tvl,
                age_days=max(0, age_days),
                launch_date=launch_date,
                audit_count=audit_count,
                bounty_present=bounty_present,
                incidents=incidents,
                data_sources=["DeFiLlama"]
            )
        except Exception as e:
            logger.error(f"Failed to parse protocol data: {e}")
            return None

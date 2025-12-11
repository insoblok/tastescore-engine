"""OFAC Sanctions List Ingester - Downloads and parses SDN CSV."""
import csv
import io
import re
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import requests
from service.utils import logger
from service.models import AddressLabel
from service.database import FirestoreDB


class OFACIngester:
    """Ingests OFAC SDN (Specially Designated Nationals) list."""
    
    SDN_CSV_URL = "https://www.treasury.gov/ofac/downloads/sdn.csv"
    
    # Common blockchain address patterns
    ETH_ADDRESS_PATTERN = re.compile(r'0x[a-fA-F0-9]{40}')
    BTC_ADDRESS_PATTERN = re.compile(r'[13][a-km-zA-HJ-NP-Z1-9]{25,34}|bc1[a-z0-9]{39,59}')
    SOL_ADDRESS_PATTERN = re.compile(r'[1-9A-HJ-NP-Za-km-z]{32,44}')
    BNB_ADDRESS_PATTERN = re.compile(r'0x[a-fA-F0-9]{40}')  # Same as ETH format
    
    def __init__(self):
        self.db = FirestoreDB()
        logger.info("OFAC Ingester initialized")
    
    def download_sdn_csv(self) -> str:
        """Download SDN CSV from OFAC website. Falls back to local sdn.csv if download fails."""
        # First, try to use local file if it exists
        current_file = Path(__file__)
        backend_dir = current_file.parent.parent.parent
        sdn_csv_path = backend_dir / "sdn.csv"
        
        if sdn_csv_path.exists():
            try:
                with open(sdn_csv_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                logger.info(f"Loaded SDN CSV from local file ({len(content)} bytes)")
                return content
            except Exception as e:
                logger.warning(f"Failed to read local sdn.csv: {e}, trying to download...")
        
        # If local file doesn't exist or failed to read, try downloading
        try:
            logger.info(f"Downloading SDN CSV from {self.SDN_CSV_URL}")
            response = requests.get(self.SDN_CSV_URL, timeout=60)
            response.raise_for_status()
            logger.info(f"Downloaded SDN CSV ({len(response.content)} bytes)")
            return response.text
        except Exception as e:
            logger.error(f"Failed to download SDN CSV: {e}")
            # If download failed and local file exists, use it anyway
            if sdn_csv_path.exists():
                try:
                    with open(sdn_csv_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    logger.info(f"Using local sdn.csv file as fallback ({len(content)} bytes)")
                    return content
                except Exception as read_error:
                    logger.error(f"Failed to read local sdn.csv: {read_error}")
            
            raise FileNotFoundError(
                f"Failed to download SDN CSV from {self.SDN_CSV_URL} "
                f"and local sdn.csv not found at {sdn_csv_path}"
            )
    
    def parse_digital_currency_addresses(self, csv_content: str) -> List[AddressLabel]:
        """Parse digital currency addresses from SDN CSV."""
        labels = []
        reader = csv.reader(io.StringIO(csv_content))
        
        current_timestamp = int(datetime.now().timestamp())
        
        # Chain mapping from OFAC abbreviations to our chain codes
        CHAIN_MAPPING = {
            'XBT': 'BTC',      # Bitcoin
            'BTC': 'BTC',      # Bitcoin (alternative)
            'ETH': 'ETH',      # Ethereum
            'ZEC': 'ZEC',      # Zcash
            'USDT': 'TRX',     # Tether on Tron (most common in OFAC)
            'TRX': 'TRX',      # Tron
            'LTC': 'LTC',      # Litecoin
            'BCH': 'BCH',      # Bitcoin Cash
            'XMR': 'XMR',      # Monero
            'DASH': 'DASH',    # Dash
        }
        
        # Pattern to match "Digital Currency Address - [CHAIN] [ADDRESS];"
        digital_currency_pattern = re.compile(
            r'Digital Currency Address\s*-\s*([A-Z0-9]+)\s+([A-Za-z0-9]+);?',
            re.IGNORECASE
        )
        
        row_count = 0
        for row in reader:
            row_count += 1
            
            # Skip header row if it exists
            if row_count == 1 and len(row) > 0 and not row[0].isdigit():
                continue
            
            # Column 11 (index 11) contains the digital currency addresses
            if len(row) > 11:
                digital_currency_field = row[11]
                
                # Extract program name (usually in column 3, index 3)
                program = row[3] if len(row) > 3 else 'OFAC'
                
                # Extract entity number (usually in column 0, index 0)
                ent_num = row[0] if len(row) > 0 else ''
                source = f"OFAC-SDN-{ent_num}" if ent_num else "OFAC-SDN"
                
                # Extract SDN name (usually in column 1, index 1)
                sdn_name = row[1] if len(row) > 1 else ''
                
                # Find all digital currency addresses in the format
                matches = digital_currency_pattern.findall(digital_currency_field)
                
                for chain_abbr, address in matches:
                    chain_abbr = chain_abbr.upper()
                    chain = CHAIN_MAPPING.get(chain_abbr)
                    
                    if chain:
                        # Normalize address based on chain
                        normalized_address = address
                        if chain in ['ETH', 'TRX']:
                            normalized_address = address.lower()
                        elif chain == 'BTC':
                            normalized_address = address  # Keep as-is for BTC
                        
                        # Check if we already have this address/chain combination
                        if not any(l.address == normalized_address and l.chain == chain for l in labels):
                            labels.append(AddressLabel(
                                address=normalized_address,
                                chain=chain,
                                label='blacklisted',
                                program=program,
                                first_seen=current_timestamp,
                                source=source,
                                metadata={
                                    'sdn_name': sdn_name,
                                    'ent_num': ent_num,
                                    'ofac_chain_abbr': chain_abbr
                                }
                            ))
                
                # Also search in the digital currency field for addresses using regex patterns
                # (fallback for addresses not in the standard format)
                eth_addresses = self.ETH_ADDRESS_PATTERN.findall(digital_currency_field)
                for addr in eth_addresses:
                    normalized_addr = addr.lower()
                    if not any(l.address == normalized_addr and l.chain == 'ETH' for l in labels):
                        labels.append(AddressLabel(
                            address=normalized_addr,
                            chain='ETH',
                            label='blacklisted',
                            program=program,
                            first_seen=current_timestamp,
                            source=source,
                            metadata={'sdn_name': sdn_name, 'ent_num': ent_num}
                        ))
                
                btc_addresses = self.BTC_ADDRESS_PATTERN.findall(digital_currency_field)
                for addr in btc_addresses:
                    if not any(l.address == addr and l.chain == 'BTC' for l in labels):
                        labels.append(AddressLabel(
                            address=addr,
                            chain='BTC',
                            label='blacklisted',
                            program=program,
                            first_seen=current_timestamp,
                            source=source,
                            metadata={'sdn_name': sdn_name, 'ent_num': ent_num}
                        ))
        
        logger.info(f"Parsed {len(labels)} digital currency addresses from SDN CSV")
        return labels
    
    def add_mixer_addresses(self) -> List[AddressLabel]:
        """Add known mixer addresses (e.g., Tornado Cash)."""
        labels = []
        current_timestamp = int(datetime.now().timestamp())
        
        # Tornado Cash Ethereum addresses (known mixer addresses)
        tornado_cash_addresses = [
            # Tornado Cash: 0.1 ETH
            "0x12d66f87a04a9e220743712ce6d9bb1b5616b8fc",
            # Tornado Cash: 1 ETH
            "0x47ce0c6ed5b0ce3d3a51fdb1c52dc66a7c3c2936",
            # Tornado Cash: 10 ETH
            "0x910cbd523d972eb0a6f4cae4618ad62622b39dbf",
            # Tornado Cash: 100 ETH
            "0xa160cdab225685da1d56aa342ad8841c3b53f291",
            # Tornado Cash: 1000 ETH
            "0xd4b88df4d29f5cedd6857912842cff3b20c8cfa3",
            # Tornado Cash: 10000 ETH
            "0xfd8610d20aa15b7b2e3be39b396a1bc3516c7144",
            # Tornado Cash: 100000 ETH
            "0x07687e702b410fa43f4cb4af7fa097917ff63c0f",
            # Tornado Cash: 1000000 ETH
            "0x23773e65ed146a459791799d01336db287f25334",
        ]
        
        for addr in tornado_cash_addresses:
            labels.append(AddressLabel(
                address=addr.lower(),
                chain='ETH',
                label='mixer',
                program='Tornado Cash',
                first_seen=current_timestamp,
                source='known-mixer-list',
                metadata={'mixer_name': 'Tornado Cash'}
            ))
        
        logger.info(f"Added {len(labels)} mixer addresses")
        return labels
    
    def ingest(self) -> bool:
        """Main ingestion method - downloads and processes OFAC data."""
        try:
            logger.info("Starting OFAC sanctions ingestion")
            
            # Download SDN CSV
            csv_content = self.download_sdn_csv()
            
            # Parse addresses
            sanctioned_labels = self.parse_digital_currency_addresses(csv_content)
            
            # Add mixer addresses
            mixer_labels = self.add_mixer_addresses()
            
            # Combine all labels
            all_labels = sanctioned_labels + mixer_labels
            
            # Insert into database
            if all_labels:
                self.db.insert_address_labels(all_labels)
                logger.info(f"Successfully ingested {len(all_labels)} address labels")
                return True
            else:
                logger.warning("No address labels found to ingest")
                return False
                
        except Exception as e:
            logger.error(f"OFAC ingestion failed: {e}")
            return False


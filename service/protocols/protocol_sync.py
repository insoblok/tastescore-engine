"""Nightly job to sync protocol data and calculate scores."""
from typing import List
from service.protocols.defillama_fetcher import DeFiLlamaFetcher
from service.protocols.l2beat_fetcher import L2BEATFetcher
from service.protocols.scoring_calculator import ProtocolScoringCalculator
from service.database import FirestoreDB
from service.models import ProtocolRegistry
from service.utils import logger


class ProtocolSyncJob:
    """Handles nightly synchronization of protocol data."""
    
    def __init__(self):
        self.defillama = DeFiLlamaFetcher()
        self.l2beat = L2BEATFetcher()
        self.scorer = ProtocolScoringCalculator()
        self.db = FirestoreDB()
    
    def sync_all_protocols(self) -> bool:
        """
        Main sync job: fetch all protocols, calculate scores, and save to database.
        """
        try:
            logger.info("Starting protocol sync job")
            
            # Fetch all protocols from DeFiLlama
            protocols_data = self.defillama.get_all_protocols()
            
            if not protocols_data:
                logger.warning("No protocols fetched from DeFiLlama")
                return False
            
            synced_count = 0
            error_count = 0
            
            for protocol_data in protocols_data:
                try:
                    # Parse protocol data
                    protocol = self.defillama.parse_protocol_data(protocol_data)
                    
                    if not protocol:
                        continue
                    
                    # Get L2 risk if applicable
                    if protocol.chain:
                        l2_risk = self.l2beat.get_l2_risk_for_protocol(protocol.chain)
                        if l2_risk is not None:
                            protocol.l2_risk_score = l2_risk
                            if "L2BEAT" not in protocol.data_sources:
                                protocol.data_sources.append("L2BEAT")
                    
                    # Get TVL history for growth stability calculation (with longer timeout for sync)
                    tvl_history = []
                    if protocol.slug:
                        try:
                            tvl_history = self.defillama.get_protocol_tvl_history(protocol.slug, timeout=15)
                        except Exception as e:
                            logger.warning(f"Failed to fetch TVL history for {protocol.slug}: {e}")
                            tvl_history = []
                    
                    # Calculate scores with TVL history
                    protocol = self.scorer.calculate_protocol_score(protocol, tvl_history=tvl_history)
                    
                    # Save to database
                    self.db.save_protocol_registry(protocol)
                    
                    synced_count += 1
                    
                    if synced_count % 10 == 0:
                        logger.info(f"Synced {synced_count} protocols...")
                
                except Exception as e:
                    error_count += 1
                    logger.error(f"Error processing protocol {protocol_data.get('slug', 'unknown')}: {e}")
                    continue
            
            logger.info(f"Protocol sync completed: {synced_count} synced, {error_count} errors")
            return synced_count > 0
        
        except Exception as e:
            logger.error(f"Protocol sync job failed: {e}")
            return False
    
    def sync_single_protocol(self, protocol_slug: str) -> bool:
        """Sync a single protocol by slug."""
        try:
            # Get protocol details
            protocol_data = self.defillama.get_protocol_details(protocol_slug)
            
            if not protocol_data:
                logger.warning(f"Protocol {protocol_slug} not found")
                return False
            
            # Parse and score
            protocol = self.defillama.parse_protocol_data(protocol_data)
            if not protocol:
                return False
            
            # Get L2 risk
            if protocol.chain:
                l2_risk = self.l2beat.get_l2_risk_for_protocol(protocol.chain)
                if l2_risk is not None:
                    protocol.l2_risk_score = l2_risk
                    if "L2BEAT" not in protocol.data_sources:
                        protocol.data_sources.append("L2BEAT")
            
            # Get TVL history for growth stability calculation (with longer timeout for sync)
            tvl_history = []
            try:
                tvl_history = self.defillama.get_protocol_tvl_history(protocol_slug, timeout=15)
            except Exception as e:
                logger.warning(f"Failed to fetch TVL history for {protocol_slug}: {e}")
            
            # Calculate scores with TVL history
            protocol = self.scorer.calculate_protocol_score(protocol, tvl_history=tvl_history)
            
            # Save to database
            self.db.save_protocol_registry(protocol)
            
            logger.info(f"Synced protocol {protocol_slug}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to sync protocol {protocol_slug}: {e}")
            return False

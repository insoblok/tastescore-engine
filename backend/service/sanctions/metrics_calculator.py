"""Exposure Metrics Calculator - Computes sanctions and mixer exposure metrics."""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from service.utils import logger
from service.models import ExposureMetrics, RiskFlags
from service.database import FirestoreDB


class MetricsCalculator:
    """Calculates exposure metrics for wallet addresses."""
    
    def __init__(self):
        self.db = FirestoreDB()
        logger.info("Metrics Calculator initialized")
    
    def calculate_direct_blacklist_hits(
        self, 
        address: str, 
        chain: str, 
        transactions: List[Dict[str, Any]],
        days: int
    ) -> tuple[int, float]:
        """
        Calculate direct blacklist hits (count and USD value).
        
        Args:
            address: Wallet address
            chain: Blockchain chain identifier
            transactions: List of transaction dictionaries
            days: Number of days to look back
            
        Returns:
            Tuple of (hit_count, usd_value)
        """
        cutoff_time = int((datetime.now() - timedelta(days=days)).timestamp())
        
        # Get all sanctioned and mixer addresses for this chain
        sanctioned_addresses = set(self.db.get_all_addresses_by_label('sanctioned', chain))
        mixer_addresses = set(self.db.get_all_addresses_by_label('mixer', chain))
        blacklist_addresses = sanctioned_addresses | mixer_addresses
        
        if not blacklist_addresses:
            return 0, 0.0
        
        hit_count = 0
        total_value = 0.0
        
        for tx in transactions:
            tx_time = tx.get('time', 0) or tx.get('timestamp', 0)
            if tx_time < cutoff_time:
                continue
            
            # Check transaction participants
            tx_addresses = set()
            
            # Extract addresses from transaction
            if 'src' in tx or 'from' in tx:
                tx_addresses.add((tx.get('src') or tx.get('from', '')).lower())
            if 'dst' in tx or 'to' in tx:
                tx_addresses.add((tx.get('dst') or tx.get('to', '')).lower())
            if 'inputs' in tx:
                for inp in tx.get('inputs', []):
                    if 'addr' in inp:
                        tx_addresses.add(inp['addr'].lower())
            if 'outputs' in tx:
                for out in tx.get('outputs', []):
                    if 'addr' in out:
                        tx_addresses.add(out['addr'].lower())
            
            # Check for blacklist intersection
            if tx_addresses & blacklist_addresses:
                hit_count += 1
                # Get transaction value in USD
                amount = tx.get('amount', 0) or tx.get('value', 0)
                if isinstance(amount, str):
                    try:
                        amount = float(amount)
                    except:
                        amount = 0.0
                # For now, use raw amount (would need price conversion for accurate USD)
                total_value += abs(amount)
        
        return hit_count, total_value
    
    def calculate_mixer_tx_share(
        self,
        address: str,
        chain: str,
        transactions: List[Dict[str, Any]],
        days: int
    ) -> float:
        """
        Calculate mixer transaction share as percentage.
        
        Args:
            address: Wallet address
            chain: Blockchain chain identifier
            transactions: List of transaction dictionaries
            days: Number of days to look back
            
        Returns:
            Mixer transaction share as percentage (0.0 to 100.0)
        """
        cutoff_time = int((datetime.now() - timedelta(days=days)).timestamp())
        
        mixer_addresses = set(self.db.get_all_addresses_by_label('mixer', chain))
        if not mixer_addresses:
            return 0.0
        
        mixer_tx_count = 0
        total_tx_count = 0
        
        for tx in transactions:
            tx_time = tx.get('time', 0) or tx.get('timestamp', 0)
            if tx_time < cutoff_time:
                continue
            
            total_tx_count += 1
            
            # Check if transaction involves mixer
            tx_addresses = set()
            if 'src' in tx or 'from' in tx:
                tx_addresses.add((tx.get('src') or tx.get('from', '')).lower())
            if 'dst' in tx or 'to' in tx:
                tx_addresses.add((tx.get('dst') or tx.get('to', '')).lower())
            
            if tx_addresses & mixer_addresses:
                mixer_tx_count += 1
        
        if total_tx_count == 0:
            return 0.0
        
        return (mixer_tx_count / total_tx_count) * 100.0
    
    def calculate_clean_tx_ratio(
        self,
        address: str,
        chain: str,
        transactions: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate clean transaction ratio.
        
        Args:
            address: Wallet address
            chain: Blockchain chain identifier
            transactions: List of transaction dictionaries
            
        Returns:
            Clean transaction ratio (0.0 to 1.0)
        """
        if not transactions:
            return 0.90  # Default neutral-conservative
        
        # Get all blacklist addresses
        sanctioned_addresses = set(self.db.get_all_addresses_by_label('sanctioned', chain))
        mixer_addresses = set(self.db.get_all_addresses_by_label('mixer', chain))
        watchlist_addresses = set(self.db.get_all_addresses_by_label('watchlist', chain))
        blacklist_addresses = sanctioned_addresses | mixer_addresses | watchlist_addresses
        
        if not blacklist_addresses:
            return 0.90  # Default if no blacklist data
        
        clean_tx_count = 0
        total_tx_count = len(transactions)
        
        for tx in transactions:
            tx_addresses = set()
            if 'src' in tx or 'from' in tx:
                tx_addresses.add((tx.get('src') or tx.get('from', '')).lower())
            if 'dst' in tx or 'to' in tx:
                tx_addresses.add((tx.get('dst') or tx.get('to', '')).lower())
            
            if not (tx_addresses & blacklist_addresses):
                clean_tx_count += 1
        
        if total_tx_count == 0:
            return 0.90
        
        return clean_tx_count / total_tx_count
    
    def calculate_exposure_metrics(
        self,
        address: str,
        chain: str,
        transactions: List[Dict[str, Any]],
        sanctions_data_available: bool = True
    ) -> ExposureMetrics:
        """
        Calculate all exposure metrics for an address.
        
        Args:
            address: Wallet address
            chain: Blockchain chain identifier
            transactions: List of transaction dictionaries
            sanctions_data_available: Whether sanctions data is available
            
        Returns:
            ExposureMetrics object
        """
        # Check if sanctions data is available
        if not sanctions_data_available:
            return ExposureMetrics(
                address=address,
                chain=chain,
                clean_tx_ratio=0.90,  # Default neutral-conservative
                sanctions_data_unknown=True,
                confidence=-0.15,  # Reduced confidence
                last_updated=int(datetime.now().timestamp())
            )
        
        # Calculate direct blacklist hits
        hits_30, value_30 = self.calculate_direct_blacklist_hits(address, chain, transactions, 30)
        hits_90, value_90 = self.calculate_direct_blacklist_hits(address, chain, transactions, 90)
        hits_all, value_all = self.calculate_direct_blacklist_hits(address, chain, transactions, 9999)
        
        # Calculate mixer transaction shares
        mixer_share_7 = self.calculate_mixer_tx_share(address, chain, transactions, 7)
        mixer_share_30 = self.calculate_mixer_tx_share(address, chain, transactions, 30)
        mixer_share_90 = self.calculate_mixer_tx_share(address, chain, transactions, 90)
        
        # Calculate clean transaction ratio
        clean_tx_ratio = self.calculate_clean_tx_ratio(address, chain, transactions)
        
        # Calculate confidence (starts at 1.0, reduced by exposure)
        confidence = 1.0
        if hits_all > 0:
            confidence -= 0.3
        if mixer_share_90 > 10.0:  # More than 10% mixer transactions
            confidence -= 0.2
        if clean_tx_ratio < 0.5:
            confidence -= 0.2
        confidence = max(0.0, confidence)  # Don't go below 0
        
        metrics = ExposureMetrics(
            address=address,
            chain=chain,
            direct_blacklist_hits_30=hits_30,
            direct_blacklist_hits_90=hits_90,
            direct_blacklist_hits_all=hits_all,
            direct_blacklist_value_30=value_30,
            direct_blacklist_value_90=value_90,
            direct_blacklist_value_all=value_all,
            mixer_tx_share_7=mixer_share_7,
            mixer_tx_share_30=mixer_share_30,
            mixer_tx_share_90=mixer_share_90,
            clean_tx_ratio=clean_tx_ratio,
            sanctions_data_unknown=False,
            confidence=confidence,
            last_updated=int(datetime.now().timestamp())
        )
        
        # Save to database
        self.db.update_exposure_metrics(metrics.model_dump())
        
        return metrics
    
    def get_risk_flags(self, address: str, chain: str) -> RiskFlags:
        """
        Get risk flags for an address based on exposure metrics.
        
        Args:
            address: Wallet address
            chain: Blockchain chain identifier
            
        Returns:
            RiskFlags object
        """
        metrics = self.db.get_exposure_metrics(address, chain)
        
        if not metrics:
            return RiskFlags(
                sanctions_data_unknown=True,
                flags=['no_metrics_available']
            )
        
        flags = []
        has_sanctioned = metrics['direct_blacklist_hits_all'] > 0
        has_mixer = metrics['mixer_tx_share_90'] > 0
        has_watchlist = False  # Would need to check watchlist separately
        
        if has_sanctioned:
            flags.append('sanctioned_exposure')
        if has_mixer:
            flags.append('mixer_exposure')
        if has_watchlist:
            flags.append('watchlist_exposure')
        
        if metrics['clean_tx_ratio'] < 0.5:
            flags.append('low_clean_tx_ratio')
        
        if metrics['sanctions_data_unknown']:
            flags.append('sanctions_data_unknown')
        
        return RiskFlags(
            has_sanctioned_exposure=has_sanctioned,
            has_mixer_exposure=has_mixer,
            has_watchlist_exposure=has_watchlist,
            sanctions_data_unknown=metrics['sanctions_data_unknown'],
            flags=flags
        )


"""Firestore database connection and operations."""
import os
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from firebase_admin import initialize_app, firestore, credentials, get_app
from firebase_admin.exceptions import FirebaseError
from dotenv import load_dotenv
from service.utils import logger
from service.models import AddressLabel, ProtocolRegistry, ProtocolIncident
from service.firebase_config import PROJECT_ID, DEFAULT_SERVICE_ACCOUNT_PATH

load_dotenv()

class FirestoreDB:
    """Firestore database client for address labels and metrics."""
    
    def __init__(self):
        self.connected = False
        self.db = None
        
        try:
            # Check if Firebase app is already initialized
            try:
                app = get_app()
                logger.debug("Firebase app already initialized, reusing existing app")
            except (ValueError, FirebaseError):
                # Firebase not initialized yet, so initialize it
                # Option 1: Use service account key file (recommended for production)
                service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY", "")
                
                # If not set in env, try default path relative to backend directory
                if not service_account_path:
                    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    default_path = os.path.join(backend_dir, DEFAULT_SERVICE_ACCOUNT_PATH)
                    if os.path.exists(default_path):
                        service_account_path = default_path
                        logger.info(f"Using default service account path: {service_account_path}")
                
                if service_account_path and os.path.exists(service_account_path):
                    cred = credentials.Certificate(service_account_path)
                    initialize_app(cred, {'projectId': PROJECT_ID})
                    logger.info(f"Firebase initialized with service account key: {service_account_path}")
                else:
                    # Option 2: Use environment variable with JSON credentials
                    firebase_creds_json = os.getenv("FIREBASE_CREDENTIALS_JSON", "")
                    
                    if firebase_creds_json:
                        cred_dict = json.loads(firebase_creds_json)
                        cred = credentials.Certificate(cred_dict)
                        initialize_app(cred, {'projectId': PROJECT_ID})
                        logger.info("Firebase initialized with JSON credentials from env")
                    else:
                        # Option 3: Try default credentials (works in Google Cloud environments)
                        try:
                            initialize_app({'projectId': PROJECT_ID})
                            logger.info("Firebase initialized with default credentials")
                        except Exception as e:
                            logger.warning(f"Firebase default credentials failed: {e}")
                            raise ValueError(
                                f"Firebase credentials not found. Please set FIREBASE_SERVICE_ACCOUNT_KEY "
                                f"or FIREBASE_CREDENTIALS_JSON environment variable.\n"
                                f"Expected service account file: {DEFAULT_SERVICE_ACCOUNT_PATH}"
                            )
            
            self.db = firestore.client()
            self.connected = True
            logger.info(f"Firestore connection established for project: {PROJECT_ID}")
        except Exception as e:
            logger.error(f"Failed to connect to Firestore: {e}")
            self.connected = False
    
    def _get_address_label_doc_id(self, address: str, chain: str, label: str) -> str:
        """Generate document ID for address label."""
        return f"{address.lower()}_{chain.upper()}_{label}"
    
    def _get_metrics_doc_id(self, address: str, chain: str) -> str:
        """Generate document ID for exposure metrics."""
        return f"{address.lower()}_{chain.upper()}"
    
    def insert_address_labels(self, labels: List[AddressLabel]):
        """Insert or merge address labels into the database."""
        if not self.connected or not labels:
            return
        
        try:
            batch = self.db.batch()
            count = 0
            
            for label in labels:
                doc_id = self._get_address_label_doc_id(label.address, label.chain, label.label)
                doc_ref = self.db.collection('address_labels').document(doc_id)
                
                data = {
                    'address': label.address.lower(),
                    'chain': label.chain.upper(),
                    'label': label.label,
                    'program': label.program,
                    'first_seen': label.first_seen,
                    'source': label.source,
                    'metadata': label.metadata or {},
                    'updated_at': firestore.SERVER_TIMESTAMP
                }
                
                # Use set with merge to update if exists, create if not
                batch.set(doc_ref, data, merge=True)
                count += 1
                
                # Firestore batch limit is 500
                if count >= 500:
                    batch.commit()
                    batch = self.db.batch()
                    count = 0
            
            if count > 0:
                batch.commit()
            
            logger.info(f"Inserted {len(labels)} address labels into Firestore")
        except Exception as e:
            logger.error(f"Failed to insert address labels: {e}")
    
    def get_address_label(self, address: str, chain: Optional[str] = None) -> Optional[AddressLabel]:
        """Get address label if it exists. If chain is None, searches across all chains."""
        if not self.connected:
            return None
        
        try:
            # Normalize address - lowercase for ETH/TRX, keep case for BTC and others
            # But since we store all addresses as lowercase in the database, we need to query with lowercase
            address_normalized = address.lower().strip()
            
            # Validate that we're doing exact matching
            if not address_normalized:
                return None
            
            if chain:
                # Query for specific chain
                query = self.db.collection('address_labels').where('address', '==', address_normalized).where('chain', '==', chain.upper()).limit(1)
            else:
                # Query across all chains - get first match
                query = self.db.collection('address_labels').where('address', '==', address_normalized).limit(1)
            
            docs = query.stream()
            
            for doc in docs:
                data = doc.to_dict()
                stored_address = data.get('address', '').strip()
                
                # CRITICAL: Verify exact match to prevent false positives
                # This ensures we don't return a match for similar addresses
                if stored_address != address_normalized:
                    logger.warning(
                        f"Address mismatch detected: "
                        f"queried '{address_normalized}' (length: {len(address_normalized)}) "
                        f"but got '{stored_address}' (length: {len(stored_address)}) - skipping false positive"
                    )
                    continue
                
                # Double-check: verify the addresses are exactly the same character by character
                if stored_address != address_normalized:
                    logger.error(f"Exact match verification failed for address: {address_normalized}")
                    continue
                
                return AddressLabel(
                    address=stored_address,
                    chain=data.get('chain', ''),
                    label=data.get('label', ''),
                    program=data.get('program'),
                    first_seen=data.get('first_seen'),
                    source=data.get('source'),
                    metadata=data.get('metadata')
                )
            return None
        except Exception as e:
            logger.error(f"Failed to get address label: {e}")
            return None
    
    def get_all_address_labels(self, address: str) -> List[AddressLabel]:
        """Get all address labels across all chains for an address."""
        if not self.connected:
            return []
        
        try:
            address_normalized = address.lower().strip()
            if not address_normalized:
                return []
            
            query = self.db.collection('address_labels').where('address', '==', address_normalized)
            docs = query.stream()
            
            labels = []
            for doc in docs:
                data = doc.to_dict()
                stored_address = data.get('address', '').strip()
                
                # CRITICAL: Verify exact match to prevent false positives
                if stored_address != address_normalized:
                    logger.warning(
                        f"Address mismatch in get_all_address_labels: "
                        f"queried '{address_normalized}' but got '{stored_address}' - skipping"
                    )
                    continue
                
                labels.append(AddressLabel(
                    address=stored_address,
                    chain=data.get('chain', ''),
                    label=data.get('label', ''),
                    program=data.get('program'),
                    first_seen=data.get('first_seen'),
                    source=data.get('source'),
                    metadata=data.get('metadata')
                ))
            return labels
        except Exception as e:
            logger.error(f"Failed to get all address labels: {e}")
            return []
    
    def check_address_in_labels(self, address: str, chain: str, label_types: List[str]) -> bool:
        """Check if address exists in specified label types."""
        if not self.connected:
            return False
        
        try:
            query = self.db.collection('address_labels').where('address', '==', address.lower()).where('chain', '==', chain.upper()).where('label', 'in', label_types).limit(1)
            docs = list(query.stream())
            return len(docs) > 0
        except Exception as e:
            logger.error(f"Failed to check address in labels: {e}")
            return False
    
    def get_all_addresses_by_label(self, label: str, chain: Optional[str] = None) -> List[str]:
        """Get all addresses with a specific label."""
        if not self.connected:
            return []
        
        try:
            query = self.db.collection('address_labels').where('label', '==', label)
            if chain:
                query = query.where('chain', '==', chain.upper())
            
            docs = query.stream()
            addresses = set()
            for doc in docs:
                data = doc.to_dict()
                addr = data.get('address', '').strip()
                # Only add non-empty addresses to prevent false matches
                if addr:
                    addresses.add(addr)
            
            return list(addresses)
        except Exception as e:
            logger.error(f"Failed to get addresses by label: {e}")
            return []
    
    def update_exposure_metrics(self, metrics: Dict[str, Any]):
        """Insert or update exposure metrics for an address."""
        if not self.connected:
            return
        
        try:
            doc_id = self._get_metrics_doc_id(metrics['address'], metrics['chain'])
            doc_ref = self.db.collection('exposure_metrics').document(doc_id)
            
            data = {
                'address': metrics['address'].lower(),
                'chain': metrics['chain'].upper(),
                'direct_blacklist_hits_30': metrics.get('direct_blacklist_hits_30', 0),
                'direct_blacklist_hits_90': metrics.get('direct_blacklist_hits_90', 0),
                'direct_blacklist_hits_all': metrics.get('direct_blacklist_hits_all', 0),
                'direct_blacklist_value_30': metrics.get('direct_blacklist_value_30', 0.0),
                'direct_blacklist_value_90': metrics.get('direct_blacklist_value_90', 0.0),
                'direct_blacklist_value_all': metrics.get('direct_blacklist_value_all', 0.0),
                'mixer_tx_share_7': metrics.get('mixer_tx_share_7', 0.0),
                'mixer_tx_share_30': metrics.get('mixer_tx_share_30', 0.0),
                'mixer_tx_share_90': metrics.get('mixer_tx_share_90', 0.0),
                'indirect_exposure_1_hop': metrics.get('indirect_exposure_1_hop'),
                'indirect_exposure_2_hops': metrics.get('indirect_exposure_2_hops'),
                'indirect_exposure_3_hops': metrics.get('indirect_exposure_3_hops'),
                'clean_tx_ratio': metrics.get('clean_tx_ratio', 0.90),
                'sanctions_data_unknown': metrics.get('sanctions_data_unknown', False),
                'confidence': metrics.get('confidence', 0.0),
                'last_updated': firestore.SERVER_TIMESTAMP
            }
            
            doc_ref.set(data, merge=True)
            logger.info(f"Updated exposure metrics for {metrics['address']} on {metrics['chain']}")
        except Exception as e:
            logger.error(f"Failed to update exposure metrics: {e}")
    
    def get_exposure_metrics(self, address: str, chain: str) -> Optional[Dict[str, Any]]:
        """Get exposure metrics for an address."""
        if not self.connected:
            return None
        
        try:
            doc_id = self._get_metrics_doc_id(address, chain)
            doc_ref = self.db.collection('exposure_metrics').document(doc_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                # Convert Firestore timestamp to Unix timestamp if needed
                last_updated = data.get('last_updated')
                if last_updated and hasattr(last_updated, 'timestamp'):
                    last_updated = int(last_updated.timestamp())
                
                return {
                    'address': data.get('address', ''),
                    'chain': data.get('chain', ''),
                    'direct_blacklist_hits_30': data.get('direct_blacklist_hits_30', 0),
                    'direct_blacklist_hits_90': data.get('direct_blacklist_hits_90', 0),
                    'direct_blacklist_hits_all': data.get('direct_blacklist_hits_all', 0),
                    'direct_blacklist_value_30': data.get('direct_blacklist_value_30', 0.0),
                    'direct_blacklist_value_90': data.get('direct_blacklist_value_90', 0.0),
                    'direct_blacklist_value_all': data.get('direct_blacklist_value_all', 0.0),
                    'mixer_tx_share_7': data.get('mixer_tx_share_7', 0.0),
                    'mixer_tx_share_30': data.get('mixer_tx_share_30', 0.0),
                    'mixer_tx_share_90': data.get('mixer_tx_share_90', 0.0),
                    'indirect_exposure_1_hop': data.get('indirect_exposure_1_hop'),
                    'indirect_exposure_2_hops': data.get('indirect_exposure_2_hops'),
                    'indirect_exposure_3_hops': data.get('indirect_exposure_3_hops'),
                    'clean_tx_ratio': data.get('clean_tx_ratio', 0.90),
                    'sanctions_data_unknown': data.get('sanctions_data_unknown', False),
                    'confidence': data.get('confidence', 0.0),
                    'last_updated': last_updated
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get exposure metrics: {e}")
            return None
    
    def save_protocol_registry(self, protocol: ProtocolRegistry):
        """Save or update protocol registry entry."""
        if not self.connected:
            return
        
        try:
            doc_ref = self.db.collection('protocol_registry').document(protocol.protocol_id)
            
            # Convert incidents to dict
            incidents_data = []
            for incident in protocol.incidents:
                incidents_data.append({
                    'date': incident.date,
                    'description': incident.description,
                    'amount_lost_usd': incident.amount_lost_usd,
                    'severity': incident.severity,
                    'source': incident.source
                })
            
            data = {
                'protocol_id': protocol.protocol_id,
                'name': protocol.name,
                'slug': protocol.slug,
                'category': protocol.category,
                'chain': protocol.chain,
                'chains': getattr(protocol, 'chains', []) or [],
                'contract_addresses': protocol.contract_addresses,
                'tvl': protocol.tvl,
                'tvl_normalized': protocol.tvl_normalized,
                'age_days': protocol.age_days,
                'longevity_score': protocol.longevity_score,
                'launch_date': protocol.launch_date,
                'audit_score': protocol.audit_score,
                'audit_count': protocol.audit_count,
                'audit_firms': protocol.audit_firms,
                'last_audit_date': protocol.last_audit_date,
                'bounty_present': protocol.bounty_present,
                'incidents': incidents_data,
                'incident_penalty': protocol.incident_penalty,
                'l2_risk_score': protocol.l2_risk_score,
                'l2_technology': protocol.l2_technology,
                'protocol_score': protocol.protocol_score,
                'confidence': protocol.confidence,
                'last_updated': firestore.SERVER_TIMESTAMP,
                'data_sources': protocol.data_sources
            }
            
            doc_ref.set(data, merge=True)
            logger.info(f"Saved protocol registry: {protocol.protocol_id}")
        except Exception as e:
            logger.error(f"Failed to save protocol registry: {e}")
    
    def get_protocol_registry(self, protocol_id: str) -> Optional[ProtocolRegistry]:
        """Get protocol registry entry by ID."""
        if not self.connected:
            return None
        
        try:
            doc_ref = self.db.collection('protocol_registry').document(protocol_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                
                # Convert incidents back to ProtocolIncident objects
                incidents = []
                for inc_data in data.get('incidents', []):
                    incidents.append(ProtocolIncident(
                        date=inc_data.get('date', ''),
                        description=inc_data.get('description', ''),
                        amount_lost_usd=inc_data.get('amount_lost_usd'),
                        severity=inc_data.get('severity', 'medium'),
                        source=inc_data.get('source')
                    ))
                
                return ProtocolRegistry(
                    protocol_id=data.get('protocol_id', ''),
                    name=data.get('name', ''),
                    slug=data.get('slug'),
                    category=data.get('category'),
                    chain=data.get('chain'),
                    chains=data.get('chains', []) or [],
                    contract_addresses=data.get('contract_addresses', []),
                    tvl=data.get('tvl', 0.0),
                    tvl_normalized=data.get('tvl_normalized', 0.0),
                    age_days=data.get('age_days', 0),
                    longevity_score=data.get('longevity_score', 0.0),
                    launch_date=data.get('launch_date'),
                    audit_score=data.get('audit_score', 0.0),
                    audit_count=data.get('audit_count', 0),
                    audit_firms=data.get('audit_firms', []),
                    last_audit_date=data.get('last_audit_date'),
                    bounty_present=data.get('bounty_present', False),
                    incidents=incidents,
                    incident_penalty=data.get('incident_penalty', 0.0),
                    l2_risk_score=data.get('l2_risk_score', 0.0),
                    l2_technology=data.get('l2_technology'),
                    protocol_score=data.get('protocol_score', 0.5),
                    confidence=data.get('confidence', 0.0),
                    last_updated=data.get('last_updated'),
                    data_sources=data.get('data_sources', [])
                )
            return None
        except Exception as e:
            logger.error(f"Failed to get protocol registry: {e}")
            return None
    
    def get_protocol_by_contract(self, contract_address: str) -> Optional[ProtocolRegistry]:
        """Get protocol by contract address."""
        if not self.connected:
            return None
        
        try:
            # Search for protocol with this contract address
            query = self.db.collection('protocol_registry').where(
                'contract_addresses', 'array_contains', contract_address.lower()
            ).limit(1)
            
            docs = list(query.stream())
            if docs:
                data = docs[0].to_dict()
                
                # Convert incidents
                incidents = []
                for inc_data in data.get('incidents', []):
                    incidents.append(ProtocolIncident(
                        date=inc_data.get('date', ''),
                        description=inc_data.get('description', ''),
                        amount_lost_usd=inc_data.get('amount_lost_usd'),
                        severity=inc_data.get('severity', 'medium'),
                        source=inc_data.get('source')
                    ))
                
                return ProtocolRegistry(
                    protocol_id=data.get('protocol_id', ''),
                    name=data.get('name', ''),
                    slug=data.get('slug'),
                    category=data.get('category'),
                    chain=data.get('chain'),
                    chains=data.get('chains', []) or [],
                    contract_addresses=data.get('contract_addresses', []),
                    tvl=data.get('tvl', 0.0),
                    tvl_normalized=data.get('tvl_normalized', 0.0),
                    age_days=data.get('age_days', 0),
                    longevity_score=data.get('longevity_score', 0.0),
                    launch_date=data.get('launch_date'),
                    audit_score=data.get('audit_score', 0.0),
                    audit_count=data.get('audit_count', 0),
                    audit_firms=data.get('audit_firms', []),
                    last_audit_date=data.get('last_audit_date'),
                    bounty_present=data.get('bounty_present', False),
                    incidents=incidents,
                    incident_penalty=data.get('incident_penalty', 0.0),
                    l2_risk_score=data.get('l2_risk_score', 0.0),
                    l2_technology=data.get('l2_technology'),
                    protocol_score=data.get('protocol_score', 0.5),
                    confidence=data.get('confidence', 0.0),
                    last_updated=data.get('last_updated'),
                    data_sources=data.get('data_sources', [])
                )
            return None
        except Exception as e:
            logger.error(f"Failed to get protocol by contract: {e}")
            return None
    
    def get_all_protocols(self, limit: int = 100) -> List[ProtocolRegistry]:
        """Get all protocols, optionally limited."""
        if not self.connected:
            return []
        
        try:
            query = self.db.collection('protocol_registry').limit(limit)
            docs = query.stream()
            
            protocols = []
            for doc in docs:
                data = doc.to_dict()
                
                # Convert incidents
                incidents = []
                for inc_data in data.get('incidents', []):
                    incidents.append(ProtocolIncident(
                        date=inc_data.get('date', ''),
                        description=inc_data.get('description', ''),
                        amount_lost_usd=inc_data.get('amount_lost_usd'),
                        severity=inc_data.get('severity', 'medium'),
                        source=inc_data.get('source')
                    ))
                
                protocols.append(ProtocolRegistry(
                    protocol_id=data.get('protocol_id', ''),
                    name=data.get('name', ''),
                    slug=data.get('slug'),
                    category=data.get('category'),
                    chain=data.get('chain'),
                    contract_addresses=data.get('contract_addresses', []),
                    tvl=data.get('tvl', 0.0),
                    tvl_normalized=data.get('tvl_normalized', 0.0),
                    age_days=data.get('age_days', 0),
                    longevity_score=data.get('longevity_score', 0.0),
                    launch_date=data.get('launch_date'),
                    audit_score=data.get('audit_score', 0.0),
                    audit_count=data.get('audit_count', 0),
                    audit_firms=data.get('audit_firms', []),
                    last_audit_date=data.get('last_audit_date'),
                    bounty_present=data.get('bounty_present', False),
                    incidents=incidents,
                    incident_penalty=data.get('incident_penalty', 0.0),
                    l2_risk_score=data.get('l2_risk_score', 0.0),
                    l2_technology=data.get('l2_technology'),
                    protocol_score=data.get('protocol_score', 0.5),
                    confidence=data.get('confidence', 0.0),
                    last_updated=data.get('last_updated'),
                    data_sources=data.get('data_sources', [])
                ))
            
            return protocols
        except Exception as e:
            logger.error(f"Failed to get all protocols: {e}")
            return []


# Alias for backward compatibility (if any code still references ClickHouseDB)
ClickHouseDB = FirestoreDB

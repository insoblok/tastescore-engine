"""API endpoints for protocol reputation system."""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional
from service.database import FirestoreDB
from service.protocols.protocol_sync import ProtocolSyncJob
from service.protocols.scoring_calculator import ProtocolScoringCalculator
from service.models import ProtocolSafetyCheck, ProtocolRegistry
from service.utils import logger

router = APIRouter(prefix="/api/protocols")

db = FirestoreDB()
protocol_sync = ProtocolSyncJob()
scorer = ProtocolScoringCalculator()


@router.get("/check")
def check_protocol_safety(
    contract_address: str = Query(..., description="Smart contract address to check"),
    chain: Optional[str] = Query(None, description="Blockchain chain (optional)")
):
    """
    Check protocol safety for a contract address.
    
    Returns safety assessment with score, quality, and recommendations.
    """
    try:
        contract_address = contract_address.lower().strip()
        
        # Try to find protocol by contract address
        protocol = db.get_protocol_by_contract(contract_address)
        
        if protocol:
            # Protocol found in registry
            quality = scorer.get_protocol_quality(protocol.protocol_score)
            safe = protocol.protocol_score >= 0.5
            
            # Calculate reward/penalty
            reward_multiplier = 1.0
            penalty_fee = 0.0
            warning = None
            message = None
            
            if protocol.protocol_score >= 0.8:
                reward_multiplier = 1.5
                message = "Highly reputable protocol - bonus rewards available"
            elif protocol.protocol_score >= 0.6:
                reward_multiplier = 1.2
                message = "Good protocol - standard rewards"
            elif protocol.protocol_score >= 0.5:
                reward_multiplier = 1.0
                message = "Moderate risk protocol"
            elif protocol.protocol_score >= 0.3:
                penalty_fee = 0.05  # 5% extra fee
                warning = "High risk protocol detected - proceed with caution"
            else:
                penalty_fee = 0.10  # 10% extra fee
                warning = "Very high risk protocol - significant caution advised"
            
            return JSONResponse(content={
                "success": True,
                "data": {
                    "contract_address": contract_address,
                    "protocol": {
                        "protocol_id": protocol.protocol_id,
                        "name": protocol.name,
                        "category": protocol.category,
                        "chain": protocol.chain
                    },
                    "protocol_score": protocol.protocol_score,
                    "quality": quality,
                    "safe": safe,
                    "reward_multiplier": reward_multiplier,
                    "penalty_fee": penalty_fee,
                    "warning": warning,
                    "message": message,
                    "confidence": protocol.confidence,
                    "details": {
                        "tvl": protocol.tvl,
                        "age_days": protocol.age_days,
                        "audit_count": protocol.audit_count,
                        "incident_count": len(protocol.incidents),
                        "bounty_present": protocol.bounty_present
                    }
                }
            })
        else:
            # Unknown contract - return low score (not neutral) to indicate risk
            return JSONResponse(content={
                "success": True,
                "data": {
                    "contract_address": contract_address,
                    "protocol": None,
                    "protocol_score": 0.2,  # Low score for unknown protocols (not 0.5)
                    "quality": "unknown",
                    "safe": False,  # Unknown = not safe by default
                    "reward_multiplier": 0.5,  # Reduced rewards for unknown
                    "penalty_fee": 0.05,  # 5% extra fee for unknown protocols
                    "warning": "Protocol not found in registry - proceed with caution",
                    "message": "Unknown protocol - insufficient data for safety assessment",
                    "confidence": 0.0,
                    "details": {}
                }
            })
    
    except Exception as e:
        logger.error(f"Error checking protocol safety: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{protocol_id}")
def get_protocol(
    protocol_id: str
):
    """Get detailed protocol information by ID."""
    try:
        protocol = db.get_protocol_registry(protocol_id.lower())
        
        if not protocol:
            raise HTTPException(status_code=404, detail="Protocol not found")
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "protocol_id": protocol.protocol_id,
                "name": protocol.name,
                "slug": protocol.slug,
                "category": protocol.category,
                "chain": protocol.chain,
                "contract_addresses": protocol.contract_addresses,
                "tvl": protocol.tvl,
                "tvl_normalized": protocol.tvl_normalized,
                "age_days": protocol.age_days,
                "longevity_score": protocol.longevity_score,
                "launch_date": protocol.launch_date,
                "audit_score": protocol.audit_score,
                "audit_count": protocol.audit_count,
                "audit_firms": protocol.audit_firms,
                "last_audit_date": protocol.last_audit_date,
                "bounty_present": protocol.bounty_present,
                "incidents": [
                    {
                        "date": inc.date,
                        "description": inc.description,
                        "amount_lost_usd": inc.amount_lost_usd,
                        "severity": inc.severity,
                        "source": inc.source
                    }
                    for inc in protocol.incidents
                ],
                "incident_penalty": protocol.incident_penalty,
                "l2_risk_score": protocol.l2_risk_score,
                "l2_technology": protocol.l2_technology,
                "protocol_score": protocol.protocol_score,
                "quality": scorer.get_protocol_quality(protocol.protocol_score),
                "confidence": protocol.confidence,
                "last_updated": protocol.last_updated,
                "data_sources": protocol.data_sources
            }
        })
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting protocol: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
def list_protocols(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of protocols to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_score: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum protocol score")
):
    """List all protocols with optional filters."""
    try:
        protocols = db.get_all_protocols(limit=limit)
        
        # Apply filters
        if category:
            protocols = [p for p in protocols if p.category and p.category.lower() == category.lower()]
        
        if min_score is not None:
            protocols = [p for p in protocols if p.protocol_score >= min_score]
        
        # Sort by score descending
        protocols.sort(key=lambda p: p.protocol_score, reverse=True)
        
        return JSONResponse(content={
            "success": True,
            "data": [
                {
                    "protocol_id": p.protocol_id,
                    "name": p.name,
                    "category": p.category,
                    "chain": p.chain,
                    "tvl": p.tvl,
                    "protocol_score": p.protocol_score,
                    "quality": scorer.get_protocol_quality(p.protocol_score),
                    "confidence": p.confidence
                }
                for p in protocols
            ],
            "count": len(protocols)
        })
    
    except Exception as e:
        logger.error(f"Error listing protocols: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync")
def sync_protocols(
    protocol_slug: Optional[str] = Query(None, description="Sync specific protocol by slug, or all if not provided")
):
    """Manually trigger protocol sync (admin endpoint)."""
    try:
        if protocol_slug:
            success = protocol_sync.sync_single_protocol(protocol_slug)
            if not success:
                raise HTTPException(status_code=404, detail=f"Protocol {protocol_slug} not found or sync failed")
            return JSONResponse(content={
                "success": True,
                "message": f"Protocol {protocol_slug} synced successfully"
            })
        else:
            success = protocol_sync.sync_all_protocols()
            if not success:
                raise HTTPException(status_code=500, detail="Protocol sync failed")
            return JSONResponse(content={
                "success": True,
                "message": "All protocols synced successfully"
            })
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing protocols: {e}")
        raise HTTPException(status_code=500, detail=str(e))

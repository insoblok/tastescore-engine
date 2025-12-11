"""API endpoints for sanctions and mixer detection."""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional
from service.database import FirestoreDB
from service.sanctions.metrics_calculator import MetricsCalculator
from service.sanctions.ofac_ingester import OFACIngester
from service.utils import logger

router = APIRouter(prefix="/api/sanctions")

db = FirestoreDB()
metrics_calc = MetricsCalculator()
ofac_ingester = OFACIngester()


@router.get("/check")
def check_address(
    address: str = Query(..., description="Wallet address to check"),
    chain: Optional[str] = Query(None, description="Blockchain chain (optional, searches all chains if not provided)")
):
    """
    Check if an address is in sanctions, mixer, or watchlist.
    If chain is not provided, searches across all blockchains.
    
    Returns:
        JSON with address label information
    """
    try:
        # Normalize address input (strip whitespace, lowercase)
        address_normalized = address.strip()
        
        # Log the query for debugging
        logger.info(f"Checking address: '{address_normalized}' (original: '{address}'), chain: {chain}")
        
        # Search across all chains if chain not provided
        label = db.get_address_label(address_normalized, chain.upper() if chain else None)
        
        if label:
            logger.info(f"Found label for address '{address_normalized}': chain={label.chain}, label={label.label}")
            return JSONResponse(content={
                "success": True,
                "data": {
                    "address": label.address,
                    "chain": label.chain,
                    "label": label.label,
                    "program": label.program,
                    "source": label.source,
                    "first_seen": label.first_seen,
                    "metadata": label.metadata,
                    "is_blacklisted": True
                }
            })
        else:
            logger.info(f"No label found for address '{address_normalized}'")
            return JSONResponse(content={
                "success": True,
                "data": {
                    "address": address_normalized,
                    "chain": chain if chain else None,
                    "label": None,
                    "is_blacklisted": False
                }
            })
    except Exception as e:
        logger.error(f"Error checking address '{address}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
def get_exposure_metrics(
    address: str = Query(..., description="Wallet address"),
    chain: str = Query(..., description="Blockchain chain (BTC, ETH, BNB, SOL)")
):
    """
    Get exposure metrics for an address.
    
    Returns:
        JSON with exposure metrics including blacklist hits, mixer shares, etc.
    """
    try:
        chain = chain.upper()
        metrics = db.get_exposure_metrics(address, chain)
        
        if metrics:
            return JSONResponse(content={
                "success": True,
                "data": metrics
            })
        else:
            return JSONResponse(content={
                "success": True,
                "data": {
                    "address": address,
                    "chain": chain,
                    "message": "No metrics available. Metrics will be calculated on next transaction scan."
                }
            })
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/risk-flags")
def get_risk_flags(
    address: str = Query(..., description="Wallet address"),
    chain: Optional[str] = Query(None, description="Blockchain chain (optional, searches all chains if not provided)")
):
    """
    Get risk flags for an address.
    If chain is not provided, searches across all blockchains.
    
    Returns:
        JSON with risk flags
    """
    try:
        # If no chain provided, get all labels and check across all chains
        if chain:
            chain = chain.upper()
            risk_flags = metrics_calc.get_risk_flags(address, chain)
        else:
            # Search across all chains - get first match or aggregate
            all_labels = db.get_all_address_labels(address)
            if all_labels:
                # Use the first label's chain for risk flags calculation
                risk_flags = metrics_calc.get_risk_flags(address, all_labels[0].chain)
            else:
                # No labels found, return default risk flags
                from service.models import RiskFlags
                risk_flags = RiskFlags()
        
        return JSONResponse(content={
            "success": True,
            "data": risk_flags.model_dump()
        })
    except Exception as e:
        logger.error(f"Error getting risk flags: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest")
def trigger_ingestion():
    """
    Manually trigger OFAC sanctions ingestion.
    
    Note: This is typically run nightly via scheduled job.
    """
    try:
        success = ofac_ingester.ingest()
        
        if success:
            return JSONResponse(content={
                "success": True,
                "message": "OFAC ingestion completed successfully"
            })
        else:
            return JSONResponse(
                content={
                    "success": False,
                    "message": "OFAC ingestion failed or no data found"
                },
                status_code=500
            )
    except Exception as e:
        logger.error(f"Error during ingestion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calculate-metrics")
def calculate_metrics(
    address: str = Query(..., description="Wallet address"),
    chain: str = Query(..., description="Blockchain chain (BTC, ETH, BNB, SOL)"),
    transactions: Optional[list] = None
):
    """
    Calculate exposure metrics for an address based on transaction history.
    
    Note: This is typically called automatically when scanning an address.
    """
    try:
        chain = chain.upper()
        
        # If transactions not provided, return existing metrics
        if not transactions:
            metrics = db.get_exposure_metrics(address, chain)
            if metrics:
                return JSONResponse(content={
                    "success": True,
                    "data": metrics
                })
            else:
                return JSONResponse(content={
                    "success": False,
                    "message": "No transactions provided and no existing metrics found"
                }, status_code=400)
        
        # Calculate metrics
        metrics = metrics_calc.calculate_exposure_metrics(
            address=address,
            chain=chain,
            transactions=transactions,
            sanctions_data_available=True
        )
        
        return JSONResponse(content={
            "success": True,
            "data": metrics.model_dump()
        })
    except Exception as e:
        logger.error(f"Error calculating metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


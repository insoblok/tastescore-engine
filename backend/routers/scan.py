from typing import Optional
NULL: Optional[None] = None
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from service.blockchain import BlockchainClient
from service.btc.btc import BitcoinScan
from service.eth.eth import EthereumScan
from service.bnb.bnb import BNBScan
from service.solana.sol import SolanaScan

router = APIRouter(prefix="/api/explore")

@router.get("/")
def get_info(request: Request):
    """Retrieve blockchain wallet transaction information."""
    params = dict(request.query_params)
    wallet = params.get("wallet")
    network = int(params.get("network"))
    print(network)
    if not wallet or not network:
        raise HTTPException(status_code=400, detail="Wallet address must be entered.")
    result = {}
    if (network == 2):
        eScan = EthereumScan()
        summary = eScan.get_eth_address_summary(wallet)
        histories = eScan.get_eth_address(wallet)
        result["histories"] = histories
        result["summary"] = summary
    elif (network == 1):
        bScan = BitcoinScan()
        histories = bScan.get_address(wallet)
        result["histories"] = histories
    elif (network == 3):
        print("This is BNBScan")
        bnbScan = BNBScan()
        result = bnbScan.get_bnb_transactions(wallet)
        print(result)
    elif (network == 4):
        solScan = SolanaScan()
        result["histories"] = solScan.get_sol_transactions(wallet)
        result["summary"] = solScan.get_sol_address_summary(wallet)
        
    return JSONResponse(content={"success": True, "data": result}, status_code=200)        
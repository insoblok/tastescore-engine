from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from service.blockchain import BlockchainClient
from service.btc import BitcoinScan
from service.eth import EthereumScan

router = APIRouter(prefix="/api/explore")

@router.get("/")
def get_info(request: Request):
    """Retrieve blockchain wallet transaction information."""
    params = dict(request.query_params)
    wallet = params.get("wallet")
    if not wallet:
        raise HTTPException(status_code=400, detail="Wallet address must be entered.")
    network = BlockchainClient().check_wallet_network(wallet)
    print(f"network is {network}")
    result = {}
    if (network == 0):
        eScan = EthereumScan()
        summary = eScan.get_eth_address_summary(wallet)
        histories = eScan.get_eth_address(wallet)
        result["histories"] = histories
        result["summary"] = summary
        print(result)
    elif (network == 1):
        bScan = BitcoinScan()
        histories = bScan.get_address(wallet)
        result["histories"] = histories
    return JSONResponse(content={"success": True, "data": result}, status_code=200)        
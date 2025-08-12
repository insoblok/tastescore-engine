from service.btc import BitcoinScan

BTC_NETWORK = 1
ETH_NETWORK = 0
SATOSHI_TO_BITCOIN = 100000000


class BlockchainClient:
    """Python implementation of the Go Blockchain client"""
    def __init__(self):
        print("")
        
    def check_wallet_network(self, wallet_addr: str) -> int:
        if len(wallet_addr) == 42 and wallet_addr.startswith("0x"):
            return ETH_NETWORK
        elif 25 < len(wallet_addr) < 36 and BitcoinScan().validate_btc_address_format(wallet_addr):
            return BTC_NETWORK
        elif len(wallet_addr) == 42 and wallet_addr.startswith("bc1"):
            return BTC_NETWORK
        return -1
    
    
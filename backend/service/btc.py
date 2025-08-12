import requests
from typing import List, Set
from .models import Address, AddressDTO, Tx, TxDTO
from .utils import Utils


class BitcoinScan:
    """Service for interacting with Bitcoin blockchain APIs."""
    
    SATOSHI_TO_BITCOIN = 100000000

    def __init__(self) -> None:
        self.info_api = "https://blockchain.info"
        self.price_api = "https://blockchain.info/ticker"

    def get_address(self, btc_address: str) -> Address:
        """
        Get Bitcoin address information including balance and transactions.

        Args:
            btc_address: Bitcoin address string (e.g. "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")

        Returns:
            Address dataclass with address details

        Raises:
            ValueError: If address is invalid or API request fails
        """
        if not self.validate_btc_address_format(btc_address):
            raise ValueError("Invalid Bitcoin address format")

        url = f"{self.info_api}/address/{btc_address}?format=json"

        try:
            data = Utils().load_response(url)
            return self._parse_address_data(data)
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to fetch BTC address: {e}")
        except KeyError as e:
            raise ValueError(f"Invalid response format: {e}")

    def _parse_address_data(self, data: dict) -> Address:
        """Parse raw API response into AddressDTO object."""
        srcs: Set[str] = set()
        dsts: Set[str] = set()
        tx_dtos: List[TxDTO] = []

        for tx in data['txs']:
            tx_dtos.append(self._create_transaction_dto(tx))

        return AddressDTO(
            hash160=data['hash160'],
            token="BTC",
            address=data['address'],
            n_tx=data['n_tx'],
            total_received=data['total_received'],
            total_sent=data['total_sent'],
            final_balance=float(data['final_balance']) / self.SATOSHI_TO_BITCOIN,
            txs=tx_dtos
        ).model_dump_json()

    def _create_transaction_dto(self, tx: dict) -> TxDTO:
        """Create TxDTO from transaction data."""
        return TxDTO(
            balance=tx["balance"] / self.SATOSHI_TO_BITCOIN,
            result=float(tx["result"]) / self.SATOSHI_TO_BITCOIN,
            time=tx["time"],
            hash=tx["hash"],
            fee=tx["fee"],
            inputs=tx.get("inputs", []),
            outputs=tx.get("out", [])
        )

    def validate_btc_address_format(self, wallet_addr: str) -> bool:
        """Validate Bitcoin address format."""
        return wallet_addr.startswith(("1", "3", "bc1"))

    def get_bitcoin_price(self) -> float:
        """Get current Bitcoin price in USD."""
        resp = Utils().load_response(self.price_api)
        return resp["USD"]["last"]
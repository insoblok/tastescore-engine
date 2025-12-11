import requests
from typing import List
from ..models import Address, AddressDTO, TxDTO
from dotenv import load_dotenv
from ..utils import Utils
import os
from service.constants import SATOSHI_TO_BITCOIN

load_dotenv()

class BitcoinScan:
    """Service for interacting with Bitcoin blockchain APIs."""
    

    def __init__(self) -> None:
        self.info_api = os.getenv("BTC_INFO_URL")
        self.price_api = os.getenv("BTC_PRICE_URL")

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
        tx_dtos: List[TxDTO] = []

        for tx in data['txs']:
            tx_dtos.append(self._create_transaction_dto(tx))

        return AddressDTO(
            hash160=data.get('hash160', ''),
            token="BTC",
            address=data.get('address', ''),
            n_tx=int(data.get('n_tx', 0)),
            total_received=int(data.get('total_received', 0)),
            total_sent=int(data.get('total_sent', 0)),
            final_balance=float(data.get('final_balance', 0)) / SATOSHI_TO_BITCOIN,
            txs=tx_dtos
        ).model_dump_json()

    def _create_transaction_dto(self, tx: dict) -> TxDTO:
        """Create TxDTO from transaction data."""
        return TxDTO(
            balance=float(tx.get("balance", 0.0)) / SATOSHI_TO_BITCOIN,
            result=float(tx.get("result", 0.0)) / SATOSHI_TO_BITCOIN,
            time=int(tx.get("time", 0)),
            hash=tx.get("hash", ""),
            fee=int(tx.get("fee", 0)),
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
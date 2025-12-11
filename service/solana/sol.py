import requests
from typing import List
from ..models import SOLTransactionDTO, SOLResponse, SOLAddressSummary, SOLTransfer
from ..utils import Utils
from dotenv import load_dotenv
import os

load_dotenv()


class SolanaScan:
    """Service for interacting with Solana blockchain APIs."""

    PAGE_SIZE = 20
    PAGE_NO = 0

    def __init__(self) -> None:
        # Using the public Helius RPC for simplicity; replace with your API key in production
        self.url = os.getenv("SOLANA_HELIUS_MAINNET_URL")
        self.enhanced_url = os.getenv("SOLANA_HELIUS_MAINNET_ENHANCED_URL")
        self.api_key = os.getenv("SOLANA_HELIUS_API_KEY")

    def get_sol_transactions(self, sol_address: str) -> SOLResponse:
        """
        Get full Solana address information with transactions.

        Args:
            sol_address: Solana address string (e.g. "vines1vzrYbzLMRdu58ou5XTby4qAqVRLmqo36NKPTg")

        Returns:
            SOLResponse with transaction history

        Raises:
            ValueError: If address is invalid or API request fails
        """

        url = f"{self.enhanced_url}/v0/addresses/{sol_address}/transactions?api-key={self.api_key}"

        try:
            # Helius transactions API uses REST with API key parameter
            params = {
                "api-key": self.api_key,  # Replace with actual API key
            }
            response = Utils().load_response(url)
            transactions = self._parse_transactions(response, sol_address)
            return self._build_sol_response(transactions)
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to fetch SOL address: {e}")
        except KeyError as e:
            raise ValueError(f"Invalid response format: {e}")

    def get_sol_address_summary(self, sol_address: str) -> SOLAddressSummary:
        """
        Get Solana address summary information.

        Args:
            sol_address: Solana address string

        Returns:
            SOLAddressSummary dataclass with summary info

        Raises:
            ValueError: If address is invalid or API request fails
        """
        url = f"{self.url}?api-key={self.api_key}"

        try:
            # Payload to get account balance and info
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getAccountInfo",
                "params": [
                    sol_address,
                    {
                        "encoding": "base58"
                    }
                ]
            }
            data = Utils().load_response(url, method="post", params=payload)
            price = self._get_sol_price()
            transaction_cnt = self._get_signatures_for_address(sol_address)
            return self._parse_summary_data(data.get("result", {}), price, transaction_cnt, sol_address)
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to fetch SOL summary: {e}")
        except KeyError as e:
            raise ValueError(f"Invalid response format: {e}")

    def _parse_transactions(self, transactions: List[dict], address: str) -> List[SOLTransactionDTO]:
        """Parse raw transaction data into SOLAddressDTO objects."""
        return [
            self._create_transaction_dto(transaction, address)
            for transaction in transactions
        ]

    def _create_transaction_dto(self, transaction: dict, address: str) -> SOLTransactionDTO:
        """Create SOLAddressDTO from transaction data."""
        # For Solana, we need to determine direction based on the address
        # This is a simplified approach - real implementation would need more logic
        signer = transaction.get("signer", "")
        direction = "out" if signer == address else "in"
        return SOLTransactionDTO(
            description=transaction.get("description", ""),
            direction=direction,
            type=transaction.get("type", ""),
            source=transaction.get("source", ""),
            fee=transaction.get("fee", 0),
            feePayer=transaction.get("feePayer", ""),
            signature=transaction.get("signature", ""),
            slot=transaction.get("slot", 0),
            timestamp=transaction.get("timestamp", 0),
            nativeTransfers=[SOLTransfer(fromUserAccount=one.get("fromUserAccount", ""), toUserAccount=one.get("toUserAccount", ""), amount=one.get("amount", 0)) for one in transaction.get("nativeTransfers", [])]
        )

    def _build_sol_response(self, transactions: List[SOLTransactionDTO]) -> SOLResponse:
        """Build SOLResponse from parsed transactions."""
        return SOLResponse(
            transactions=transactions,
            token="SOL",
            page=self.PAGE_NO,
            size=self.PAGE_SIZE
        ).model_dump_json()

    def _parse_summary_data(self, data: dict, price:dict, cnt: int, address: str) -> SOLAddressSummary:
        """Parse raw summary data into SOLAddressSummary object."""
        # Get balance information
        balance_lamports = data.get("value", {}).get("lamports", 0) if data else 0
        balance_sol = balance_lamports / 1_000_000_000
        print(f"Price is {price}")
        return SOLAddressSummary(
            address=address,
            price=price.get("price_per_token", 0),
            balance=balance_sol,
            balanceLamports=balance_lamports,
            transactionCount=cnt,  
            executable=data.get("value", {}).get("executable", False) if data else False,
            owner=data.get("value", {}).get("owner", "") if data else ""
        ).model_dump_json()
        
    def _get_sol_price(self):
        json = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "getAsset",
            "params": {
            "id": "So11111111111111111111111111111111111111112",
            "displayOptions": {
                "showFungible": False
            }
            }
        }
        url = f"{self.url}?api-key={self.api_key}"
        response = Utils().load_response(url, method="post", params=json)
        return response.get("result", {}).get("token_info").get("price_info", {})
        
    def _get_signatures_for_address(self, address: str):
        json = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "getSignaturesForAddress",
            "params": [
                address
            ]
        }
        url = f"{self.url}?api-key={self.api_key}"
        response = Utils().load_response(url, method="post", params=json)
        return len(response.get("result", []))
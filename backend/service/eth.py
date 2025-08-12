import requests
from typing import List
from .models import ETHAddress, ETHAddressDTO, ETHResponse, ETHAddressSummary
from .utils import Utils


class EthereumScan:
    """Service for interacting with Ethereum blockchain APIs."""

    PAGE_SIZE = 20
    PAGE_NO = 0
    ETHER_IN_WEI = 10 ** 18

    def __init__(self) -> None:
        self.api = "https://api.blockchain.info"

    def get_eth_address(self, eth_address: str) -> ETHResponse:
        """
        Get full Ethereum address information with transactions.

        Args:
            eth_address: Ethereum address string (e.g. "0x742d35Cc6634C0532925a3b844Bc454e4438f44e")

        Returns:
            ETHResponse with transaction history

        Raises:
            ValueError: If address is invalid or API request fails
        """
        url = self._build_transactions_url(eth_address)

        try:
            response = Utils().load_response(url)
            transactions = self._parse_transactions(response["transactions"])
            return self._build_eth_response(response, transactions)
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to fetch ETH address: {e}")
        except KeyError as e:
            raise ValueError(f"Invalid response format: {e}")

    def get_eth_address_summary(self, eth_address: str) -> ETHAddress:
        """
        Get Ethereum address summary information.

        Args:
            eth_address: Ethereum address string

        Returns:
            ETHAddress dataclass with summary info

        Raises:
            ValueError: If address is invalid or API request fails
        """
        url = f"{self.api}/v2/eth/data/account/{eth_address}/summary"

        try:
            data = Utils().load_response(url)
            return self._parse_summary_data(data)
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to fetch ETH summary: {e}")
        except KeyError as e:
            raise ValueError(f"Invalid response format: {e}")

    def _build_transactions_url(self, eth_address: str) -> str:
        """Construct the URL for fetching transactions."""
        return f"{self.api}/v2/eth/data/account/{eth_address}/transactions?page={self.PAGE_NO}&size={self.PAGE_SIZE}"

    def _parse_transactions(self, transactions: List[dict]) -> List[ETHAddressDTO]:
        """Parse raw transaction data into ETHAddressDTO objects."""
        return [
            self._create_transaction_dto(transaction)
            for transaction in transactions
        ]

    def _create_transaction_dto(self, transaction: dict) -> ETHAddressDTO:
        """Create ETHAddressDTO from transaction data."""
        return ETHAddressDTO(
            hash=transaction["hash"],
            success=transaction["success"],
            state=transaction["state"],
            time=transaction["timestamp"],
            blockNumber=transaction["blockNumber"],
            src=transaction["from"],
            dst=transaction["to"],
            amount=float(transaction["value"]) / self.ETHER_IN_WEI,
            fee=float(transaction["gasUsed"]) / self.ETHER_IN_WEI
        )

    def _build_eth_response(self, response: dict, transactions: List[ETHAddressDTO]) -> ETHResponse:
        """Build ETHResponse from API response and parsed transactions."""
        return ETHResponse(
            transactions=transactions,
            token="ETH",
            page=response['page'],
            size=response['size']
        ).model_dump_json()

    def _parse_summary_data(self, data: dict) -> ETHAddressSummary:
        """Parse raw summary data into ETHAddressSummary object."""
        return ETHAddressSummary(
            hash=data['hash'],
            nonce=data['nonce'],
            balance=float(data['balance']) / self.ETHER_IN_WEI,
            transactionCount=data['transactionCount'],
            internalTransactionCount=data['internalTransactionCount'],
            totalSent=float(data['totalSent']) / self.ETHER_IN_WEI,
            totalReceived=float(data['totalReceived']) / self.ETHER_IN_WEI,
            totalFees=float(data['totalFees']) / self.ETHER_IN_WEI,
            lastUpdatedAtNumber=data['lastUpdatedAtNumber'],
            tokenTransferCount=data['tokenTransferCount']
        ).model_dump_json()
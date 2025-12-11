from json import load
import requests
from typing import List
from dotenv import load_dotenv
import os
import json
from service.constants import ETHER_IN_WEI
from service.models import BNBTransactionDTO
from ..utils import Utils

load_dotenv()

class BNBScan:
    def __init__(self):
        self.api = os.getenv("ETHER_SCAN_HTTPS_URL")
        self.ether_scan_api_key = os.getenv("ETHER_SCAN_API_KEY")
    def get_bnb_transactions(self, address: str):
        url = self._build_transactions_url(address)
        response = Utils().load_response(url)
        print(response)
        transactions = []
        summary = {}
        total_received = 0
        total_sent = 0
        if(response['message'] == 'OK'): 
            transactionsResponse = self._parse_transactions(response["result"])
            for tx in transactionsResponse:
                transaction = json.loads(tx)
                transactions.append(transaction)
                value = int(transaction["value"]) / ETHER_IN_WEI
                if transaction["dst"].lower() == address.lower():
                    total_received += value
                elif transaction["src"].lower() == address.lower():
                    total_sent += value
            summary = self._get_wallet_summary(address)
            summary["total_received"] = total_received
            summary["total_sent"] = total_sent
        return self._build_eth_response(transactions, summary)         
        
    def _build_transactions_url(self, address: str) -> str:
        
        return f"{self.api}?chainid=56&module=account&action=txlist&address={address}&startblock=0&endblock=99999999&tag=latest&sort=asc&apikey={self.ether_scan_api_key}"

    def _parse_transactions(self, transactions):
        return [
            self._create_transaction_dto(transaction)
            for transaction in transactions
        ]
    
    def _create_transaction_dto(self, transaction:dict):
        return BNBTransactionDTO(
            blockNumber=transaction["blockNumber"],
            blockHash=transaction["blockHash"],
            time=transaction["timeStamp"],
            hash=transaction["hash"],
            transactionIndex=transaction["transactionIndex"],
            src=transaction["from"],
            dst=transaction["to"],
            value=transaction["value"],
            gas=transaction["gas"],
            gasPrice=transaction["gasPrice"],
            input=transaction["input"],
            contractAddress=transaction["contractAddress"],
            gasUsed=transaction["gasUsed"],
            isError=transaction["isError"],
        ).model_dump_json()

    def _build_eth_response(self, transactions, summary):
        return json.dumps({
            "transactions": transactions,
            "summary": summary,
            "token": "BNB"
        })
    
    def _get_bnb_balance(self, address):
        url = f"{self.api}?chainid=56&module=account&action=balance&address={address}&tag=latest&apikey={self.ether_scan_api_key}"
        response = requests.get(url).json()
        if response["status"] == "1":
            wei_balance = int(response["result"])
            bnb_balance = wei_balance / ETHER_IN_WEI
            return bnb_balance
        return None

    def _get_transaction_count(self, address):
        url = f"{self.api}?chainid=56&module=account&action=txlist&address={address}&startblock=0&endblock=99999999&sort=asc&apikey={self.ether_scan_api_key}"
        response = requests.get(url).json()
        if response["status"] == "1":
            return len(response["result"])
        return 0

    def _get_token_balances(self, address):
        url = f"{self.api}?chainid=56&module=account&action=tokentx&address={address}&startblock=0&endblock=99999999&sort=asc&apikey={self.ether_scan_api_key}"
        response = requests.get(url).json()
        tokens = {}
        if response["status"] == "1":
            for tx in response["result"]:
                symbol = tx["tokenSymbol"]
                decimals = int(tx["tokenDecimal"])
                value = int(tx["value"]) / (10 ** decimals)
                if tx["to"].lower() == address.lower():
                    tokens[symbol] = tokens.get(symbol, 0) + value
                elif tx["from"].lower() == address.lower():
                    tokens[symbol] = tokens.get(symbol, 0) - value
        return tokens

    def _get_wallet_summary(self, address):
        result = {}
        bnb_balance = self._get_bnb_balance(address)
        result["balance"] = bnb_balance       
        tx_count = self._get_transaction_count(address)
        result["transactionCount"] = tx_count
        result["tokens"] = {}
        tokens = self._get_token_balances(address)
        for symbol, amount in tokens.items():
            if amount > 0:
                result["tokens"][symbol] = amount
        return result
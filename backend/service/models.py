from typing import List
from pydantic import BaseModel, Field


class PrevOut(BaseModel):
    """Previous output data structure"""
    spent: bool
    tx_index: int
    type: int
    addr: str
    value: int
    n: int
    script: str

class Input(BaseModel):
    """Transaction input data structure"""
    sequence: int
    script: str
    prev_out: PrevOut
    witness: str
    index: int

class Out(BaseModel):
    """Transaction output data structure"""
    spent: bool
    tx_index: int
    type: int
    addr: str
    value: int
    n: int
    script: str

class Tx(BaseModel):
    """Bitcoin transaction data structure"""
    balance: int
    result: int
    ver: int
    size: int
    inputs: List[Input]
    time: int
    weight: int
    fee: int
    lock_time: int
    double_spend: bool
    block_index: int
    block_height: int
    tx_index: int
    vin_sz: int
    hash: str
    vout_sz: int
    relayed_by: str
    out: List[Out]

class TxDTO(BaseModel):
    """ Transaction Data Structure which will be consumed in the frontend """
    balance: float
    result: float
    time: int
    hash: str
    fee: int
    inputs: set[str]
    outputs: set[str]

class Address(BaseModel):
    """Bitcoin address data structure"""
    hash160: str
    address: str
    n_tx: int
    total_received: int
    total_sent: int
    final_balance: int
    txs: List[Tx]

class AddressDTO(BaseModel):
    """Bitcoin address data structure"""
    hash160: str
    token: str
    address: str
    n_tx: int
    total_received: int
    total_sent: int
    final_balance: float
    txs: List[TxDTO]



class ETHAddressSummary(BaseModel):
    """Ethereum address summary data structure"""
    hash: str
    nonce: str
    balance: float
    transactionCount: str
    internalTransactionCount: str
    totalSent: float
    totalReceived: float
    totalFees: float
    lastUpdatedAtNumber: str
    tokenTransferCount: str
    
class ETHAddress(BaseModel):
    """ Ethereum Address Data Structure """
    hash: str
    blockHash: str
    blockNumber: str
    to: str
    from_address: str = Field(..., alias="from")
    value: int
    nonce: int
    gasPrice: int
    gasLimit: int
    gasUsed: int
    data: str
    transactionIndex: int
    success: bool
    state: str
    timestamp: int
    internalTransactions: List[str]

class ETHAddressDTO(BaseModel):
    """ Ethereum Address Data Structure which will be consumed in frontend """
    hash: str
    success: bool
    state: str
    time: int
    blockNumber: int
    src: str
    dst: str
    amount: float
    fee: float

class ETHResponse(BaseModel):
    """Full Ethereum address response with transactions"""
    transactions: List[ETHAddressDTO]
    token: str
    page: str
    size: int

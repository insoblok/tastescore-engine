from typing import List, Optional
from pydantic import BaseModel, Field


class PrevOut(BaseModel):
    """Previous output data structure"""
    spent: Optional[bool] = False
    tx_index: Optional[int] = 0
    type: Optional[int] = 0
    addr: Optional[str] = ""
    value: Optional[int] = 0
    n: Optional[int] = 0
    script: Optional[str] = ""

class Input(BaseModel):
    """Transaction input data structure"""
    sequence: Optional[int] = 0
    script: Optional[str] = ""
    prev_out: PrevOut
    witness: Optional[str] = ""
    index: Optional[int] = 0

class Out(BaseModel):
    """Transaction output data structure"""
    spent: Optional[bool] = False
    tx_index: Optional[int] = 0
    type: Optional[int] = 0
    addr: Optional[str] = ""
    value: Optional[int] = 0
    n: Optional[int] = 0
    script: Optional[str] = ""

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
    inputs: List[Input]
    outputs: List[Out]

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
    hash160: Optional[str] = ""
    token: Optional[str] = ""
    address: Optional[str] = ""
    n_tx: Optional[int] = 0
    total_received: Optional[int] = 0
    total_sent: Optional[int] = 0
    final_balance: Optional[float] = 0
    txs: Optional[List[TxDTO]]=[]



class ETHAddressSummary(BaseModel):
    """Ethereum address summary data structure"""
    hash: str
    nonce: str
    balance: float
    transactionCount: int
    internalTransactionCount: int
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
    blockNumber: str
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

"""Web3 client for RPC connection and transaction management."""

import logging
import os
from typing import Optional
from web3 import Web3
from web3.types import TxParams, Wei
from eth_account import Account

logger = logging.getLogger(__name__)


class Web3Client:
    """Manages Web3 connection and account."""
    
    def __init__(self, rpc_url: str, private_key: Optional[str] = None):
        """Initialize Web3 client.
        
        Args:
            rpc_url: RPC endpoint URL
            private_key: Private key for signing transactions (optional)
        """
        self.rpc_url = rpc_url
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        
        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to RPC: {rpc_url}")
        
        self.account = None
        if private_key:
            self.account = Account.from_key(private_key)
            logger.info(f"Initialized account: {self.account.address}")
    
    def get_balance(self, address: Optional[str] = None) -> int:
        """Get ETH/MATIC balance.
        
        Args:
            address: Address to check (default: account address)
        
        Returns:
            Balance in wei
        """
        if address is None:
            if self.account is None:
                raise ValueError("No account or address provided")
            address = self.account.address
        
        return self.w3.eth.get_balance(address)
    
    def send_transaction(
        self,
        to: str,
        data: bytes,
        value: int = 0,
        gas_limit: Optional[int] = None
    ) -> str:
        """Send a transaction.
        
        Args:
            to: Recipient address
            data: Transaction data
            value: Value to send (in wei)
            gas_limit: Gas limit (optional)
        
        Returns:
            Transaction hash
        """
        if self.account is None:
            raise ValueError("No account configured for sending transactions")
        
        # Build transaction
        tx_params: TxParams = {
            "from": self.account.address,
            "to": to,
            "data": data,
            "value": Wei(value),
            "nonce": self.w3.eth.get_transaction_count(self.account.address),
            "chainId": self.w3.eth.chain_id
        }
        
        # Estimate gas if not provided
        if gas_limit is None:
            try:
                gas_limit = self.w3.eth.estimate_gas(tx_params)
            except Exception as e:
                logger.warning(f"Gas estimation failed: {e}, using default")
                gas_limit = 200000
        
        tx_params["gas"] = gas_limit
        
        # Get gas price
        gas_price = self.w3.eth.gas_price
        tx_params["gasPrice"] = gas_price
        
        # Sign and send
        signed_tx = self.account.sign_transaction(tx_params)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        logger.info(f"Sent transaction: {tx_hash.hex()}")
        return tx_hash.hex()
    
    def wait_for_receipt(self, tx_hash: str, timeout: int = 300) -> dict:
        """Wait for transaction receipt.
        
        Args:
            tx_hash: Transaction hash
            timeout: Timeout in seconds
        
        Returns:
            Transaction receipt
        """
        return self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)


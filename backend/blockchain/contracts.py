"""Contract ABI loading and instance creation."""

import logging
import json
from pathlib import Path
from typing import Dict, Optional
from web3 import Web3
from web3.contract import Contract

logger = logging.getLogger(__name__)


class ContractLoader:
    """Loads contract ABIs and creates contract instances."""
    
    def __init__(self, web3_client, contracts_dir: Optional[str] = None):
        """Initialize contract loader.
        
        Args:
            web3_client: Web3Client instance
            contracts_dir: Directory containing contract ABIs (optional)
        """
        self.w3 = web3_client.w3
        self.contracts_dir = Path(contracts_dir) if contracts_dir else Path(__file__).parent.parent.parent / "contracts" / "out"
        self._abis: Dict[str, list] = {}
        self._contracts: Dict[str, Contract] = {}
    
    def load_abi(self, contract_name: str) -> Optional[list]:
        """Load ABI from JSON file.
        
        Args:
            contract_name: Name of contract (e.g., "Vault")
        
        Returns:
            ABI as list or None
        """
        if contract_name in self._abis:
            return self._abis[contract_name]
        
        # Try to find ABI file
        abi_file = self.contracts_dir / contract_name / f"{contract_name}.sol" / f"{contract_name}.json"
        if not abi_file.exists():
            # Alternative path
            abi_file = self.contracts_dir / f"{contract_name}.json"
        
        if not abi_file.exists():
            logger.warning(f"ABI file not found for {contract_name}")
            return None
        
        try:
            with open(abi_file, "r") as f:
                abi_data = json.load(f)
                # Foundry output format
                if "abi" in abi_data:
                    abi = abi_data["abi"]
                else:
                    abi = abi_data
                self._abis[contract_name] = abi
                return abi
        except Exception as e:
            logger.error(f"Error loading ABI for {contract_name}: {e}")
            return None
    
    def get_contract(self, contract_name: str, address: str) -> Optional[Contract]:
        """Get contract instance.
        
        Args:
            contract_name: Name of contract
            address: Contract address
        
        Returns:
            Contract instance or None
        """
        cache_key = f"{contract_name}:{address}"
        if cache_key in self._contracts:
            return self._contracts[cache_key]
        
        abi = self.load_abi(contract_name)
        if abi is None:
            return None
        
        try:
            contract = self.w3.eth.contract(address=address, abi=abi)
            self._contracts[cache_key] = contract
            return contract
        except Exception as e:
            logger.error(f"Error creating contract instance for {contract_name}: {e}")
            return None
    
    def load_contracts(self, addresses: Dict[str, str]) -> Dict[str, Contract]:
        """Load multiple contracts.
        
        Args:
            addresses: Dictionary mapping contract names to addresses
        
        Returns:
            Dictionary of contract instances
        """
        contracts = {}
        for name, address in addresses.items():
            contract = self.get_contract(name, address)
            if contract:
                contracts[name.lower()] = contract
        
        return contracts


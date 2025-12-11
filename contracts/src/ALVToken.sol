// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/// @title ALV Token
/// @notice Fixed supply ERC20 token with no minting after deployment
contract ALVToken is ERC20, Ownable {
    uint256 public constant MAX_SUPPLY = 1_000_000_000 * 10**18; // 1 billion tokens

    /// @notice Deploy token with fixed supply
    /// @param initialRecipient Address to receive initial supply
    constructor(address initialRecipient) ERC20("Alevor", "ALV") Ownable(msg.sender) {
        _mint(initialRecipient, MAX_SUPPLY);
    }

    /// @notice Burn tokens (reduces total supply)
    /// @param amount Amount to burn
    function burn(uint256 amount) external {
        _burn(msg.sender, amount);
    }

    /// @notice Burn tokens from a specific address (with approval)
    /// @param from Address to burn from
    /// @param amount Amount to burn
    function burnFrom(address from, uint256 amount) external {
        _spendAllowance(from, msg.sender, amount);
        _burn(from, amount);
    }
}

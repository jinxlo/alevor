// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "./interfaces/ITreasury.sol";
import "./interfaces/IVault.sol";
import "./interfaces/ILiquidityEngine.sol";

/// @title Treasury
/// @notice Distributes profits: 75% to vault, 20% to protocol, 5% to liquidity engine
contract Treasury is ITreasury, Ownable {
    using SafeERC20 for IERC20;

    IERC20 public immutable asset;
    IVault public vault;
    ILiquidityEngine public liquidityEngine;
    address public protocolWallet;

    uint256 public constant VAULT_PCT = 7500; // 75% in basis points
    uint256 public constant PROTOCOL_PCT = 2000; // 20% in basis points
    uint256 public constant LIQUIDITY_PCT = 500; // 5% in basis points
    uint256 private constant BASIS_POINTS = 10000;

    modifier onlyTrader() {
        require(msg.sender == owner(), "Treasury: not authorized"); // Trader should be owner or authorized
        _;
    }

    constructor(address _asset, address _owner) Ownable(_owner) {
        asset = IERC20(_asset);
    }

    /// @notice Set vault address
    function setVault(address _vault) external onlyOwner {
        vault = IVault(_vault);
    }

    /// @notice Set liquidity engine address
    function setLiquidityEngine(address _liquidityEngine) external onlyOwner {
        liquidityEngine = ILiquidityEngine(_liquidityEngine);
    }

    /// @notice Set protocol wallet address
    function setProtocolWallet(address _protocolWallet) external onlyOwner {
        protocolWallet = _protocolWallet;
    }

    /// @inheritdoc ITreasury
    function handleTradeResult(uint256 principal, int256 profit) external onlyTrader {
        if (profit <= 0) {
            // Loss: return only principal to vault
            asset.safeTransfer(address(vault), principal);
            return;
        }

        uint256 profitAmount = uint256(profit);
        uint256 total = principal + profitAmount;

        // Calculate distribution amounts
        uint256 vaultAmount = (profitAmount * VAULT_PCT) / BASIS_POINTS;
        uint256 protocolAmount = (profitAmount * PROTOCOL_PCT) / BASIS_POINTS;
        uint256 liquidityAmount = (profitAmount * LIQUIDITY_PCT) / BASIS_POINTS;

        // Return principal + 75% of profit to vault
        asset.safeTransfer(address(vault), principal + vaultAmount);

        // Send 20% of profit to protocol wallet
        if (protocolAmount > 0 && protocolWallet != address(0)) {
            asset.safeTransfer(protocolWallet, protocolAmount);
        }

        // Send 5% of profit to liquidity engine for buyback & burn
        if (liquidityAmount > 0 && address(liquidityEngine) != address(0)) {
            asset.safeApprove(address(liquidityEngine), liquidityAmount);
            liquidityEngine.buyAndBurn(liquidityAmount, 0); // Slippage handled by liquidity engine
        }
    }

    /// @inheritdoc ITreasury
    function getDistributionPcts()
        external
        pure
        returns (
            uint256 vaultPct,
            uint256 protocolPct,
            uint256 liquidityPct
        )
    {
        return (VAULT_PCT, PROTOCOL_PCT, LIQUIDITY_PCT);
    }

    /// @inheritdoc ITreasury
    function protocolWallet() external view returns (address) {
        return protocolWallet;
    }
}

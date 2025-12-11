// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface ITreasury {
    /// @notice Handle trade result and distribute profits
    /// @param principal Original capital amount
    /// @param profit Profit amount (positive for profit, negative for loss)
    function handleTradeResult(uint256 principal, int256 profit) external;

    /// @notice Get distribution percentages
    /// @return vaultPct Percentage to vault (basis points, e.g., 7500 = 75%)
    /// @return protocolPct Percentage to protocol (basis points, e.g., 2000 = 20%)
    /// @return liquidityPct Percentage to liquidity engine (basis points, e.g., 500 = 5%)
    function getDistributionPcts()
        external
        view
        returns (
            uint256 vaultPct,
            uint256 protocolPct,
            uint256 liquidityPct
        );

    /// @notice Get protocol wallet address
    /// @return Address that receives protocol share
    function protocolWallet() external view returns (address);
}

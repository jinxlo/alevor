// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface ILiquidityEngine {
    /// @notice Buy ALV tokens and burn them
    /// @param amountIn Amount of base token (e.g., USDC) to spend
    /// @param amountOutMin Minimum ALV tokens to receive (slippage protection)
    /// @return amountOut Amount of ALV tokens bought and burned
    function buyAndBurn(uint256 amountIn, uint256 amountOutMin) external returns (uint256 amountOut);

    /// @notice Get ALV token address
    /// @return Address of ALV token contract
    function alvToken() external view returns (address);

    /// @notice Get DEX router address
    /// @return Address of DEX router
    function dexRouter() external view returns (address);

    /// @notice Get ALV/USDC pool address
    /// @return Address of the liquidity pool
    function alvPool() external view returns (address);
}

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface ITrader {
    /// @notice Execute a trade (swap)
    /// @param tokenIn Address of input token
    /// @param tokenOut Address of output token
    /// @param amountIn Amount of input token
    /// @param amountOutMin Minimum amount of output token (slippage protection)
    /// @param deadline Transaction deadline
    /// @return amountOut Actual amount of output token received
    function executeTrade(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 amountOutMin,
        uint256 deadline
    ) external returns (uint256 amountOut);

    /// @notice Close a position (reverse swap)
    /// @param tokenIn Address of input token
    /// @param tokenOut Address of output token
    /// @param amountIn Amount of input token
    /// @param amountOutMin Minimum amount of output token
    /// @param deadline Transaction deadline
    /// @return amountOut Actual amount of output token received
    function closePosition(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 amountOutMin,
        uint256 deadline
    ) external returns (uint256 amountOut);

    /// @notice Get maximum capital allowed per trade
    /// @return Maximum amount in base units
    function maxCapitalPerTrade() external view returns (uint256);

    /// @notice Request capital from vault (only callable by authorized caller)
    /// @param amount Amount requested
    function requestCapital(uint256 amount) external;

    /// @notice Return capital + profit to treasury
    /// @param principal Original capital amount
    /// @param profit Profit (can be negative if loss)
    function returnCapital(uint256 principal, int256 profit) external;
}

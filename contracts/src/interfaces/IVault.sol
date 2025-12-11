// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IVault {
    /// @notice Deposit assets into the vault
    /// @param amount Amount of assets to deposit
    /// @return shares Number of shares minted
    function deposit(uint256 amount) external returns (uint256 shares);

    /// @notice Withdraw assets from the vault
    /// @param shares Number of shares to redeem
    /// @return amount Amount of assets withdrawn
    function withdraw(uint256 shares) external returns (uint256 amount);

    /// @notice Get total assets under management
    /// @return Total assets in the vault
    function totalAssets() external view returns (uint256);

    /// @notice Get total shares outstanding
    /// @return Total shares minted
    function totalShares() external view returns (uint256);

    /// @notice Convert assets to shares
    /// @param assets Amount of assets
    /// @return shares Equivalent shares
    function convertToShares(uint256 assets) external view returns (uint256 shares);

    /// @notice Convert shares to assets
    /// @param shares Amount of shares
    /// @return assets Equivalent assets
    function convertToAssets(uint256 shares) external view returns (uint256 assets);

    /// @notice Transfer assets to trader (only callable by authorized trader)
    /// @param amount Amount to transfer
    function transferToTrader(uint256 amount) external;

    /// @notice Receive assets from treasury (profit distribution)
    /// @param amount Amount received
    function receiveProfit(uint256 amount) external;
}

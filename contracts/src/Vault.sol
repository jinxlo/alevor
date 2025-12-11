// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "./interfaces/IVault.sol";

/// @title Vault
/// @notice Manages user deposits and withdrawals, issues shares
contract Vault is IVault, Ownable {
    using SafeERC20 for IERC20;

    IERC20 public immutable asset; // Base asset (e.g., USDC)
    uint256 private _totalAssets;
    uint256 private _totalShares;
    address public trader;
    address public treasury;

    event Deposit(address indexed user, uint256 assets, uint256 shares);
    event Withdraw(address indexed user, uint256 assets, uint256 shares);
    event AssetsTransferred(address indexed to, uint256 amount);
    event ProfitReceived(uint256 amount);

    modifier onlyTrader() {
        require(msg.sender == trader, "Vault: not trader");
        _;
    }

    modifier onlyTreasury() {
        require(msg.sender == treasury, "Vault: not treasury");
        _;
    }

    constructor(address _asset, address _owner) Ownable(_owner) {
        asset = IERC20(_asset);
    }

    /// @notice Set trader address (only owner)
    function setTrader(address _trader) external onlyOwner {
        trader = _trader;
    }

    /// @notice Set treasury address (only owner)
    function setTreasury(address _treasury) external onlyOwner {
        treasury = _treasury;
    }

    /// @inheritdoc IVault
    function deposit(uint256 amount) external returns (uint256 shares) {
        require(amount > 0, "Vault: amount must be > 0");
        
        asset.safeTransferFrom(msg.sender, address(this), amount);
        shares = convertToShares(amount);
        _totalAssets += amount;
        _totalShares += shares;

        emit Deposit(msg.sender, amount, shares);
        return shares;
    }

    /// @inheritdoc IVault
    function withdraw(uint256 shares) external returns (uint256 amount) {
        require(shares > 0, "Vault: shares must be > 0");
        require(shares <= _totalShares, "Vault: insufficient shares");

        amount = convertToAssets(shares);
        _totalAssets -= amount;
        _totalShares -= shares;

        asset.safeTransfer(msg.sender, amount);
        emit Withdraw(msg.sender, amount, shares);
        return amount;
    }

    /// @inheritdoc IVault
    function totalAssets() external view returns (uint256) {
        return _totalAssets;
    }

    /// @inheritdoc IVault
    function totalShares() external view returns (uint256) {
        return _totalShares;
    }

    /// @inheritdoc IVault
    function convertToShares(uint256 assets) public view returns (uint256) {
        if (_totalShares == 0) {
            return assets; // 1:1 on first deposit
        }
        return (assets * _totalShares) / _totalAssets;
    }

    /// @inheritdoc IVault
    function convertToAssets(uint256 shares) public view returns (uint256) {
        if (_totalShares == 0) {
            return 0;
        }
        return (shares * _totalAssets) / _totalShares;
    }

    /// @inheritdoc IVault
    function transferToTrader(uint256 amount) external onlyTrader {
        require(amount <= _totalAssets, "Vault: insufficient assets");
        _totalAssets -= amount;
        asset.safeTransfer(trader, amount);
        emit AssetsTransferred(trader, amount);
    }

    /// @inheritdoc IVault
    function receiveProfit(uint256 amount) external onlyTreasury {
        asset.safeTransferFrom(treasury, address(this), amount);
        _totalAssets += amount;
        emit ProfitReceived(amount);
    }
}

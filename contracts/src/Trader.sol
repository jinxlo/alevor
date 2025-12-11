// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "./interfaces/ITrader.sol";
import "./interfaces/IVault.sol";
import "./interfaces/ITreasury.sol";

/// @title Trader
/// @notice Executes trades with capital from vault, enforces 2-5% position size limits
contract Trader is ITrader, Ownable {
    using SafeERC20 for IERC20;

    IVault public vault;
    ITreasury public treasury;
    address public dexRouter;
    
    uint256 public maxCapitalPerTradePct = 500; // 5% in basis points
    uint256 public minCapitalPerTradePct = 200; // 2% in basis points
    uint256 private constant BASIS_POINTS = 10000;

    modifier onlyAuthorized() {
        require(msg.sender == owner(), "Trader: not authorized");
        _;
    }

    constructor(
        address _vault,
        address _treasury,
        address _dexRouter,
        address _owner
    ) Ownable(_owner) {
        vault = IVault(_vault);
        treasury = ITreasury(_treasury);
        dexRouter = _dexRouter;
    }

    /// @notice Set max capital per trade percentage
    function setMaxCapitalPerTradePct(uint256 _pct) external onlyOwner {
        require(_pct <= 500 && _pct >= 200, "Trader: pct must be 2-5%");
        maxCapitalPerTradePct = _pct;
    }

    /// @notice Set min capital per trade percentage
    function setMinCapitalPerTradePct(uint256 _pct) external onlyOwner {
        require(_pct <= 500 && _pct >= 200, "Trader: pct must be 2-5%");
        minCapitalPerTradePct = _pct;
    }

    /// @notice Set DEX router address
    function setDexRouter(address _dexRouter) external onlyOwner {
        dexRouter = _dexRouter;
    }

    /// @inheritdoc ITrader
    function maxCapitalPerTrade() external view returns (uint256) {
        uint256 tvl = vault.totalAssets();
        return (tvl * maxCapitalPerTradePct) / BASIS_POINTS;
    }

    /// @inheritdoc ITrader
    function requestCapital(uint256 amount) external onlyAuthorized {
        uint256 tvl = vault.totalAssets();
        uint256 maxAmount = (tvl * maxCapitalPerTradePct) / BASIS_POINTS;
        uint256 minAmount = (tvl * minCapitalPerTradePct) / BASIS_POINTS;

        require(amount >= minAmount, "Trader: amount below minimum");
        require(amount <= maxAmount, "Trader: amount exceeds maximum");

        vault.transferToTrader(amount);
    }

    /// @inheritdoc ITrader
    function executeTrade(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 amountOutMin,
        uint256 deadline
    ) external onlyAuthorized returns (uint256 amountOut) {
        require(block.timestamp <= deadline, "Trader: deadline passed");
        
        IERC20(tokenIn).safeApprove(dexRouter, amountIn);
        
        // Simplified swap call - actual implementation depends on DEX router interface
        // This is a placeholder - replace with actual router call
        bytes memory data = abi.encodeWithSignature(
            "swapExactTokensForTokens(uint256,uint256,address[],address,uint256)",
            amountIn,
            amountOutMin,
            _getPath(tokenIn, tokenOut),
            address(this),
            deadline
        );
        
        (bool success, bytes memory result) = dexRouter.call(data);
        require(success, "Trader: swap failed");
        
        amountOut = abi.decode(result, (uint256));
        return amountOut;
    }

    /// @inheritdoc ITrader
    function closePosition(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 amountOutMin,
        uint256 deadline
    ) external onlyAuthorized returns (uint256 amountOut) {
        return executeTrade(tokenIn, tokenOut, amountIn, amountOutMin, deadline);
    }

    /// @inheritdoc ITrader
    function returnCapital(uint256 principal, int256 profit) external onlyAuthorized {
        treasury.handleTradeResult(principal, profit);
    }

    /// @notice Get swap path for two tokens
    function _getPath(address tokenIn, address tokenOut) private pure returns (address[] memory) {
        address[] memory path = new address[](2);
        path[0] = tokenIn;
        path[1] = tokenOut;
        return path;
    }
}

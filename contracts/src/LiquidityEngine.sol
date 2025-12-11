// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "./interfaces/ILiquidityEngine.sol";
import "./ALVToken.sol";

/// @title LiquidityEngine
/// @notice Buys ALV tokens and burns them using profits from treasury
contract LiquidityEngine is ILiquidityEngine, Ownable {
    using SafeERC20 for IERC20;

    ALVToken public immutable alvToken;
    IERC20 public immutable baseToken; // e.g., USDC
    address public dexRouter;
    address public alvPool;

    event BuyAndBurn(uint256 baseAmount, uint256 alvBurned);

    modifier onlyTreasury() {
        require(msg.sender == owner(), "LiquidityEngine: not authorized");
        _;
    }

    constructor(
        address _alvToken,
        address _baseToken,
        address _dexRouter,
        address _alvPool,
        address _owner
    ) Ownable(_owner) {
        alvToken = ALVToken(_alvToken);
        baseToken = IERC20(_baseToken);
        dexRouter = _dexRouter;
        alvPool = _alvPool;
    }

    /// @notice Set DEX router address
    function setDexRouter(address _dexRouter) external onlyOwner {
        dexRouter = _dexRouter;
    }

    /// @notice Set ALV pool address
    function setAlvPool(address _alvPool) external onlyOwner {
        alvPool = _alvPool;
    }

    /// @inheritdoc ILiquidityEngine
    function buyAndBurn(uint256 amountIn, uint256 amountOutMin) 
        external 
        onlyTreasury 
        returns (uint256 amountOut) 
    {
        require(amountIn > 0, "LiquidityEngine: amount must be > 0");

        baseToken.safeTransferFrom(msg.sender, address(this), amountIn);
        baseToken.safeApprove(dexRouter, amountIn);

        // Simplified swap call - replace with actual router interface
        bytes memory data = abi.encodeWithSignature(
            "swapExactTokensForTokens(uint256,uint256,address[],address,uint256)",
            amountIn,
            amountOutMin,
            _getPath(address(baseToken), address(alvToken)),
            address(this),
            block.timestamp + 300
        );

        (bool success, bytes memory result) = dexRouter.call(data);
        require(success, "LiquidityEngine: swap failed");

        amountOut = abi.decode(result, (uint256));

        // Burn the ALV tokens
        alvToken.burn(amountOut);

        emit BuyAndBurn(amountIn, amountOut);
        return amountOut;
    }

    /// @inheritdoc ILiquidityEngine
    function alvToken() external view returns (address) {
        return address(alvToken);
    }

    /// @inheritdoc ILiquidityEngine
    function dexRouter() external view returns (address) {
        return dexRouter;
    }

    /// @inheritdoc ILiquidityEngine
    function alvPool() external view returns (address) {
        return alvPool;
    }

    /// @notice Get swap path
    function _getPath(address tokenIn, address tokenOut) private pure returns (address[] memory) {
        address[] memory path = new address[](2);
        path[0] = tokenIn;
        path[1] = tokenOut;
        return path;
    }
}

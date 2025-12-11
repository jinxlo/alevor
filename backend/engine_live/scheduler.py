"""Scheduler for trading loop timing."""

import logging
import time
import signal
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class TradingScheduler:
    """Manages timing for trading loop."""
    
    def __init__(self, interval_seconds: int = 60):
        """Initialize scheduler.
        
        Args:
            interval_seconds: Interval between loop iterations
        """
        self.interval_seconds = interval_seconds
        self.running = False
        self.shutdown_requested = False
    
    def run_loop(self, callback: Callable[[], None]) -> None:
        """Run trading loop with scheduled intervals.
        
        Args:
            callback: Function to call on each iteration
        """
        self.running = True
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info(f"Starting trading loop with {self.interval_seconds}s interval")
        
        while self.running and not self.shutdown_requested:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error in trading loop: {e}", exc_info=True)
            
            if not self.shutdown_requested:
                time.sleep(self.interval_seconds)
        
        logger.info("Trading loop stopped")
    
    def _signal_handler(self, signum, frame) -> None:
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.shutdown_requested = True
        self.running = False
    
    def stop(self) -> None:
        """Stop the scheduler."""
        self.running = False
        self.shutdown_requested = True

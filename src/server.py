"""
System Monitor Server

Basic web server implementation for the System Resource Monitor.
This module will be expanded in Task 1.3.
"""

import asyncio
import logging
from pathlib import Path

class SystemMonitorServer:
    """Basic server class - to be implemented in Task 1.3"""
    
    def __init__(self, config, logger):
        """
        Initialize server
        
        Args:
            config: Configuration object
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.app = None
        self.runner = None
        self.site = None
    
    async def start(self):
        """Start the server - placeholder for Task 1.3"""
        self.logger.info("🔧 Server module placeholder - will be implemented in Task 1.3")
        self.logger.info(f"📍 Configured to run on {self.config.server.host}:{self.config.server.port}")
        
        # For now, just wait for interrupt
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            pass
    
    async def stop(self):
        """Stop the server - placeholder for Task 1.3"""
        self.logger.info("🛑 Stopping server...")

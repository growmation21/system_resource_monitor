#!/usr/bin/env python3
"""
System Resource Monitor - Main Application Entry Point

A standalone Chrome app for real-time system resource monitoring
with always-on-top display capabilities.

Author: growmation21
Repository: https://github.com/growmation21/system_resource_monitor
"""

import sys
import os
import argparse
import asyncio
import logging
from pathlib import Path

# Add the project directory to Python path for imports
PROJECT_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_DIR))

# Import our modules after path setup
from src.config import Config
from src.logger import setup_logging
from src.server import SystemMonitorServer

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='System Resource Monitor - Chrome App',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Start with default settings
  python main.py --port 8080        # Start on custom port
  python main.py --debug            # Enable debug logging
  python main.py --no-browser       # Don't auto-open browser
        """
    )
    
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=8888,
        help='Port to run the web server on (default: 8888)'
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default='localhost',
        help='Host to bind the server to (default: localhost)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    parser.add_argument(
        '--no-browser',
        action='store_true',
        help='Do not automatically open browser'
    )
    
    parser.add_argument(
        '--config',
        type=Path,
        default=PROJECT_DIR / 'config' / 'settings.json',
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='System Resource Monitor v1.0.0'
    )
    
    return parser.parse_args()

def check_dependencies():
    """Check if all required dependencies are available"""
    missing_deps = []
    
    try:
        import psutil
    except ImportError:
        missing_deps.append('psutil>=5.8.0')
    
    try:
        import pynvml
    except ImportError:
        missing_deps.append('pynvml>=11.4.1')
    
    try:
        import aiohttp
    except ImportError:
        missing_deps.append('aiohttp>=3.8.0')
    
    try:
        import torch
    except ImportError:
        missing_deps.append('torch>=1.9.0')
    
    if missing_deps:
        print("❌ Missing required dependencies:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\nPlease install missing dependencies:")
        print("   pip install " + " ".join(missing_deps))
        return False
    
    return True

async def main():
    """Main application function"""
    # Parse command line arguments
    args = parse_arguments()
    
    # Set up logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logger = setup_logging(level=log_level)
    
    logger.info("🚀 Starting System Resource Monitor")
    logger.info(f"📁 Project directory: {PROJECT_DIR}")
    
    # Check dependencies
    if not check_dependencies():
        logger.error("❌ Dependency check failed")
        return 1
    
    logger.info("✅ All dependencies available")
    
    # Load configuration
    try:
        config = Config(args.config)
        logger.info(f"📋 Configuration loaded from: {args.config}")
    except Exception as e:
        logger.error(f"❌ Failed to load configuration: {e}")
        return 1
    
    # Override config with command line arguments
    config.server.host = args.host
    config.server.port = args.port
    config.app.auto_open_browser = not args.no_browser
    
    # Create and start the server
    try:
        server = SystemMonitorServer(config, logger)
        logger.info(f"🌐 Starting server on http://{args.host}:{args.port}")
        
        # Start the server
        await server.start()
        
    except KeyboardInterrupt:
        logger.info("🛑 Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        return 1
    finally:
        logger.info("👋 System Resource Monitor stopped")
    
    return 0

def run():
    """Entry point function for setup.py console scripts"""
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    run()

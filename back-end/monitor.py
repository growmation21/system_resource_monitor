#!/usr/bin/env python3
"""
System Resource Monitor - Backend Server
Provides REST API and WebSocket endpoints for real-time system monitoring.
"""

import asyncio
import aiohttp
from aiohttp import web, WSMsgType
import json
import time
import threading
import argparse
import logging
import weakref
from pathlib import Path

# Import hardware monitoring
from hardware import CHardwareInfo

# Global variables
connected_clients = weakref.WeakSet()
monitor_data = {}
monitor_lock = threading.Lock()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemMonitorServer:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.app = web.Application()
        self.hardware_monitor = None
        self.monitor_thread = None
        self.running = False
        
        # Setup routes
        self.setup_routes()
        
        # Initialize hardware monitoring
        self.hardware_monitor = CHardwareInfo(True, True, True, True, True)
    
    def setup_routes(self):
        """Setup HTTP routes and WebSocket endpoint."""
        # REST API endpoints
        self.app.router.add_get('/api/status', self.get_status)
        self.app.router.add_get('/api/cpu', self.get_cpu)
        self.app.router.add_get('/api/memory', self.get_memory)
        self.app.router.add_get('/api/disk', self.get_disk)
        self.app.router.add_get('/api/gpu', self.get_gpu)
        self.app.router.add_get('/api/system', self.get_system_info)
        
        # WebSocket endpoint
        self.app.router.add_get('/ws', self.websocket_handler)
        
        # CORS middleware
        self.app.middlewares.append(self.cors_middleware)
    
    @web.middleware
    async def cors_middleware(self, request, handler):
        """CORS middleware to allow cross-origin requests."""
        response = await handler(request)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    def start_monitoring(self):
        """Start hardware monitoring in background thread."""
        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Hardware monitoring started")
    
    def stop_monitoring(self):
        """Stop hardware monitoring."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        logger.info("Hardware monitoring stopped")
    
    def monitor_loop(self):
        """Background monitoring loop."""
        while self.running:
            try:
                # Get hardware data
                data = self.hardware_monitor.getStatus()
                
                with monitor_lock:
                    global monitor_data
                    monitor_data = data
                
                # Broadcast to all connected WebSocket clients
                if connected_clients:
                    # Create a new event loop for this thread if none exists
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    # Run the broadcast in the main event loop instead
                    for client in list(connected_clients):
                        try:
                            if hasattr(client, '_loop') and client._loop:
                                asyncio.run_coroutine_threadsafe(
                                    self.send_to_client(client, data),
                                    client._loop
                                )
                        except Exception as e:
                            logger.debug(f"Error sending to client: {e}")
                            connected_clients.discard(client)
                
                time.sleep(1)  # Update every second
                
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                time.sleep(5)
    
    async def send_to_client(self, client, data):
        """Send data to a specific client."""
        try:
            # Format data in the expected Chrome app format
            formatted_data = {
                'type': 'monitor_data',
                'data': {
                    'cpu': {
                        'usage': data.get('cpu_utilization', 0)
                    },
                    'memory': {
                        'percent': data.get('ram_used_percent', 0),
                        'used': data.get('ram_used', 0),
                        'total': data.get('ram_total', 0)
                    },
                    'drives': [],
                    'gpus': []
                }
            }
            
            # Add GPU data if available
            if 'gpus' in data and data['gpus']:
                for i, gpu in enumerate(data['gpus']):
                    formatted_data['data']['gpus'].append({
                        'name': f"GPU {i}",
                        'gpu_utilization': gpu.get('gpu_utilization', 0),
                        'gpu_temperature': gpu.get('gpu_temperature', 0),
                        'vram_used_percent': gpu.get('vram_used_percent', 0),
                        'vram_used': gpu.get('vram_used', 0),
                        'vram_total': gpu.get('vram_total', 0)
                    })
            
            # Add disk data (simplified for now)
            if 'hdd_total' in data and 'hdd_used' in data:
                formatted_data['data']['drives'].append({
                    'path': 'C:',
                    'used_percent': data.get('hdd_used_percent', 0),
                    'used_bytes': data.get('hdd_used', 0),
                    'total_bytes': data.get('hdd_total', 0)
                })
            
            message = json.dumps(formatted_data)
            await client.send_str(message)
        except Exception as e:
            logger.debug(f"Client disconnected during send: {e}")
            connected_clients.discard(client)
    
    async def broadcast_data(self, data):
        """Broadcast data to all connected WebSocket clients."""
        if not connected_clients:
            return
        
        # Format data in the expected Chrome app format
        formatted_data = {
            'type': 'monitor_data',
            'data': {
                'cpu': {
                    'usage': data.get('cpu_utilization', 0)
                },
                'memory': {
                    'percent': data.get('ram_used_percent', 0),
                    'used': data.get('ram_used', 0),
                    'total': data.get('ram_total', 0)
                },
                'drives': [],
                'gpus': []
            }
        }
        
        # Add GPU data if available
        if 'gpus' in data and data['gpus']:
            for i, gpu in enumerate(data['gpus']):
                formatted_data['data']['gpus'].append({
                    'name': f"GPU {i}",
                    'gpu_utilization': gpu.get('gpu_utilization', 0),
                    'gpu_temperature': gpu.get('gpu_temperature', 0),
                    'vram_used_percent': gpu.get('vram_used_percent', 0),
                    'vram_used': gpu.get('vram_used', 0),
                    'vram_total': gpu.get('vram_total', 0)
                })
        
        # Add disk data (simplified for now)
        if 'hdd_total' in data and 'hdd_used' in data:
            formatted_data['data']['drives'].append({
                'path': 'C:',
                'used_percent': data.get('hdd_used_percent', 0),
                'used_bytes': data.get('hdd_used', 0),
                'total_bytes': data.get('hdd_total', 0)
            })
        
        message = json.dumps(formatted_data)
        disconnected = []
        
        for client in connected_clients:
            try:
                await client.send_str(message)
            except Exception as e:
                logger.debug(f"Client disconnected: {e}")
                disconnected.append(client)
        
        # Remove disconnected clients
        for client in disconnected:
            connected_clients.discard(client)
    
    # REST API Handlers
    async def get_status(self, request):
        """Get current system status."""
        try:
            with monitor_lock:
                data = monitor_data.copy() if monitor_data else self.hardware_monitor.getStatus()
            return web.json_response(data)
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_cpu(self, request):
        """Get CPU information."""
        try:
            data = self.hardware_monitor.getCPUInfo()
            return web.json_response(data)
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_memory(self, request):
        """Get memory information."""
        try:
            data = self.hardware_monitor.getRAMInfo()
            return web.json_response(data)
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_disk(self, request):
        """Get disk information."""
        try:
            data = self.hardware_monitor.getHDDInfo()
            return web.json_response(data)
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_gpu(self, request):
        """Get GPU information."""
        try:
            data = self.hardware_monitor.getGPUInfo()
            return web.json_response(data)
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_system_info(self, request):
        """Get general system information."""
        try:
            data = self.hardware_monitor.getSystemInfo()
            return web.json_response(data)
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def websocket_handler(self, request):
        """Handle WebSocket connections."""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        # Store the event loop reference for this WebSocket
        ws._loop = asyncio.get_event_loop()
        
        # Add client to connected clients
        connected_clients.add(ws)
        logger.info(f"WebSocket client connected. Total clients: {len(connected_clients)}")
        
        try:
            # Send connection confirmation
            await ws.send_str(json.dumps({'type': 'connected', 'message': 'WebSocket connected'}))
            
            # Send initial data if available
            with monitor_lock:
                if monitor_data:
                    await self.send_to_client(ws, monitor_data)
            
            # Handle incoming messages
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        if data.get('type') == 'ping':
                            await ws.send_str(json.dumps({'type': 'pong'}))
                        elif data.get('type') == 'get_status':
                            # Send current status
                            with monitor_lock:
                                if monitor_data:
                                    status_data = {
                                        'type': 'status',
                                        'data': monitor_data
                                    }
                                    await ws.send_str(json.dumps(status_data))
                    except json.JSONDecodeError:
                        pass
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f'WebSocket error: {ws.exception()}')
                    break
        
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        
        finally:
            connected_clients.discard(ws)
            logger.info(f"WebSocket client disconnected. Total clients: {len(connected_clients)}")
        
        return ws
    
    async def start_server(self):
        """Start the web server."""
        try:
            # Start monitoring
            self.start_monitoring()
            
            # Create and start web server
            runner = web.AppRunner(self.app)
            await runner.setup()
            
            site = web.TCPSite(runner, self.host, self.port)
            await site.start()
            
            logger.info(f"Server started on http://{self.host}:{self.port}")
            logger.info(f"WebSocket endpoint: ws://{self.host}:{self.port}/ws")
            logger.info("Press Ctrl+C to stop the server")
            
            # Keep server running
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                logger.info("Shutting down server...")
            finally:
                self.stop_monitoring()
                await runner.cleanup()
                
        except Exception as e:
            logger.error(f"Error starting server: {e}")
            raise

async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="System Resource Monitor Server")
    parser.add_argument("--host", default="localhost", help="Server host (default: localhost)")
    parser.add_argument("--port", type=int, default=8888, help="Server port (default: 8888)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create and start server
    server = SystemMonitorServer(args.host, args.port)
    await server.start_server()

if __name__ == "__main__":
    asyncio.run(main())


"""
System Monitor Server

Aiohttp-based web server implementation for the System Resource Monitor.
Provides WebSocket communication, static file serving, and API endpoints.
"""

import asyncio
import logging
import json
import weakref
from pathlib import Path
from typing import Set, Any, Dict

import aiohttp
from aiohttp import web, WSMsgType
import aiohttp_cors

from .monitor import SystemMonitor

class WebSocketManager:
    """Manages WebSocket connections for real-time data broadcasting"""
    
    def __init__(self, logger):
        self.logger = logger
        self._connections: Set[aiohttp.web.WebSocketResponse] = set()
    
    @property
    def connection_count(self) -> int:
        """Get the number of active connections"""
        return len(self._connections)
    
    def add_connection(self, ws: aiohttp.web.WebSocketResponse):
        """Add a new WebSocket connection"""
        self._connections.add(ws)
        self.logger.info(f"🔌 WebSocket connected. Total connections: {len(self._connections)}")
    
    def remove_connection(self, ws: aiohttp.web.WebSocketResponse):
        """Remove a WebSocket connection"""
        self._connections.discard(ws)
        self.logger.info(f"🔌 WebSocket disconnected. Total connections: {len(self._connections)}")
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected WebSocket clients"""
        if not self._connections:
            return
        
        message_str = json.dumps(message)
        disconnected = set()
        
        for ws in self._connections:
            try:
                if ws.closed:
                    disconnected.add(ws)
                else:
                    await ws.send_str(message_str)
            except Exception as e:
                self.logger.warning(f"Failed to send to WebSocket: {e}")
                disconnected.add(ws)
        
        # Clean up disconnected clients
        for ws in disconnected:
            self.remove_connection(ws)
    
    @property
    def connection_count(self) -> int:
        """Get the number of active connections"""
        return len(self._connections)

class SystemMonitorServer:
    """Main server class for the System Resource Monitor"""
    
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
        self.ws_manager = WebSocketManager(logger)
        
        # Store project root for static files
        self.project_root = Path(__file__).parent.parent
        
        # Initialize system monitoring
        try:
            self.system_monitor = SystemMonitor(
                enable_cpu=self.config.monitoring.enable_cpu,
                enable_ram=self.config.monitoring.enable_ram,
                enable_disk=self.config.monitoring.enable_disk,
                enable_gpu=self.config.monitoring.enable_gpu,
                enable_vram=self.config.monitoring.enable_vram,
                enable_temperature=self.config.monitoring.enable_temperature,
                selected_drives=self.config.monitoring.selected_drives,
                logger=self.logger
            )
            self.logger.info("✅ System monitor initialized successfully")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize system monitor: {e}")
            self.system_monitor = None
        
        # Monitoring task
        self._monitoring_task = None
    
    def create_app(self) -> web.Application:
        """Create and configure the aiohttp application"""
        # Create the web application
        app = web.Application()
        
        # Store references for handlers
        app['config'] = self.config
        app['logger'] = self.logger
        app['ws_manager'] = self.ws_manager
        
        # Set up CORS
        cors = aiohttp_cors.setup(app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        # Add routes
        self._setup_routes(app, cors)
        
        # Add middleware
        app.middlewares.append(self._error_middleware)
        app.middlewares.append(self._logging_middleware)
        
        return app
    
    async def _monitoring_loop(self):
        """Background task for periodic system monitoring and broadcasting"""
        self.logger.info("🔄 Starting monitoring loop")
        
        while True:
            try:
                if self.system_monitor and self.ws_manager.connection_count > 0:
                    # Get system status
                    status_data = self.system_monitor.get_full_status()
                    
                    # Broadcast to all connected WebSocket clients
                    await self.ws_manager.broadcast({
                        'type': 'monitoring_update',
                        'data': status_data
                    })
                
                # Wait for the configured interval
                await asyncio.sleep(self.config.monitoring.update_interval)
                
            except asyncio.CancelledError:
                self.logger.info("📡 Monitoring loop cancelled")
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                # Wait a bit before retrying on error
                await asyncio.sleep(5)
    
    def create_app(self) -> web.Application:
        """Create and configure the aiohttp application"""
        # Create the web application
        app = web.Application()
        
        # Store references for handlers
        app['config'] = self.config
        app['logger'] = self.logger
        app['ws_manager'] = self.ws_manager
        
        # Set up CORS
        cors = aiohttp_cors.setup(app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        # Add routes
        self._setup_routes(app, cors)
        
        # Add middleware
        app.middlewares.append(self._error_middleware)
        app.middlewares.append(self._logging_middleware)
        
        return app
    
    def _setup_routes(self, app: web.Application, cors):
        """Set up application routes"""
        
        # WebSocket endpoint
        app.router.add_get('/ws', self._websocket_handler)
        
        # API endpoints
        app.router.add_get('/api/status', self._status_handler)
        app.router.add_get('/api/config', self._config_handler)
        app.router.add_post('/api/config', self._update_config_handler)
        
        # Resource monitoring endpoints (Task 3.1)
        app.router.add_patch('/resources/monitor', self._update_monitor_settings_handler)
        app.router.add_get('/resources/monitor/GPU', self._gpu_info_handler)
        app.router.add_patch('/resources/monitor/GPU/{index}', self._update_gpu_settings_handler)
        app.router.add_get('/resources/monitor/HDD', self._hdd_info_handler)
        
        # Static file serving
        static_path = self.project_root / 'static'
        static_path.mkdir(exist_ok=True)
        app.router.add_static('/static/', static_path, name='static')
        
        # Chrome app files
        chrome_app_path = self.project_root / 'chrome-app'
        app.router.add_static('/chrome-app/', chrome_app_path, name='chrome-app')
        
        # Frontend files
        frontend_path = self.project_root / 'front-end'
        if frontend_path.exists():
            app.router.add_static('/frontend/', frontend_path, name='frontend')
        
        # Root redirect
        app.router.add_get('/', self._root_handler)
        
        # Add CORS to all routes
        for route in list(app.router.routes()):
            cors.add(route)
    
    async def _websocket_handler(self, request: web.Request) -> web.WebSocketResponse:
        """Handle WebSocket connections"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        # Add connection to manager
        request.app['ws_manager'].add_connection(ws)
        
        try:
            # Send initial status
            await ws.send_str(json.dumps({
                'type': 'connected',
                'message': 'Connected to System Resource Monitor',
                'timestamp': asyncio.get_event_loop().time()
            }))
            
            # Handle incoming messages
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        await self._handle_websocket_message(ws, data)
                    except json.JSONDecodeError:
                        await ws.send_str(json.dumps({
                            'type': 'error',
                            'message': 'Invalid JSON format'
                        }))
                elif msg.type == WSMsgType.ERROR:
                    self.logger.error(f'WebSocket error: {ws.exception()}')
                    break
        
        except Exception as e:
            self.logger.error(f"WebSocket handler error: {e}")
        
        finally:
            # Remove connection from manager
            request.app['ws_manager'].remove_connection(ws)
        
        return ws
    
    async def _handle_websocket_message(self, ws: web.WebSocketResponse, data: Dict[str, Any]):
        """Handle incoming WebSocket messages"""
        message_type = data.get('type')
        
        if message_type == 'ping':
            await ws.send_str(json.dumps({
                'type': 'pong',
                'timestamp': asyncio.get_event_loop().time()
            }))
        
        elif message_type == 'get_status':
            # Get real system status data
            if self.system_monitor:
                try:
                    system_status = self.system_monitor.get_full_status()
                    await ws.send_str(json.dumps({
                        'type': 'status',
                        'data': system_status
                    }))
                except Exception as e:
                    self.logger.error(f"Error getting system status: {e}")
                    await ws.send_str(json.dumps({
                        'type': 'status',
                        'error': str(e),
                        'data': {
                            'server': 'running',
                            'connections': self.ws_manager.connection_count,
                            'timestamp': asyncio.get_event_loop().time()
                        }
                    }))
            else:
                await ws.send_str(json.dumps({
                    'type': 'status',
                    'data': {
                        'server': 'running',
                        'connections': self.ws_manager.connection_count,
                        'timestamp': asyncio.get_event_loop().time(),
                        'error': 'System monitoring not available'
                    }
                }))
        
        else:
            await ws.send_str(json.dumps({
                'type': 'error',
                'message': f'Unknown message type: {message_type}'
            }))
    
    async def _status_handler(self, request: web.Request) -> web.Response:
        """Handle status API requests"""
        # Get basic server status
        status = {
            'server': 'running',
            'version': '1.0.0',
            'connections': request.app['ws_manager'].connection_count,
            'config': {
                'host': self.config.server.host,
                'port': self.config.server.port,
                'websocket_path': self.config.server.websocket_path
            },
            'timestamp': asyncio.get_event_loop().time()
        }
        
        # Add system monitoring data if available
        if self.system_monitor:
            try:
                system_status = self.system_monitor.get_full_status()
                status.update(system_status)
                
                # Add monitoring capabilities
                status['monitoring_capabilities'] = self.system_monitor.get_monitoring_capabilities()
                
            except Exception as e:
                self.logger.error(f"Error getting system status for API: {e}")
                status['monitoring_error'] = str(e)
        else:
            status['monitoring_error'] = 'System monitoring not initialized'
        
        return web.json_response(status)
    
    async def _config_handler(self, request: web.Request) -> web.Response:
        """Handle configuration API requests"""
        return web.json_response(self.config.to_dict())
    
    async def _update_config_handler(self, request: web.Request) -> web.Response:
        """Handle configuration update requests"""
        try:
            data = await request.json()
            self.config.update_from_dict(data)
            
            # Save configuration if requested
            if data.get('save', False):
                self.config.save()
            
            return web.json_response({
                'status': 'success',
                'message': 'Configuration updated',
                'config': self.config.to_dict()
            })
        
        except Exception as e:
            self.logger.error(f"Failed to update configuration: {e}")
            return web.json_response({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    async def _root_handler(self, request: web.Request) -> web.Response:
        """Handle root path requests"""
        # Check if this is from Chrome app
        user_agent = request.headers.get('User-Agent', '')
        
        if 'Chrome' in user_agent and 'app' in user_agent.lower():
            # Redirect to Chrome app
            raise web.HTTPFound('/chrome-app/window.html')
        else:
            # Return simple status page
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>System Resource Monitor</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; background: #1a1a1a; color: #fff; }}
                    .container {{ max-width: 600px; margin: 0 auto; }}
                    .status {{ background: #2d2d2d; padding: 20px; border-radius: 8px; }}
                    .success {{ color: #00ff00; }}
                    .info {{ color: #00aaff; }}
                    a {{ color: #00aaff; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🖥️ System Resource Monitor</h1>
                    <div class="status">
                        <h2 class="success">✅ Server Running</h2>
                        <p><strong>Host:</strong> {self.config.server.host}</p>
                        <p><strong>Port:</strong> {self.config.server.port}</p>
                        <p><strong>WebSocket Connections:</strong> {self.ws_manager.connection_count}</p>
                        <h3>Available Endpoints:</h3>
                        <ul>
                            <li><a href="/api/status">API Status</a></li>
                            <li><a href="/api/config">Configuration</a></li>
                            <li><a href="/chrome-app/window.html">Chrome App</a></li>
                            <li class="info">WebSocket: ws://{self.config.server.host}:{self.config.server.port}/ws</li>
                        </ul>
                        <h3>Resource Monitoring API (Task 3.1):</h3>
                        <ul>
                            <li><a href="/resources/monitor/GPU">GPU Information</a></li>
                            <li><a href="/resources/monitor/HDD">HDD Information</a></li>
                            <li class="info">PATCH /resources/monitor - Update monitoring settings</li>
                            <li class="info">PATCH /resources/monitor/GPU/{{index}} - Update GPU settings</li>
                        </ul>
                    </div>
                </div>
            </body>
            </html>
            """
            return web.Response(text=html, content_type='text/html')
    
    # ===== Task 3.1: Resource Monitoring API Endpoints =====
    
    async def _update_monitor_settings_handler(self, request: web.Request) -> web.Response:
        """
        PATCH /resources/monitor - Update global monitoring settings
        
        Expected JSON body:
        {
            "enable_cpu": true,
            "enable_ram": true,
            "enable_disk": true,
            "enable_gpu": true,
            "enable_vram": true,
            "enable_temperature": true,
            "update_interval": 5.0,
            "selected_drives": ["C:\\", "D:\\"]
        }
        """
        try:
            data = await request.json()
            
            if not self.system_monitor:
                return web.json_response({
                    'success': False,
                    'error': 'System monitoring not available'
                }, status=503)
            
            # Validate settings
            valid_keys = {
                'enable_cpu', 'enable_ram', 'enable_disk', 'enable_gpu', 
                'enable_vram', 'enable_temperature', 'update_interval', 'selected_drives'
            }
            
            # Filter to only valid settings
            settings = {k: v for k, v in data.items() if k in valid_keys}
            
            if not settings:
                return web.json_response({
                    'success': False,
                    'error': 'No valid settings provided',
                    'valid_keys': list(valid_keys)
                }, status=400)
            
            # Update system monitor configuration
            self.system_monitor.update_configuration(settings)
            
            # Update config object if needed
            if 'update_interval' in settings:
                self.config.monitoring.update_interval = settings['update_interval']
                self.config.monitoring.refresh_rate = settings['update_interval']
            
            for key in ['enable_cpu', 'enable_ram', 'enable_disk', 'enable_gpu', 'enable_vram', 'enable_temperature']:
                if key in settings:
                    setattr(self.config.monitoring, key, settings[key])
            
            if 'selected_drives' in settings:
                self.config.monitoring.selected_drives = settings['selected_drives']
            
            # Save configuration if requested
            if data.get('save', True):
                self.config.save()
            
            self.logger.info(f"Updated monitoring settings: {settings}")
            
            return web.json_response({
                'success': True,
                'message': 'Monitoring settings updated successfully',
                'updated_settings': settings,
                'current_config': {
                    'enable_cpu': self.config.monitoring.enable_cpu,
                    'enable_ram': self.config.monitoring.enable_ram,
                    'enable_disk': self.config.monitoring.enable_disk,
                    'enable_gpu': self.config.monitoring.enable_gpu,
                    'enable_vram': self.config.monitoring.enable_vram,
                    'enable_temperature': self.config.monitoring.enable_temperature,
                    'update_interval': self.config.monitoring.update_interval,
                    'selected_drives': self.config.monitoring.selected_drives
                }
            })
            
        except json.JSONDecodeError:
            return web.json_response({
                'success': False,
                'error': 'Invalid JSON in request body'
            }, status=400)
        except Exception as e:
            self.logger.error(f"Error updating monitor settings: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def _gpu_info_handler(self, request: web.Request) -> web.Response:
        """
        GET /resources/monitor/GPU - Get GPU information and current status
        
        Returns detailed GPU information including:
        - Available GPUs with names and indices
        - Current utilization, VRAM usage, temperature
        - Capabilities (CUDA, PyTorch support)
        """
        try:
            if not self.system_monitor or not self.system_monitor.gpu:
                return web.json_response({
                    'success': False,
                    'error': 'GPU monitoring not available',
                    'gpus': [],
                    'gpu_count': 0,
                    'capabilities': {
                        'cuda_available': False,
                        'torch_available': False,
                        'pynvml_available': False
                    }
                })
            
            # Get comprehensive GPU status
            gpu_status = self.system_monitor.gpu.get_status()
            gpu_info = self.system_monitor.gpu.get_gpu_info()
            
            response_data = {
                'success': True,
                'gpu_count': gpu_info.get('gpu_count', 0),
                'device_type': gpu_status.get('device_type', 'cpu'),
                'capabilities': {
                    'cuda_available': gpu_info.get('cuda_available', False),
                    'torch_available': gpu_info.get('torch_available', False),
                    'pynvml_available': gpu_info.get('pynvml_available', False)
                },
                'gpus': gpu_status.get('gpus', []),
                'timestamp': gpu_status.get('timestamp', 0)
            }
            
            return web.json_response(response_data)
            
        except Exception as e:
            self.logger.error(f"Error getting GPU info: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def _update_gpu_settings_handler(self, request: web.Request) -> web.Response:
        """
        PATCH /resources/monitor/GPU/{index} - Update per-GPU monitoring settings
        
        Expected JSON body:
        {
            "enable_monitoring": true,
            "enable_vram": true,
            "enable_temperature": true
        }
        """
        try:
            gpu_index = int(request.match_info['index'])
            data = await request.json()
            
            if not self.system_monitor or not self.system_monitor.gpu:
                return web.json_response({
                    'success': False,
                    'error': 'GPU monitoring not available'
                }, status=503)
            
            # Check if GPU index is valid
            gpu_info = self.system_monitor.gpu.get_gpu_info()
            if gpu_index >= gpu_info.get('gpu_count', 0):
                return web.json_response({
                    'success': False,
                    'error': f'GPU index {gpu_index} not found. Available GPUs: 0-{gpu_info.get("gpu_count", 0)-1}'
                }, status=404)
            
            # For now, we'll update global GPU settings since the current implementation
            # doesn't support per-GPU configuration. This can be enhanced later.
            valid_settings = {}
            if 'enable_monitoring' in data:
                valid_settings['enable_gpu'] = data['enable_monitoring']
            if 'enable_vram' in data:
                valid_settings['enable_vram'] = data['enable_vram']
            if 'enable_temperature' in data:
                valid_settings['enable_temperature'] = data['enable_temperature']
            
            if valid_settings:
                self.system_monitor.update_configuration(valid_settings)
                
                # Update config
                for key, value in valid_settings.items():
                    setattr(self.config.monitoring, key, value)
                
                if data.get('save', True):
                    self.config.save()
            
            self.logger.info(f"Updated GPU {gpu_index} settings: {valid_settings}")
            
            return web.json_response({
                'success': True,
                'message': f'GPU {gpu_index} settings updated successfully',
                'gpu_index': gpu_index,
                'updated_settings': valid_settings,
                'note': 'Per-GPU settings currently apply globally to all GPUs'
            })
            
        except ValueError:
            return web.json_response({
                'success': False,
                'error': 'Invalid GPU index - must be a number'
            }, status=400)
        except json.JSONDecodeError:
            return web.json_response({
                'success': False,
                'error': 'Invalid JSON in request body'
            }, status=400)
        except Exception as e:
            self.logger.error(f"Error updating GPU {request.match_info.get('index', 'unknown')} settings: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def _hdd_info_handler(self, request: web.Request) -> web.Response:
        """
        GET /resources/monitor/HDD - Get available disk drives and current usage
        
        Returns:
        - List of available disk drives/mount points
        - Current usage for each drive
        - Drive capabilities and filesystem information
        """
        try:
            if not self.system_monitor:
                return web.json_response({
                    'success': False,
                    'error': 'System monitoring not available',
                    'drives': [],
                    'available_drives': []
                })
            
            # Get available drives
            available_drives = self.system_monitor.get_available_drives()
            
            # Get current disk status
            disk_status = self.system_monitor.hardware.get_disk_info() if self.system_monitor.hardware else {}
            
            # Compile drive information
            drives_info = []
            drives_data = disk_status.get('drives', {})
            
            for drive in available_drives:
                drive_data = drives_data.get(drive, {})
                drive_info = {
                    'path': drive,
                    'available': drive in drives_data,
                    'total_bytes': drive_data.get('total_bytes', 0),
                    'used_bytes': drive_data.get('used_bytes', 0),
                    'free_bytes': drive_data.get('free_bytes', 0),
                    'used_percent': drive_data.get('used_percent', 0),
                    'filesystem': drive_data.get('filesystem', 'unknown'),
                    'device': drive_data.get('device', 'unknown')
                }
                drives_info.append(drive_info)
            
            # Get monitoring configuration
            current_config = {
                'enable_disk': self.config.monitoring.enable_disk,
                'selected_drives': self.config.monitoring.selected_drives,
                'monitored_drives': disk_status.get('monitored_drives', [])
            }
            
            response_data = {
                'success': True,
                'available_drives': available_drives,
                'drives': drives_info,
                'total_summary': disk_status.get('total', {}),
                'monitoring_config': current_config,
                'timestamp': disk_status.get('timestamp', 0)
            }
            
            return web.json_response(response_data)
            
        except Exception as e:
            self.logger.error(f"Error getting HDD info: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    # ===== End Task 3.1 Endpoints =====
    
    @web.middleware
    async def _error_middleware(self, request: web.Request, handler):
        """Error handling middleware"""
        try:
            return await handler(request)
        except web.HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Request error: {e}")
            return web.json_response({
                'error': 'Internal server error',
                'message': str(e)
            }, status=500)
    
    @web.middleware
    async def _logging_middleware(self, request: web.Request, handler):
        """Request logging middleware"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            response = await handler(request)
            duration = asyncio.get_event_loop().time() - start_time
            
            self.logger.debug(
                f"{request.method} {request.path} -> {response.status} "
                f"({duration:.3f}s)"
            )
            
            return response
        
        except Exception as e:
            duration = asyncio.get_event_loop().time() - start_time
            self.logger.error(
                f"{request.method} {request.path} -> ERROR "
                f"({duration:.3f}s): {e}"
            )
            raise
    
    async def start(self):
        """Start the web server"""
        try:
            # Create application
            self.app = self.create_app()
            
            # Create runner
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            
            # Create site
            self.site = web.TCPSite(
                self.runner,
                self.config.server.host,
                self.config.server.port
            )
            
            # Start server
            await self.site.start()
            
            self.logger.info(f"🌐 Server started on http://{self.config.server.host}:{self.config.server.port}")
            self.logger.info(f"🔌 WebSocket endpoint: ws://{self.config.server.host}:{self.config.server.port}/ws")
            
            # Start monitoring task if system monitor is available
            if self.system_monitor:
                self._monitoring_task = asyncio.create_task(self._monitoring_loop())
                self.logger.info("📡 Monitoring task started")
            
            # Auto-open browser if configured
            if self.config.app.auto_open_browser:
                await self._open_browser()
            
            # Keep running until interrupted
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                self.logger.info("🛑 Received interrupt signal")
        
        except Exception as e:
            self.logger.error(f"❌ Failed to start server: {e}")
            raise
        
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the web server"""
        self.logger.info("🛑 Stopping server...")
        
        # Cancel monitoring task
        if self._monitoring_task and not self._monitoring_task.done():
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        # Close all WebSocket connections
        if self.ws_manager:
            await self.ws_manager.broadcast({
                'type': 'server_shutdown',
                'message': 'Server is shutting down'
            })
        
        # Clean up system monitor
        if self.system_monitor:
            try:
                self.system_monitor.close()
                self.logger.info("✅ System monitor closed")
            except Exception as e:
                self.logger.error(f"Error closing system monitor: {e}")
        
        # Stop server components
        if self.site:
            await self.site.stop()
        
        if self.runner:
            await self.runner.cleanup()
        
        self.logger.info("✅ Server stopped")
    
    async def _open_browser(self):
        """Open browser to the application"""
        import webbrowser
        import platform
        
        url = f"http://{self.config.server.host}:{self.config.server.port}"
        
        try:
            # Use different approach based on platform
            if platform.system() == "Windows":
                # Try to open as Chrome app if Chrome is available
                chrome_args = [
                    f"--app={url}/chrome-app/window.html",
                    "--window-size=300,200",
                    "--window-position=100,100"
                ]
                
                try:
                    import subprocess
                    subprocess.Popen([
                        "chrome.exe", 
                        f"--app={url}/chrome-app/window.html",
                        "--window-size=300,200"
                    ])
                    self.logger.info("🌐 Opened Chrome app window")
                    return
                except:
                    pass
            
            # Fallback to default browser
            webbrowser.open(url)
            self.logger.info(f"🌐 Opened browser: {url}")
            
        except Exception as e:
            self.logger.warning(f"Failed to open browser: {e}")

    async def broadcast_data(self, data: Dict[str, Any]):
        """Broadcast data to all connected WebSocket clients"""
        await self.ws_manager.broadcast(data)

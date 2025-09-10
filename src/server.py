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

class WebSocketManager:
    """Manages WebSocket connections for real-time data broadcasting"""
    
    def __init__(self, logger):
        self.logger = logger
        self._connections: Set[aiohttp.web.WebSocketResponse] = set()
    
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
            # This will be implemented when we add hardware monitoring
            await ws.send_str(json.dumps({
                'type': 'status',
                'data': {
                    'server': 'running',
                    'connections': self.ws_manager.connection_count,
                    'timestamp': asyncio.get_event_loop().time()
                }
            }))
        
        else:
            await ws.send_str(json.dumps({
                'type': 'error',
                'message': f'Unknown message type: {message_type}'
            }))
    
    async def _status_handler(self, request: web.Request) -> web.Response:
        """Handle status API requests"""
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
                    </div>
                </div>
            </body>
            </html>
            """
            return web.Response(text=html, content_type='text/html')
    
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
        
        # Close all WebSocket connections
        if self.ws_manager:
            await self.ws_manager.broadcast({
                'type': 'server_shutdown',
                'message': 'Server is shutting down'
            })
        
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

#!/usr/bin/env python3
"""
System Resource Monitor Launcher
Main entry point for launching the System Resource Monitor application.
"""

import os
import sys
import time
import signal
import asyncio
import argparse
import subprocess
from pathlib import Path
from threading import Thread

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "back-end"))

class MonitorLauncher:
    def __init__(self, minimized=False, port=8888):
        self.project_root = project_root
        self.minimized = minimized
        self.port = port
        self.backend_process = None
        self.chrome_process = None
        self.running = True
        
    def check_dependencies(self):
        """Check if required dependencies are installed."""
        print("🔍 Checking dependencies...")
        
        required_packages = ['aiohttp', 'psutil', 'GPUtil']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.lower())
                print(f"   ✅ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"   ❌ {package} (missing)")
        
        if missing_packages:
            print(f"\n⚠️  Missing dependencies: {', '.join(missing_packages)}")
            print("Installing missing packages...")
            
            for package in missing_packages:
                try:
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                    print(f"   ✅ Installed {package}")
                except subprocess.CalledProcessError as e:
                    print(f"   ❌ Failed to install {package}: {e}")
                    return False
        
        return True
    
    def start_backend_server(self):
        """Start the Python backend server."""
        print("🚀 Starting backend server...")
        
        try:
            backend_script = self.project_root / "back-end" / "monitor.py"
            
            # Start backend in subprocess
            self.backend_process = subprocess.Popen([
                sys.executable, str(backend_script),
                "--port", str(self.port)
            ], 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            
            # Give server time to start
            time.sleep(2)
            
            # Check if process is still running
            if self.backend_process.poll() is None:
                print(f"   ✅ Backend server started on port {self.port}")
                return True
            else:
                stdout, stderr = self.backend_process.communicate()
                print(f"   ❌ Backend server failed to start")
                if stderr:
                    print(f"      Error: {stderr.decode()}")
                return False
                
        except Exception as e:
            print(f"   ❌ Failed to start backend server: {e}")
            return False
    
    def launch_chrome_app(self):
        """Launch the Chrome app."""
        print("🌐 Launching Chrome app...")
        
        try:
            chrome_app_dir = self.project_root / "chrome-app"
            
            # Try different Chrome executable names
            chrome_commands = [
                'google-chrome',
                'chrome',
                'chromium',
                'chromium-browser',
                r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
            ]
            
            chrome_exe = None
            for cmd in chrome_commands:
                try:
                    # Test if command exists
                    if os.path.exists(cmd):
                        chrome_exe = cmd
                        break
                    else:
                        subprocess.check_output([cmd, '--version'], 
                                              stderr=subprocess.DEVNULL)
                        chrome_exe = cmd
                        break
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            
            if not chrome_exe:
                print("   ⚠️  Chrome not found. Opening in default browser...")
                self.open_in_default_browser()
                return True
            
            # Chrome app arguments
            chrome_args = [
                chrome_exe,
                f'--app=file:///{chrome_app_dir}/window.html',
                '--disable-web-security',
                '--allow-file-access-from-files',
                '--disable-features=VizDisplayCompositor',
                '--no-first-run',
                '--no-default-browser-check'
            ]
            
            if self.minimized:
                chrome_args.append('--start-minimized')
            
            # Start Chrome app
            self.chrome_process = subprocess.Popen(
                chrome_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            
            print(f"   ✅ Chrome app launched")
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to launch Chrome app: {e}")
            print("   ⚠️  Falling back to default browser...")
            self.open_in_default_browser()
            return True
    
    def open_in_default_browser(self):
        """Open the app in the default web browser."""
        import webbrowser
        
        chrome_app_dir = self.project_root / "chrome-app"
        url = f"file:///{chrome_app_dir}/window.html"
        
        try:
            webbrowser.open(url)
            print(f"   ✅ Opened in default browser")
        except Exception as e:
            print(f"   ❌ Failed to open in browser: {e}")
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            print("\n🛑 Shutdown signal received...")
            self.shutdown()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def monitor_processes(self):
        """Monitor backend and Chrome processes."""
        while self.running:
            try:
                # Check backend process
                if self.backend_process and self.backend_process.poll() is not None:
                    print("⚠️  Backend server stopped unexpectedly")
                    self.restart_backend()
                
                # Check Chrome process
                if self.chrome_process and self.chrome_process.poll() is not None:
                    print("ℹ️  Chrome app closed")
                    if not self.minimized:  # Don't auto-restart if started minimized
                        self.shutdown()
                        break
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                print(f"⚠️  Error monitoring processes: {e}")
                time.sleep(5)
    
    def restart_backend(self):
        """Restart the backend server."""
        print("🔄 Restarting backend server...")
        
        if self.backend_process:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
        
        time.sleep(2)
        self.start_backend_server()
    
    def shutdown(self):
        """Shutdown all processes gracefully."""
        print("🛑 Shutting down System Resource Monitor...")
        self.running = False
        
        # Stop Chrome process
        if self.chrome_process:
            try:
                self.chrome_process.terminate()
                self.chrome_process.wait(timeout=5)
                print("   ✅ Chrome app stopped")
            except subprocess.TimeoutExpired:
                self.chrome_process.kill()
                print("   ⚠️  Chrome app forcibly killed")
            except Exception as e:
                print(f"   ⚠️  Error stopping Chrome: {e}")
        
        # Stop backend process
        if self.backend_process:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
                print("   ✅ Backend server stopped")
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
                print("   ⚠️  Backend server forcibly killed")
            except Exception as e:
                print(f"   ⚠️  Error stopping backend: {e}")
    
    def launch(self):
        """Launch the complete application."""
        print("🎯 System Resource Monitor Launcher")
        print("=" * 40)
        
        try:
            # Check dependencies
            if not self.check_dependencies():
                print("❌ Dependency check failed")
                return False
            
            # Start backend server
            if not self.start_backend_server():
                print("❌ Failed to start backend server")
                return False
            
            # Launch Chrome app
            if not self.launch_chrome_app():
                print("❌ Failed to launch frontend")
                self.shutdown()
                return False
            
            # Setup signal handlers
            self.setup_signal_handlers()
            
            print("\n✅ System Resource Monitor launched successfully!")
            print(f"   • Backend server: http://localhost:{self.port}")
            print(f"   • WebSocket: ws://localhost:{self.port}/ws")
            print("   • Press Ctrl+C to stop")
            
            # Monitor processes
            monitor_thread = Thread(target=self.monitor_processes, daemon=True)
            monitor_thread.start()
            
            # Keep main thread alive
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            
            return True
            
        except Exception as e:
            print(f"❌ Launch failed: {e}")
            self.shutdown()
            return False
        finally:
            self.shutdown()

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="System Resource Monitor Launcher")
    parser.add_argument("--minimized", action="store_true", 
                       help="Start application minimized")
    parser.add_argument("--port", type=int, default=8888,
                       help="Backend server port (default: 8888)")
    parser.add_argument("--install", action="store_true",
                       help="Install desktop integration")
    parser.add_argument("--uninstall", action="store_true",
                       help="Uninstall desktop integration")
    
    args = parser.parse_args()
    
    # Handle installation/uninstallation
    if args.install or args.uninstall:
        desktop_integration_script = project_root / "desktop_integration.py"
        cmd = [sys.executable, str(desktop_integration_script)]
        
        if args.install:
            cmd.append("--install")
        elif args.uninstall:
            cmd.append("--uninstall")
        
        subprocess.run(cmd)
        return
    
    # Launch application
    launcher = MonitorLauncher(minimized=args.minimized, port=args.port)
    success = launcher.launch()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()

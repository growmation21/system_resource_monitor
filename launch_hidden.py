#!/usr/bin/env python3
"""
System Resource Monitor - Hidden Console Launcher
Runs the monitor in the background without showing the console window.
"""

import os
import sys
import time
import subprocess
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "back-end"))


class HiddenLauncher:
    def __init__(self, port=8888):
        self.project_root = project_root
        self.port = port
        self.backend_process = None
        
    def start_backend_hidden(self):
        """Start the backend server with hidden console."""
        try:
            backend_script = self.project_root / "back-end" / "monitor.py"
            
            # Configure startup to hide console window
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            # Start backend process
            self.backend_process = subprocess.Popen([
                sys.executable, str(backend_script),
                "--port", str(self.port)
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Give server time to start
            time.sleep(2)
            
            # Check if process started successfully
            if self.backend_process.poll() is None:
                return True
            else:
                stdout, stderr = self.backend_process.communicate()
                print(f"Backend failed to start:")
                if stderr:
                    print(f"Error: {stderr.decode()}")
                return False
                
        except Exception as e:
            print(f"Failed to start backend: {e}")
            return False
    
    def show_instructions(self):
        """Show Chrome Extension setup instructions in a notification."""
        chrome_extension_dir = self.project_root / "chrome-extension"
        
        instructions = f"""System Resource Monitor Started Successfully!

Backend Server: http://localhost:{self.port}
WebSocket: ws://localhost:{self.port}/ws

Chrome Extension Setup:
1. Open Chrome → chrome://extensions/
2. Enable 'Developer mode' (top-right)
3. Click 'Load unpacked'
4. Select: {chrome_extension_dir}
5. Click extension icon in toolbar

The server is now running in the background.
To stop: End 'python.exe' process in Task Manager
or use the system tray launcher instead."""

        # Show Windows notification if available
        try:
            import win10toast
            toaster = win10toast.ToastNotifier()
            toaster.show_toast(
                "System Resource Monitor",
                "Started successfully! Check console for setup instructions.",
                duration=10,
                threaded=True
            )
        except ImportError:
            pass
        
        # Also print to console (will be hidden but logged)
        print("=" * 60)
        print(instructions)
        print("=" * 60)
        
        return instructions
    
    def launch_hidden(self):
        """Launch the monitor in hidden mode."""
        print("Starting System Resource Monitor in background mode...")
        
        if not self.start_backend_hidden():
            print("Failed to start backend server.")
            return False
        
        print(f"Backend server started successfully on port {self.port}")
        
        # Show setup instructions
        self.show_instructions()
        
        # Keep process alive to monitor backend
        try:
            while True:
                time.sleep(10)
                
                # Check if backend is still running
                if self.backend_process.poll() is not None:
                    print("Backend server stopped unexpectedly.")
                    break
                    
        except KeyboardInterrupt:
            print("Shutdown requested...")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.cleanup()
        
        return True
    
    def cleanup(self):
        """Clean up resources."""
        if self.backend_process:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
                print("Backend server stopped.")
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
                print("Backend server forcibly killed.")
            except Exception as e:
                print(f"Error stopping backend: {e}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="System Resource Monitor - Hidden Mode")
    parser.add_argument("--port", type=int, default=8888,
                       help="Backend server port (default: 8888)")
    
    args = parser.parse_args()
    
    # Create and run hidden launcher
    launcher = HiddenLauncher(port=args.port)
    success = launcher.launch_hidden()
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()

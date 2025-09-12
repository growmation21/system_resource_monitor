#!/usr/bin/env python3
"""
System Resource Monitor - System Tray Launcher
Runs the monitor in the background with a system tray interface.
"""

import os
import sys
import time
import threading
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
import pystray
from pystray import MenuItem, Icon
from PIL import Image, ImageDraw

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "back-end"))


class SystemTrayMonitor:
    def __init__(self):
        self.project_root = project_root
        self.backend_process = None
        self.running = False
        self.port = 8888
        
    def create_icon(self):
        """Create a system tray icon."""
        # Create a simple icon with CPU/Memory representation
        width = 64
        height = 64
        
        # Create image
        image = Image.new('RGB', (width, height), color='black')
        dc = ImageDraw.Draw(image)
        
        # Draw a simple monitor representation
        # Monitor frame
        dc.rectangle([8, 12, 56, 44], fill='darkblue', outline='lightblue', width=2)
        
        # Screen
        dc.rectangle([12, 16, 52, 40], fill='blue')
        
        # Monitor stand
        dc.rectangle([28, 44, 36, 52], fill='darkgray')
        dc.rectangle([20, 52, 44, 56], fill='darkgray')
        
        # Activity indicator (small green dot when running)
        if self.running:
            dc.ellipse([48, 8, 58, 18], fill='lime', outline='green')
        else:
            dc.ellipse([48, 8, 58, 18], fill='red', outline='darkred')
        
        return image
    
    def start_backend(self):
        """Start the backend server process."""
        if self.backend_process and self.backend_process.poll() is None:
            return True  # Already running
            
        try:
            backend_script = self.project_root / "back-end" / "monitor.py"
            
            # Start backend with no console window
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            self.backend_process = subprocess.Popen([
                sys.executable, str(backend_script),
                "--port", str(self.port)
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            time.sleep(2)  # Give server time to start
            
            if self.backend_process.poll() is None:
                self.running = True
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Failed to start backend: {e}")
            return False
    
    def stop_backend(self):
        """Stop the backend server process."""
        if self.backend_process:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
            except Exception as e:
                print(f"Error stopping backend: {e}")
        
        self.running = False
        self.backend_process = None
    
    def open_chrome_extension_page(self):
        """Open Chrome extensions page."""
        import webbrowser
        webbrowser.open("chrome://extensions/")
    
    def open_monitor_url(self):
        """Open the monitor in default browser."""
        import webbrowser
        webbrowser.open(f"http://localhost:{self.port}")
    
    def show_setup_instructions(self):
        """Show Chrome Extension setup instructions."""
        instructions = f"""Chrome Extension Setup Instructions:

1. Open Chrome and go to chrome://extensions/
2. Enable 'Developer mode' (top-right toggle)
3. Click 'Load unpacked'
4. Select folder: {self.project_root}/chrome-extension
5. Click the extension icon in Chrome toolbar

Backend Server: http://localhost:{self.port}
WebSocket: ws://localhost:{self.port}/ws

The extension will connect automatically once loaded."""
        
        # Create a simple dialog
        root = tk.Tk()
        root.withdraw()  # Hide main window
        root.attributes('-topmost', True)
        messagebox.showinfo("System Resource Monitor Setup", instructions)
        root.destroy()
    
    def show_status(self):
        """Show current status."""
        if self.running and self.backend_process and self.backend_process.poll() is None:
            status = f"✅ System Resource Monitor Running\n\n" \
                    f"Backend Server: http://localhost:{self.port}\n" \
                    f"WebSocket: ws://localhost:{self.port}/ws\n\n" \
                    f"Process ID: {self.backend_process.pid}\n" \
                    f"Status: Active and ready for connections"
        else:
            status = "❌ System Resource Monitor Stopped\n\n" \
                    "Use 'Start Monitor' to begin monitoring."
        
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        messagebox.showinfo("System Resource Monitor Status", status)
        root.destroy()
    
    def restart_monitor(self):
        """Restart the monitoring service."""
        self.stop_backend()
        time.sleep(1)
        if self.start_backend():
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            messagebox.showinfo("Restart Complete", "System Resource Monitor restarted successfully!")
            root.destroy()
        else:
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            messagebox.showerror("Restart Failed", "Failed to restart System Resource Monitor.")
            root.destroy()
    
    def quit_application(self, icon, item):
        """Quit the application completely."""
        self.stop_backend()
        icon.stop()
    
    def create_menu(self):
        """Create the system tray menu."""
        return pystray.Menu(
            MenuItem("System Resource Monitor", None, enabled=False),
            MenuItem("─" * 25, None, enabled=False),  # Separator
            
            MenuItem("Start Monitor", self.start_monitor_action, 
                    enabled=lambda item: not self.running),
            MenuItem("Stop Monitor", self.stop_monitor_action, 
                    enabled=lambda item: self.running),
            MenuItem("Restart Monitor", self.restart_monitor),
            
            MenuItem("─" * 25, None, enabled=False),  # Separator
            
            MenuItem("Open in Browser", self.open_monitor_url, 
                    enabled=lambda item: self.running),
            MenuItem("Chrome Extensions", self.open_chrome_extension_page),
            MenuItem("Setup Instructions", self.show_setup_instructions),
            
            MenuItem("─" * 25, None, enabled=False),  # Separator
            
            MenuItem("Show Status", self.show_status),
            MenuItem("Quit", self.quit_application)
        )
    
    def start_monitor_action(self, icon, item):
        """Start monitor action for menu."""
        if self.start_backend():
            # Update icon to show running state
            icon.icon = self.create_icon()
    
    def stop_monitor_action(self, icon, item):
        """Stop monitor action for menu."""
        self.stop_backend()
        # Update icon to show stopped state
        icon.icon = self.create_icon()
    
    def monitor_backend(self, icon):
        """Monitor the backend process and update icon accordingly."""
        while True:
            try:
                # Check if backend is still running
                if self.backend_process and self.backend_process.poll() is not None:
                    if self.running:  # Was running but now stopped
                        self.running = False
                        icon.icon = self.create_icon()
                
                # Update icon every 10 seconds
                time.sleep(10)
                
            except Exception as e:
                print(f"Monitor error: {e}")
                time.sleep(5)
    
    def run(self):
        """Run the system tray application."""
        # Create and show system tray icon
        icon = Icon(
            name="System Resource Monitor",
            icon=self.create_icon(),
            title="System Resource Monitor",
            menu=self.create_menu()
        )
        
        # Start backend monitoring thread
        monitor_thread = threading.Thread(target=self.monitor_backend, args=(icon,), daemon=True)
        monitor_thread.start()
        
        # Auto-start the backend
        if self.start_backend():
            icon.icon = self.create_icon()
        
        # Show startup notification
        try:
            icon.notify("System Resource Monitor started", "Right-click icon for options")
        except:
            pass  # Notifications might not be supported
        
        # Run the system tray
        icon.run()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="System Resource Monitor - System Tray")
    parser.add_argument("--port", type=int, default=8888,
                       help="Backend server port (default: 8888)")
    
    args = parser.parse_args()
    
    # Check dependencies
    try:
        import pystray
        from PIL import Image
    except ImportError as e:
        print("Missing dependencies for system tray mode.")
        print("Please install: pip install pystray pillow")
        print(f"Error: {e}")
        return
    
    # Create and run system tray monitor
    tray_monitor = SystemTrayMonitor()
    tray_monitor.port = args.port
    tray_monitor.run()


if __name__ == "__main__":
    main()

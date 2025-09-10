#!/usr/bin/env python3
"""
System Resource Monitor System Tray Application
Provides system tray icon with monitoring capabilities and quick access.
"""

import os
import sys
import threading
import webbrowser
from pathlib import Path

# Platform-specific tray imports
try:
    import pystray
    from pystray import MenuItem as item
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False
    print("⚠️  System tray requires 'pystray' and 'Pillow' packages")

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from launch_monitor import MonitorLauncher

class SystemTrayApp:
    def __init__(self):
        self.project_root = project_root
        self.launcher = None
        self.tray_icon = None
        self.is_running = False
        
        # Create tray icon
        if TRAY_AVAILABLE:
            self.create_tray_icon()
    
    def create_tray_icon(self):
        """Create system tray icon with monitoring visualization."""
        # Create icon image
        width = 64
        height = 64
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Draw monitor outline
        monitor_rect = (8, 12, width-8, height-16)
        draw.rectangle(monitor_rect, outline=(100, 150, 255), width=3)
        
        # Draw screen
        screen_rect = (12, 16, width-12, height-20)
        draw.rectangle(screen_rect, fill=(20, 30, 40))
        
        # Draw progress bars (simplified)
        bar_width = width - 24
        bar_height = 4
        
        # CPU bar (green)
        cpu_y = 20
        draw.rectangle((16, cpu_y, 16 + bar_width * 0.7, cpu_y + bar_height), 
                      fill=(0, 255, 100))
        
        # RAM bar (blue)
        ram_y = cpu_y + 8
        draw.rectangle((16, ram_y, 16 + bar_width * 0.5, ram_y + bar_height), 
                      fill=(100, 150, 255))
        
        # GPU bar (orange)
        gpu_y = ram_y + 8
        draw.rectangle((16, gpu_y, 16 + bar_width * 0.3, gpu_y + bar_height), 
                      fill=(255, 150, 50))
        
        # Draw base
        base_rect = (width//2 - 8, height-12, width//2 + 8, height-8)
        draw.rectangle(base_rect, fill=(100, 150, 255))
        
        return image
    
    def create_menu(self):
        """Create system tray context menu."""
        return pystray.Menu(
            item('System Resource Monitor', self.show_monitor, default=True),
            item('Open Dashboard', self.open_dashboard),
            pystray.Menu.SEPARATOR,
            item('Settings', self.show_settings),
            item('About', self.show_about),
            pystray.Menu.SEPARATOR,
            item('Start Monitor', self.start_monitor, enabled=lambda _: not self.is_running),
            item('Stop Monitor', self.stop_monitor, enabled=lambda _: self.is_running),
            pystray.Menu.SEPARATOR,
            item('Exit', self.quit_app)
        )
    
    def show_monitor(self, icon, item):
        """Show main monitor window."""
        if not self.is_running:
            self.start_monitor(icon, item)
        else:
            self.open_dashboard(icon, item)
    
    def open_dashboard(self, icon, item):
        """Open dashboard in browser."""
        try:
            chrome_app_dir = self.project_root / "chrome-app"
            url = f"file:///{chrome_app_dir}/window.html"
            webbrowser.open(url)
        except Exception as e:
            print(f"Error opening dashboard: {e}")
    
    def start_monitor(self, icon, item):
        """Start the monitoring system."""
        if self.is_running:
            return
        
        print("🚀 Starting System Resource Monitor from tray...")
        
        def run_launcher():
            self.launcher = MonitorLauncher(minimized=True)
            self.is_running = True
            
            try:
                self.launcher.launch()
            except Exception as e:
                print(f"Error running launcher: {e}")
            finally:
                self.is_running = False
                self.launcher = None
        
        # Start launcher in separate thread
        launcher_thread = threading.Thread(target=run_launcher, daemon=True)
        launcher_thread.start()
    
    def stop_monitor(self, icon, item):
        """Stop the monitoring system."""
        if not self.is_running or not self.launcher:
            return
        
        print("🛑 Stopping System Resource Monitor from tray...")
        
        try:
            self.launcher.shutdown()
            self.is_running = False
        except Exception as e:
            print(f"Error stopping monitor: {e}")
    
    def show_settings(self, icon, item):
        """Show settings dialog."""
        # For now, just open the Chrome app
        self.open_dashboard(icon, item)
    
    def show_about(self, icon, item):
        """Show about information."""
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            
            about_text = """System Resource Monitor v1.0
            
Real-time system monitoring with:
• CPU, RAM, Disk usage
• GPU monitoring (NVIDIA)
• Temperature monitoring
• WebSocket real-time updates

Built with Python, TypeScript, and Chrome App Platform
            
© 2024 - Open Source Project"""
            
            messagebox.showinfo("About System Resource Monitor", about_text)
            root.destroy()
            
        except ImportError:
            print("About: System Resource Monitor v1.0 - Real-time system monitoring")
    
    def quit_app(self, icon, item):
        """Quit the tray application."""
        print("👋 Exiting System Resource Monitor...")
        
        # Stop monitor if running
        if self.is_running and self.launcher:
            self.launcher.shutdown()
        
        # Stop tray icon
        if self.tray_icon:
            self.tray_icon.stop()
    
    def run(self):
        """Run the system tray application."""
        if not TRAY_AVAILABLE:
            print("❌ System tray not available. Running launcher directly...")
            launcher = MonitorLauncher()
            return launcher.launch()
        
        print("🔧 Starting System Resource Monitor in system tray...")
        
        try:
            icon_image = self.create_tray_icon()
            menu = self.create_menu()
            
            self.tray_icon = pystray.Icon(
                "System Resource Monitor",
                icon_image,
                "System Resource Monitor",
                menu
            )
            
            # Auto-start monitor
            self.start_monitor(None, None)
            
            # Run tray icon (blocking)
            self.tray_icon.run()
            
        except Exception as e:
            print(f"❌ System tray error: {e}")
            print("Falling back to direct launcher...")
            launcher = MonitorLauncher()
            return launcher.launch()

def main():
    """Main entry point for system tray application."""
    import argparse
    
    parser = argparse.ArgumentParser(description="System Resource Monitor System Tray")
    parser.add_argument("--no-tray", action="store_true",
                       help="Run without system tray (direct launcher)")
    parser.add_argument("--install-tray-deps", action="store_true",
                       help="Install system tray dependencies")
    
    args = parser.parse_args()
    
    if args.install_tray_deps:
        print("📦 Installing system tray dependencies...")
        import subprocess
        
        packages = ['pystray', 'Pillow']
        for package in packages:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"   ✅ Installed {package}")
            except subprocess.CalledProcessError as e:
                print(f"   ❌ Failed to install {package}: {e}")
        return
    
    if args.no_tray or not TRAY_AVAILABLE:
        # Run launcher directly
        launcher = MonitorLauncher()
        success = launcher.launch()
        sys.exit(0 if success else 1)
    
    # Run system tray app
    tray_app = SystemTrayApp()
    tray_app.run()

if __name__ == "__main__":
    main()

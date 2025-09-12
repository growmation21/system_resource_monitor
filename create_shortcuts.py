#!/usr/bin/env python3
"""
Desktop Integration for System Resource Monitor
Creates desktop shortcuts for easy background launching.
"""

import os
import sys
import winshell
from pathlib import Path
import argparse


def create_desktop_shortcuts():
    """Create desktop shortcuts for the monitor."""
    project_root = Path(__file__).parent
    desktop = winshell.desktop()
    
    shortcuts_created = []
    
    try:
        # Shortcut 1: Normal launcher (with console)
        shortcut_path = os.path.join(desktop, "System Resource Monitor.lnk")
        with winshell.shortcut(shortcut_path) as shortcut:
            shortcut.path = sys.executable
            shortcut.arguments = f'"{project_root}/launch_monitor.py"'
            shortcut.working_directory = str(project_root)
            shortcut.description = "System Resource Monitor - Normal Mode"
            shortcut.icon_location = (sys.executable, 0)
        
        shortcuts_created.append("System Resource Monitor.lnk")
        
        # Shortcut 2: Hidden launcher (no console)
        shortcut_path = os.path.join(desktop, "System Resource Monitor (Background).lnk")
        with winshell.shortcut(shortcut_path) as shortcut:
            shortcut.path = sys.executable.replace("python.exe", "pythonw.exe")
            shortcut.arguments = f'"{project_root}/launch_monitor.py" --hidden'
            shortcut.working_directory = str(project_root)
            shortcut.description = "System Resource Monitor - Background Mode (No Console)"
            shortcut.icon_location = (sys.executable, 0)
        
        shortcuts_created.append("System Resource Monitor (Background).lnk")
        
        # Shortcut 3: System Tray launcher (if dependencies available)
        try:
            import pystray
            from PIL import Image
            
            shortcut_path = os.path.join(desktop, "System Resource Monitor (Tray).lnk")
            with winshell.shortcut(shortcut_path) as shortcut:
                shortcut.path = sys.executable.replace("python.exe", "pythonw.exe")
                shortcut.arguments = f'"{project_root}/system_tray_launcher.py"'
                shortcut.working_directory = str(project_root)
                shortcut.description = "System Resource Monitor - System Tray Mode"
                shortcut.icon_location = (sys.executable, 0)
            
            shortcuts_created.append("System Resource Monitor (Tray).lnk")
            
        except ImportError:
            print("System tray dependencies not available. Skipping tray shortcut.")
        
        # Shortcut 4: PowerShell launcher
        try:
            shortcut_path = os.path.join(desktop, "Start System Monitor (PowerShell).lnk")
            with winshell.shortcut(shortcut_path) as shortcut:
                shortcut.path = "powershell.exe"
                shortcut.arguments = f'-ExecutionPolicy Bypass -File "{project_root}/Start-Monitor.ps1" -SystemTray'
                shortcut.working_directory = str(project_root)
                shortcut.description = "System Resource Monitor - PowerShell Launcher"
                shortcut.icon_location = ("powershell.exe", 0)
            
            shortcuts_created.append("Start System Monitor (PowerShell).lnk")
            
        except Exception:
            pass  # PowerShell shortcut is optional
        
        return shortcuts_created
        
    except Exception as e:
        print(f"Error creating shortcuts: {e}")
        return []


def remove_desktop_shortcuts():
    """Remove desktop shortcuts."""
    desktop = winshell.desktop()
    
    shortcuts = [
        "System Resource Monitor.lnk",
        "System Resource Monitor (Background).lnk", 
        "System Resource Monitor (Tray).lnk",
        "Start System Monitor (PowerShell).lnk"
    ]
    
    removed = []
    for shortcut in shortcuts:
        shortcut_path = os.path.join(desktop, shortcut)
        try:
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
                removed.append(shortcut)
        except Exception as e:
            print(f"Could not remove {shortcut}: {e}")
    
    return removed


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Desktop Integration for System Resource Monitor")
    parser.add_argument("--create", action="store_true", help="Create desktop shortcuts")
    parser.add_argument("--remove", action="store_true", help="Remove desktop shortcuts")
    
    args = parser.parse_args()
    
    if not args.create and not args.remove:
        print("Desktop Integration for System Resource Monitor")
        print("=" * 50)
        choice = input("Create desktop shortcuts? (y/n): ").lower()
        args.create = choice in ['y', 'yes', '1', 'true']
    
    if args.create:
        print("Creating desktop shortcuts...")
        try:
            import winshell
        except ImportError:
            print("Installing winshell for shortcut creation...")
            import subprocess
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'winshell'])
            import winshell
        
        shortcuts = create_desktop_shortcuts()
        if shortcuts:
            print("Desktop shortcuts created successfully:")
            for shortcut in shortcuts:
                print(f"  ✅ {shortcut}")
        else:
            print("❌ Failed to create shortcuts.")
    
    elif args.remove:
        print("Removing desktop shortcuts...")
        removed = remove_desktop_shortcuts()
        if removed:
            print("Desktop shortcuts removed:")
            for shortcut in removed:
                print(f"  ✅ {shortcut}")
        else:
            print("No shortcuts found to remove.")


if __name__ == "__main__":
    main()

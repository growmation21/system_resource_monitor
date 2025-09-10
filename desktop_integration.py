#!/usr/bin/env python3
"""
Desktop Integration Installer for System Resource Monitor
Creates desktop shortcuts and handles app installation process.
"""

import os
import sys
import shutil
import platform
import subprocess
import json
from pathlib import Path

class DesktopIntegrator:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.chrome_app_dir = self.project_root / "chrome-app"
        self.app_name = "System Resource Monitor"
        self.app_id = "system-resource-monitor"
        
        # Platform-specific paths
        self.platform = platform.system().lower()
        self.setup_platform_paths()
    
    def setup_platform_paths(self):
        """Setup platform-specific installation paths."""
        if self.platform == "windows":
            self.desktop_dir = Path.home() / "Desktop"
            self.start_menu_dir = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs"
            self.app_data_dir = Path.home() / "AppData" / "Local" / self.app_id
        elif self.platform == "darwin":  # macOS
            self.desktop_dir = Path.home() / "Desktop"
            self.app_data_dir = Path.home() / "Library" / "Application Support" / self.app_id
        else:  # Linux
            self.desktop_dir = Path.home() / "Desktop"
            self.app_data_dir = Path.home() / ".local" / "share" / self.app_id
    
    def create_desktop_shortcut(self):
        """Create desktop shortcut for the application."""
        print("Creating desktop shortcut...")
        
        if self.platform == "windows":
            self._create_windows_shortcut()
        elif self.platform == "darwin":
            self._create_macos_shortcut()
        else:
            self._create_linux_shortcut()
    
    def _create_windows_shortcut(self):
        """Create Windows .lnk shortcut."""
        try:
            import win32com.client
            
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut_path = self.desktop_dir / f"{self.app_name}.lnk"
            shortcut = shell.CreateShortCut(str(shortcut_path))
            
            # Python script to launch the app
            launcher_script = self.project_root / "launch_monitor.py"
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{launcher_script}"'
            shortcut.WorkingDirectory = str(self.project_root)
            shortcut.IconLocation = str(self.chrome_app_dir / "icons" / "icon-256.png")
            shortcut.Description = "System Resource Monitor - Real-time hardware monitoring"
            shortcut.save()
            
            print(f"✅ Windows shortcut created: {shortcut_path}")
            
        except ImportError:
            print("⚠️  Creating Windows shortcut requires pywin32. Creating batch file instead...")
            self._create_windows_batch_file()
    
    def _create_windows_batch_file(self):
        """Create Windows batch file as alternative to .lnk shortcut."""
        batch_content = f'''@echo off
cd /d "{self.project_root}"
python launch_monitor.py
pause
'''
        batch_path = self.desktop_dir / f"{self.app_name}.bat"
        with open(batch_path, 'w') as f:
            f.write(batch_content)
        
        print(f"✅ Windows batch file created: {batch_path}")
    
    def _create_macos_shortcut(self):
        """Create macOS application bundle."""
        app_bundle_dir = self.desktop_dir / f"{self.app_name}.app"
        contents_dir = app_bundle_dir / "Contents"
        macos_dir = contents_dir / "MacOS"
        resources_dir = contents_dir / "Resources"
        
        # Create directory structure
        macos_dir.mkdir(parents=True, exist_ok=True)
        resources_dir.mkdir(parents=True, exist_ok=True)
        
        # Create Info.plist
        plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>{self.app_name}</string>
    <key>CFBundleIdentifier</key>
    <string>com.growmation21.{self.app_id}</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleExecutable</key>
    <string>launcher</string>
    <key>LSUIElement</key>
    <true/>
</dict>
</plist>'''
        
        with open(contents_dir / "Info.plist", 'w') as f:
            f.write(plist_content)
        
        # Create launcher script
        launcher_content = f'''#!/bin/bash
cd "{self.project_root}"
python3 launch_monitor.py
'''
        launcher_path = macos_dir / "launcher"
        with open(launcher_path, 'w') as f:
            f.write(launcher_content)
        os.chmod(launcher_path, 0o755)
        
        print(f"✅ macOS app bundle created: {app_bundle_dir}")
    
    def _create_linux_shortcut(self):
        """Create Linux .desktop file."""
        desktop_content = f'''[Desktop Entry]
Name={self.app_name}
Comment=Real-time system resource monitoring
Exec=python3 "{self.project_root / "launch_monitor.py"}"
Icon={self.chrome_app_dir / "icons" / "icon-256.png"}
Terminal=false
Type=Application
Categories=System;Monitor;Utility;
StartupNotify=true
'''
        
        desktop_path = self.desktop_dir / f"{self.app_id}.desktop"
        with open(desktop_path, 'w') as f:
            f.write(desktop_content)
        os.chmod(desktop_path, 0o755)
        
        print(f"✅ Linux desktop file created: {desktop_path}")
    
    def create_start_menu_entry(self):
        """Create start menu entry (Windows only)."""
        if self.platform != "windows":
            return
        
        print("Creating Start Menu entry...")
        self.start_menu_dir.mkdir(parents=True, exist_ok=True)
        
        # Create shortcut in Start Menu
        try:
            import win32com.client
            
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut_path = self.start_menu_dir / f"{self.app_name}.lnk"
            shortcut = shell.CreateShortCut(str(shortcut_path))
            
            launcher_script = self.project_root / "launch_monitor.py"
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{launcher_script}"'
            shortcut.WorkingDirectory = str(self.project_root)
            shortcut.IconLocation = str(self.chrome_app_dir / "icons" / "icon-256.png")
            shortcut.Description = "System Resource Monitor"
            shortcut.save()
            
            print(f"✅ Start Menu entry created: {shortcut_path}")
            
        except ImportError:
            print("⚠️  Start Menu entry requires pywin32")
    
    def setup_autostart(self, enable=False):
        """Configure application autostart."""
        print(f"{'Enabling' if enable else 'Configuring'} autostart...")
        
        if self.platform == "windows":
            self._setup_windows_autostart(enable)
        elif self.platform == "darwin":
            self._setup_macos_autostart(enable)
        else:
            self._setup_linux_autostart(enable)
    
    def _setup_windows_autostart(self, enable):
        """Setup Windows autostart via registry."""
        import winreg
        
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_key = self.app_id
        launcher_script = self.project_root / "launch_monitor.py"
        command = f'"{sys.executable}" "{launcher_script}" --minimized'
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            
            if enable:
                winreg.SetValueEx(key, app_key, 0, winreg.REG_SZ, command)
                print(f"✅ Windows autostart enabled")
            else:
                try:
                    winreg.DeleteValue(key, app_key)
                    print(f"✅ Windows autostart disabled")
                except FileNotFoundError:
                    print(f"ℹ️  Autostart entry not found")
            
            winreg.CloseKey(key)
            
        except Exception as e:
            print(f"❌ Error setting up Windows autostart: {e}")
    
    def _setup_macos_autostart(self, enable):
        """Setup macOS autostart via LaunchAgents."""
        plist_name = f"com.growmation21.{self.app_id}.plist"
        launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
        plist_path = launch_agents_dir / plist_name
        
        if enable:
            launch_agents_dir.mkdir(parents=True, exist_ok=True)
            
            plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.growmation21.{self.app_id}</string>
    <key>ProgramArguments</key>
    <array>
        <string>python3</string>
        <string>{self.project_root / "launch_monitor.py"}</string>
        <string>--minimized</string>
    </array>
    <key>WorkingDirectory</key>
    <string>{self.project_root}</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>'''
            
            with open(plist_path, 'w') as f:
                f.write(plist_content)
            
            print(f"✅ macOS autostart enabled: {plist_path}")
        else:
            if plist_path.exists():
                plist_path.unlink()
                print(f"✅ macOS autostart disabled")
    
    def _setup_linux_autostart(self, enable):
        """Setup Linux autostart via .desktop file."""
        autostart_dir = Path.home() / ".config" / "autostart"
        desktop_path = autostart_dir / f"{self.app_id}.desktop"
        
        if enable:
            autostart_dir.mkdir(parents=True, exist_ok=True)
            
            desktop_content = f'''[Desktop Entry]
Name={self.app_name}
Comment=System Resource Monitor
Exec=python3 "{self.project_root / "launch_monitor.py"}" --minimized
Icon={self.chrome_app_dir / "icons" / "icon-256.png"}
Terminal=false
Type=Application
Categories=System;Monitor;
X-GNOME-Autostart-enabled=true
Hidden=false
'''
            
            with open(desktop_path, 'w') as f:
                f.write(desktop_content)
            os.chmod(desktop_path, 0o755)
            
            print(f"✅ Linux autostart enabled: {desktop_path}")
        else:
            if desktop_path.exists():
                desktop_path.unlink()
                print(f"✅ Linux autostart disabled")
    
    def create_app_data_directory(self):
        """Create application data directory for settings and logs."""
        print("Creating application data directory...")
        
        self.app_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.app_data_dir / "config").mkdir(exist_ok=True)
        (self.app_data_dir / "logs").mkdir(exist_ok=True)
        (self.app_data_dir / "chrome-app").mkdir(exist_ok=True)
        
        # Copy Chrome app files to user directory
        chrome_app_user_dir = self.app_data_dir / "chrome-app"
        for file in self.chrome_app_dir.glob("*"):
            if file.is_file():
                shutil.copy2(file, chrome_app_user_dir)
            elif file.is_dir() and file.name != "__pycache__":
                if (chrome_app_user_dir / file.name).exists():
                    shutil.rmtree(chrome_app_user_dir / file.name)
                shutil.copytree(file, chrome_app_user_dir / file.name)
        
        print(f"✅ App data directory created: {self.app_data_dir}")
        
        return self.app_data_dir
    
    def install(self, autostart=False):
        """Complete installation process."""
        print(f"🚀 Installing {self.app_name}...")
        print(f"Platform: {self.platform}")
        print(f"Project root: {self.project_root}")
        
        try:
            # Create app data directory
            self.create_app_data_directory()
            
            # Create desktop shortcuts
            self.create_desktop_shortcut()
            
            # Create Start Menu entry (Windows only)
            if self.platform == "windows":
                self.create_start_menu_entry()
            
            # Setup autostart if requested
            if autostart:
                self.setup_autostart(True)
            
            print(f"\n✅ {self.app_name} installed successfully!")
            print("\n📋 Installation Summary:")
            print(f"   • Desktop shortcut created")
            if self.platform == "windows":
                print(f"   • Start Menu entry created")
            if autostart:
                print(f"   • Autostart enabled")
            print(f"   • App data directory: {self.app_data_dir}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Installation failed: {e}")
            return False
    
    def uninstall(self):
        """Uninstall the application and remove all created files."""
        print(f"🗑️  Uninstalling {self.app_name}...")
        
        removed_items = []
        
        # Remove desktop shortcut
        for ext in ['.lnk', '.bat', '.desktop']:
            shortcut_path = self.desktop_dir / f"{self.app_name}{ext}"
            if shortcut_path.exists():
                shortcut_path.unlink()
                removed_items.append(f"Desktop shortcut ({shortcut_path.name})")
        
        # Remove macOS app bundle
        app_bundle = self.desktop_dir / f"{self.app_name}.app"
        if app_bundle.exists():
            shutil.rmtree(app_bundle)
            removed_items.append("macOS app bundle")
        
        # Remove Start Menu entry (Windows)
        if self.platform == "windows":
            start_menu_shortcut = self.start_menu_dir / f"{self.app_name}.lnk"
            if start_menu_shortcut.exists():
                start_menu_shortcut.unlink()
                removed_items.append("Start Menu entry")
        
        # Disable autostart
        self.setup_autostart(False)
        removed_items.append("Autostart configuration")
        
        # Remove app data directory
        if self.app_data_dir.exists():
            shutil.rmtree(self.app_data_dir)
            removed_items.append(f"App data directory")
        
        print(f"✅ Uninstallation complete!")
        print("Removed items:")
        for item in removed_items:
            print(f"   • {item}")

def main():
    """Main installation script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="System Resource Monitor Desktop Integration")
    parser.add_argument("--install", action="store_true", help="Install desktop integration")
    parser.add_argument("--uninstall", action="store_true", help="Uninstall desktop integration")
    parser.add_argument("--autostart", action="store_true", help="Enable autostart (with --install)")
    parser.add_argument("--icons-only", action="store_true", help="Generate icons only")
    
    args = parser.parse_args()
    
    if args.icons_only:
        # Generate icons only
        icons_script = Path(__file__).parent / "chrome-app" / "icons" / "generate_icons.py"
        subprocess.run([sys.executable, str(icons_script)])
        return
    
    integrator = DesktopIntegrator()
    
    if args.uninstall:
        integrator.uninstall()
    elif args.install:
        success = integrator.install(autostart=args.autostart)
        if success:
            print(f"\n🎉 Installation complete! You can now launch {integrator.app_name} from:")
            print(f"   • Desktop shortcut")
            if integrator.platform == "windows":
                print(f"   • Start Menu")
            if args.autostart:
                print(f"   • Automatically at system startup")
        else:
            sys.exit(1)
    else:
        print("Use --install to install or --uninstall to remove desktop integration")
        print("Use --help for more options")

if __name__ == "__main__":
    main()

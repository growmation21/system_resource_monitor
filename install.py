#!/usr/bin/env python3
"""
System Resource Monitor - Installer Script

Handles global dependency installation and system setup
without requiring virtual environments.
"""

import sys
import subprocess
import platform
import os
from pathlib import Path

def get_python_executable():
    """Get the Python executable path"""
    return sys.executable

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            shell=True if platform.system() == "Windows" else False
        )
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {' '.join(command) if isinstance(command, list) else command}")
        print(f"   Return code: {e.returncode}")
        if e.stdout:
            print(f"   Output: {e.stdout}")
        if e.stderr:
            print(f"   Error: {e.stderr}")
        return False

def install_dependencies():
    """Install Python dependencies globally"""
    python_exe = get_python_executable()
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print(f"❌ Requirements file not found: {requirements_file}")
        return False
    
    # Upgrade pip first
    if not run_command(
        [python_exe, "-m", "pip", "install", "--upgrade", "pip"],
        "Upgrading pip"
    ):
        print("⚠️  Warning: Failed to upgrade pip, continuing anyway...")
    
    # Install requirements
    install_cmd = [
        python_exe, "-m", "pip", "install", "-r", str(requirements_file)
    ]
    
    # Add --user flag if not running as admin/root
    if not is_admin():
        install_cmd.insert(-2, "--user")
        print("📝 Installing to user directory (use --global for system-wide installation)")
    
    return run_command(install_cmd, "Installing Python dependencies")

def install_pytorch_cuda():
    """Install PyTorch with CUDA support if NVIDIA GPU detected"""
    if not check_nvidia_gpu():
        print("ℹ️  No NVIDIA GPU detected, skipping CUDA PyTorch installation")
        return True
    
    python_exe = get_python_executable()
    
    # Uninstall CPU-only PyTorch first
    run_command(
        [python_exe, "-m", "pip", "uninstall", "torch", "torchvision", "-y"],
        "Removing CPU-only PyTorch"
    )
    
    # Install CUDA version
    install_cmd = [
        python_exe, "-m", "pip", "install", 
        "torch", "torchvision", 
        "--index-url", "https://download.pytorch.org/whl/cu124"
    ]
    
    if not is_admin():
        install_cmd.insert(-4, "--user")
    
    return run_command(install_cmd, "Installing PyTorch with CUDA support")

def check_nvidia_gpu():
    """Check if NVIDIA GPU is available"""
    try:
        result = subprocess.run(
            ["nvidia-smi"],
            capture_output=True,
            text=True,
            check=True
        )
        return "NVIDIA" in result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def is_admin():
    """Check if running with administrator privileges"""
    try:
        if platform.system() == "Windows":
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        else:
            return os.geteuid() == 0
    except:
        return False

def verify_installation():
    """Verify that all dependencies are correctly installed"""
    print("\n🔍 Verifying installation...")
    
    python_exe = get_python_executable()
    test_script = '''
import sys
errors = []

try:
    import psutil
    print(f"✅ psutil {psutil.__version__}")
except ImportError as e:
    errors.append(f"❌ psutil: {e}")

try:
    import pynvml
    print("✅ pynvml (nvidia-ml-py)")
except ImportError as e:
    errors.append(f"❌ pynvml: {e}")

try:
    import cpuinfo
    print("✅ py-cpuinfo")
except ImportError as e:
    errors.append(f"❌ py-cpuinfo: {e}")

try:
    import torch
    print(f"✅ torch {torch.__version__}")
    print(f"   CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"   GPU count: {torch.cuda.device_count()}")
except ImportError as e:
    errors.append(f"❌ torch: {e}")

try:
    import aiohttp
    print(f"✅ aiohttp {aiohttp.__version__}")
except ImportError as e:
    errors.append(f"❌ aiohttp: {e}")

if errors:
    print("\\n❌ Installation errors:")
    for error in errors:
        print(f"   {error}")
    sys.exit(1)
else:
    print("\\n🎉 All dependencies installed successfully!")
    '''
    
    return run_command(
        [python_exe, "-c", test_script],
        "Running installation verification"
    )

def create_launcher():
    """Create desktop launcher/shortcut"""
    if platform.system() == "Windows":
        return create_windows_shortcut()
    elif platform.system() == "Linux":
        return create_linux_desktop_entry()
    elif platform.system() == "Darwin":
        return create_macos_app()
    else:
        print("⚠️  Unsupported platform for launcher creation")
        return True

def create_windows_shortcut():
    """Create Windows desktop shortcut"""
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        shortcut_path = os.path.join(desktop, "System Resource Monitor.lnk")
        
        python_exe = get_python_executable()
        main_script = Path(__file__).parent / "main.py"
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = python_exe
        shortcut.Arguments = f'"{main_script}"'
        shortcut.WorkingDirectory = str(Path(__file__).parent)
        shortcut.IconLocation = python_exe
        shortcut.save()
        
        print(f"✅ Desktop shortcut created: {shortcut_path}")
        return True
        
    except ImportError:
        print("⚠️  pywin32 not available, skipping Windows shortcut creation")
        print("   You can manually create a shortcut to main.py")
        return True
    except Exception as e:
        print(f"⚠️  Failed to create Windows shortcut: {e}")
        return True

def create_linux_desktop_entry():
    """Create Linux desktop entry"""
    # Implementation for Linux desktop entry
    print("ℹ️  Linux desktop entry creation not implemented yet")
    return True

def create_macos_app():
    """Create macOS app bundle"""
    # Implementation for macOS app
    print("ℹ️  macOS app creation not implemented yet")
    return True

def main():
    """Main installer function"""
    print("🚀 System Resource Monitor - Installation")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Check admin privileges
    if is_admin():
        print("⚡ Running with administrator privileges")
    else:
        print("👤 Running in user mode")
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install basic dependencies")
        return 1
    
    # Install PyTorch with CUDA if applicable
    if not install_pytorch_cuda():
        print("❌ Failed to install PyTorch with CUDA")
        return 1
    
    # Verify installation
    if not verify_installation():
        print("❌ Installation verification failed")
        return 1
    
    # Create launcher
    create_launcher()
    
    print("\n" + "=" * 50)
    print("🎉 Installation completed successfully!")
    print("\nTo start the System Resource Monitor:")
    print(f"   python {Path(__file__).parent / 'main.py'}")
    print("\nOr use the desktop shortcut if created.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

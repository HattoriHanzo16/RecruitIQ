#!/usr/bin/env python3
"""
RecruitIQ Installation Script
Sets up RecruitIQ with all dependencies and configuration
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def print_header():
    """Print the installation header"""
    try:
        # Import the ASCII art from our utility module
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from recruitiq.utils.ascii_art import print_welcome_banner
        
        print_welcome_banner()
        print("\n🚀 INSTALLATION STARTING...")
        print("   Setting up your Job Market Intelligence Platform\n")
    except ImportError:
        # Fallback to simple banner if import fails
        print("""
╭─────────────────────────────────────────────────────────────╮
│                                                             │
│           🎯 RecruitIQ Installation                         │
│           Job Market Intelligence CLI Tool                   │
│                                                             │
╰─────────────────────────────────────────────────────────────╯
        """)

def check_python_version():
    """Check if Python version is compatible"""
    print("🔍 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing dependencies...")
    
    try:
        # Upgrade pip first
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install requirements
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)

def setup_database():
    """Initialize the database"""
    print("\n🗄️  Setting up database...")
    
    try:
        # Package should already be installed at this point
        from recruitiq.db.session import init_db
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        print("   You can run 'recruitiq init' later to set up the database")

def install_chrome_driver():
    """Install Chrome driver for web scraping"""
    print("\n🌐 Setting up web driver...")
    
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        ChromeDriverManager().install()
        print("✅ Chrome driver installed successfully")
    except Exception as e:
        print(f"⚠️  Chrome driver setup failed: {e}")
        print("   Web scraping may not work properly")

def create_desktop_shortcut():
    """Create a desktop shortcut (optional)"""
    system = platform.system()
    
    if system == "Windows":
        # Windows shortcut creation
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            path = os.path.join(desktop, "RecruitIQ.lnk")
            target = sys.executable
            wDir = os.getcwd()
            icon = target
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = target
            shortcut.Arguments = f'"{os.path.join(wDir, "main.py")}"'
            shortcut.WorkingDirectory = wDir
            shortcut.IconLocation = icon
            shortcut.save()
            
            print("✅ Desktop shortcut created")
        except ImportError:
            print("⚠️  Desktop shortcut creation requires pywin32 package")
        except Exception as e:
            print(f"⚠️  Could not create desktop shortcut: {e}")
    
    elif system == "Darwin":  # macOS
        try:
            app_path = "/Applications/RecruitIQ.app"
            # Create a simple app bundle
            print("⚠️  macOS app creation not implemented yet")
        except Exception as e:
            print(f"⚠️  Could not create macOS app: {e}")
    
    elif system == "Linux":
        try:
            # Create .desktop file
            desktop_entry = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=RecruitIQ
Comment=Job Market Intelligence CLI Tool
Exec={sys.executable} {os.path.join(os.getcwd(), "main.py")}
Icon=terminal
Terminal=true
Categories=Development;
"""
            
            desktop_path = Path.home() / "Desktop" / "RecruitIQ.desktop"
            with open(desktop_path, "w") as f:
                f.write(desktop_entry)
            
            # Make executable
            os.chmod(desktop_path, 0o755)
            print("✅ Desktop shortcut created")
        except Exception as e:
            print(f"⚠️  Could not create Linux desktop entry: {e}")

def setup_command_alias():
    """Set up command alias for easy access"""
    print("\n⚡ Setting up command alias...")
    
    # Install as editable package
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])
        print("✅ 'recruitiq' command installed globally")
        print("   You can now run 'recruitiq' from anywhere!")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Failed to install global command: {e}")
        print("   You can run the tool using 'python cli.py'")

def print_success():
    """Print success message and usage instructions"""
    print("""
╭─────────────────────────────────────────────────────────────╮
│                                                             │
│           🎉 Installation Complete!                         │
│                                                             │
│   Get started:                                              │
│   • Run 'recruitiq' to open the interactive interface       │
│   • Or use 'python main.py' if global install failed       │
│                                                             │
│   First steps:                                              │
│   1. Start scraping: Use the interactive interface          │
│   2. Analyze data: Built-in analytics and search            │
│   3. Generate reports: Export beautiful HTML reports        │
│                                                             │
│           Happy job hunting! 🚀                             │
│                                                             │
╰─────────────────────────────────────────────────────────────╯
    """)

def main():
    """Main installation function"""
    print_header()
    
    try:
        check_python_version()
        install_dependencies()
        setup_command_alias()  # Install package first
        setup_database()       # Then initialize database
        install_chrome_driver()
        
        # Optional features
        response = input("\n🎨 Create desktop shortcut? (y/N): ").lower()
        if response in ['y', 'yes']:
            create_desktop_shortcut()
        
        print_success()
        
    except KeyboardInterrupt:
        print("\n❌ Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Installation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
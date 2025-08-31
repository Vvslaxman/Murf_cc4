#!/usr/bin/env python3
"""
SocialCast Setup Script
Helps users set up the SocialCast project quickly
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_node_version():
    """Check if Node.js is installed"""
    print("📦 Checking Node.js...")
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        version = result.stdout.strip()
        print(f"✅ Node.js {version} found")
        return True
    except FileNotFoundError:
        print("❌ Node.js not found. Please install Node.js 16+ from https://nodejs.org/")
        return False

def install_python_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    # Check if pip is available
    try:
        subprocess.run([sys.executable, '-m', 'pip', '--version'], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("❌ pip not available. Please install pip first.")
        return False
    
    # Install requirements
    if os.path.exists('requirements.txt'):
        return run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing Python packages")
    else:
        print("❌ requirements.txt not found")
        return False

def setup_environment():
    """Setup environment variables"""
    print("🔧 Setting up environment...")
    
    env_file = Path('.env')
    env_example = Path('env.example')
    
    if not env_file.exists() and env_example.exists():
        # Copy example file
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from template")
        print("⚠️ Please edit .env file with your API keys:")
        print("   - MURF_API_KEY: Get from https://murf.ai")
        print("   - OPENAI_API_KEY: Get from https://openai.com (optional)")
        return True
    elif env_file.exists():
        print("✅ .env file already exists")
        return True
    else:
        print("❌ No environment template found")
        return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = ['temp_audio', 'chrome-extension/dist']
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created {directory}/")
    return True
    
def setup_chrome_extension():
    """Setup Chrome extension"""
    print("🔧 Setting up Chrome extension...")
    
    extension_dir = Path('chrome-extension')
    if not extension_dir.exists():
        print("❌ Chrome extension directory not found")
        return False
    
    # Create placeholder icons if they don't exist
    icons_dir = extension_dir / 'icons'
    icons_dir.mkdir(exist_ok=True)
    
    # Create simple placeholder icons (colored squares)
    icon_sizes = [16, 48, 128]
    for size in icon_sizes:
        icon_path = icons_dir / f'icon{size}.png'
        if not icon_path.exists():
            # Create a simple colored square as placeholder
            try:
                from PIL import Image, ImageDraw
                img = Image.new('RGB', (size, size), color='#667eea')
                draw = ImageDraw.Draw(img)
                # Add a simple microphone icon
                draw.ellipse([size//4, size//4, 3*size//4, 3*size//4], outline='white', width=2)
                img.save(icon_path)
                print(f"✅ Created placeholder icon: {icon_path}")
            except ImportError:
                print(f"⚠️ PIL not available, skipping icon creation for {size}x{size}")
            except Exception as e:
                print(f"⚠️ Could not create icon {size}x{size}: {e}")
    
    print("✅ Chrome extension setup completed")
    print("📋 To load the extension in Chrome:")
    print("   1. Open Chrome and go to chrome://extensions/")
    print("   2. Enable 'Developer mode'")
    print("   3. Click 'Load unpacked'")
    print("   4. Select the 'chrome-extension' folder")
    
    return True

def test_setup():
    """Test the setup"""
    print("🧪 Testing setup...")
    
    # Test Python imports
    try:
        import fastapi
        import uvicorn
        import websockets
        print("✅ Python dependencies imported successfully")
    except ImportError as e:
        print(f"❌ Python dependency import failed: {e}")
        return False
    
    # Test if backend can start
    print("🚀 Testing backend startup...")
    try:
        # Try to import the app
        from app import app
        print("✅ Backend app imported successfully")
    except Exception as e:
        print(f"❌ Backend import failed: {e}")
        return False
    
    return True

def main():
    """Main setup function"""
    print("🎙️ SocialCast Setup")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python_version():
        return False
    
    if not check_node_version():
        print("⚠️ Node.js not found, but it's only needed for Chrome extension development")
    
    # Setup steps
    steps = [
        ("Installing Python dependencies", install_python_dependencies),
        ("Setting up environment", setup_environment),
        ("Creating directories", create_directories),
        ("Setting up Chrome extension", setup_chrome_extension),
        ("Testing setup", test_setup)
    ]
    
    for description, step_func in steps:
        if not step_func():
            print(f"❌ Setup failed at: {description}")
            return False
    
    print("\n" + "=" * 50)
    print("🎉 SocialCast setup completed successfully!")
    print("=" * 50)
    
    print("\n📋 Next steps:")
    print("1. Edit .env file with your API keys")
    print("2. Start the backend: python app.py")
    print("3. Load the Chrome extension in your browser")
    print("4. Visit a social media site and start listening!")
    
    print("\n🔗 Useful links:")
    print("- Murf API: https://murf.ai")
    print("- OpenAI API: https://openai.com")
    print("- Chrome Extensions: chrome://extensions/")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


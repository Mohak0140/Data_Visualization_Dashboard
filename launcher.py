#!/usr/bin/env python3
"""
Data Visualization Dashboard Launcher
Replaces bash scripts with Python-based startup functionality
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path
import time
import signal

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def setup_virtual_environment():
    """Create virtual environment if it doesn't exist"""
    venv_path = Path("venv")
    
    if not venv_path.exists():
        print("📦 Creating virtual environment...")
        try:
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
            print("✅ Virtual environment created")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
    else:
        print("✅ Virtual environment exists")
    
    return True

def install_dependencies(app_type="streamlit"):
    """Install dependencies for the specified application"""
    if app_type == "streamlit":
        requirements_file = Path("requirements.txt")
    else:  # flask
        requirements_file = Path("backend/requirements.txt")
    
    if not requirements_file.exists():
        print(f"❌ Requirements file not found: {requirements_file}")
        return False
    
    print(f"📦 Installing {app_type} dependencies...")
    
    # Determine pip path
    if os.name == 'nt':  # Windows
        pip_path = Path("venv/Scripts/pip")
    else:  # Unix/Linux/MacOS
        pip_path = Path("venv/bin/pip")
    
    try:
        subprocess.run([
            str(pip_path), "install", "-r", str(requirements_file)
        ], check=True)
        print(f"✅ {app_type.title()} dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {app_type} dependencies: {e}")
        return False

def start_streamlit():
    """Start the Streamlit application"""
    print("🚀 Starting Streamlit Application...")
    print("=" * 50)
    
    # Check environment
    check_python_version()
    if not setup_virtual_environment():
        return False
    
    if not install_dependencies("streamlit"):
        return False
    
    # Determine python path
    if os.name == 'nt':  # Windows
        python_path = Path("venv/Scripts/python")
    else:  # Unix/Linux/MacOS
        python_path = Path("venv/bin/python")
    
    print("🌐 Starting Streamlit server...")
    print("   URL: http://localhost:8501")
    print("   Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        # Start streamlit
        process = subprocess.run([
            str(python_path), "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--server.headless", "true"
        ])
        return True
    except KeyboardInterrupt:
        print("\n👋 Streamlit stopped by user")
        return True
    except Exception as e:
        print(f"❌ Failed to start Streamlit: {e}")
        return False

def start_flask():
    """Start the Flask backend"""
    print("🚀 Starting Flask Backend API...")
    print("=" * 50)
    
    # Check environment
    check_python_version()
    if not setup_virtual_environment():
        return False
    
    if not install_dependencies("flask"):
        return False
    
    # Change to backend directory
    original_dir = os.getcwd()
    try:
        os.chdir("backend")
        
        # Determine python path
        if os.name == 'nt':  # Windows
            python_path = Path("../venv/Scripts/python")
        else:  # Unix/Linux/MacOS
            python_path = Path("../venv/bin/python")
        
        print("🌐 Starting Flask server...")
        print("   API URL: http://localhost:5001")
        print("   Frontend: Open frontend.html in browser")
        print("   Press Ctrl+C to stop")
        print("=" * 50)
        
        # Start Flask
        process = subprocess.run([str(python_path), "app.py"])
        return True
        
    except KeyboardInterrupt:
        print("\n👋 Flask stopped by user")
        return True
    except Exception as e:
        print(f"❌ Failed to start Flask: {e}")
        return False
    finally:
        os.chdir(original_dir)

def start_both():
    """Start both Streamlit and Flask applications"""
    print("🚀 Starting Both Applications...")
    print("=" * 50)
    
    # Check environment
    check_python_version()
    if not setup_virtual_environment():
        return False
    
    # Install dependencies for both
    if not install_dependencies("streamlit"):
        return False
    if not install_dependencies("flask"):
        return False
    
    print("🌐 Starting both servers...")
    print("   Streamlit: http://localhost:8501")
    print("   Flask API: http://localhost:5001")
    print("   Press Ctrl+C to stop both")
    print("=" * 50)
    
    # Determine python path
    if os.name == 'nt':  # Windows
        python_path = Path("venv/Scripts/python")
    else:  # Unix/Linux/MacOS
        python_path = Path("venv/bin/python")
    
    processes = []
    
    try:
        # Start Streamlit
        print("📱 Starting Streamlit...")
        streamlit_process = subprocess.Popen([
            str(python_path), "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--server.headless", "true"
        ])
        processes.append(streamlit_process)
        
        # Wait a moment
        time.sleep(2)
        
        # Start Flask
        print("🔧 Starting Flask...")
        flask_process = subprocess.Popen([
            str(python_path), "backend/app.py"
        ])
        processes.append(flask_process)
        
        print("✅ Both applications started successfully!")
        print("\n🌐 Access URLs:")
        print("   • Streamlit App: http://localhost:8501")
        print("   • Flask API: http://localhost:5001")
        print("   • HTML Frontend: Open frontend.html in browser")
        
        # Wait for processes
        try:
            while True:
                time.sleep(1)
                # Check if processes are still running
                for process in processes:
                    if process.poll() is not None:
                        print(f"⚠️  Process {process.pid} stopped unexpectedly")
        except KeyboardInterrupt:
            print("\n👋 Stopping both applications...")
            
    except Exception as e:
        print(f"❌ Error starting applications: {e}")
        return False
    finally:
        # Clean up processes
        for process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception:
                pass
        print("✅ All processes stopped")
    
    return True

def show_status():
    """Show current status of the project"""
    print("📊 Data Visualization Dashboard Status")
    print("=" * 50)
    
    # Check Python
    print(f"🐍 Python: {sys.version.split()[0]} ({'✅ Compatible' if sys.version_info >= (3, 8) else '❌ Too old'})")
    
    # Check virtual environment
    venv_exists = Path("venv").exists()
    print(f"📦 Virtual Environment: {'✅ Exists' if venv_exists else '❌ Missing'}")
    
    # Check requirements files
    streamlit_req = Path("requirements.txt").exists()
    flask_req = Path("backend/requirements.txt").exists()
    print(f"📋 Streamlit Requirements: {'✅ Found' if streamlit_req else '❌ Missing'}")
    print(f"📋 Flask Requirements: {'✅ Found' if flask_req else '❌ Missing'}")
    
    # Check main files
    streamlit_app = Path("app.py").exists()
    flask_app = Path("backend/app.py").exists()
    frontend = Path("frontend.html").exists()
    print(f"📱 Streamlit App: {'✅ Found' if streamlit_app else '❌ Missing'}")
    print(f"🔧 Flask Backend: {'✅ Found' if flask_app else '❌ Missing'}")
    print(f"🎨 HTML Frontend: {'✅ Found' if frontend else '❌ Missing'}")
    
    print("\n🚀 Available Commands:")
    print("   python launcher.py streamlit  # Start Streamlit app")
    print("   python launcher.py flask      # Start Flask backend")
    print("   python launcher.py both       # Start both applications")
    print("   python launcher.py status     # Show this status")

def main():
    """Main launcher function"""
    parser = argparse.ArgumentParser(
        description="Data Visualization Dashboard Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python launcher.py streamlit    # Start Streamlit application
  python launcher.py flask        # Start Flask backend
  python launcher.py both         # Start both applications
  python launcher.py status       # Show project status
        """
    )
    
    parser.add_argument(
        'mode',
        choices=['streamlit', 'flask', 'both', 'status'],
        help='Application mode to run'
    )
    
    args = parser.parse_args()
    
    try:
        if args.mode == 'streamlit':
            return start_streamlit()
        elif args.mode == 'flask':
            return start_flask()
        elif args.mode == 'both':
            return start_both()
        elif args.mode == 'status':
            show_status()
            return True
    except KeyboardInterrupt:
        print("\n👋 Launcher stopped by user")
        return True
    except Exception as e:
        print(f"❌ Launcher error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
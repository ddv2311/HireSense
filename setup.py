#!/usr/bin/env python3
"""
🚀 HireSense AI - Quick Setup Script
===================================

This script helps you quickly set up the HireSense AI system with all dependencies.
"""

import os
import sys
import subprocess
import platform

def print_header(title):
    print(f"\n🚀 {title}")
    print("=" * 60)

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"⏳ {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} is not compatible. Please use Python 3.8+")
        return False

def check_node_version():
    """Check if Node.js is installed"""
    try:
        result = subprocess.run("node --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Node.js {version} is installed")
            return True
        else:
            print("❌ Node.js is not installed")
            return False
    except:
        print("❌ Node.js is not installed")
        return False

def setup_backend():
    """Set up the backend"""
    print_header("Setting up Backend")
    
    # Create virtual environment
    if not run_command("python -m venv venv", "Creating virtual environment"):
        return False
    
    # Activate virtual environment and install dependencies
    if platform.system() == "Windows":
        activate_cmd = "venv\\Scripts\\activate"
    else:
        activate_cmd = "source venv/bin/activate"
    
    install_cmd = f"{activate_cmd} && cd backend && pip install -r requirements.txt"
    if not run_command(install_cmd, "Installing Python dependencies"):
        return False
    
    # Download spaCy model
    spacy_cmd = f"{activate_cmd} && python -m spacy download en_core_web_sm"
    if not run_command(spacy_cmd, "Downloading spaCy model"):
        print("⚠️ spaCy model download failed, but continuing...")
    
    # Initialize database
    db_cmd = f"{activate_cmd} && cd backend && python database.py"
    if not run_command(db_cmd, "Initializing database"):
        return False
    
    return True

def setup_frontend():
    """Set up the frontend"""
    print_header("Setting up Frontend")
    
    # Install npm dependencies
    if not run_command("cd frontend && npm install", "Installing Node.js dependencies"):
        return False
    
    return True

def create_directories():
    """Create necessary directories"""
    print_header("Creating Directories")
    
    directories = [
        "uploads/resumes",
        "uploads/videos", 
        "uploads/code_samples",
        "uploads/job_descriptions",
        "docs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True

def main():
    """Main setup function"""
    print("🚀 Welcome to HireSense AI Setup")
    print("=" * 60)
    print("This script will set up the complete HireSense AI system")
    print("Estimated time: 5-10 minutes")
    print("=" * 60)
    
    # Check prerequisites
    print_header("Checking Prerequisites")
    
    if not check_python_version():
        print("Please install Python 3.8+ and try again")
        return False
    
    if not check_node_version():
        print("Please install Node.js 16+ and try again")
        return False
    
    # Setup steps
    steps = [
        ("Creating directories", create_directories),
        ("Backend setup", setup_backend),
        ("Frontend setup", setup_frontend)
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            print(f"\n❌ Setup failed at: {step_name}")
            return False
    
    # Success message
    print_header("Setup Complete! 🎉")
    print("✅ HireSense AI has been successfully set up!")
    print("\n🚀 Next Steps:")
    print("1. Start the backend server:")
    if platform.system() == "Windows":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("   cd backend")
    print("   python main.py")
    
    print("\n2. In a new terminal, start the frontend:")
    print("   cd frontend")
    print("   npm start")
    
    print("\n3. Access the application:")
    print("   • Frontend: http://localhost:3000")
    print("   • API Docs: http://localhost:8000/docs")
    print("   • Health Check: http://localhost:8000/health")
    
    print("\n4. Run the system test:")
    print("   python test_complete_system.py")
    
    print("\n🎯 HireSense AI is ready to transform your hiring process!")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup failed with error: {e}")
        sys.exit(1) 
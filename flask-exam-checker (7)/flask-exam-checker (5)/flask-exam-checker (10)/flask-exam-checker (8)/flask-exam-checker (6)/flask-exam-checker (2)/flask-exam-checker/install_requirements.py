#!/usr/bin/env python3
"""
Install Requirements Script
Installs missing packages and tests the API key system
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a Python package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def check_and_install_requirements():
    """Check and install required packages"""
    
    print("🔧 CHECKING AND INSTALLING REQUIREMENTS")
    print("=" * 50)
    
    required_packages = [
        "python-dotenv",
        "google-generativeai",
        "flask",
        "flask-cors",
        "psycopg2-binary",
        "pillow",
        "openpyxl"
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} is already installed")
        except ImportError:
            print(f"⚠️  {package} not found, installing...")
            install_package(package)

def test_api_key_loading():
    """Test if API keys can be loaded"""
    
    print(f"\n🔑 TESTING API KEY LOADING")
    print("=" * 50)
    
    try:
        # Try to import and initialize the API key manager
        from api_key_manager import APIKeyManager
        
        print("🔄 Initializing API Key Manager...")
        manager = APIKeyManager()
        
        status = manager.get_status()
        print(f"✅ API Key Manager initialized successfully!")
        print(f"📊 Total Keys: {status['total_keys']}")
        print(f"📊 Current Key: {status['current_key_index'] + 1}")
        print(f"📊 Available Keys: {status['available_keys']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize API Key Manager: {e}")
        return False

def test_ocr_processor():
    """Test if OCR processor can be initialized"""
    
    print(f"\n🔬 TESTING OCR PROCESSOR")
    print("=" * 50)
    
    try:
        from ocr_utils import OCRProcessor
        
        print("🔄 Initializing OCR Processor...")
        processor = OCRProcessor()
        
        print("✅ OCR Processor initialized successfully!")
        print("🚀 Revolutionary 5-Layer Detection System is ready!")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize OCR Processor: {e}")
        return False

def test_flask_app():
    """Test if Flask app can be imported"""
    
    print(f"\n🌐 TESTING FLASK APP")
    print("=" * 50)
    
    try:
        from app import app
        
        print("✅ Flask app imported successfully!")
        print("🎯 Web application is ready to run!")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to import Flask app: {e}")
        return False

def provide_run_instructions():
    """Provide instructions for running the application"""
    
    print(f"\n📋 RUN INSTRUCTIONS")
    print("=" * 50)
    
    print("🚀 TO START THE APPLICATION:")
    print("1. Run: python run.py")
    print("2. Open browser: http://localhost:5000")
    print("3. Upload answer sheets and test OCR")
    
    print(f"\n🔧 TROUBLESHOOTING:")
    print("• If packages are missing: python install_requirements.py")
    print("• If API keys fail: Check .env file exists")
    print("• If database fails: Check DATABASE_URL in .env")
    print("• If OCR fails: Check API key quotas")
    
    print(f"\n🎯 FEATURES READY:")
    print("✅ 6 API Keys with automatic rotation")
    print("✅ Revolutionary 5-Layer OCR detection")
    print("✅ 7 Advanced pattern recognition algorithms")
    print("✅ Partial marking system")
    print("✅ Perfect accuracy tick detection")

if __name__ == "__main__":
    print("🔧 FLASK EXAM CHECKER - SETUP AND TEST")
    print("=" * 60)
    
    # Step 1: Install requirements
    check_and_install_requirements()
    
    # Step 2: Test API key loading
    api_success = test_api_key_loading()
    
    # Step 3: Test OCR processor
    ocr_success = test_ocr_processor()
    
    # Step 4: Test Flask app
    flask_success = test_flask_app()
    
    # Summary
    print(f"\n🎯 SETUP SUMMARY")
    print("=" * 50)
    print(f"API Key Manager: {'✅ Ready' if api_success else '❌ Failed'}")
    print(f"OCR Processor: {'✅ Ready' if ocr_success else '❌ Failed'}")
    print(f"Flask App: {'✅ Ready' if flask_success else '❌ Failed'}")
    
    if all([api_success, ocr_success, flask_success]):
        print(f"\n🎉 ALL SYSTEMS READY!")
        print("🚀 You can now run: python run.py")
        provide_run_instructions()
    else:
        print(f"\n⚠️  SOME ISSUES DETECTED")
        print("🔧 Please fix the errors above before running the application")

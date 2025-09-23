#!/usr/bin/env python3
"""
Flask Exam Checker System
Run this file to start the application
"""

from app import app, init_database

if __name__ == '__main__':
    # Only show startup messages on main process, not on Flask debug restart
    import os
    if not os.environ.get('WERKZEUG_RUN_MAIN'):
        print("=" * 50)
        print("🎓 FLASK EXAM CHECKER SYSTEM")
        print("=" * 50)
        print("Initializing database...")
    
    if init_database():
        if not os.environ.get('WERKZEUG_RUN_MAIN'):
            print("✅ Database initialized successfully!")
    else:
        print("❌ Failed to initialize database!")
        exit(1)
    
    if not os.environ.get('WERKZEUG_RUN_MAIN'):
        print("\n🚀 Starting Flask application...")
        print("📝 Teacher Section: Upload answer keys with OCR")
        print("🎓 Student Section: Submit answer sheets")
        print("📊 Results Section: View detailed results and analytics")
        print("\n" + "=" * 50)
        print("🌐 Access the application at: http://localhost:5000")
        print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)  # Keep debug mode for development

#!/usr/bin/env python3
"""
Test environment variable loading
"""

import os

# Try to load dotenv
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ dotenv loaded successfully")
except ImportError:
    print("❌ dotenv not available")
except Exception as e:
    print(f"❌ dotenv error: {e}")

# Check environment variables
print("\n🔍 CHECKING ENVIRONMENT VARIABLES:")
print("=" * 40)

env_vars = [
    'GEMINI_API_KEY',
    'GEMINI_API_KEY_BACKUP_1',
    'GEMINI_API_KEY_BACKUP_2',
    'GEMINI_API_KEY_BACKUP_3',
    'GEMINI_API_KEY_BACKUP_4',
    'GEMINI_API_KEY_BACKUP_5',
    'DATABASE_URL'
]

for var in env_vars:
    value = os.environ.get(var)
    if value:
        # Mask the value for security
        if 'API_KEY' in var:
            masked = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            print(f"✅ {var}: {masked}")
        else:
            print(f"✅ {var}: {value[:50]}...")
    else:
        print(f"❌ {var}: Not found")

# Check if .env file exists
env_file = '.env'
if os.path.exists(env_file):
    print(f"\n✅ .env file exists")
    with open(env_file, 'r') as f:
        lines = f.readlines()
        print(f"📄 .env file has {len(lines)} lines")
        for i, line in enumerate(lines[:10], 1):  # Show first 10 lines
            if 'API_KEY' in line:
                parts = line.split('=')
                if len(parts) >= 2:
                    key = parts[0]
                    value = parts[1].strip()
                    masked = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
                    print(f"   Line {i}: {key}={masked}")
            else:
                print(f"   Line {i}: {line.strip()}")
else:
    print(f"\n❌ .env file not found")

print(f"\n🔍 TESTING API KEY MANAGER:")
print("=" * 40)

try:
    from api_key_manager import APIKeyManager
    manager = APIKeyManager()
    status = manager.get_status()
    print(f"✅ API Key Manager works!")
    print(f"📊 Total keys: {status['total_keys']}")
except Exception as e:
    print(f"❌ API Key Manager failed: {e}")

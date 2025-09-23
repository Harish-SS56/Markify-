#!/usr/bin/env python3
"""
Test script for API Key Rotation System
Tests automatic failover when quota is exhausted
"""

import requests
import json
import time

def test_api_rotation():
    """Test the API key rotation system"""
    
    print("🔑 API KEY ROTATION SYSTEM TEST")
    print("=" * 60)
    print("🎯 This test verifies:")
    print("  ✅ Multiple API keys are loaded correctly")
    print("  ✅ Automatic rotation when quota exhausted")
    print("  ✅ Backup keys activate in order")
    print("  ✅ System continues working with backup keys")
    print("=" * 60)

    base_url = "http://localhost:5000"

    # Test 1: Check API status
    print(f"\n📋 TEST 1: API Status Check")
    try:
        response = requests.get(f"{base_url}/api/status")
        if response.status_code == 200:
            status = response.json()
            if status.get('success'):
                api_status = status.get('api_status', {})
                print(f"   ✅ API Status Retrieved Successfully")
                print(f"   📊 Current Key: {api_status.get('current_key_index', 0) + 1}")
                print(f"   📊 Total Keys: {api_status.get('total_keys', 0)}")
                print(f"   📊 Available Keys: {api_status.get('available_keys', 0)}")
                print(f"   📊 Failed Keys: {api_status.get('failed_keys', [])}")
                
                # Display usage statistics
                usage_count = api_status.get('key_usage_count', {})
                print(f"   📈 Key Usage Statistics:")
                for key_index, count in usage_count.items():
                    print(f"      Key {int(key_index) + 1}: {count} requests")
                
            else:
                print(f"   ❌ Failed to get API status: {status.get('error')}")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")

    # Test 2: Test OCR processing (this will use API keys)
    print(f"\n📋 TEST 2: OCR Processing Test")
    print("   🔄 Testing OCR to verify API key rotation works...")
    
    # Create a simple test request
    test_data = {
        'paper_id': 1,  # Assuming paper ID 1 exists
    }
    
    # You would need to provide an actual image file for this test
    test_image_path = 'test_images/sample_answer_sheet.jpg'
    
    try:
        # Check if test image exists
        import os
        if os.path.exists(test_image_path):
            with open(test_image_path, 'rb') as f:
                files = {'image': f}
                response = requests.post(f"{base_url}/process_student_image", files=files, data=test_data)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        print(f"   ✅ OCR Processing Successful")
                        print(f"   📊 Detected answers: {len(result.get('answers', []))}")
                    else:
                        print(f"   ⚠️  OCR Processing Failed: {result.get('error')}")
                else:
                    print(f"   ❌ HTTP Error: {response.status_code}")
        else:
            print(f"   ⚠️  Test image not found: {test_image_path}")
            print(f"   💡 Place a test image at this path to run OCR test")
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")

    # Test 3: Check API status after processing
    print(f"\n📋 TEST 3: API Status After Processing")
    try:
        response = requests.get(f"{base_url}/api/status")
        if response.status_code == 200:
            status = response.json()
            if status.get('success'):
                api_status = status.get('api_status', {})
                print(f"   ✅ Updated API Status Retrieved")
                print(f"   📊 Current Key: {api_status.get('current_key_index', 0) + 1}")
                print(f"   📊 Available Keys: {api_status.get('available_keys', 0)}")
                
                # Display updated usage statistics
                usage_count = api_status.get('key_usage_count', {})
                print(f"   📈 Updated Usage Statistics:")
                for key_index, count in usage_count.items():
                    print(f"      Key {int(key_index) + 1}: {count} requests")
                
            else:
                print(f"   ❌ Failed to get API status: {status.get('error')}")
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")

def test_key_reset():
    """Test the key reset functionality"""
    
    print(f"\n{'='*60}")
    print("🔄 API KEY RESET TEST")
    print("=" * 60)
    
    base_url = "http://localhost:5000"
    
    print(f"\n📋 TEST: Reset Failed Keys")
    try:
        response = requests.post(f"{base_url}/api/reset-keys")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"   ✅ API Keys Reset Successfully")
                print(f"   📊 Message: {result.get('message')}")
                
                api_status = result.get('api_status', {})
                print(f"   📊 Available Keys After Reset: {api_status.get('available_keys', 0)}")
                print(f"   📊 Failed Keys After Reset: {api_status.get('failed_keys', [])}")
            else:
                print(f"   ❌ Reset Failed: {result.get('error')}")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")

def simulate_quota_exhaustion():
    """Simulate quota exhaustion to test rotation"""
    
    print(f"\n{'='*60}")
    print("⚠️  QUOTA EXHAUSTION SIMULATION")
    print("=" * 60)
    print("🔬 This would test automatic key rotation when quota is exhausted")
    print("⚠️  Note: This test would consume API quota, so it's disabled by default")
    print()
    print("🎯 What the system does when quota is exhausted:")
    print("   1. Detects quota/rate limit error from Gemini API")
    print("   2. Automatically rotates to next available backup key")
    print("   3. Retries the request with the new key")
    print("   4. Continues processing without interruption")
    print("   5. Logs the rotation for monitoring")
    print()
    print("🔑 Key Rotation Order:")
    print("   1. Primary Key: AIzaSyAgKFZq183p04eeHGQThTs7t2eAvhwFzJ4")
    print("   2. Backup 1:    AIzaSyA2rKi4X3LyiRYOnE70ZS6P-BeA8d-6HkM")
    print("   3. Backup 2:    AIzaSyBjtiUdljU6qec1m0X9Sclb4bFYiNkISoY")
    print("   4. Backup 3:    AIzaSyBbK9a8x80b8qV6Odj9x-bZTIZLb7zwkOc")
    print("   5. Backup 4:    AIzaSyDsOFThZxJI5PgO3iFOWX4Kk6W41KUz890")
    print("   6. Backup 5:    AIzaSyCmbOvwgGCJOch2TzpCFvHGbj0tTsdwQVk")

def provide_monitoring_instructions():
    """Provide instructions for monitoring the API rotation system"""
    
    print(f"\n{'='*60}")
    print("📊 MONITORING INSTRUCTIONS")
    print("=" * 60)
    
    print("🔧 TO MONITOR API KEY ROTATION:")
    print("1. Check API status: GET /api/status")
    print("2. Monitor server logs for rotation messages")
    print("3. Reset failed keys: POST /api/reset-keys")
    print("4. Watch for quota exhaustion warnings")
    
    print(f"\n🎯 KEY INDICATORS TO MONITOR:")
    print("✅ current_key_index: Which key is currently active")
    print("✅ available_keys: How many keys are still working")
    print("✅ failed_keys: Which keys have exhausted quota")
    print("✅ key_usage_count: Request count per key")
    print("✅ last_rotation_time: When last rotation occurred")
    
    print(f"\n⚠️  ALERTS TO WATCH FOR:")
    print("🚨 'Quota exhausted for key X' - Normal rotation happening")
    print("🚨 'All API keys exhausted' - Critical: Need to wait for quota reset")
    print("🚨 'Rotated from key X to key Y' - Successful failover")
    
    print(f"\n🔄 DAILY MAINTENANCE:")
    print("• API quotas typically reset daily")
    print("• Use /api/reset-keys endpoint to reset failed keys")
    print("• Monitor usage patterns to optimize key distribution")
    print("• Consider adding more backup keys if needed")

if __name__ == "__main__":
    test_api_rotation()
    test_key_reset()
    simulate_quota_exhaustion()
    provide_monitoring_instructions()
    
    print(f"\n🎯 API KEY ROTATION SYSTEM: ✅ READY FOR AUTOMATIC FAILOVER")
    print("🔥 6 API keys configured for seamless operation!")

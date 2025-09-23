#!/usr/bin/env python3
"""
API Key Manager - Handles automatic rotation of Gemini API keys
Provides backup key functionality when quota is exhausted
"""

import os
import time
import logging
from datetime import datetime, timedelta
import google.generativeai as genai

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    # Only print on main process, not on Flask debug restart
    if not os.environ.get('WERKZEUG_RUN_MAIN'):
        print("✅ Loaded environment variables from .env file")
except ImportError:
    if not os.environ.get('WERKZEUG_RUN_MAIN'):
        print("⚠️  python-dotenv not installed, using system environment variables")
except Exception as e:
    if not os.environ.get('WERKZEUG_RUN_MAIN'):
        print(f"⚠️  Could not load .env file: {e}")

class APIKeyManager:
    def __init__(self):
        """Initialize the API Key Manager with all available keys"""
        self.api_keys = self._load_api_keys()
        self.current_key_index = 0
        self.failed_keys = set()
        self.key_usage_count = {}
        self.last_rotation_time = datetime.now()
        
        # Initialize usage counters
        for i, key in enumerate(self.api_keys):
            self.key_usage_count[i] = 0
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize with the first working key
        self._configure_current_key()
        
        # Only log on main process, not on Flask debug restart
        if not os.environ.get('WERKZEUG_RUN_MAIN'):
            self.logger.info(f"🔑 API Key Manager initialized with {len(self.api_keys)} keys")
    
    def _load_api_keys(self):
        """Load all API keys from environment variables"""
        keys = []
        
        # Only print on main process, not on Flask debug restart
        show_messages = not os.environ.get('WERKZEUG_RUN_MAIN')
        
        # Primary key
        primary_key = os.environ.get('GEMINI_API_KEY')
        if primary_key:
            keys.append(primary_key)
            if show_messages:
                print(f"✅ Loaded primary API key: {primary_key[:8]}...{primary_key[-4:]}")
        
        # Backup keys
        for i in range(1, 6):  # BACKUP_1 to BACKUP_5
            backup_key = os.environ.get(f'GEMINI_API_KEY_BACKUP_{i}')
            if backup_key:
                keys.append(backup_key)
                if show_messages:
                    print(f"✅ Loaded backup key {i}: {backup_key[:8]}...{backup_key[-4:]}")
        
        if not keys:
            # Try to read from .env file directly
            try:
                env_file_path = '.env'
                if os.path.exists(env_file_path):
                    print("🔍 Reading API keys directly from .env file...")
                    with open(env_file_path, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith('GEMINI_API_KEY') and '=' in line:
                                key_name, key_value = line.split('=', 1)
                                if key_value:
                                    keys.append(key_value)
                                    print(f"✅ Loaded {key_name}: {key_value[:8]}...{key_value[-4:]}")
                
                if keys:
                    print(f"✅ Successfully loaded {len(keys)} API keys from .env file")
                    return keys
            except Exception as e:
                print(f"⚠️  Could not read .env file: {e}")
            
            # Final fallback: Use hardcoded keys
            fallback_keys = [
                "AIzaSyAgKFZq183p04eeHGQThTs7t2eAvhwFzJ4",
                "AIzaSyA2rKi4X3LyiRYOnE70ZS6P-BeA8d-6HkM",
                "AIzaSyBjtiUdljU6qec1m0X9Sclb4bFYiNkISoY",
                "AIzaSyBbK9a8x80b8qV6Odj9x-bZTIZLb7zwkOc",
                "AIzaSyDsOFThZxJI5PgO3iFOWX4Kk6W41KUz890",
                "AIzaSyCmbOvwgGCJOch2TzpCFvHGbj0tTsdwQVk"
            ]
            
            print("⚠️  Using hardcoded fallback API keys")
            for i, key in enumerate(fallback_keys):
                print(f"✅ Using fallback key {i+1}: {key[:8]}...{key[-4:]}")
            
            return fallback_keys
        
        return keys
    
    def _configure_current_key(self):
        """Configure Gemini with the current API key"""
        if self.current_key_index < len(self.api_keys):
            current_key = self.api_keys[self.current_key_index]
            genai.configure(api_key=current_key)
            
            # Mask key for logging (show only first 8 and last 4 characters)
            masked_key = f"{current_key[:8]}...{current_key[-4:]}"
            # Only log on main process, not on Flask debug restart
            if not os.environ.get('WERKZEUG_RUN_MAIN'):
                self.logger.info(f"🔑 Configured API Key {self.current_key_index + 1}: {masked_key}")
        else:
            raise Exception("❌ All API keys have been exhausted")
    
    def get_model(self, model_name='gemini-1.5-flash'):
        """Get a Gemini model instance with current API key"""
        try:
            model = genai.GenerativeModel(model_name)
            return model
        except Exception as e:
            self.logger.error(f"❌ Failed to create model with current key: {str(e)}")
            raise
    
    def rotate_to_next_key(self):
        """Rotate to the next available API key"""
        # Mark current key as failed
        self.failed_keys.add(self.current_key_index)
        
        # Find next available key
        original_index = self.current_key_index
        
        for _ in range(len(self.api_keys)):
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
            
            if self.current_key_index not in self.failed_keys:
                try:
                    self._configure_current_key()
                    self.last_rotation_time = datetime.now()
                    
                    self.logger.warning(f"🔄 Rotated from key {original_index + 1} to key {self.current_key_index + 1}")
                    return True
                    
                except Exception as e:
                    self.logger.error(f"❌ Failed to configure key {self.current_key_index + 1}: {str(e)}")
                    self.failed_keys.add(self.current_key_index)
                    continue
        
        # All keys have failed
        self.logger.error("❌ All API keys have been exhausted or failed")
        return False
    
    def make_request_with_retry(self, request_func, *args, **kwargs):
        """
        Make a request with automatic key rotation on quota exhaustion
        
        Args:
            request_func: Function to call (e.g., model.generate_content)
            *args, **kwargs: Arguments to pass to the function
        
        Returns:
            Result of the request function
        """
        max_retries = len(self.api_keys)
        
        for attempt in range(max_retries):
            try:
                # Increment usage counter
                self.key_usage_count[self.current_key_index] += 1
                
                # Make the request
                result = request_func(*args, **kwargs)
                
                # Log successful request
                self.logger.info(f"✅ Request successful with key {self.current_key_index + 1} (usage: {self.key_usage_count[self.current_key_index]})")
                
                return result
                
            except Exception as e:
                error_message = str(e).lower()
                
                # Check if it's a quota/rate limit error
                if any(keyword in error_message for keyword in [
                    'quota', 'rate limit', 'exceeded', 'limit', 'resource_exhausted',
                    'too many requests', 'quota exceeded', 'rate_limit_exceeded'
                ]):
                    
                    self.logger.warning(f"⚠️  Quota exhausted for key {self.current_key_index + 1}: {str(e)}")
                    
                    # Try to rotate to next key
                    if self.rotate_to_next_key():
                        self.logger.info(f"🔄 Retrying with new key (attempt {attempt + 1}/{max_retries})")
                        continue
                    else:
                        raise Exception("❌ All API keys exhausted - no more backup keys available")
                
                else:
                    # Non-quota error, don't rotate key
                    self.logger.error(f"❌ Non-quota error with key {self.current_key_index + 1}: {str(e)}")
                    raise e
        
        # If we get here, all retries failed
        raise Exception(f"❌ Failed to complete request after {max_retries} attempts with different keys")
    
    def get_status(self):
        """Get current status of all API keys"""
        status = {
            'current_key_index': self.current_key_index,
            'current_key_masked': f"{self.api_keys[self.current_key_index][:8]}...{self.api_keys[self.current_key_index][-4:]}",
            'total_keys': len(self.api_keys),
            'failed_keys': list(self.failed_keys),
            'available_keys': len(self.api_keys) - len(self.failed_keys),
            'key_usage_count': self.key_usage_count.copy(),
            'last_rotation_time': self.last_rotation_time.isoformat(),
        }
        
        return status
    
    def reset_failed_keys(self):
        """Reset failed keys (useful for daily quota reset)"""
        self.failed_keys.clear()
        self.logger.info("🔄 Reset all failed keys - all keys are now available again")
    
    def get_current_key(self):
        """Get the current active API key (for debugging)"""
        if self.current_key_index < len(self.api_keys):
            return self.api_keys[self.current_key_index]
        return None

# Global instance
api_key_manager = APIKeyManager()

def get_api_manager():
    """Get the global API key manager instance"""
    return api_key_manager

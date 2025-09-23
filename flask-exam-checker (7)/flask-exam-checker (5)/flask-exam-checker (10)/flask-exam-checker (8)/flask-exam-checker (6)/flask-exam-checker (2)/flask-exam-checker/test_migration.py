#!/usr/bin/env python3
"""
Simple test script to verify the multiple MCQ feature works
"""

import os
import sys
from app import get_db_connection, init_database

def test_database_connection():
    """Test if database connection works"""
    print("🔄 Testing database connection...")
    conn = get_db_connection()
    if conn:
        print("✅ Database connection successful!")
        conn.close()
        return True
    else:
        print("❌ Database connection failed!")
        return False

def test_database_initialization():
    """Test if database initialization works (includes migration)"""
    print("🔄 Testing database initialization and migration...")
    success = init_database()
    if success:
        print("✅ Database initialization and migration successful!")
        return True
    else:
        print("❌ Database initialization failed!")
        return False

def test_new_columns_exist():
    """Test if new columns were created successfully"""
    print("🔄 Testing if new columns exist...")
    conn = get_db_connection()
    if not conn:
        print("❌ Cannot connect to database")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Check if correct_options column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='correct_answers' AND column_name='correct_options';
        """)
        
        if cursor.fetchone():
            print("✅ correct_options column exists")
        else:
            print("❌ correct_options column missing")
            return False
        
        # Check if question_type column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='correct_answers' AND column_name='question_type';
        """)
        
        if cursor.fetchone():
            print("✅ question_type column exists")
        else:
            print("❌ question_type column missing")
            return False
        
        # Check if selected_options column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='student_answers' AND column_name='selected_options';
        """)
        
        if cursor.fetchone():
            print("✅ selected_options column exists")
        else:
            print("❌ selected_options column missing")
            return False
        
        cursor.close()
        conn.close()
        print("✅ All new columns exist!")
        return True
        
    except Exception as e:
        print(f"❌ Error checking columns: {e}")
        if conn:
            conn.close()
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Multiple MCQ Feature Tests")
    print("=" * 50)
    
    # Test 1: Database connection
    if not test_database_connection():
        print("❌ Database connection test failed. Please check your .env file and database settings.")
        sys.exit(1)
    
    print()
    
    # Test 2: Database initialization (includes migration)
    if not test_database_initialization():
        print("❌ Database initialization test failed.")
        sys.exit(1)
    
    print()
    
    # Test 3: Check if new columns exist
    if not test_new_columns_exist():
        print("❌ New columns test failed.")
        sys.exit(1)
    
    print()
    print("🎉 All tests passed! Multiple MCQ feature is ready to use!")
    print()
    print("Next steps:")
    print("1. Start your Flask application")
    print("2. Try creating an answer key with multiple options (e.g., 1-A,B,C)")
    print("3. Test student submissions")
    print("4. Verify strict marking is working correctly")

if __name__ == "__main__":
    main()

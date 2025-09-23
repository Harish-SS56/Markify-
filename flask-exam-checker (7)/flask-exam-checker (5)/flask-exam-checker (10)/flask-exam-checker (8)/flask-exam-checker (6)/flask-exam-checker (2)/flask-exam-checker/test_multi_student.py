#!/usr/bin/env python3
"""
Test script for multi-student upload functionality
"""

import os
import sys
from app import get_db_connection

def test_multi_student_schema():
    """Test if the multi-student schema is properly set up"""
    print("🔄 Testing multi-student database schema...")
    
    conn = get_db_connection()
    if not conn:
        print("❌ Database connection failed!")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Check if paper info columns exist
        paper_info_columns = [
            'extracted_paper_name', 'extracted_subject', 'extracted_date', 
            'extracted_duration', 'extracted_total_marks', 'extracted_class_grade'
        ]
        
        for column in paper_info_columns:
            cursor.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='student_submissions' AND column_name='{column}';
            """)
            
            if cursor.fetchone():
                print(f"✅ {column} column exists")
            else:
                print(f"❌ {column} column missing")
                return False
        
        cursor.close()
        conn.close()
        print("✅ Multi-student schema test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        if conn:
            conn.close()
        return False

def print_usage_guide():
    """Print usage guide for multi-student uploads"""
    print("\n" + "="*60)
    print("📚 MULTI-STUDENT UPLOAD GUIDE")
    print("="*60)
    print()
    print("🎯 HOW IT WORKS:")
    print("1. Upload multiple answer sheet images")
    print("2. System detects unique roll numbers")
    print("3. Groups answers by student (roll number)")
    print("4. Shows confirmation for all detected students")
    print("5. Creates separate submissions for each student")
    print()
    print("📸 EXAMPLE SCENARIOS:")
    print("• 2 images, same student (Roll 123) → 1 submission with combined answers")
    print("• 2 images, different students (Roll 123, Roll 456) → 2 separate submissions")
    print("• 3 images, 2 students (Roll 123×2, Roll 456×1) → 2 submissions")
    print()
    print("🔍 WHAT GETS EXTRACTED:")
    print("• Roll number from each image")
    print("• Section information")
    print("• Paper details (name, subject, date, etc.)")
    print("• All marked answers")
    print("• Number of images per student")
    print()
    print("💾 WHAT GETS STORED:")
    print("• Separate database entry for each unique student")
    print("• Individual results calculation")
    print("• Paper information for each submission")
    print("• Image count tracking")
    print()
    print("🎉 EXPECTED RESULTS:")
    print("• Each student gets their own submission ID")
    print("• Individual result calculations")
    print("• Separate entries in results search")
    print("• Complete audit trail")

def main():
    """Run multi-student feature tests"""
    print("🚀 Testing Multi-Student Upload Feature")
    print("=" * 50)
    
    # Test database schema
    if not test_multi_student_schema():
        print("❌ Multi-student schema test failed!")
        print("💡 Run the Flask app once to apply migrations automatically.")
        sys.exit(1)
    
    print_usage_guide()
    
    print("\n✅ Multi-student upload feature is ready!")
    print("\n🎯 Next steps:")
    print("1. Start your Flask application")
    print("2. Upload multiple answer sheet images with different roll numbers")
    print("3. Verify the confirmation shows multiple students")
    print("4. Check that separate submissions are created")
    print("5. Search for each student individually in results")

if __name__ == "__main__":
    main()

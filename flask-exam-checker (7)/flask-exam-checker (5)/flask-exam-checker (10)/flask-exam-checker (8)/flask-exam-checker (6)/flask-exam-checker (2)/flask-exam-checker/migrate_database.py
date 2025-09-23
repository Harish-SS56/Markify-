#!/usr/bin/env python3
"""
Database migration script to add section column to student_submissions table
Run this script to update your existing database schema
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    """Get database connection using the same method as the Flask app"""
    try:
        # Try to get DATABASE_URL from environment
        database_url = os.getenv('DATABASE_URL')
        
        if database_url:
            conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        else:
            # Fallback to local connection
            conn = psycopg2.connect(
                host="localhost",
                database="exam_checker",  # Change this to your database name
                user="postgres",          # Change this to your username
                password="your_password", # Change this to your password
                cursor_factory=RealDictCursor
            )
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

def run_migration():
    """Run the database migration to add section column"""
    conn = get_db_connection()
    if not conn:
        print("❌ Failed to connect to database")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='student_submissions' AND column_name='section';
        """)
        
        if cursor.fetchone():
            print("✅ Section column already exists in student_submissions table")
        else:
            # Add the section column
            cursor.execute("ALTER TABLE student_submissions ADD COLUMN section VARCHAR(10);")
            print("✅ Added section column to student_submissions table")
        
        # Create index if it doesn't exist
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_student_submissions_section 
            ON student_submissions(section);
        """)
        print("✅ Created index on section column")
        
        # Commit changes
        conn.commit()
        cursor.close()
        conn.close()
        
        print("🎉 Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("🔄 Running database migration...")
    success = run_migration()
    
    if success:
        print("\n✅ Migration complete! You can now use the Submit Answer Sheet feature.")
    else:
        print("\n❌ Migration failed. Please check your database connection settings.")
        sys.exit(1)

#!/usr/bin/env python3
"""
Database migration script to support multiple correct options for MCQ questions
This adds support for questions that can have multiple correct answers
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
    """Run the database migration to support multiple correct options"""
    conn = get_db_connection()
    if not conn:
        print("❌ Failed to connect to database")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Check if correct_options column already exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='correct_answers' AND column_name='correct_options';
        """)
        
        if cursor.fetchone():
            print("✅ correct_options column already exists in correct_answers table")
        else:
            # Add the correct_options column (JSON array to store multiple options)
            cursor.execute("ALTER TABLE correct_answers ADD COLUMN correct_options TEXT[];")
            print("✅ Added correct_options column to correct_answers table")
        
        # Check if selected_options column already exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='student_answers' AND column_name='selected_options';
        """)
        
        if cursor.fetchone():
            print("✅ selected_options column already exists in student_answers table")
        else:
            # Add the selected_options column (JSON array to store multiple selected options)
            cursor.execute("ALTER TABLE student_answers ADD COLUMN selected_options TEXT[];")
            print("✅ Added selected_options column to student_answers table")
        
        # Check if question_type column already exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='correct_answers' AND column_name='question_type';
        """)
        
        if cursor.fetchone():
            print("✅ question_type column already exists in correct_answers table")
        else:
            # Add question_type column to distinguish single vs multiple correct answers
            cursor.execute("ALTER TABLE correct_answers ADD COLUMN question_type VARCHAR(20) DEFAULT 'single';")
            print("✅ Added question_type column to correct_answers table")
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_correct_answers_type ON correct_answers(question_type);")
        print("✅ Created index on question_type column")
        
        # Migrate existing data - populate correct_options array from correct_option
        cursor.execute("""
            UPDATE correct_answers 
            SET correct_options = ARRAY[correct_option]
            WHERE correct_options IS NULL AND correct_option IS NOT NULL;
        """)
        print("✅ Migrated existing single correct answers to array format")
        
        # Migrate existing student answers - populate selected_options array from selected_option
        cursor.execute("""
            UPDATE student_answers 
            SET selected_options = ARRAY[selected_option]
            WHERE selected_options IS NULL AND selected_option IS NOT NULL;
        """)
        print("✅ Migrated existing student answers to array format")
        
        # Commit changes
        conn.commit()
        cursor.close()
        conn.close()
        
        print("🎉 Database migration for multiple correct options completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("🔄 Running database migration for multiple correct options...")
    success = run_migration()
    
    if success:
        print("\n✅ Migration complete! You can now use multiple correct answer questions.")
    else:
        print("\n❌ Migration failed. Please check your database connection settings.")
        sys.exit(1)

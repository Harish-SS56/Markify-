import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL
database_url = os.getenv('DATABASE_URL')

try:
    # Connect to database
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    # Add section column
    cursor.execute("ALTER TABLE student_submissions ADD COLUMN IF NOT EXISTS section VARCHAR(10);")
    
    # Create index
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_student_submissions_section ON student_submissions(section);")
    
    # Commit changes
    conn.commit()
    cursor.close()
    conn.close()
    
    print("✅ Migration completed successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")

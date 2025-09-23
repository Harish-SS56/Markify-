-- Migration script to add section column to student_submissions table
-- Run this script on your existing database

ALTER TABLE student_submissions 
ADD COLUMN IF NOT EXISTS section VARCHAR(10);

-- Add index for better performance on section queries
CREATE INDEX IF NOT EXISTS idx_student_submissions_section ON student_submissions(section);

-- Update any existing records to have NULL section (optional)
-- UPDATE student_submissions SET section = NULL WHERE section IS NULL;

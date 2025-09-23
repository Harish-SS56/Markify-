-- Initialize database schema for exam checker system

-- Create question_papers table (for teacher uploads)
CREATE TABLE IF NOT EXISTS question_papers (
    id SERIAL PRIMARY KEY,
    paper_name VARCHAR(255) NOT NULL,
    total_questions INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create correct_answers table
CREATE TABLE IF NOT EXISTS correct_answers (
    id SERIAL PRIMARY KEY,
    paper_id INTEGER REFERENCES question_papers(id),
    question_number INTEGER NOT NULL,
    correct_option VARCHAR(10) NOT NULL,
    marks INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create student_submissions table
CREATE TABLE IF NOT EXISTS student_submissions (
    id SERIAL PRIMARY KEY,
    paper_id INTEGER REFERENCES question_papers(id),
    roll_number VARCHAR(50) NOT NULL,
    section VARCHAR(10),
    student_name VARCHAR(255),
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create student_answers table
CREATE TABLE IF NOT EXISTS student_answers (
    id SERIAL PRIMARY KEY,
    submission_id INTEGER REFERENCES student_submissions(id),
    question_number INTEGER NOT NULL,
    selected_option VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create results table
CREATE TABLE IF NOT EXISTS results (
    id SERIAL PRIMARY KEY,
    submission_id INTEGER REFERENCES student_submissions(id),
    total_questions INTEGER NOT NULL,
    correct_answers INTEGER NOT NULL,
    total_marks INTEGER NOT NULL,
    percentage DECIMAL(5,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_correct_answers_paper_id ON correct_answers(paper_id);
CREATE INDEX IF NOT EXISTS idx_student_submissions_roll ON student_submissions(roll_number);
CREATE INDEX IF NOT EXISTS idx_student_answers_submission ON student_answers(submission_id);
CREATE INDEX IF NOT EXISTS idx_results_submission ON results(submission_id);

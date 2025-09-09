-- Migration script to add user roles and question management features

-- Add role column to users table
ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user' CHECK (role IN ('user', 'admin'));

-- Create user_questions table for user-created questions
CREATE TABLE user_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    difficulty TEXT NOT NULL CHECK (difficulty IN ('Easy', 'Medium', 'Hard')),
    topics TEXT, -- JSON array of topics
    solution TEXT, -- Optional solution explanation
    is_public BOOLEAN DEFAULT FALSE,
    is_approved BOOLEAN DEFAULT FALSE,
    created_by INTEGER NOT NULL,
    approved_by INTEGER NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP NULL,
    FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES users (id) ON DELETE SET NULL
);

-- Create question_references table for URLs and references
CREATE TABLE question_references (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NULL, -- For original questions
    user_question_id INTEGER NULL, -- For user-created questions
    url TEXT NOT NULL,
    title TEXT,
    description TEXT,
    is_approved BOOLEAN DEFAULT FALSE,
    created_by INTEGER NOT NULL,
    approved_by INTEGER NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP NULL,
    FOREIGN KEY (question_id) REFERENCES questions (id) ON DELETE CASCADE,
    FOREIGN KEY (user_question_id) REFERENCES user_questions (id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES users (id) ON DELETE SET NULL,
    CHECK ((question_id IS NOT NULL AND user_question_id IS NULL) OR 
           (question_id IS NULL AND user_question_id IS NOT NULL))
);

-- Create user_question_companies table for company associations
CREATE TABLE user_question_companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_question_id INTEGER NOT NULL,
    company_id INTEGER NOT NULL,
    time_period TEXT NOT NULL,
    frequency REAL DEFAULT 1.0,
    is_approved BOOLEAN DEFAULT FALSE,
    created_by INTEGER NOT NULL,
    approved_by INTEGER NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP NULL,
    FOREIGN KEY (user_question_id) REFERENCES user_questions (id) ON DELETE CASCADE,
    FOREIGN KEY (company_id) REFERENCES companies (id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES users (id) ON DELETE SET NULL,
    UNIQUE(user_question_id, company_id, time_period)
);

-- Create approval_requests table to track pending approvals
CREATE TABLE approval_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_type TEXT NOT NULL CHECK (request_type IN ('question_public', 'reference', 'company_association')),
    entity_id INTEGER NOT NULL, -- ID of the entity being requested for approval
    entity_type TEXT NOT NULL CHECK (entity_type IN ('user_question', 'question_reference', 'user_question_company')),
    requested_by INTEGER NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    admin_notes TEXT,
    processed_by INTEGER NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP NULL,
    FOREIGN KEY (requested_by) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (processed_by) REFERENCES users (id) ON DELETE SET NULL
);

-- Create user_favorites table for users to favorite questions
CREATE TABLE user_favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    question_id INTEGER NULL,
    user_question_id INTEGER NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions (id) ON DELETE CASCADE,
    FOREIGN KEY (user_question_id) REFERENCES user_questions (id) ON DELETE CASCADE,
    UNIQUE(user_id, question_id),
    UNIQUE(user_id, user_question_id),
    CHECK ((question_id IS NOT NULL AND user_question_id IS NULL) OR 
           (question_id IS NULL AND user_question_id IS NOT NULL))
);

-- Add indexes for better performance
CREATE INDEX idx_user_questions_created_by ON user_questions(created_by);
CREATE INDEX idx_user_questions_public ON user_questions(is_public);
CREATE INDEX idx_user_questions_approved ON user_questions(is_approved);
CREATE INDEX idx_question_references_question ON question_references(question_id);
CREATE INDEX idx_question_references_user_question ON question_references(user_question_id);
CREATE INDEX idx_question_references_approved ON question_references(is_approved);
CREATE INDEX idx_user_question_companies_question ON user_question_companies(user_question_id);
CREATE INDEX idx_user_question_companies_company ON user_question_companies(company_id);
CREATE INDEX idx_approval_requests_status ON approval_requests(status);
CREATE INDEX idx_approval_requests_type ON approval_requests(request_type);
CREATE INDEX idx_user_favorites_user ON user_favorites(user_id);

-- Insert a default admin user (password: admin123)
INSERT OR IGNORE INTO users (email, username, full_name, password_hash, role) 
VALUES ('admin@devprep.com', 'admin', 'System Administrator', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyN4zg8vB3UJQu', 'admin');

-- Update existing users to have 'user' role if not set
UPDATE users SET role = 'user' WHERE role IS NULL;

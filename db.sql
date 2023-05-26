-- Create the users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(50) NOT NULL
);

-- Create the candidates table
CREATE TABLE candidates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_name VARCHAR(50) NOT NULL,
    votes INT DEFAULT 0
);

-- Insert dummy data into the users table
INSERT INTO users (username, password) VALUES
    ('john_doe', 'password123'),
    ('jane_smith', 'secret321'),
    ('admin', 'adminpass');

-- Insert dummy data into the candidates table
INSERT INTO candidates (candidate_name, votes) VALUES
    ('Candidate 1', 150),
    ('Candidate 2', 200),
    ('Candidate 3', 180);

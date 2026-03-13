USE advanced_complaint_dbsqli;

CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password VARCHAR(200) NOT NULL, -- Stores the Bcrypt hash
    role VARCHAR(20) DEFAULT 'user' -- 'user' or 'admin'
);


CREATE TABLE IF NOT EXISTS complaint (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50), -- AI Predicted
    priority VARCHAR(20), -- AI Predicted (High, Medium, Low)
    status VARCHAR(20) DEFAULT 'Pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);
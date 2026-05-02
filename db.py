import os
import pymysql
import pymysql.cursors
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'online_book_reader'),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
        charset='utf8mb4'
    )

def init_db():
    # Connect without database first to create it if it doesn't exist
    conn = pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        autocommit=True,
        charset='utf8mb4'
    )
    
    try:
        with conn.cursor() as cursor:
            db_name = os.getenv('DB_NAME', 'online_book_reader')
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    finally:
        conn.close()

    # Connect to the specific database
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Create Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    preferred_genres TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create Books table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    author VARCHAR(255) NOT NULL,
                    genre VARCHAR(100),
                    description TEXT,
                    cover_image_path VARCHAR(255),
                    added_by INT,
                    is_private BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (added_by) REFERENCES users(id) ON DELETE SET NULL
                )
            """)
            
            # Create Pages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    book_id INT NOT NULL,
                    page_number INT NOT NULL,
                    text_content LONGTEXT NOT NULL,
                    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
                )
            """)
            
            # Create User_Books table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_books (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    book_id INT NOT NULL,
                    last_page_read INT DEFAULT 1,
                    is_favourite BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
                )
            """)
            
            # Create Reading_History table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reading_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    book_id INT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
                )
            """)
            
            # Ensure existing tables are using utf8mb4 (for Marathi support)
            tables = ['users', 'books', 'pages', 'user_books', 'reading_history']
            for table in tables:
                try:
                    if table == 'users':
                        # Reduce email length to prevent 'Specified key was too long' error in older MySQL
                        cursor.execute("ALTER TABLE users MODIFY email VARCHAR(191) UNIQUE NOT NULL")
                    cursor.execute(f"ALTER TABLE {table} CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                except Exception as e:
                    print(f"Error converting {table}: {e}")
                
            # Ensure time_spent column exists in user_books
            try:
                cursor.execute("ALTER TABLE user_books ADD COLUMN time_spent INT DEFAULT 0")
            except Exception as e:
                pass
                
            # Ensure is_private column exists in books
            try:
                cursor.execute("ALTER TABLE books ADD COLUMN is_private BOOLEAN DEFAULT FALSE")
            except Exception as e:
                pass

    finally:
        conn.close()

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialized successfully.")

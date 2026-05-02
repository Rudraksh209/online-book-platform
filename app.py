from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory, jsonify
from functools import wraps
import os
import json
import bcrypt
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from db import init_db, get_db_connection
from pdf_extractor import extract_text_from_pdf

load_dotenv()

# Admin Configuration
ADMIN_EMAIL = 'rudrakshgoswami209@gmail.com'

def is_admin():
    return session.get('user_email') == ADMIN_EMAIL

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin():
            flash('Access denied. Admin only!', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key_for_dev')
app.config['UPLOAD_FOLDER'] = os.path.join('uploads')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024 # 50MB max upload

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Auto-initialize database tables on startup
try:
    init_db()
    print('Database tables initialized!')
except Exception as e:
    print(f'DB init warning: {e}')

# --- Authentication Decorator ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password').encode('utf-8')
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()
                
                if user and bcrypt.checkpw(password, user['password_hash'].encode('utf-8')):
                    session['user_id'] = user['id']
                    session['user_name'] = user['name']
                    session['user_email'] = user['email']
                    flash('Login successful!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid email or password.', 'danger')
        finally:
            conn.close()
            
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password').encode('utf-8')
        genres = request.form.getlist('genres')
        
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')
        genres_json = json.dumps(genres)
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Check if email exists
                cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    flash('Email already exists. Please login.', 'warning')
                    return redirect(url_for('login'))
                
                cursor.execute(
                    "INSERT INTO users (name, email, password_hash, preferred_genres) VALUES (%s, %s, %s, %s)",
                    (name, email, hashed_password, genres_json)
                )
                conn.commit()
                flash('Account created successfully! Please log in.', 'success')
                return redirect(url_for('login'))
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
        finally:
            conn.close()
            
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/catalog')
def catalog():
    conn = get_db_connection()
    books = []
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, title, author, genre, description, cover_image_path FROM books WHERE is_private = FALSE ORDER BY title ASC")
            books = cursor.fetchall()
    finally:
        conn.close()
    return render_template('catalog.html', books=books)

@app.route('/my_books')
@login_required
def my_books():
    conn = get_db_connection()
    books = []
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT b.id, b.title, b.author, b.genre, b.description, b.cover_image_path, b.is_private, ub.last_page_read, ub.time_spent
                FROM books b
                JOIN user_books ub ON b.id = ub.book_id
                WHERE ub.user_id = %s
                ORDER BY ub.id DESC
            """, (session['user_id'],))
            books = cursor.fetchall()
    finally:
        conn.close()
    return render_template('my_books.html', books=books)

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    books = []
    stats = {'total_books': 0, 'total_time': 0}
    try:
        with conn.cursor() as cursor:
            # Get recently added books (public or owned by user)
            cursor.execute("SELECT id, title, author, genre, description, cover_image_path, added_by, is_private FROM books WHERE is_private = FALSE OR added_by = %s ORDER BY created_at DESC LIMIT 10", (session['user_id'],))
            books = cursor.fetchall()
            
            # Get user stats
            cursor.execute("SELECT COUNT(id) as total_books, SUM(time_spent) as total_time FROM user_books WHERE user_id = %s", (session['user_id'],))
            result = cursor.fetchone()
            if result and result['total_books']:
                stats['total_books'] = result['total_books']
                stats['total_time'] = result['total_time'] or 0
    finally:
        conn.close()
    return render_template('dashboard.html', books=books, stats=stats, is_admin=is_admin())

@app.route('/reader/<int:book_id>')
@login_required
def reader(book_id):
    conn = get_db_connection()
    book = None
    pages = []
    user_book = None
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
            book = cursor.fetchone()
            
            if book:
                cursor.execute("SELECT * FROM pages WHERE book_id = %s ORDER BY page_number ASC", (book_id,))
                pages = cursor.fetchall()
                
                # Get user progress
                cursor.execute("SELECT * FROM user_books WHERE user_id = %s AND book_id = %s", 
                              (session['user_id'], book_id))
                user_book = cursor.fetchone()
    finally:
        conn.close()
        
    if not book:
        flash('Book not found.', 'danger')
        return redirect(url_for('dashboard'))
        
    # Default to page 1 if no record
    last_page = user_book['last_page_read'] if user_book else 1
        
    return render_template('reader.html', book=book, pages=pages, last_page=last_page)

@app.route('/api/update_progress', methods=['POST'])
@login_required
def update_progress():
    data = request.json
    book_id = data.get('book_id')
    last_page = data.get('last_page_read', 1)
    time_spent = data.get('time_spent', 0)
    
    if not book_id:
        return jsonify({'error': 'book_id required'}), 400
        
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM user_books WHERE user_id = %s AND book_id = %s", 
                          (session['user_id'], book_id))
            record = cursor.fetchone()
            
            if record:
                cursor.execute("""
                    UPDATE user_books 
                    SET last_page_read = %s, time_spent = time_spent + %s 
                    WHERE id = %s
                """, (last_page, time_spent, record['id']))
            else:
                cursor.execute("""
                    INSERT INTO user_books (user_id, book_id, last_page_read, time_spent) 
                    VALUES (%s, %s, %s, %s)
                """, (session['user_id'], book_id, last_page, time_spent))
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()
        
    return jsonify({'success': True})

@app.route('/delete_book/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT added_by, cover_image_path FROM books WHERE id = %s", (book_id,))
            book = cursor.fetchone()
            
            if not book:
                flash('Book not found.', 'danger')
                return redirect(url_for('dashboard'))
                
            if book['added_by'] != session['user_id']:
                flash('You do not have permission to delete this book.', 'danger')
                return redirect(url_for('dashboard'))
                
            cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
            
            if book['cover_image_path']:
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], book['cover_image_path']))
                except:
                    pass
                    
        flash('Book deleted successfully.', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
    finally:
        conn.close()
        
    return redirect(url_for('dashboard'))

@app.route('/add_book', methods=['GET', 'POST'])
@login_required
@admin_required
def add_book():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        genre = request.form.get('genre')
        description = request.form.get('description')
        is_private = 'is_private' in request.form
        
        cover_image = request.files.get('cover_image')
        book_pdf = request.files.get('book_pdf')
        
        if not book_pdf or not book_pdf.filename.endswith('.pdf'):
            flash('A valid PDF file is required.', 'danger')
            return redirect(request.url)
            
        # Save files
        cover_filename = ""
        if cover_image and cover_image.filename:
            cover_filename = secure_filename(cover_image.filename)
            cover_image.save(os.path.join(app.config['UPLOAD_FOLDER'], cover_filename))
            
        pdf_filename = secure_filename(book_pdf.filename)
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
        book_pdf.save(pdf_path)
        
        # Extract Text
        pages_text = extract_text_from_pdf(pdf_path)
        if not pages_text:
            flash('Failed to extract text from the PDF. It might be scanned images.', 'warning')
            
        # Save to DB
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Insert Book
                cursor.execute(
                    "INSERT INTO books (title, author, genre, description, cover_image_path, added_by, is_private) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (title, author, genre, description, cover_filename, session['user_id'], is_private)
                )
                book_id = cursor.lastrowid
                
                # Insert Pages
                for i, page_text in enumerate(pages_text):
                    if page_text: # only insert if there is text
                        cursor.execute(
                            "INSERT INTO pages (book_id, page_number, text_content) VALUES (%s, %s, %s)",
                            (book_id, i + 1, page_text)
                        )
            flash('Book added and processed successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f'Database error: {str(e)}', 'danger')
        finally:
            conn.close()
            
    return render_template('add_book.html')

@app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_book(book_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
            book = cursor.fetchone()
            
            if not book:
                flash('Book not found.', 'danger')
                return redirect(url_for('dashboard'))
                
            if book['added_by'] != session['user_id']:
                flash('You do not have permission to edit this book.', 'danger')
                return redirect(url_for('dashboard'))
                
            if request.method == 'POST':
                title = request.form.get('title')
                author = request.form.get('author')
                genre = request.form.get('genre')
                description = request.form.get('description')
                is_private = 'is_private' in request.form
                
                cursor.execute("""
                    UPDATE books 
                    SET title = %s, author = %s, genre = %s, description = %s, is_private = %s 
                    WHERE id = %s
                """, (title, author, genre, description, is_private, book_id))
                
                flash('Book details updated successfully!', 'success')
                return redirect(url_for('dashboard'))
                
    except Exception as e:
        flash(f'Database error: {str(e)}', 'danger')
    finally:
        conn.close()
        
    return render_template('edit_book.html', book=book)

if __name__ == '__main__':
    # Initialize DB on startup (optional, can also run db.py directly)
    try:
        init_db()
        print("Database connected and verified.")
    except Exception as e:
        print(f"Warning: Could not connect to database on startup. Error: {e}")
    
    app.run(debug=False, port=5000)

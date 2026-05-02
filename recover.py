import os

templates = {
    'base.html': """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Goodreads Book Platform{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    <header>
        <div class="top-bar">
            <div class="brand-container">
                <a href="{{ url_for('index') }}" class="brand">
                    Goodreads
                    <span>Free eBooks Library</span>
                </a>
            </div>
            <div class="search-bar">
                <form action="{{ url_for('catalog') }}" method="GET" style="display:flex;">
                    <input type="text" name="q" placeholder="Quick search">
                    <button type="submit">Go!</button>
                </form>
            </div>
            <div class="auth-buttons">
                {% if not session.get('user_id') %}
                    <a href="{{ url_for('login') }}" class="btn" style="background:#f0ad4e; color:white;">Login</a>
                    <a href="{{ url_for('signup') }}" class="btn" style="background:#5bc0de; color:white;">Register</a>
                {% else %}
                    <span style="color:white; margin-right: 10px;">Hi, {{ session.get('user_name') }}</span>
                    <a href="{{ url_for('logout') }}" class="btn" style="background:#d9534f; color:white;">Logout</a>
                {% endif %}
            </div>
        </div>
        <nav class="nav-links">
            <a href="{{ url_for('about') }}">About ▼</a>
            <a href="{{ url_for('catalog') }}">Library Catalog</a>
            {% if session.get('user_id') %}
            <a href="{{ url_for('dashboard') }}">Dashboard</a>
            <a href="{{ url_for('my_books') }}">My Reading List</a>
            <a href="{{ url_for('add_book') }}">Add Book</a>
            {% endif %}
        </nav>
    </header>
    <div class="flash-messages">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
    </div>
    <main class="content">
        {% block content %}{% endblock %}
    </main>
    <footer style="background: var(--bg-color); padding: 2rem 5%; border-top: 1px solid #ddd; text-align:center; font-size: 0.9rem; margin-top: 2rem;">
        <p>Goodreads Project - A platform for reading and exploring literature.</p>
        <p>&copy; 2026 Rudraksh, Pankaj, Ankit.</p>
    </footer>
    {% block extra_js %}{% endblock %}
</body>
</html>""",
    'index.html': """{% extends 'base.html' %}
{% block content %}
<div style="text-align: center; padding: 4rem 2rem;">
    <h1 style="font-size: 3rem; margin-bottom: 1rem;">Welcome to Goodreads</h1>
    <p style="font-size: 1.2rem; color: #555; max-width: 600px; margin: 0 auto 2rem auto;">
        Your personal library and reading companion. Upload books, listen with AI-powered text-to-speech, and track your reading journey.
    </p>
    <div>
        <a href="{{ url_for('signup') }}" class="btn btn-primary" style="font-size: 1.2rem; padding: 1rem 2rem; margin-right: 1rem;">Start Reading Now</a>
        <a href="{{ url_for('catalog') }}" class="btn" style="font-size: 1.2rem; padding: 1rem 2rem; background: #ddd; color: #333;">Browse Library</a>
    </div>
</div>
{% endblock %}""",
    'login.html': """{% extends 'base.html' %}
{% block title %}Login - Goodreads{% endblock %}
{% block content %}
<div class="auth-container">
    <h2>Welcome Back</h2>
    <form method="POST">
        <div class="form-group">
            <label>Email Address</label>
            <input type="email" name="email" required>
        </div>
        <div class="form-group">
            <label>Password</label>
            <input type="password" name="password" required>
        </div>
        <button type="submit" class="btn btn-primary btn-block">Log In</button>
    </form>
    <p style="margin-top: 1rem;">Don't have an account? <a href="{{ url_for('signup') }}">Sign Up</a></p>
</div>
{% endblock %}""",
    'signup.html': """{% extends 'base.html' %}
{% block title %}Sign Up - Goodreads{% endblock %}
{% block content %}
<div class="auth-container">
    <h2>Create an Account</h2>
    <form method="POST">
        <div class="form-group">
            <label>Full Name</label>
            <input type="text" name="name" required>
        </div>
        <div class="form-group">
            <label>Email Address</label>
            <input type="email" name="email" required>
        </div>
        <div class="form-group">
            <label>Password</label>
            <input type="password" name="password" required>
        </div>
        <button type="submit" class="btn btn-primary btn-block">Sign Up</button>
    </form>
    <p style="margin-top: 1rem;">Already have an account? <a href="{{ url_for('login') }}">Log In</a></p>
</div>
{% endblock %}""",
    'add_book.html': """{% extends 'base.html' %}
{% block title %}Add Book - Goodreads{% endblock %}
{% block content %}
<div class="auth-container" style="max-width: 600px;">
    <h2>Add a New Book</h2>
    <form method="POST" enctype="multipart/form-data">
        <div class="form-group">
            <label>Title</label>
            <input type="text" name="title" required>
        </div>
        <div class="form-group">
            <label>Author</label>
            <input type="text" name="author" required>
        </div>
        <div class="form-group">
            <label>Genre</label>
            <select name="genre">
                <option value="Fiction">Fiction</option>
                <option value="Non-Fiction">Non-Fiction</option>
                <option value="Science">Science</option>
                <option value="History">History</option>
                <option value="Fantasy">Fantasy</option>
            </select>
        </div>
        <div class="form-group">
            <label>Description</label>
            <textarea name="description" rows="3"></textarea>
        </div>
        <div class="form-group">
            <label>Cover Image (Optional)</label>
            <input type="file" name="cover_image" accept="image/*">
        </div>
        <div class="form-group">
            <label>Book PDF (Required)</label>
            <input type="file" name="book_pdf" accept=".pdf" required>
        </div>
        <button type="submit" class="btn btn-primary btn-block">Upload & Process Book</button>
    </form>
</div>
{% endblock %}""",
    'about.html': """{% extends 'base.html' %}
{% block title %}About Us - Goodreads{% endblock %}
{% block extra_css %}
<style>
    .about-container { max-width: 800px; margin: 0 auto; padding: 3rem; background: #f9fbfd; border: 1px solid #eef2f5; border-radius: 8px; }
    .team-member { display: flex; align-items: center; margin-bottom: 2rem; padding: 1.5rem; background: white; border: 1px solid #eee; border-radius: 4px; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }
    .member-icon { width: 60px; height: 60px; background: var(--primary-color); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; font-weight: bold; margin-right: 1.5rem; }
    .member-details h3 { margin: 0 0 0.5rem 0; color: var(--primary-color); }
    .member-details p { margin: 0; color: #666; }
    .about-header { text-align: center; margin-bottom: 3rem; }
    .about-header p { font-size: 1.1rem; color: #555; }
</style>
{% endblock %}
{% block content %}
<div class="about-container">
    <div class="about-header">
        <h2>About Goodreads Project</h2>
        <p>This online book reading platform was developed as part of our academic project. Our goal is to provide a seamless, accessible, and enjoyable reading experience for everyone, featuring tools like AI-powered text-to-speech reading.</p>
    </div>
    <h3 style="border-bottom: 2px solid var(--primary-color); padding-bottom: 0.5rem; margin-bottom: 1.5rem;">Our Development Team</h3>
    <div class="team-member"><div class="member-icon">R</div><div class="member-details"><h3>Rudraksh Goswami</h3><p>Email: rudrakshgoswami209@gmail.com</p></div></div>
    <div class="team-member"><div class="member-icon">P</div><div class="member-details"><h3>Pankaj Aadhe</h3><p>Email: pankaj.aadhe25@mmit.edu.in</p></div></div>
    <div class="team-member"><div class="member-icon">A</div><div class="member-details"><h3>Ankit Khade</h3><p>Email: ankit.khade25@mmit.edu.in</p></div></div>
</div>
{% endblock %}""",
    'catalog.html': """{% extends 'base.html' %}
{% block title %}Library Catalog - Goodreads{% endblock %}
{% block extra_css %}
<style>
    .catalog-header { text-align: center; margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid #ddd; }
    .book-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 1.5rem; }
    .book-item { background: white; border: 1px solid #ddd; border-radius: 8px; padding: 0.8rem; display: flex; flex-direction: column; transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.3s ease; position: relative; overflow: hidden; }
    .book-item:hover { transform: translateY(-8px); box-shadow: 0 12px 20px rgba(0,0,0,0.15); }
    .book-cover { width: 100%; height: 240px; object-fit: cover; background: #eee; margin-bottom: 1rem; border: 1px solid #ccc; border-radius: 4px; transition: transform 0.5s ease; }
    .book-item:hover .book-cover { transform: scale(1.05); }
    .book-title { font-weight: bold; color: var(--primary-color); font-size: 1rem; margin-bottom: 0.3rem; line-height: 1.2; }
    .book-author { font-size: 0.85rem; color: #666; margin-bottom: 1rem; }
    .btn-read { margin-top: auto; padding: 0.4rem; font-size: 0.9rem; text-align: center; background: var(--primary-color); color: white; border-radius: 3px; display: block; }
    .btn-read:hover { background: var(--secondary-color); text-decoration: none; }
</style>
{% endblock %}
{% block content %}
<div class="catalog-header">
    <h2>Full Library Catalog</h2>
    <p>Browse our complete collection of digitized books.</p>
</div>
<div class="book-grid">
    {% for book in books %}
    <div class="book-item">
        {% if book.cover_image_path %}
            <img src="{{ url_for('uploaded_file', filename=book.cover_image_path) }}" alt="Cover" class="book-cover">
        {% else %}
            <div class="book-cover" style="display: flex; align-items: center; justify-content: center; background: #e0e0e0;"><span style="color: #666; font-style: italic;">No Cover</span></div>
        {% endif %}
        <div class="book-title">{{ book.title }}</div>
        <div class="book-author">by {{ book.author }}</div>
        <div style="font-size: 0.8rem; background: #f0f0f0; padding: 2px 5px; display: inline-block; margin-bottom: 10px;">{{ book.genre }}</div>
        <a href="{{ url_for('reader', book_id=book.id) }}" class="btn-read">Read Book</a>
    </div>
    {% else %}
    <div style="grid-column: 1 / -1; text-align: center; padding: 3rem;"><h3>The library is currently empty.</h3></div>
    {% endfor %}
</div>
{% endblock %}""",
    'dashboard.html': """{% extends 'base.html' %}
{% block title %}Dashboard - Goodreads{% endblock %}
{% block extra_css %}
<style>
    .dashboard-header { background: #f4f8fa; padding: 2rem; border-radius: 8px; margin-bottom: 2rem; border: 1px solid #e1e8ed; display: flex; justify-content: space-between; align-items: center; }
    .stats-container { display: flex; gap: 2rem; }
    .stat-box { background: white; padding: 1rem 1.5rem; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); text-align: center; border-left: 4px solid var(--primary-color); }
    .stat-number { font-size: 2rem; font-weight: bold; color: var(--primary-color); font-family: var(--font-heading); }
    .stat-label { color: #666; font-size: 0.9rem; }
    .section-title { font-size: 1.5rem; margin-bottom: 1.5rem; border-bottom: 2px solid var(--primary-color); padding-bottom: 0.5rem; display: inline-block; }
    .book-list { background: #f9fbfd; padding: 1.5rem; border-radius: 8px; border: 1px solid #eef2f5; margin-bottom: 2rem; }
    .book-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 1.5rem; }
    .book-item { background: white; border: 1px solid #ddd; border-radius: 8px; padding: 0.8rem; display: flex; flex-direction: column; transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.3s ease; position: relative; overflow: hidden; }
    .book-item:hover { transform: translateY(-8px); box-shadow: 0 12px 20px rgba(0,0,0,0.15); }
    .book-cover { width: 100%; height: 240px; object-fit: cover; background: #eee; margin-bottom: 1rem; border: 1px solid #ccc; border-radius: 4px; transition: transform 0.5s ease; }
    .book-item:hover .book-cover { transform: scale(1.05); }
    .book-title { font-weight: bold; color: var(--primary-color); font-size: 1rem; margin-bottom: 0.3rem; line-height: 1.2; }
    .book-author { font-size: 0.85rem; color: #666; margin-bottom: 1rem; }
    .btn-read { margin-top: auto; padding: 0.4rem; font-size: 0.9rem; text-align: center; background: var(--primary-color); color: white; border-radius: 3px; display: block; }
    .btn-read:hover { background: var(--secondary-color); text-decoration: none; }
    .delete-form { position: absolute; top: 10px; right: 10px; background: rgba(255,255,255,0.9); border-radius: 50%; z-index: 10; }
    .delete-btn { background: #D90429; color: white; border: none; width: 30px; height: 30px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; font-weight: bold; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }
    .delete-btn:hover { background: #ef233c; }
</style>
{% endblock %}
{% block content %}
<div class="dashboard-header">
    <div>
        <h2 style="margin-top:0;">Welcome back, {{ session.get('user_name') }}!</h2>
        <div id="quote-container" style="margin-top: 1rem; padding-left: 1rem; border-left: 3px solid var(--accent-color); font-style: italic; color: #555; transition: opacity 0.5s ease; opacity: 0; min-height: 50px; max-width: 500px;">
            <p id="quote-text" style="margin:0 0 0.5rem 0;">"Loading wisdom..."</p>
            <p id="quote-author" style="margin:0; font-size: 0.9rem; font-weight: bold; color: var(--primary-color);">-</p>
        </div>
    </div>
    <div class="stats-container">
        <div class="stat-box"><div class="stat-number">{{ stats.total_books }}</div><div class="stat-label">Books Started</div></div>
        <div class="stat-box"><div class="stat-number">{{ (stats.total_time / 60)|round(1) }}</div><div class="stat-label">Minutes Read</div></div>
    </div>
</div>
<div class="book-list">
    <h3 class="section-title">Recently Added to Library</h3>
    <div class="book-grid">
        {% for book in books %}
        <div class="book-item">
            {% if book.added_by == session.get('user_id') %}
            <form action="{{ url_for('delete_book', book_id=book.id) }}" method="POST" class="delete-form" onsubmit="return confirm('Are you sure you want to delete this book?');">
                <button type="submit" class="delete-btn" title="Delete Book">X</button>
            </form>
            {% endif %}
            {% if book.cover_image_path %}
                <img src="{{ url_for('uploaded_file', filename=book.cover_image_path) }}" alt="Cover" class="book-cover">
            {% else %}
                <div class="book-cover" style="display: flex; align-items: center; justify-content: center; background: #e0e0e0;"><span style="color: #666; font-style: italic;">No Cover</span></div>
            {% endif %}
            <div class="book-title">{{ book.title }}</div>
            <div class="book-author">by {{ book.author }}</div>
            <a href="{{ url_for('reader', book_id=book.id) }}" class="btn-read">Read Online</a>
        </div>
        {% else %}
        <p>No books found. <a href="{{ url_for('add_book') }}">Be the first to add one!</a></p>
        {% endfor %}
    </div>
</div>
{% endblock %}
{% block extra_js %}
<script>
    document.addEventListener('DOMContentLoaded', () => {
        const quotes = [
            { text: "A reader lives a thousand lives before he dies. The man who never reads lives only one.", author: "George R.R. Martin" },
            { text: "There is no friend as loyal as a book.", author: "Ernest Hemingway" },
            { text: "I have always imagined that Paradise will be a kind of library.", author: "Jorge Luis Borges" },
            { text: "Books are a uniquely portable magic.", author: "Stephen King" },
            { text: "Reading is essential for those who seek to rise above the ordinary.", author: "Jim Rohn" },
            { text: "A book is a dream that you hold in your hand.", author: "Neil Gaiman" }
        ];
        const quoteContainer = document.getElementById('quote-container');
        const quoteText = document.getElementById('quote-text');
        const quoteAuthor = document.getElementById('quote-author');
        const randomQuote = quotes[Math.floor(Math.random() * quotes.length)];
        quoteText.textContent = `"${randomQuote.text}"`;
        quoteAuthor.textContent = `- ${randomQuote.author}`;
        setTimeout(() => { quoteContainer.style.opacity = "1"; }, 100);
    });
</script>
{% endblock %}""",
    'my_books.html': """{% extends 'base.html' %}
{% block title %}My Reading List - Goodreads{% endblock %}
{% block extra_css %}
<style>
    .list-container { max-width: 900px; margin: 0 auto; }
    .book-row { display: flex; background: white; border: 1px solid #e1e8ed; border-radius: 4px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05); transition: transform 0.3s ease; }
    .book-row:hover { transform: translateY(-4px); box-shadow: 0 8px 15px rgba(0,0,0,0.1); }
    .book-cover { width: 120px; height: 180px; object-fit: cover; background: #eee; border: 1px solid #ccc; margin-right: 2rem; }
    .book-info { flex: 1; display: flex; flex-direction: column; }
    .book-title { font-size: 1.4rem; color: var(--primary-color); margin: 0 0 0.5rem 0; font-family: var(--font-heading); }
    .book-meta { color: #666; margin-bottom: 1rem; }
    .progress-stats { background: #f4f8fa; padding: 1rem; border-radius: 4px; display: flex; gap: 2rem; margin-top: auto; }
    .stat { font-size: 0.9rem; }
    .stat strong { color: var(--primary-color); font-size: 1.1rem; }
    .action-area { display: flex; align-items: center; margin-left: 2rem; }
</style>
{% endblock %}
{% block content %}
<div class="list-container">
    <h2 style="border-bottom: 2px solid var(--primary-color); padding-bottom: 0.5rem; margin-bottom: 2rem;">My Reading List</h2>
    {% for book in books %}
    <div class="book-row">
        {% if book.cover_image_path %}
            <img src="{{ url_for('uploaded_file', filename=book.cover_image_path) }}" alt="Cover" class="book-cover">
        {% else %}
            <div class="book-cover" style="display: flex; align-items: center; justify-content: center; background: #e0e0e0;"><span style="color: #666; font-style: italic;">No Cover</span></div>
        {% endif %}
        <div class="book-info">
            <h3 class="book-title">{{ book.title }}</h3>
            <div class="book-meta">by {{ book.author }} | Genre: {{ book.genre }}</div>
            <p style="font-size: 0.9rem; color: #555; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">{{ book.description }}</p>
            <div class="progress-stats">
                <div class="stat">Resuming at Page <br><strong>{{ book.last_page_read }}</strong></div>
                <div class="stat">Time Spent Reading <br><strong>{{ (book.time_spent / 60)|round }} mins</strong></div>
            </div>
        </div>
        <div class="action-area">
            <a href="{{ url_for('reader', book_id=book.id) }}" class="btn btn-primary" style="padding: 0.8rem 2rem; font-size: 1.1rem;">Continue Reading</a>
        </div>
    </div>
    {% else %}
    <div style="text-align: center; padding: 4rem; background: #f9fbfd; border-radius: 8px;">
        <h3>You haven't started reading any books yet.</h3>
        <p>Explore the <a href="{{ url_for('catalog') }}">Library Catalog</a> to find your first read!</p>
    </div>
    {% endfor %}
</div>
{% endblock %}""",
    'reader.html': """{% extends 'base.html' %}
{% block title %}{{ book.title }} - Goodreads Reader{% endblock %}
{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/reader.css') }}">
{% endblock %}
{% block content %}
<div class="reader-toolbar">
    <div class="toolbar-left">
        <a href="{{ url_for('dashboard') }}" class="btn">&larr; Back</a>
        <h3 class="reader-title">{{ book.title }}</h3>
    </div>
    <div class="tts-controls">
        <button id="tts-play" class="btn btn-primary">🔊 Play</button>
        <button id="tts-pause" class="btn" disabled>⏸ Pause</button>
        <button id="tts-stop" class="btn" disabled>⏹ Stop</button>
        <select id="tts-voice" class="form-control" style="width: auto; display: inline-block;"><option value="">Default Voice</option></select>
        <select id="tts-rate" class="form-control" style="width: auto; display: inline-block;">
            <option value="0.5">0.5x</option>
            <option value="1" selected>1.0x</option>
            <option value="1.5">1.5x</option>
            <option value="2">2.0x</option>
        </select>
    </div>
    <div class="reader-settings">
        <button id="theme-toggle" class="btn">🌙 Dark</button>
        <button id="font-increase" class="btn">A+</button>
        <button id="font-decrease" class="btn">A-</button>
    </div>
</div>
<div class="reader-container" id="reader-container">
    <div class="book-pages-wrapper">
        <div class="page-nav prev-page" id="prev-btn">&lt;</div>
        <div class="book-spread">
            <div class="page-content" id="page-display"></div>
        </div>
        <div class="page-nav next-page" id="next-btn">&gt;</div>
    </div>
    <div class="progress-container">
        <div class="progress-bar" id="progress-bar"></div>
        <div class="page-indicator">Page <span id="current-page-num">1</span> of {{ pages|length }}</div>
    </div>
</div>
{% endblock %}
{% block extra_js %}
<script>
    const bookId = {{ book.id }};
    const lastPageRead = {{ last_page }};
    const bookPagesData = [
        {% for page in pages %}
            {{ page.text_content|tojson|safe }}{% if not loop.last %},{% endif %}
        {% endfor %}
    ];
</script>
<script src="{{ url_for('static', filename='js/reader.js') }}"></script>
<script src="{{ url_for('static', filename='js/tts.js') }}"></script>
{% endblock %}"""
}

for filename, content in templates.items():
    with open(f"templates/{filename}", "w", encoding="utf-8") as f:
        f.write(content)

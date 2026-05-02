import os
import glob

replacements = [
    ('background: white;', 'background: var(--card-bg);'),
    ('background: #white;', 'background: var(--card-bg);'),
    ('background-color: white;', 'background-color: var(--card-bg);'),
    ('background: #f4f8fa;', 'background: var(--header-bg);'),
    ('background: #f9fbfd;', 'background: var(--bg-color);'),
    ('color: #333;', 'color: var(--text-color);'),
    ('color: #555;', 'color: var(--text-muted);'),
    ('color: #666;', 'color: var(--text-muted);'),
    ('border: 1px solid #ddd;', 'border: 1px solid var(--border-color);'),
    ('border: 1px solid #ccc;', 'border: 1px solid var(--border-color);'),
    ('border: 1px solid #eee;', 'border: 1px solid var(--border-color);'),
    ('border: 1px solid #e1e8ed;', 'border: 1px solid var(--border-color);'),
    ('border: 1px solid #eef2f5;', 'border: 1px solid var(--border-color);'),
    ('border-bottom: 1px solid #ddd;', 'border-bottom: 1px solid var(--border-color);'),
    ('border-top: 1px solid #ddd;', 'border-top: 1px solid var(--border-color);'),
    ('background: #eee;', 'background: var(--border-color);'),
    ('background: #e0e0e0;', 'background: var(--border-color);'),
    ('background: #f0f0f0;', 'background: var(--border-color);'),
]

for f in glob.glob('templates/*.html') + glob.glob('static/css/*.css'):
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    for old, new in replacements:
        content = content.replace(old, new)
        
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)

"""
Standalone Flask setup.py - Create proper folder structure
Run this once to organize files correctly for Flask
"""

import os
import shutil

# Define the base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Create necessary directories
DIRS_TO_CREATE = [
    os.path.join(BASE_DIR, 'templates'),
    os.path.join(BASE_DIR, 'static'),
    os.path.join(BASE_DIR, 'uploads')
]

for directory in DIRS_TO_CREATE:
    os.makedirs(directory, exist_ok=True)
    print(f"✓ Directory created: {directory}")

# Copy HTML to templates if it exists in root
html_src = os.path.join(BASE_DIR, 'index.html')
html_dst = os.path.join(BASE_DIR, 'templates', 'index.html')

if os.path.exists(html_src) and not os.path.exists(html_dst):
    shutil.copy(html_src, html_dst)
    print(f"✓ Copied index.html to templates/")

# Copy CSS to static if it exists in root
css_src = os.path.join(BASE_DIR, 'style.css')
css_dst = os.path.join(BASE_DIR, 'static', 'style.css')

if os.path.exists(css_src) and not os.path.exists(css_dst):
    shutil.copy(css_src, css_dst)
    print(f"✓ Copied style.css to static/")

# Copy JS to static if it exists in root
js_src = os.path.join(BASE_DIR, 'script.js')
js_dst = os.path.join(BASE_DIR, 'static', 'script.js')

if os.path.exists(js_src) and not os.path.exists(js_dst):
    shutil.copy(js_src, js_dst)
    print(f"✓ Copied script.js to static/")

print("\n✓ Setup complete! All directories and files are organized.")
print("Run 'python app.py' to start the server.")

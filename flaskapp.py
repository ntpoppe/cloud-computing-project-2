from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort
import sqlite3
import os

app = Flask(__name__)

BASE = os.path.dirname(os.path.abspath(__file__))
db = os.path.join(BASE, 'flask_app_db.db')
UPLOADS = os.path.join(BASE, 'uploads')

# SQLite setup
conn = sqlite3.connect(db)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users 
             (username TEXT, password TEXT, first_name TEXT, last_name TEXT, email TEXT, address TEXT)''')
conn.commit()
conn.close()

def user_dir(username):
    return os.path.join(UPLOADS, username)

def get_upload(username):
    d = user_dir(username)
    if os.path.isdir(d):
        files = os.listdir(d)
        if files:
            return files[0]
    return None

@app.route('/')
def index():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    address = request.form['address']

    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password, first_name, last_name, email, address) VALUES (?, ?, ?, ?, ?, ?)",
              (username, password, first_name, last_name, email, address))
    conn.commit()
    conn.close()

    f = request.files.get('file')
    if f and f.filename:
        d = user_dir(username)
        os.makedirs(d, exist_ok=True)
        f.save(os.path.join(d, f.filename))

    return redirect(url_for('profile', username=username))

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        return redirect(url_for('profile', username=username))
    return render_template('login.html', error="Invalid username or password")

@app.route('/profile/<username>')
def profile(username):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()

    filename = get_upload(username)
    word_count = None
    if filename:
        with open(os.path.join(user_dir(username), filename), encoding='utf-8', errors='ignore') as fh:
            word_count = len(fh.read().split())

    return render_template('profile.html', user=user, filename=filename, word_count=word_count)

@app.route('/download/<username>')
def download(username):
    filename = get_upload(username)
    if not filename:
        abort(404)
    return send_from_directory(user_dir(username), filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

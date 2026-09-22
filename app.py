from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# SQLite setup
conn = sqlite3.connect('flask_app_db.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users 
             (username TEXT, password TEXT, first_name TEXT, last_name TEXT, email TEXT, address TEXT)''')
conn.commit()
conn.close()

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

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password, first_name, last_name, email, address) VALUES (?, ?, ?, ?, ?, ?)",
              (username, password, first_name, last_name, email, address))
    conn.commit()
    conn.close()

    return redirect(url_for('profile', username=username))

@app.route('/profile/<username>')
def profile(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()

    return render_template('profile.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)

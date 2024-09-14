from flask import Flask, request, redirect, jsonify
import sqlite3
import random
import string

app = Flask(__name__)

# Helper function to generate short URL code
def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

# Initialize database
def init_db():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_url TEXT NOT NULL,
                short_code TEXT UNIQUE NOT NULL
            )
        ''')
        conn.commit()

init_db()

# Route to create a short URL
@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    original_url = data.get('url')

    if not original_url:
        return jsonify({'error': 'URL is required'}), 400

    short_code = generate_short_code()

    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO urls (original_url, short_code) VALUES (?, ?)', (original_url, short_code))
            conn.commit()
        except sqlite3.IntegrityError:
            return jsonify({'error': 'Short code already exists'}), 500

    short_url = request.host_url + short_code
    return jsonify({'short_url': short_url}), 201

# Route to redirect to the original URL
@app.route('/<short_code>')
def redirect_to_url(short_code):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT original_url FROM urls WHERE short_code = ?', (short_code,))
        result = cursor.fetchone()

    if result:
        return redirect(result[0])
    else:
        return jsonify({'error': 'URL not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)

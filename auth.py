from flask import Blueprint, request, jsonify, session
from database import get_db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    pin = str(data.get('pin', ''))

    if not username:
        return jsonify({'error': 'Username is required'}), 400
    if len(pin) != 4 or not pin.isdigit():
        return jsonify({'error': 'PIN must be exactly 4 digits'}), 400

    db = get_db()
    try:
        db.execute('INSERT INTO users (username, pin) VALUES (?, ?)', (username, pin))
        db.commit()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['is_admin'] = user['is_admin']
        return jsonify({'ok': True, 'username': username, 'is_admin': user['is_admin']})
    except Exception:
        return jsonify({'error': 'Username already taken'}), 409
    finally:
        db.close()


@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    pin = str(data.get('pin', ''))

    db = get_db()
    user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    db.close()

    if not user or user['pin'] != pin:
        return jsonify({'error': 'Wrong username or PIN'}), 401

    session['user_id'] = user['id']
    session['username'] = user['username']
    session['is_admin'] = user['is_admin']
    return jsonify({'ok': True, 'username': username, 'is_admin': user['is_admin']})


@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'ok': True})


@auth_bp.route('/api/me', methods=['GET'])
def me():
    if 'user_id' not in session:
        return jsonify({'logged_in': False}), 401
    return jsonify({
        'logged_in': True,
        'user_id': session['user_id'],
        'username': session['username'],
        'is_admin': session.get('is_admin', 0)
    })

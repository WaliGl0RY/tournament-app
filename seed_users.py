"""
Seed users from users_seed.json into the database.
Run from inside tournament_app/:

    python seed_users.py

Skips users that already exist (safe to run multiple times).
"""

import json
import os
import sys

# make sure imports resolve when run from this folder
sys.path.insert(0, os.path.dirname(__file__))

from database import get_db, init_db
from flask_bcrypt import Bcrypt

# need a minimal Flask app to use bcrypt
from app import app, bcrypt

SEED_FILE = os.path.join(os.path.dirname(__file__), 'users_seed.json')


def seed():
    with app.app_context():
        init_db()

    users = json.load(open(SEED_FILE, encoding='utf-8'))

    added = 0
    skipped = 0

    with app.app_context():
        db = get_db()
        for u in users:
            username = u['username'].strip()
            pin = str(u['pin']).strip()

            if len(pin) != 4 or not pin.isdigit():
                print(f'  SKIP  {username!r} — PIN must be 4 digits (got {pin!r})')
                skipped += 1
                continue

            exists = db.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
            if exists:
                print(f'  skip  {username} (already exists)')
                skipped += 1
                continue

            pin_hash = bcrypt.generate_password_hash(pin).decode('utf-8')
            db.execute('INSERT INTO users (username, pin_hash) VALUES (?, ?)', (username, pin_hash))
            print(f'  added {username}')
            added += 1

        db.commit()
        db.close()

    print(f'\nDone — {added} added, {skipped} skipped.')


if __name__ == '__main__':
    seed()

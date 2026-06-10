import sqlite3
import os

DB_PATH = os.environ.get('DB_PATH', os.path.join(os.path.dirname(__file__), 'tournament.db'))


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()

    c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT    UNIQUE NOT NULL,
            pin        TEXT    NOT NULL,
            is_admin   INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS tournaments (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            invite_code TEXT    UNIQUE NOT NULL,
            admin_id    INTEGER NOT NULL,
            max_players INTEGER DEFAULT 0,
            tournament_type TEXT DEFAULT 'championnat',
            legs        INTEGER DEFAULT 2,
            status      TEXT    DEFAULT 'setup',
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS participants (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            tournament_id INTEGER NOT NULL,
            user_id       INTEGER NOT NULL,
            team_name     TEXT,
            team_overall  INTEGER,
            team_stars    REAL,
            UNIQUE (tournament_id, user_id)
        );

        CREATE TABLE IF NOT EXISTS matches (
            id                   INTEGER PRIMARY KEY AUTOINCREMENT,
            tournament_id        INTEGER NOT NULL,
            matchday             INTEGER NOT NULL,
            home_participant_id  INTEGER NOT NULL,
            away_participant_id  INTEGER NOT NULL,
            home_score           INTEGER,
            away_score           INTEGER,
            submitted_at         TIMESTAMP,
            leg                  INTEGER DEFAULT 1,
            round_label          TEXT DEFAULT NULL
        );

        CREATE TABLE IF NOT EXISTS activity_log (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            event_type    TEXT NOT NULL,
            tournament_id INTEGER,
            username      TEXT,
            details       TEXT
        );
    """)

    # Safe migrations
    for migration in [
        'ALTER TABLE tournaments ADD COLUMN max_players INTEGER DEFAULT 0',
        "ALTER TABLE tournaments ADD COLUMN tournament_type TEXT DEFAULT 'championnat'",
        'ALTER TABLE tournaments ADD COLUMN legs INTEGER DEFAULT 2',
        'ALTER TABLE matches ADD COLUMN leg INTEGER DEFAULT 1',
        'ALTER TABLE matches ADD COLUMN round_label TEXT DEFAULT NULL',
        'ALTER TABLE users ADD COLUMN pin TEXT',
    ]:
        try:
            c.execute(migration)
            conn.commit()
        except Exception:
            pass

    conn.commit()
    conn.close()
    print('Database ready.')

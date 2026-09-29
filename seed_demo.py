"""
Fill a fresh database with invented demo players and three tournaments:
a league with one score awaiting validation, a two-leg knockout cup
waiting for its final, and a finished cup with a champion.

    python seed_demo.py                       # seeds ./tournament.db
    DB_PATH=demo.db python seed_demo.py       # seeds another file

Goes through the real API (Flask test client), so fixtures, score
validation and knockout auto-advance run exactly as in the app.
Refuses to touch a database that already contains users.

Every demo account uses PIN 0000.
"""

import os
import random
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import DB_PATH  # noqa: E402

PIN = '0000'
PLAYERS = ['nova', 'blaze', 'orbit', 'pixel', 'echo', 'raven', 'comet', 'zephyr']
rng = random.Random(26)


def db_has_users():
    if not os.path.exists(DB_PATH):
        return False
    conn = sqlite3.connect(DB_PATH)
    try:
        return conn.execute('SELECT COUNT(*) FROM users').fetchone()[0] > 0
    except sqlite3.OperationalError:
        return False
    finally:
        conn.close()


def client_for(app, username):
    c = app.test_client()
    r = c.post('/api/login', json={'username': username, 'pin': PIN})
    if r.status_code != 200:
        c.post('/api/register', json={'username': username, 'pin': PIN})
    return c


def check(resp):
    data = resp.get_json()
    if resp.status_code >= 400:
        raise SystemExit(f'API error {resp.status_code}: {data}')
    return data


def play(clients, tid, match, draw_ok=True):
    """Home player submits a score, away player validates it."""
    parts = {p['id']: p['username'] for p in check(clients['nova'].get(f'/api/tournament/{tid}/participants'))}
    home, away = parts[match['home_participant_id']], parts[match['away_participant_id']]
    while True:
        hs, as_ = rng.randint(0, 4), rng.randint(0, 3)
        if draw_ok or hs != as_:
            break
    check(clients[home].post(f"/api/match/{match['id']}/result", json={'home_score': hs, 'away_score': as_}))
    check(clients[away].post(f"/api/match/{match['id']}/validate", json={'action': 'accept'}))


def matches(clients, tid):
    return check(clients['nova'].get(f'/api/tournament/{tid}/matches'))


def seed():
    if db_has_users():
        raise SystemExit(f'{DB_PATH} already has users — refusing to seed. '
                         'Use a fresh file, e.g. DB_PATH=demo.db python seed_demo.py')

    from app import app
    from routes import LOG_ADMIN

    clients = {name: client_for(app, name) for name in PLAYERS}
    client_for(app, LOG_ADMIN)  # super-admin account (ADMIN_USERNAME)

    # ── League: 6 players, single round-robin, last matchday still open ──
    league = check(clients['nova'].post('/api/tournament/create', json={
        'name': 'Friday Night League', 'max_players': 6,
        'tournament_type': 'championnat', 'legs': 1}))
    tid = league['tournament_id']
    for name in PLAYERS[1:6]:
        check(clients[name].post(f'/api/tournament/{tid}/join'))
    check(clients['nova'].post(f'/api/tournament/{tid}/assign-teams', json={'team_type': 'club', 'min_stars': 4}))
    check(clients['nova'].post(f'/api/tournament/{tid}/start'))

    ms = matches(clients, tid)
    last_md = max(m['matchday'] for m in ms)
    for m in ms:
        if m['matchday'] < last_md:
            play(clients, tid, m)
    # One score submitted but not yet confirmed by the opponent
    pending = next(m for m in ms if m['matchday'] == last_md)
    parts = {p['id']: p['username'] for p in check(clients['nova'].get(f'/api/tournament/{tid}/participants'))}
    check(clients[parts[pending['home_participant_id']]].post(
        f"/api/match/{pending['id']}/result", json={'home_score': 3, 'away_score': 2}))

    # ── Supercup: 8 players, two-leg knockout, final still to play ──
    cid = knockout(clients, 'Supercup Showdown', PLAYERS, rounds_to_play=2)

    # ── Finished cup: 4 players, champion crowned ──
    wid = knockout(clients, 'Winter Cup', PLAYERS[4:], rounds_to_play=2)

    print(f'Seeded {DB_PATH}: {len(PLAYERS)} players + "{LOG_ADMIN}", '
          f'league #{tid}, supercup #{cid}, finished cup #{wid}. PIN for every account: {PIN}')


def knockout(clients, name, players, rounds_to_play):
    """Create a two-leg supercup; play `rounds_to_play` rounds (auto-advance builds the next)."""
    host = players[0]
    t = check(clients[host].post('/api/tournament/create', json={
        'name': name, 'max_players': len(players),
        'tournament_type': 'supercup', 'legs': 2}))
    tid = t['tournament_id']
    for p in players[1:]:
        check(clients[p].post(f'/api/tournament/{tid}/join'))
    check(clients[host].post(f'/api/tournament/{tid}/assign-teams', json={'team_type': 'club', 'min_stars': 4}))
    check(clients[host].post(f'/api/tournament/{tid}/start'))
    for _ in range(rounds_to_play):
        for m in [m for m in matches(clients, tid) if m['home_score'] is None]:
            play(clients, tid, m, draw_ok=False)
    return tid


if __name__ == '__main__':
    seed()

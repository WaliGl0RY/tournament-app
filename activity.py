"""
Lightweight activity logger.
Call log_event(db, ...) inside any route after the action succeeds.
db must be an open connection — do NOT close it here.
"""


def log_event(db, event_type, tournament_id=None, username=None, details=None):
    db.execute(
        'INSERT INTO activity_log (event_type, tournament_id, username, details) VALUES (?, ?, ?, ?)',
        (event_type, tournament_id, username, details)
    )

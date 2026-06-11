import secrets
from flask import Blueprint, request, jsonify, session, render_template
from database import get_db
from tournament import (generate_round_robin, generate_double_round_robin, calculate_standings,
                        generate_knockout_pairs, get_aggregate_winners, get_single_leg_winners, get_round_name)
from teams import assign_teams_to_players, filter_teams, get_leagues
from activity import log_event

routes_bp = Blueprint('routes', __name__)
LOG_ADMIN = 'walid'

def require_login():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    return None

def is_walid():
    return session.get('username', '').lower() == LOG_ADMIN


# ── Pages ──────────────────────────────────────────────────────────
@routes_bp.route('/')
def index(): return render_template('login.html')
@routes_bp.route('/dashboard')
def dashboard(): return render_template('dashboard.html')
@routes_bp.route('/matches')
def matches_page(): return render_template('matches.html')
@routes_bp.route('/admin')
def admin_page(): return render_template('admin.html')
@routes_bp.route('/manage')
def manage_page(): return render_template('manage.html')
@routes_bp.route('/logs')
def logs_page(): return render_template('logs.html')
@routes_bp.route('/join/<invite_code>')
def join_page(invite_code): return render_template('login.html', invite_code=invite_code)


# ── Users ──────────────────────────────────────────────────────────
@routes_bp.route('/api/users')
def list_users():
    err = require_login()
    if err: return err
    db = get_db()
    rows = db.execute('SELECT id, username FROM users ORDER BY username').fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


# ── Tournament CRUD ────────────────────────────────────────────────
@routes_bp.route('/api/tournament/create', methods=['POST'])
def create_tournament():
    err = require_login()
    if err: return err
    data = request.get_json()
    name = data.get('name', '').strip()
    max_players = int(data.get('max_players', 0))
    ttype = data.get('tournament_type', 'championnat')
    legs = int(data.get('legs', 2))
    if not name: return jsonify({'error': 'Tournament name is required'}), 400
    if max_players < 3: return jsonify({'error': 'Need at least 3 players'}), 400
    if ttype not in ('championnat', 'supercup'): ttype = 'championnat'
    if legs not in (1, 2): legs = 2
    invite_code = secrets.token_urlsafe(8)
    db = get_db()
    try:
        db.execute('INSERT INTO tournaments (name, invite_code, admin_id, max_players, tournament_type, legs) VALUES (?,?,?,?,?,?)',
                   (name, invite_code, session['user_id'], max_players, ttype, legs))
        db.commit()
        t = db.execute('SELECT * FROM tournaments WHERE invite_code=?', (invite_code,)).fetchone()
        db.execute('INSERT OR IGNORE INTO participants (tournament_id, user_id) VALUES (?,?)', (t['id'], session['user_id']))
        db.execute('UPDATE users SET is_admin=1 WHERE id=?', (session['user_id'],))
        log_event(db, 'tournament_created', t['id'], session['username'], f'"{name}" ({ttype}, max {max_players})')
        db.commit()
        session['is_admin'] = 1
        return jsonify({'ok': True, 'tournament_id': t['id'], 'invite_code': invite_code, 'tournament_type': ttype})
    finally:
        db.close()


@routes_bp.route('/api/tournament/<int:tid>/info')
def get_tournament_info(tid):
    db = get_db()
    t = db.execute('SELECT * FROM tournaments WHERE id=?', (tid,)).fetchone()
    db.close()
    if not t: return jsonify({'error': 'Not found'}), 404
    return jsonify(dict(t))


@routes_bp.route('/api/tournament/current')
def get_current_tournament():
    """Most relevant tournament for spectators: prefer active, then setup, most recent."""
    db = get_db()
    t = db.execute("""
        SELECT * FROM tournaments
        ORDER BY CASE status WHEN 'active' THEN 0 WHEN 'setup' THEN 1 ELSE 2 END,
                 id DESC
        LIMIT 1
    """).fetchone()
    db.close()
    if not t: return jsonify({'error': 'No tournament'}), 404
    return jsonify(dict(t))


@routes_bp.route('/api/tournament/by-code/<invite_code>')
def get_tournament_by_code(invite_code):
    db = get_db()
    t = db.execute('SELECT * FROM tournaments WHERE invite_code=?', (invite_code,)).fetchone()
    db.close()
    if not t: return jsonify({'error': 'Not found'}), 404
    return jsonify(dict(t))


@routes_bp.route('/api/tournament/<int:tid>/join', methods=['POST'])
def join_tournament(tid):
    err = require_login()
    if err: return err
    db = get_db()
    try:
        t = db.execute('SELECT * FROM tournaments WHERE id=?', (tid,)).fetchone()
        if not t: return jsonify({'error': 'Not found'}), 404
        if t['status'] != 'setup': return jsonify({'error': 'Tournament already started'}), 409
        already = db.execute('SELECT id FROM participants WHERE tournament_id=? AND user_id=?', (tid, session['user_id'])).fetchone()
        if already: return jsonify({'ok': True, 'message': 'Already joined'})
        if t['max_players'] > 0:
            count = db.execute('SELECT COUNT(*) as n FROM participants WHERE tournament_id=?', (tid,)).fetchone()['n']
            if count >= t['max_players']: return jsonify({'error': f'Tournament is full ({t["max_players"]} max)'}), 409
        db.execute('INSERT INTO participants (tournament_id, user_id) VALUES (?,?)', (tid, session['user_id']))
        log_event(db, 'player_joined', tid, session['username'], f'joined "{t["name"]}"')
        db.commit()
        return jsonify({'ok': True})
    finally:
        db.close()


@routes_bp.route('/api/tournament/<int:tid>/add-player', methods=['POST'])
def add_player(tid):
    err = require_login()
    if err: return err
    username = (request.get_json() or {}).get('username', '').strip()
    if not username: return jsonify({'error': 'Username required'}), 400
    db = get_db()
    try:
        t = db.execute('SELECT * FROM tournaments WHERE id=?', (tid,)).fetchone()
        if not t: return jsonify({'error': 'Not found'}), 404
        if t['admin_id'] != session['user_id']: return jsonify({'error': 'Admin only'}), 403
        if t['status'] != 'setup': return jsonify({'error': 'Cannot add players after start'}), 409
        user = db.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
        if not user: return jsonify({'error': f'No user "{username}"'}), 404
        already = db.execute('SELECT id FROM participants WHERE tournament_id=? AND user_id=?', (tid, user['id'])).fetchone()
        if already: return jsonify({'error': f'{username} already in tournament'}), 409
        if t['max_players'] > 0:
            count = db.execute('SELECT COUNT(*) as n FROM participants WHERE tournament_id=?', (tid,)).fetchone()['n']
            if count >= t['max_players']: return jsonify({'error': f'Tournament full'}), 409
        db.execute('INSERT INTO participants (tournament_id, user_id) VALUES (?,?)', (tid, user['id']))
        log_event(db, 'player_added_by_admin', tid, username, f'added by {session["username"]}')
        db.commit()
        return jsonify({'ok': True, 'username': username})
    finally:
        db.close()


@routes_bp.route('/api/tournament/<int:tid>/remove-player', methods=['POST'])
def remove_player(tid):
    err = require_login()
    if err: return err
    username = (request.get_json() or {}).get('username', '').strip()
    if not username: return jsonify({'error': 'Username required'}), 400
    db = get_db()
    try:
        t = db.execute('SELECT * FROM tournaments WHERE id=?', (tid,)).fetchone()
        if not t: return jsonify({'error': 'Not found'}), 404
        if t['admin_id'] != session['user_id']: return jsonify({'error': 'Admin only'}), 403
        if t['status'] != 'setup': return jsonify({'error': 'Cannot remove players after start'}), 409
        user = db.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
        if not user: return jsonify({'error': f'No user "{username}"'}), 404
        db.execute('DELETE FROM participants WHERE tournament_id=? AND user_id=?', (tid, user['id']))
        db.commit()
        return jsonify({'ok': True})
    finally:
        db.close()


@routes_bp.route('/api/tournament/<int:tid>/manual-assign-teams', methods=['POST'])
def manual_assign_teams(tid):
    err = require_login()
    if err: return err
    data = request.get_json() or {}
    assignments = data.get('assignments', {})  # { participant_id: team_name }
    if not assignments: return jsonify({'error': 'No assignments provided'}), 400
    db = get_db()
    try:
        t = db.execute('SELECT * FROM tournaments WHERE id=?', (tid,)).fetchone()
        if not t or t['admin_id'] != session['user_id']: return jsonify({'error': 'Admin only'}), 403
        all_teams = {team['name']: team for team in filter_teams()}
        summary = []
        for pid_str, team_name in assignments.items():
            team = all_teams.get(team_name)
            if not team: return jsonify({'error': f'Team "{team_name}" not found'}), 404
            db.execute('UPDATE participants SET team_name=?, team_overall=?, team_stars=? WHERE id=? AND tournament_id=?',
                       (team['name'], team['overall'], team['stars'], int(pid_str), tid))
            p = db.execute('SELECT u.username FROM participants p JOIN users u ON p.user_id=u.id WHERE p.id=?', (int(pid_str),)).fetchone()
            if p: summary.append(f'{p["username"]}→{team["name"]}')
        log_event(db, 'teams_assigned', tid, session['username'], ' | '.join(summary))
        db.commit()
        return jsonify({'ok': True})
    finally:
        db.close()


@routes_bp.route('/api/tournament/<int:tid>/participants')
def get_participants(tid):
    db = get_db()
    rows = db.execute('SELECT p.*, u.username FROM participants p JOIN users u ON p.user_id=u.id WHERE p.tournament_id=?', (tid,)).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


@routes_bp.route('/api/tournament/<int:tid>/assign-teams', methods=['POST'])
def assign_teams(tid):
    err = require_login()
    if err: return err
    data = request.get_json()
    filters = {}
    if data.get('team_type'): filters['team_type'] = data['team_type']
    if data.get('min_stars') is not None: filters['min_stars'] = float(data['min_stars'])
    if data.get('max_stars') is not None: filters['max_stars'] = float(data['max_stars'])
    if data.get('league'):    filters['league']    = data['league']
    db = get_db()
    try:
        t = db.execute('SELECT * FROM tournaments WHERE id=?', (tid,)).fetchone()
        if not t or t['admin_id'] != session['user_id']: return jsonify({'error': 'Not authorized'}), 403
        parts = db.execute('SELECT * FROM participants WHERE tournament_id=?', (tid,)).fetchall()
        if not parts: return jsonify({'error': 'No participants yet'}), 400
        try:
            assignments = assign_teams_to_players([p['id'] for p in parts], filters)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        summary = []
        for pid, team in assignments.items():
            db.execute('UPDATE participants SET team_name=?, team_overall=?, team_stars=? WHERE id=?',
                       (team['name'], team['overall'], team['stars'], pid))
            p = db.execute('SELECT u.username FROM participants p JOIN users u ON p.user_id=u.id WHERE p.id=?', (pid,)).fetchone()
            if p: summary.append(f'{p["username"]}→{team["name"]}({team["stars"]}⭐)')
        log_event(db, 'teams_assigned', tid, session['username'], ' | '.join(summary))
        db.commit()
        return jsonify({'ok': True})
    finally:
        db.close()


@routes_bp.route('/api/tournament/<int:tid>/start', methods=['POST'])
def start_tournament(tid):
    err = require_login()
    if err: return err
    db = get_db()
    try:
        t = db.execute('SELECT * FROM tournaments WHERE id=?', (tid,)).fetchone()
        if not t or t['admin_id'] != session['user_id']: return jsonify({'error': 'Not authorized'}), 403
        if t['status'] != 'setup': return jsonify({'error': 'Already started'}), 409
        parts = db.execute('SELECT * FROM participants WHERE tournament_id=?', (tid,)).fetchall()
        if len(parts) < 2: return jsonify({'error': 'Need at least 2 players'}), 400
        pid_list = [p['id'] for p in parts]
        ttype = t['tournament_type'] or 'championnat'
        legs  = int(t['legs'] or 2)

        if ttype == 'championnat':
            if legs == 2:
                first, second = generate_double_round_robin(pid_list)
                n = len(first)
                for i, matchday in enumerate(first, 1):
                    label = f'1st Half — Matchday {i}'
                    for h, a in matchday:
                        db.execute('INSERT INTO matches (tournament_id, matchday, home_participant_id, away_participant_id, leg, round_label) VALUES (?,?,?,?,?,?)',
                                   (tid, i, h, a, 1, label))
                for i, matchday in enumerate(second, 1):
                    md_num = n + i
                    label  = f'2nd Half — Matchday {i}'
                    for h, a in matchday:
                        db.execute('INSERT INTO matches (tournament_id, matchday, home_participant_id, away_participant_id, leg, round_label) VALUES (?,?,?,?,?,?)',
                                   (tid, md_num, h, a, 2, label))
                log_event(db, 'tournament_started', tid, session['username'],
                          f'Championnat — {len(parts)} players, {len(first)*2} matchdays (2 halves)')
                extra = {'matchdays': len(first) * 2, 'half': len(first)}
            else:  # 1 leg
                rounds = generate_round_robin(pid_list)
                for i, matchday in enumerate(rounds, 1):
                    label = f'Matchday {i}'
                    for h, a in matchday:
                        db.execute('INSERT INTO matches (tournament_id, matchday, home_participant_id, away_participant_id, leg, round_label) VALUES (?,?,?,?,?,?)',
                                   (tid, i, h, a, 1, label))
                log_event(db, 'tournament_started', tid, session['username'],
                          f'Championnat — {len(parts)} players, {len(rounds)} matchdays (1 leg)')
                extra = {'matchdays': len(rounds), 'half': len(rounds)}

        else:  # supercup
            pairs = generate_knockout_pairs(pid_list)
            round_name = get_round_name(len(pid_list))
            for h, a in pairs:
                db.execute('INSERT INTO matches (tournament_id, matchday, home_participant_id, away_participant_id, leg, round_label) VALUES (?,?,?,?,?,?)',
                           (tid, 1, h, a, 1, round_name + (' — Leg 1' if legs == 2 else '')))
            if legs == 2:
                for h, a in pairs:
                    db.execute('INSERT INTO matches (tournament_id, matchday, home_participant_id, away_participant_id, leg, round_label) VALUES (?,?,?,?,?,?)',
                               (tid, 2, a, h, 2, round_name + ' — Leg 2'))
            log_event(db, 'tournament_started', tid, session['username'],
                      f'Supercup — {len(parts)} players, starting {round_name} ({legs} leg(s))')
            extra = {'round': round_name}

        db.execute("UPDATE tournaments SET status='active' WHERE id=?", (tid,))
        db.commit()
        return jsonify({'ok': True, 'tournament_type': ttype, **extra})
    finally:
        db.close()


@routes_bp.route('/api/tournament/<int:tid>/advance-round', methods=['POST'])
def advance_round(tid):
    err = require_login()
    if err: return err
    if not is_walid(): return jsonify({'error': 'Admin only'}), 403
    db = get_db()
    try:
        t = db.execute('SELECT * FROM tournaments WHERE id=?', (tid,)).fetchone()
        if not t: return jsonify({'error': 'Not found'}), 404
        if t['tournament_type'] != 'supercup': return jsonify({'error': 'Supercup only'}), 400

        legs = int(t['legs'] or 2)
        all_matches = [dict(m) for m in db.execute('SELECT * FROM matches WHERE tournament_id=?', (tid,)).fetchall()]
        max_md = max(m['matchday'] for m in all_matches)

        if legs == 2:
            leg1_md = max_md - 1
            leg2_md = max_md
            leg1_matches = [m for m in all_matches if m['matchday'] == leg1_md]
            cur_matches  = leg1_matches + [m for m in all_matches if m['matchday'] == leg2_md]
        else:
            leg1_md = max_md
            leg1_matches = [m for m in all_matches if m['matchday'] == leg1_md]
            cur_matches  = leg1_matches

        # Fill missing scores with 0 (walkover)
        for m in cur_matches:
            if m['home_score'] is None:
                db.execute('UPDATE matches SET home_score=0, away_score=0 WHERE id=?', (m['id'],))
        db.commit()
        all_matches = [dict(m) for m in db.execute('SELECT * FROM matches WHERE tournament_id=?', (tid,)).fetchall()]

        pairs = [(m['home_participant_id'], m['away_participant_id']) for m in leg1_matches]
        winners = get_aggregate_winners(pairs, all_matches) if legs == 2 else get_single_leg_winners(pairs, all_matches)
        if winners is None:
            return jsonify({'error': 'Could not determine winners — check match data'}), 400

        if len(winners) == 1:
            p = db.execute('SELECT u.username FROM participants p JOIN users u ON p.user_id=u.id WHERE p.id=?', (winners[0],)).fetchone()
            db.execute("UPDATE tournaments SET status='finished' WHERE id=?", (tid,))
            log_event(db, 'tournament_finished', tid, session['username'], f'Winner: {p["username"] if p else "?"}')
            db.commit()
            return jsonify({'ok': True, 'finished': True, 'winner': p['username'] if p else '?'})

        new_pairs = generate_knockout_pairs(winners)
        round_name = get_round_name(len(winners))
        next_md = max_md + 1
        for h, a in new_pairs:
            db.execute('INSERT INTO matches (tournament_id, matchday, home_participant_id, away_participant_id, leg, round_label) VALUES (?,?,?,?,?,?)',
                       (tid, next_md, h, a, 1, round_name + (' — Leg 1' if legs == 2 else '')))
        if legs == 2:
            for h, a in new_pairs:
                db.execute('INSERT INTO matches (tournament_id, matchday, home_participant_id, away_participant_id, leg, round_label) VALUES (?,?,?,?,?,?)',
                           (tid, next_md + 1, a, h, 2, round_name + ' — Leg 2'))
        log_event(db, 'round_advanced', tid, session['username'], f'Advanced to {round_name}')
        db.commit()
        return jsonify({'ok': True, 'finished': False, 'round_name': round_name})
    finally:
        db.close()


@routes_bp.route('/api/tournament/<int:tid>/standings')
def get_standings(tid):
    db = get_db()
    try:
        parts   = db.execute('SELECT p.*, u.username FROM participants p JOIN users u ON p.user_id=u.id WHERE p.tournament_id=?', (tid,)).fetchall()
        matches = db.execute('SELECT * FROM matches WHERE tournament_id=?', (tid,)).fetchall()
        return jsonify(calculate_standings([dict(m) for m in matches], [dict(p) for p in parts]))
    finally:
        db.close()


@routes_bp.route('/api/tournament/<int:tid>/matches')
def get_matches(tid):
    err = require_login()
    if err: return err
    db = get_db()
    try:
        rows = db.execute('''
            SELECT m.*,
                   uh.username  AS home_username, ph.team_name AS home_team,
                   ua.username  AS away_username, pa.team_name AS away_team
            FROM matches m
            JOIN participants ph ON m.home_participant_id=ph.id
            JOIN participants pa ON m.away_participant_id=pa.id
            JOIN users uh ON ph.user_id=uh.id
            JOIN users ua ON pa.user_id=ua.id
            WHERE m.tournament_id=?
            ORDER BY m.matchday, m.id
        ''', (tid,)).fetchall()
        return jsonify([dict(r) for r in rows])
    finally:
        db.close()


# ── Match result ───────────────────────────────────────────────────
@routes_bp.route('/api/match/<int:match_id>/result', methods=['POST'])
def submit_result(match_id):
    err = require_login()
    if err: return err
    data = request.get_json()
    hs, as_ = data.get('home_score'), data.get('away_score')
    if hs is None or as_ is None: return jsonify({'error': 'Both scores required'}), 400
    if not isinstance(hs, int) or not isinstance(as_, int): return jsonify({'error': 'Scores must be integers'}), 400
    if hs < 0 or as_ < 0: return jsonify({'error': 'Scores cannot be negative'}), 400
    db = get_db()
    try:
        match = db.execute('SELECT * FROM matches WHERE id=?', (match_id,)).fetchone()
        if not match: return jsonify({'error': 'Match not found'}), 404
        my_part = db.execute('SELECT * FROM participants WHERE tournament_id=? AND user_id=?', (match['tournament_id'], session['user_id'])).fetchone()
        if is_walid():
            # Admin bypasses validation — direct override
            hp = db.execute('SELECT u.username, p.team_name FROM participants p JOIN users u ON p.user_id=u.id WHERE p.id=?', (match['home_participant_id'],)).fetchone()
            ap = db.execute('SELECT u.username, p.team_name FROM participants p JOIN users u ON p.user_id=u.id WHERE p.id=?', (match['away_participant_id'],)).fetchone()
            db.execute('UPDATE matches SET home_score=?, away_score=?, submitted_at=CURRENT_TIMESTAMP, pending_home_score=NULL, pending_away_score=NULL, pending_by=NULL WHERE id=?', (hs, as_, match_id))
            detail = f'{hp["username"]} ({hp["team_name"]}) {hs}–{as_} {ap["username"]} ({ap["team_name"]})'
            log_event(db, 'result_overridden', match['tournament_id'], session['username'], detail)
            db.commit()
        else:
            if not my_part: return jsonify({'error': 'Not in this tournament'}), 403
            if my_part['id'] not in (match['home_participant_id'], match['away_participant_id']):
                return jsonify({'error': 'Not your match'}), 403
            if match['home_score'] is not None: return jsonify({'error': 'Result already validated'}), 409
            if match['pending_by'] == session['username']: return jsonify({'error': 'You already submitted — waiting for opponent to validate'}), 409
            # Store as pending
            db.execute('UPDATE matches SET pending_home_score=?, pending_away_score=?, pending_by=? WHERE id=?', (hs, as_, session['username'], match_id))
            log_event(db, 'result_submitted', match['tournament_id'], session['username'], f'Pending validation ({hs}–{as_})')
            db.commit()
            return jsonify({'ok': True, 'pending': True, 'msg': 'Score submitted — waiting for opponent to validate.'})


        # Auto-advance supercup round when all current-round results are in
        tid_m = match['tournament_id']
        auto_msg = None
        try:
            db2 = get_db()
            t_row = db2.execute('SELECT * FROM tournaments WHERE id=?', (tid_m,)).fetchone()
            if t_row and t_row['tournament_type'] == 'supercup' and t_row['status'] == 'active':
                t_legs = int(t_row['legs'] or 2)
                all_m = [dict(r) for r in db2.execute('SELECT * FROM matches WHERE tournament_id=?', (tid_m,)).fetchall()]
                if all_m:
                    max_md = max(m['matchday'] for m in all_m)
                    if t_legs == 2:
                        cur_round = [m for m in all_m if m['matchday'] in (max_md - 1, max_md)]
                        leg1_md   = max_md - 1 if max_md > 1 else 1
                    else:
                        cur_round = [m for m in all_m if m['matchday'] == max_md]
                        leg1_md   = max_md
                    if cur_round and all(m['home_score'] is not None for m in cur_round):
                        leg1_matches = [m for m in all_m if m['matchday'] == leg1_md]
                        pairs = [(m['home_participant_id'], m['away_participant_id']) for m in leg1_matches]
                        winners = get_aggregate_winners(pairs, all_m) if t_legs == 2 else get_single_leg_winners(pairs, all_m)
                        if winners and len(winners) == 1:
                            p = db2.execute(
                                'SELECT u.username FROM participants p JOIN users u ON p.user_id=u.id WHERE p.id=?',
                                (winners[0],)).fetchone()
                            db2.execute("UPDATE tournaments SET status='finished' WHERE id=?", (tid_m,))
                            log_event(db2, 'tournament_finished', tid_m, 'system',
                                      f'Winner: {p["username"] if p else "?"}')
                            db2.commit()
                            auto_msg = f'tournament_finished:{p["username"] if p else "?"}'
                        elif winners and len(winners) > 1:
                            new_pairs = generate_knockout_pairs(winners)
                            round_name = get_round_name(len(winners))
                            next_md = max_md + 1
                            for h, a in new_pairs:
                                db2.execute('INSERT INTO matches (tournament_id, matchday, home_participant_id, away_participant_id, leg, round_label) VALUES (?,?,?,?,?,?)',
                                           (tid_m, next_md, h, a, 1, round_name + (' — Leg 1' if t_legs == 2 else '')))
                            if t_legs == 2:
                                for h, a in new_pairs:
                                    db2.execute('INSERT INTO matches (tournament_id, matchday, home_participant_id, away_participant_id, leg, round_label) VALUES (?,?,?,?,?,?)',
                                               (tid_m, next_md + 1, a, h, 2, round_name + ' — Leg 2'))
                            log_event(db2, 'round_advanced', tid_m, 'system', f'Auto-advanced to {round_name}')
                            db2.commit()
                            auto_msg = f'round_advanced:{round_name}'
            db2.close()
        except Exception as e:
            log_event(db, 'auto_advance_error', tid_m, 'system', str(e))
            db.commit()

        return jsonify({'ok': True, 'auto': auto_msg})
    finally:
        db.close()


@routes_bp.route('/api/match/<int:match_id>/validate', methods=['POST'])
def validate_result(match_id):
    err = require_login()
    if err: return err
    action = (request.get_json() or {}).get('action', 'accept')  # 'accept' or 'reject'
    db = get_db()
    try:
        match = db.execute('SELECT * FROM matches WHERE id=?', (match_id,)).fetchone()
        if not match: return jsonify({'error': 'Match not found'}), 404
        if match['pending_by'] is None: return jsonify({'error': 'No pending score to validate'}), 409
        if match['pending_by'] == session['username'] and not is_walid():
            return jsonify({'error': 'You submitted this score — your opponent must validate'}), 403
        my_part = db.execute('SELECT * FROM participants WHERE tournament_id=? AND user_id=?', (match['tournament_id'], session['user_id'])).fetchone()
        if not is_walid():
            if not my_part: return jsonify({'error': 'Not in this tournament'}), 403
            if my_part['id'] not in (match['home_participant_id'], match['away_participant_id']):
                return jsonify({'error': 'Not your match'}), 403
        if action == 'reject':
            db.execute('UPDATE matches SET pending_home_score=NULL, pending_away_score=NULL, pending_by=NULL WHERE id=?', (match_id,))
            log_event(db, 'result_rejected', match['tournament_id'], session['username'], f'Score rejected, resubmission needed')
            db.commit()
            return jsonify({'ok': True, 'rejected': True, 'msg': 'Score rejected — both players can resubmit.'})
        # Accept: move pending to official
        hs, as_ = match['pending_home_score'], match['pending_away_score']
        hp = db.execute('SELECT u.username, p.team_name FROM participants p JOIN users u ON p.user_id=u.id WHERE p.id=?', (match['home_participant_id'],)).fetchone()
        ap = db.execute('SELECT u.username, p.team_name FROM participants p JOIN users u ON p.user_id=u.id WHERE p.id=?', (match['away_participant_id'],)).fetchone()
        db.execute('UPDATE matches SET home_score=?, away_score=?, submitted_at=CURRENT_TIMESTAMP, pending_home_score=NULL, pending_away_score=NULL, pending_by=NULL WHERE id=?', (hs, as_, match_id))
        detail = f'{hp["username"]} ({hp["team_name"]}) {hs}–{as_} {ap["username"]} ({ap["team_name"]})'
        log_event(db, 'result_validated', match['tournament_id'], session['username'], detail)
        db.commit()

        # Reuse auto-advance logic
        match_updated = db.execute('SELECT * FROM matches WHERE id=?', (match_id,)).fetchone()
        tid_m = match['tournament_id']
        auto_msg = None
        try:
            db2 = get_db()
            t_row = db2.execute('SELECT * FROM tournaments WHERE id=?', (tid_m,)).fetchone()
            if t_row and t_row['tournament_type'] == 'supercup' and t_row['status'] == 'active':
                t_legs = int(t_row['legs'] or 2)
                all_m = [dict(r) for r in db2.execute('SELECT * FROM matches WHERE tournament_id=?', (tid_m,)).fetchall()]
                if all_m:
                    max_md = max(m['matchday'] for m in all_m)
                    if t_legs == 2:
                        cur_round = [m for m in all_m if m['matchday'] in (max_md - 1, max_md)]
                        leg1_md   = max_md - 1 if max_md > 1 else 1
                    else:
                        cur_round = [m for m in all_m if m['matchday'] == max_md]
                        leg1_md   = max_md
                    if cur_round and all(m['home_score'] is not None for m in cur_round):
                        leg1_matches = [m for m in all_m if m['matchday'] == leg1_md]
                        pairs = [(m['home_participant_id'], m['away_participant_id']) for m in leg1_matches]
                        winners = get_aggregate_winners(pairs, all_m) if t_legs == 2 else get_single_leg_winners(pairs, all_m)
                        if winners and len(winners) == 1:
                            p = db2.execute('SELECT u.username FROM participants p JOIN users u ON p.user_id=u.id WHERE p.id=?', (winners[0],)).fetchone()
                            db2.execute("UPDATE tournaments SET status='finished' WHERE id=?", (tid_m,))
                            log_event(db2, 'tournament_finished', tid_m, 'system', f'Winner: {p["username"] if p else "?"}')
                            db2.commit()
                            auto_msg = f'tournament_finished:{p["username"] if p else "?"}'
                        elif winners and len(winners) > 1:
                            new_pairs = generate_knockout_pairs(winners)
                            round_name = get_round_name(len(winners))
                            next_md = max_md + 1
                            for h, a in new_pairs:
                                db2.execute('INSERT INTO matches (tournament_id, matchday, home_participant_id, away_participant_id, leg, round_label) VALUES (?,?,?,?,?,?)',
                                           (tid_m, next_md, h, a, 1, round_name + (' — Leg 1' if t_legs == 2 else '')))
                            if t_legs == 2:
                                for h, a in new_pairs:
                                    db2.execute('INSERT INTO matches (tournament_id, matchday, home_participant_id, away_participant_id, leg, round_label) VALUES (?,?,?,?,?,?)',
                                               (tid_m, next_md + 1, a, h, 2, round_name + ' — Leg 2'))
                            log_event(db2, 'round_advanced', tid_m, 'system', f'Auto-advanced to {round_name}')
                            db2.commit()
                            auto_msg = f'round_advanced:{round_name}'
            db2.close()
        except Exception as e:
            log_event(db, 'auto_advance_error', tid_m, 'system', str(e))
            db.commit()

        return jsonify({'ok': True, 'auto': auto_msg})
    finally:
        db.close()


# ── Logs ───────────────────────────────────────────────────────────
@routes_bp.route('/api/admin/users')
def get_users():
    err = require_login()
    if err: return err
    if not is_walid(): return jsonify({'error': 'Access denied'}), 403
    db = get_db()
    try:
        rows = db.execute('SELECT id, username, pin, is_admin FROM users ORDER BY username').fetchall()
        return jsonify([dict(r) for r in rows])
    finally:
        db.close()


@routes_bp.route('/api/admin/logs')
def get_logs():
    err = require_login()
    if err: return err
    if not is_walid(): return jsonify({'error': 'Access denied'}), 403
    db = get_db()
    try:
        rows = db.execute('SELECT * FROM activity_log ORDER BY timestamp DESC LIMIT 500').fetchall()
        return jsonify([dict(r) for r in rows])
    finally:
        db.close()


@routes_bp.route('/api/admin/logs/clear', methods=['POST'])
def clear_logs():
    err = require_login()
    if err: return err
    if not is_walid(): return jsonify({'error': 'Access denied'}), 403
    db = get_db()
    try:
        db.execute('DELETE FROM activity_log')
        db.commit()
        return jsonify({'ok': True})
    finally:
        db.close()


# ── Teams ──────────────────────────────────────────────────────────
@routes_bp.route('/api/teams/available')
def available_teams():
    return jsonify(filter_teams(
        team_type=request.args.get('type'),
        min_stars=request.args.get('min_stars', type=float),
        max_stars=request.args.get('max_stars', type=float),
        league=request.args.get('league')
    ))

@routes_bp.route('/api/teams/leagues')
def list_leagues():
    return jsonify(get_leagues())


# ── Delete tournament ──────────────────────────────────────────────
@routes_bp.route('/api/tournament/<int:tid>/delete', methods=['DELETE'])
def delete_tournament(tid):
    err = require_login()
    if err: return err
    db = get_db()
    try:
        t = db.execute('SELECT * FROM tournaments WHERE id=?', (tid,)).fetchone()
        if not t: return jsonify({'error': 'Not found'}), 404
        if t['admin_id'] != session['user_id']: return jsonify({'error': 'Admin only'}), 403
        log_event(db, 'tournament_deleted', tid, session['username'], f'"{t["name"]}" deleted')
        db.execute('DELETE FROM matches      WHERE tournament_id=?', (tid,))
        db.execute('DELETE FROM participants WHERE tournament_id=?', (tid,))
        db.execute('DELETE FROM tournaments  WHERE id=?', (tid,))
        db.commit()
        return jsonify({'ok': True})
    finally:
        db.close()

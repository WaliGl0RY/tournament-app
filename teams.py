import json
import os

TEAMS_FILE = os.path.join(os.path.dirname(__file__), 'data', 'teams.json')


def load_teams():
    with open(TEAMS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def overall_to_stars(overall):
    """Map team overall rating to FC26 half-star scale (1.0 to 5.0, step 0.5)."""
    if overall >= 85: return 5.0
    if overall >= 83: return 4.5
    if overall >= 80: return 4.0
    if overall >= 78: return 3.5
    if overall >= 75: return 3.0
    if overall >= 73: return 2.5
    if overall >= 70: return 2.0
    return 1.5


def filter_teams(team_type=None, min_stars=None, max_stars=None, league=None):
    teams = load_teams()
    if team_type:
        teams = [t for t in teams if t['type'] == team_type]
    if min_stars is not None:
        teams = [t for t in teams if t['stars'] >= min_stars]
    if max_stars is not None:
        teams = [t for t in teams if t['stars'] <= max_stars]
    if league:
        teams = [t for t in teams if t.get('league', '').lower() == league.lower()]
    return teams


def snake_draft_assign(teams, num_players):
    """Sort by overall desc, assign via snake draft so distribution is fair."""
    pool = sorted(teams, key=lambda t: t['overall'], reverse=True)[:num_players]
    assignments = [None] * num_players
    for i, team in enumerate(pool):
        row = i // num_players
        col = i % num_players
        idx = col if row % 2 == 0 else num_players - 1 - col
        assignments[idx] = team
    return assignments


def assign_teams_to_players(participant_ids, filters):
    """Returns dict: { participant_id -> team dict }"""
    teams = filter_teams(**filters)
    n = len(participant_ids)
    if len(teams) < n:
        raise ValueError(f'Only {len(teams)} teams match the filters, need {n}.')
    assigned = snake_draft_assign(teams, n)
    return dict(zip(participant_ids, assigned))


def get_leagues():
    """Return sorted list of unique league names."""
    teams = load_teams()
    return sorted({t.get('league', '') for t in teams if t.get('league')})

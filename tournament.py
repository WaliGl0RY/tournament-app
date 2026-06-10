# ── Round-robin ────────────────────────────────────────────────────

def generate_round_robin(participant_ids):
    """Single round-robin via circle method."""
    players = list(participant_ids)
    if len(players) % 2 == 1:
        players.append(None)
    n = len(players)
    rounds = []
    for _ in range(n - 1):
        matchday = []
        for i in range(n // 2):
            h, a = players[i], players[n - 1 - i]
            if h is not None and a is not None:
                matchday.append((h, a))
        rounds.append(matchday)
        players = [players[0]] + [players[-1]] + players[1:-1]
    return rounds


def generate_double_round_robin(participant_ids):
    """
    Double round-robin: first half = home, second half = reversed (away).
    Returns (first_half_rounds, second_half_rounds), each a list of matchdays.
    """
    first  = generate_round_robin(participant_ids)
    second = [[(a, h) for h, a in matchday] for matchday in first]
    return first, second


# ── Knockout ───────────────────────────────────────────────────────

def generate_knockout_pairs(participant_ids):
    """Seed pairing: 1 vs last, 2 vs second-last, etc."""
    seeds = list(participant_ids)
    n = len(seeds)
    return [(seeds[i], seeds[n - 1 - i]) for i in range(n // 2)]


def get_round_name(num_remaining):
    if num_remaining == 2:  return 'Final'
    if num_remaining == 4:  return 'Semi-final'
    if num_remaining == 8:  return 'Quarter-final'
    return f'Round of {num_remaining}'


def get_aggregate_winners(pairs, all_matches):
    """
    pairs: list of (home_part_id, away_part_id) from leg 1 perspective.
    all_matches: list of match dicts with leg, home/away_participant_id, scores.
    Returns list of winner participant_ids, or None if not all results are in.
    """
    winners = []
    for h_id, a_id in pairs:
        leg1 = next((m for m in all_matches
                     if m['home_participant_id'] == h_id
                     and m['away_participant_id'] == a_id
                     and m['leg'] == 1), None)
        leg2 = next((m for m in all_matches
                     if m['home_participant_id'] == a_id
                     and m['away_participant_id'] == h_id
                     and m['leg'] == 2), None)
        if not leg1 or not leg2:
            return None
        if any(s is None for s in [leg1['home_score'], leg1['away_score'],
                                    leg2['home_score'], leg2['away_score']]):
            return None
        # h_id total: leg1 home goals + leg2 away goals
        h_agg = leg1['home_score'] + leg2['away_score']
        a_agg = leg1['away_score'] + leg2['home_score']
        if h_agg > a_agg:
            winners.append(h_id)
        elif a_agg > h_agg:
            winners.append(a_id)
        else:
            # Away goals tiebreaker: away goals scored by each team
            h_away = leg2['away_score']   # h_id played away in leg 2
            a_away = leg1['away_score']   # a_id played away in leg 1
            winners.append(h_id if h_away >= a_away else a_id)
    return winners


def get_single_leg_winners(pairs, all_matches):
    """
    Determine winners from single-leg matches.
    pairs: list of (home_part_id, away_part_id).
    Returns list of winner participant_ids, or None if not all results are in.
    """
    winners = []
    for h_id, a_id in pairs:
        m = next((m for m in all_matches
                  if m['home_participant_id'] == h_id
                  and m['away_participant_id'] == a_id
                  and m['leg'] == 1), None)
        if not m or m['home_score'] is None:
            return None
        if m['home_score'] > m['away_score']:
            winners.append(h_id)
        elif m['away_score'] > m['home_score']:
            winners.append(a_id)
        else:
            winners.append(h_id)  # tiebreak: home team advances
    return winners


# ── Standings ──────────────────────────────────────────────────────

def calculate_standings(matches, participants):
    stats = {}
    for p in participants:
        stats[p['id']] = {
            'participant_id': p['id'], 'user_id': p['user_id'],
            'username': p['username'], 'team_name': p.get('team_name', '—'),
            'team_stars': p.get('team_stars', 0),
            'played': 0, 'won': 0, 'drawn': 0, 'lost': 0,
            'goals_for': 0, 'goals_against': 0, 'goal_diff': 0, 'points': 0
        }
    for m in matches:
        hs, as_ = m.get('home_score'), m.get('away_score')
        if hs is None or as_ is None: continue
        h, a = m['home_participant_id'], m['away_participant_id']
        if h not in stats or a not in stats: continue
        stats[h]['played'] += 1; stats[a]['played'] += 1
        stats[h]['goals_for'] += hs;     stats[h]['goals_against'] += as_
        stats[a]['goals_for'] += as_;    stats[a]['goals_against'] += hs
        if hs > as_:
            stats[h]['won'] += 1; stats[h]['points'] += 3; stats[a]['lost'] += 1
        elif hs < as_:
            stats[a]['won'] += 1; stats[a]['points'] += 3; stats[h]['lost'] += 1
        else:
            stats[h]['drawn'] += 1; stats[h]['points'] += 1
            stats[a]['drawn'] += 1; stats[a]['points'] += 1
    for s in stats.values():
        s['goal_diff'] = s['goals_for'] - s['goals_against']
    return sorted(stats.values(),
                  key=lambda x: (-x['points'], -x['goal_diff'], -x['goals_for']))

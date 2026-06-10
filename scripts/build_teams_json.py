"""
Run this script once after downloading the FC26 dataset from Kaggle:
  https://www.kaggle.com/datasets/rovnez/fc-26-fifa-26-player-data

Usage:
  python scripts/build_teams_json.py --csv path/to/players.csv

It reads the CSV, groups players by club, calculates team overall + avg pace,
maps to star ratings, and writes data/teams.json.
"""

import csv
import json
import argparse
import os
from collections import defaultdict

OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'data', 'teams.json')


def overall_to_stars(overall):
    if overall >= 85: return 5
    if overall >= 80: return 4
    if overall >= 75: return 3
    if overall >= 70: return 2
    return 1


def build(csv_path, min_squad=11):
    clubs = defaultdict(lambda: {'overall': [], 'pace': [], 'league': '', 'type': 'club'})
    nationals = defaultdict(lambda: {'overall': [], 'pace': [], 'league': 'International', 'type': 'national'})

    with open(csv_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                overall = int(row.get('overall', 0))
                pace    = int(row.get('pace', 0)) if row.get('pace') else 0
                club    = row.get('club_name', '').strip()
                nat     = row.get('nationality_name', '').strip()
                league  = row.get('league_name', '').strip()

                if club:
                    clubs[club]['overall'].append(overall)
                    clubs[club]['pace'].append(pace)
                    clubs[club]['league'] = league

                if nat:
                    nationals[nat]['overall'].append(overall)
                    nationals[nat]['pace'].append(pace)
            except (ValueError, KeyError):
                continue

    teams = []

    for name, data in clubs.items():
        if len(data['overall']) < min_squad:
            continue
        avg_overall = round(sum(data['overall']) / len(data['overall']))
        avg_pace    = round(sum(p for p in data['pace'] if p > 0) / max(1, sum(1 for p in data['pace'] if p > 0)))
        teams.append({
            'name':     name,
            'type':     'club',
            'league':   data['league'],
            'overall':  avg_overall,
            'stars':    overall_to_stars(avg_overall),
            'avg_pace': avg_pace
        })

    for name, data in nationals.items():
        if len(data['overall']) < 11:
            continue
        avg_overall = round(sum(data['overall'][:23]) / min(23, len(data['overall'])))
        avg_pace    = round(sum(p for p in data['pace'][:23] if p > 0) / max(1, sum(1 for p in data['pace'][:23] if p > 0)))
        teams.append({
            'name':     name,
            'type':     'national',
            'league':   'International',
            'overall':  avg_overall,
            'stars':    overall_to_stars(avg_overall),
            'avg_pace': avg_pace
        })

    teams.sort(key=lambda t: t['overall'], reverse=True)

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(teams, f, indent=2, ensure_ascii=False)

    print(f'Written {len(teams)} teams to {OUTPUT}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', required=True, help='Path to players.csv from Kaggle')
    args = parser.parse_args()
    build(args.csv)

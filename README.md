<p align="center">
  <img src="docs/banner.svg" alt="FC26 Tournament: league, knockout cup, every score confirmed by the opponent" width="100%">
</p>

<p align="center">
  <b>Run an FC 26 night with your friends</b>: one invite link, a league or a knockout cup, and no score counts until the opponent confirms it.<br>
  <sub>A small Flask + SQLite web app with plain JavaScript pages. Runs on a laptop, or deployed with gunicorn.</sub>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/Flask-3-000000?logo=flask&logoColor=white" alt="Flask 3">
  <img src="https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white" alt="SQLite">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow" alt="MIT License"></a>
</p>

<p align="center">
  <a href="#story"><img src="docs/badges/zone-story.svg" alt="The story"></a>
  <a href="#features"><img src="docs/badges/zone-features.svg" alt="Features"></a>
  <a href="#learned"><img src="docs/badges/zone-learned.svg" alt="What I learned in practice"></a>
  <a href="#run"><img src="docs/badges/zone-run.svg" alt="Run it yourself"></a>
  <a href="#notes"><img src="docs/badges/zone-notes.svg" alt="Honest notes"></a>
</p>

<p align="center">
  <img src="docs/demo.gif" alt="Demo: log in, league table, opponent validates a score, table updates, knockout bracket, champion celebration" width="820">
</p>

---

<a name="story"></a>
<p><img src="docs/zones/story.svg" alt="The story" width="100%"></p>

## Why I built it

My friends and I had an FC26 tournament going, and one person had to organise everything and keep answering everyone about the standings. At the same time, I was learning RPC and client-server in BVS2. I looked for a platform that does this, but found nothing that fit, or it cost money. So I built it myself.

## How I built it

BVS2 showed me that this was possible: one server that everyone uses at the same time, from their phones or their PCs. From my databases course I knew how to design the tables and query them from Python. I used Claude as a coding assistant to turn the idea into a working app fast, so we could use it for our tournament. I decided what the app needed; every feature came from something that happened while we played.

<a name="how-it-grew"></a>
## How it grew

<table>
  <tr>
    <td width="50%" valign="top"><img src="docs/story/phase-01.svg" alt="Phase 01: Foundation. 11.06.2026, 5 commits. The whole app in one go: accounts, tournaments with invite links, league and knockout fixtures, team assignment and the live table. Then Railway deploy prep, removing players and assigning teams by hand. Why: “The standings had to be visible to everyone, all the time, so nobody had to ask one person anymore.”" width="100%"></td>
    <td width="50%" valign="top"><img src="docs/story/phase-02.svg" alt="Phase 02: Fair play. 11.06.2026, 1 commit. A submitted score stays pending until the opponent validates or rejects it. Why: “Between friends, someone always tries a joke: a wrong score, or 1000 goals. So a result only counts once the opponent confirms it.”" width="100%"></td>
  </tr>
  <tr>
    <td width="50%" valign="top"><img src="docs/story/phase-03.svg" alt="Phase 03: Finding your way. 11.06 – 12.06.2026, 8 commits. The full bracket with future rounds as TBD, then leg and matchday filters that open on your next match. Why: “Nobody should have to dig through everyone else&#x27;s matches to find their own. Your next match comes first, and the rest stays organised.”" width="100%"></td>
    <td width="50%" valign="top"><img src="docs/story/phase-04.svg" alt="Phase 04: For everyone watching. 11.06.2026, 5 commits. A spectator view of the live table and bracket, even without an invite link, and banners for players and for people waiting. Why: “Some friends weren&#x27;t playing this time but still wanted to follow the tournament while waiting for the next one. So they got their own view.”" width="100%"></td>
  </tr>
  <tr>
    <td width="50%" valign="top"><img src="docs/story/phase-05.svg" alt="Phase 05: The big moment. 11.06.2026, 4 commits. A full-screen champion celebration with trophy and confetti, and the Squad Sheet next to the bracket. Why: “The winner should feel special. After a whole tournament, the end deserves more than a line in a table.”" width="100%"></td>
    <td width="50%" valign="top"><img src="docs/story/phase-06.svg" alt="Phase 06: In your pocket. 11.06.2026, 3 commits. A mobile-only layout: compact navigation, sideways-scrolling brackets, no page overflow. Why: “Most players were on consoles, so the phone was the easiest way to follow the tournament and enter results.”" width="100%"></td>
  </tr>
  <tr>
    <td width="50%" valign="top"><img src="docs/story/phase-07.svg" alt="Phase 07: Running the real night. 12.06.2026, 6 commits. A supervisor role, one queue of scores to validate, walkover for missing results, renaming and team reassignment. Why: “I couldn&#x27;t always be there as the admin. If someone rage-quit or a score needed fixing, someone had to step in. So whoever creates a tournament becomes its supervisor, and can give that role to people they trust.”" width="100%"></td>
    <td width="50%" valign="top"><img src="docs/story/phase-08.svg" alt="Phase 08: Ready to show. September 2026, 12 commits. Demo data with invented players, a configurable admin, the single-leg bracket fix, and this README." width="100%"></td>
  </tr>
</table>

<details>
<summary>The 8 phases as plain text</summary>

- **01 · Foundation** (11.06.2026 · 5 commits). The whole app in one go: accounts, tournaments with invite links, league and knockout fixtures, team assignment and the live table. Then Railway deploy prep, removing players and assigning teams by hand. *“The standings had to be visible to everyone, all the time, so nobody had to ask one person anymore.”*
- **02 · Fair play** (11.06.2026 · 1 commit). A submitted score stays pending until the opponent validates or rejects it. *“Between friends, someone always tries a joke: a wrong score, or 1000 goals. So a result only counts once the opponent confirms it.”*
- **03 · Finding your way** (11.06 – 12.06.2026 · 8 commits). The full bracket with future rounds as TBD, then leg and matchday filters that open on your next match. *“Nobody should have to dig through everyone else's matches to find their own. Your next match comes first, and the rest stays organised.”*
- **04 · For everyone watching** (11.06.2026 · 5 commits). A spectator view of the live table and bracket, even without an invite link, and banners for players and for people waiting. *“Some friends weren't playing this time but still wanted to follow the tournament while waiting for the next one. So they got their own view.”*
- **05 · The big moment** (11.06.2026 · 4 commits). A full-screen champion celebration with trophy and confetti, and the Squad Sheet next to the bracket. *“The winner should feel special. After a whole tournament, the end deserves more than a line in a table.”*
- **06 · In your pocket** (11.06.2026 · 3 commits). A mobile-only layout: compact navigation, sideways-scrolling brackets, no page overflow. *“Most players were on consoles, so the phone was the easiest way to follow the tournament and enter results.”*
- **07 · Running the real night** (12.06.2026 · 6 commits). A supervisor role, one queue of scores to validate, walkover for missing results, renaming and team reassignment. *“I couldn't always be there as the admin. If someone rage-quit or a score needed fixing, someone had to step in. So whoever creates a tournament becomes its supervisor, and can give that role to people they trust.”*
- **08 · Ready to show** (September 2026 · 12 commits). Demo data with invented players, a configurable admin, the single-leg bracket fix, and this README.

</details>

---

<a name="features"></a>
<p><img src="docs/zones/features.svg" alt="Features" width="100%"></p>

Built around the actual game night: someone sets up a tournament, everybody plays, and nobody wants to argue about scores afterwards.

<table>
  <tr>
    <td width="33%" align="center" valign="top"><img src="docs/screenshots/grid/teams.png" alt="Fair team assignment"><br><b>Fair team assignment</b><br><sub>the strongest matching FC 26 teams, one per player</sub></td>
    <td width="33%" align="center" valign="top"><img src="docs/screenshots/grid/validation.png" alt="Score validation"><br><b>Score validation</b><br><sub>a result counts once the opponent confirms it</sub></td>
    <td width="33%" align="center" valign="top"><img src="docs/screenshots/grid/bracket.png" alt="Live bracket"><br><b>Live bracket</b><br><sub>every round up to the champion</sub></td>
  </tr>
  <tr>
    <td width="33%" align="center" valign="top"><img src="docs/screenshots/grid/next_match.png" alt="Your next match first"><br><b>Your next match first</b><br><sub>leg and matchday filters instead of one long list</sub></td>
    <td width="33%" align="center" valign="top"><img src="docs/screenshots/grid/spectator.png" alt="Spectator mode"><br><b>Spectator mode</b><br><sub>follow the tournament without playing in it</sub></td>
    <td width="33%" align="center" valign="top"><img src="docs/screenshots/grid/champion.png" alt="Champion celebration"><br><b>Champion celebration</b><br><sub>trophy and confetti when the final is decided</sub></td>
  </tr>
</table>

**Also in the app:** knockout rounds that advance by themselves · banners for players and for people waiting · works on a phone · invite links · league or knockout, 1 or 2 legs · supervisors, rename, walkover · activity log of every action.

### More about each feature

<details>
<summary><b>Fair team assignment</b> · the strongest matching FC 26 teams, one per player</summary>
<br>
<p align="center"><img src="docs/screenshots/teams_preview.png" alt="Assign teams step with filters and the six strongest matching teams" width="600"></p>

Filter the 136 teams by clubs or national teams, star range and league, preview the result, then **Auto assign**. Each player gets one team, all taken from the top of the filtered pool, so the gap between the weakest and the strongest team stays small. You can also assign by hand, or reassign a team later from the Manage page.
</details>

<details>
<summary><b>Score validation</b> · a result only counts once the opponent confirms it</summary>
<br>
<p align="center"><img src="docs/screenshots/validation.png" alt="Player view: a proposed 3-2 with Validate and Reject buttons" width="820"><br>
<sub><b>The opponent</b> sees the proposed score and validates or rejects it</sub></p>
<p align="center"><img src="docs/screenshots/validation_queue.png" alt="Manage page: the queue of scores awaiting validation" width="620"><br>
<sub><b>Supervisors</b> get one queue of everything still waiting</sub></p>

One player enters the score, and it stays *pending*. Only the other player can accept it (you can't confirm your own), and a rejected score is cleared so both can resubmit. Supervisors can confirm or enter any score when someone has already gone home.
</details>

<details>
<summary><b>Knockout that runs itself</b> · the next round appears when the last result is in</summary>
<br>
<p align="center"><img src="docs/screenshots/cup_table.png" alt="Table page of a knockout cup: semi-finals decided, final pending" width="720"></p>

As soon as the last tie of a round is confirmed, the server works out the winners (aggregate score over two legs, away goals as tie-breaker) and creates the next round. Nobody has to press "next round". If a match never gets played, the super-admin can force the round forward with a 0-0 walkover.
</details>

<details>
<summary><b>Live bracket</b> · from the first round to the champion, future rounds as TBD</summary>
<br>
<p align="center"><img src="docs/screenshots/bracket.png" alt="Full bracket: quarter-finals, semi-finals, final and champion box, with the Squad Sheet on the right" width="820"></p>

Every tie shows leg 1, leg 2 and the aggregate with the player who goes through. Rounds that don't exist yet are already drawn as TBD, so everyone sees how far it is to the final. Single-leg cups show one game per tie.
</details>

<details>
<summary><b>Your next match first</b> · leg and matchday filters instead of one long list</summary>
<br>
<p align="center"><img src="docs/screenshots/match_filters.png" alt="Matches page: your next pending match selected, all matches filtered by leg and matchday" width="820"></p>

A two-leg league with eight players has 56 games. So the Matches page opens on *your* next pending match and filters everything else by leg and matchday. The same filter works on the Manage page.
</details>

<details>
<summary><b>Spectator mode</b> · people who aren't playing can still follow along</summary>
<br>
<p align="center"><img src="docs/screenshots/spectator.png" alt="Table page for someone not in the tournament, with the 'Patience… you're next' banner" width="720"></p>

Everyone who logs in lands on the live tournament, even without the invite link. People who aren't in it see the table and the bracket under a *„Patience… you're next“* banner instead of an empty page.
</details>

<details>
<summary><b>Banners that know who you are</b> · a cheer for players, patience for everyone else</summary>
<br>
<p align="center"><img src="docs/screenshots/standings.png" alt="League table with the 'You're in the arena' banner and the logged-in player highlighted" width="720"></p>

Players get *„You're in the arena, &lt;name&gt;!“* and their own row highlighted. The banner depends on whether you actually play in this tournament, not on your role, so an admin who plays gets the cheer too.
</details>

<details>
<summary><b>Squad Sheet and champion celebration</b> · who drives which team, and a proper finish</summary>
<br>
<p align="center"><img src="docs/screenshots/champion.png" alt="Champion overlay with trophy, confetti and the winner's name" width="720"></p>

Next to the bracket, the Squad Sheet lists every player with their team and stars, and the chips shrink as the field grows. When the final is decided, everyone gets a full-screen trophy with confetti, shown once per tournament on each device.
</details>

<details>
<summary><b>Works on a phone</b> · mobile-only layout, desktop untouched</summary>
<br>
<p align="center"><img src="docs/screenshots/mobile_standings.png" alt="League table on a phone" width="300"></p>

On a phone the navigation wraps into a scrollable row, long names are cut off cleanly, and the bracket on the Table page scrolls sideways. All of this sits in one `@media` block, so the desktop layout is untouched.
</details>

<sub>All names in screenshots and the demo are invented (`seed_demo.py`). Team names come from the FC 26 player dataset.</sub>

---

<a name="learned"></a>
<p><img src="docs/zones/learned.svg" alt="What I learned in practice" width="100%"></p>

Where topics from the module *Betriebssysteme und Verteilte Systeme 2* (TH Köln) show up in this code. Each excerpt is the smallest piece that shows the idea, with one comment per line; the link under it leads to the full code.

<details>
<summary><img src="docs/labels/concept-client-server.svg" align="absmiddle" alt="Client-server with a REST-style JSON API · the browser asks, Flask answers in JSON"></summary>
<br>

**In plain words.** The browser is the client and only draws. The Flask app is the server and only answers. Every page asks for its data with an HTTP request to a URL that names one thing (the matches of tournament 2, one match, one tournament) and gets JSON back. It's REST-*style* rather than strict REST, because a few URLs like `/start` or `/advance-round` name an action, not a thing.

The client, in the browser:
```js
const res  = await fetch(url, opts);    // CLIENT: send the HTTP request, wait for the response
const data = await res.json();          // the body is JSON -> turn it into a JS object
```
The server, in Flask:
```python
@routes_bp.route('/api/tournament/<int:tid>/matches')   # a RESOURCE: the matches of one tournament. GET only
def get_matches(tid):                                    # tid comes out of the URL, already an int
    # ... login check and database query (see full code)
        return jsonify([dict(r) for r in rows])          # rows -> list of dicts -> JSON body, status 200
```
Full code: [`static/app.js` lines 6–21](static/app.js#L6-L21) · [`routes.py` lines 422–442](routes.py#L422-L442)

> **Why I did it this way:** Everyone needed to see the same standings. One server holds the only true version of the tournament, and every phone or PC just asks it. Nobody has to install anything, a browser is enough.
</details>

<details>
<summary><img src="docs/labels/concept-stateless.svg" align="absmiddle" alt="Stateless HTTP with a session cookie · the server forgets you after every request"></summary>
<br>

**In plain words.** HTTP has no memory: every request arrives on its own. So at login Flask writes the user's ID into the **session**, which travels to the browser as a signed cookie. The browser sends it back with every request, and every protected route reads it again. The server keeps nothing in between.

```python
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))   # SIGNS the cookie so the client cannot forge it
session['user_id'] = user['id']          # LOGIN: the id goes into the session -> the signed cookie
if 'user_id' not in session:             # EVERY request: read the cookie again, nothing was remembered
    return jsonify({'error': 'Not logged in'}), 401   # no cookie -> 401, not a silent 200
```
Full code: [`app.py` line 9](app.py#L9) · [`auth.py` lines 34–50](auth.py#L34-L50) · [`routes.py` lines 19–22](routes.py#L19-L22)

> **Why I did it this way:** HTTP forgets who you are after every request. The session cookie reminds the server, so every player has their own profile and can only enter their own results.
</details>

<details>
<summary><img src="docs/labels/concept-status-codes.svg" align="absmiddle" alt="Explicit HTTP status codes · every failure says what kind of failure it is"></summary>
<br>

**In plain words.** The status code lets the client react without reading the error text. Submitting a score checks four things in order, and each "no" has its own code. Without the explicit number, Flask would answer 200 and the error would look like a success.

```python
# 1. are both scores there?          no -> 400: the request itself is incomplete
if hs is None or as_ is None: return jsonify({'error': 'Both scores required'}), 400
# 2. does the match exist?           no -> 404: request fine, the thing is not there
if not match: return jsonify({'error': 'Match not found'}), 404
# 3. are you in this tournament?     no -> 403: you are known, but not allowed
if not my_part: return jsonify({'error': 'Not in this tournament'}), 403
# 4. does it fit the current state?  no -> 409: the result is already official
if match['home_score'] is not None: return jsonify({'error': 'Result already validated'}), 409
```
Full code: [`routes.py` lines 446–481](routes.py#L446-L481)

> **Why I did it this way:** When something goes wrong, the page needs to know what happened: not allowed, not found, or bad input. Clear status codes let it show a clear message instead of just failing.
</details>

<details>
<summary><img src="docs/labels/concept-idempotency.svg" align="absmiddle" alt="Idempotency · joining twice is the same as joining once"></summary>
<br>

**In plain words.** A request is *idempotent* if sending it twice leaves the server in the same state as sending it once. `POST` normally isn't, but joining a tournament is built that way: the second time, the server finds you already in and changes nothing. A double tap on a phone does no harm.

```python
# look up: is this user already in this tournament?   (None = not yet)
already = db.execute('SELECT id FROM participants WHERE tournament_id=? AND user_id=?', (tid, session['user_id'])).fetchone()
# yes -> answer ok and change NOTHING: the 2nd request ends here
if already: return jsonify({'ok': True, 'message': 'Already joined'})
# ... (is the tournament full? see full code)
# only the FIRST request gets here and writes the row
db.execute('INSERT INTO participants (tournament_id, user_id) VALUES (?,?)', (tid, session['user_id']))
```
Full code: [`routes.py` lines 130–149](routes.py#L130-L149)

> **Why I did it this way:** Most players were on their phones, sometimes with a bad connection, and people tap twice. Sending the same action again must not count it twice.
</details>

<details>
<summary><img src="docs/labels/architecture.svg" align="absmiddle" alt="Architecture · how the browser, Flask and SQLite fit together"></summary>
<br>

```mermaid
flowchart LR
  subgraph Browser
    P["HTML pages<br/>(Jinja2 templates)"] --- JS["app.js<br/>fetch() helper"]
  end
  subgraph Server["Flask app"]
    AU["auth.py<br/>login · session"]
    RT["routes.py<br/>pages + JSON API"]
    TO["tournament.py<br/>fixtures · standings · winners"]
    TE["teams.py<br/>filters · auto-assign"]
    AC["activity.py<br/>event log"]
  end
  DB[("SQLite<br/>tournament.db")]
  TJ[("data/teams.json<br/>136 teams")]
  JS -->|"JSON over HTTP + session cookie"| AU
  JS -->|"JSON over HTTP + session cookie"| RT
  RT --> TO
  RT --> TE
  RT --> AC
  AU --> DB
  RT --> DB
  AC --> DB
  TE --> TJ
```
</details>

---

<a name="run"></a>
<p><img src="docs/zones/run.svg" alt="Run it yourself" width="100%"></p>

<a name="quick-start"></a>
<p><img src="docs/labels/quick-start.svg" alt="Quick start · three commands"></p>

With Python 3.11 or newer (on Windows, double-clicking **`run_local.bat`** does all of this for you):

```bash
git clone https://github.com/WaliGl0RY/fc26-tournament.git && cd fc26-tournament
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000. The database (`tournament.db`) is created on first start.

<details>
<summary><img src="docs/labels/demo-data.svg" align="absmiddle" alt="Demo data · invented players and three tournaments to click through"></summary>
<br>

Run `python seed_demo.py` once, before `python app.py`.

`seed_demo.py` adds eight invented players (`nova`, `blaze`, `pixel` …) and an `admin` account, all with PIN **`0000`**, plus three tournaments: a league with one score waiting for validation, a knockout cup before its final, and a finished cup. Log in as `nova` to land on the live cup. The script also prints one invite link per tournament: log out, open a link, log in, and that tournament is selected. It refuses to touch a database that already has users.
</details>

<details>
<summary><img src="docs/labels/settings.svg" align="absmiddle" alt="Settings · environment variables, all optional"></summary>
<br>

| Variable | Default | What it does |
|---|---|---|
| `ADMIN_USERNAME` | `admin` | The account that sees the activity log, assigns supervisors, renames tournaments and can override any score |
| `SECRET_KEY` | random at every start | Signs the session cookie. **Set it**, or every restart logs everyone out |
| `DB_PATH` | `./tournament.db` | Where the SQLite file lives |
| `FLASK_DEBUG` | `false` | `true` for auto-reload while developing |

```bash
ADMIN_USERNAME=alex SECRET_KEY=change-me python app.py          # PowerShell: $env:ADMIN_USERNAME="alex"; python app.py
```

> Logins use a name and a 4-digit PIN, made for a group of friends on one evening. See [Security scope](#security-scope).

**Team data:** `data/teams.json` ships with the repo. To rebuild it from the Kaggle FC 26 player dataset: `python scripts/build_teams_json.py --csv players.csv`.
</details>

<details>
<summary><img src="docs/labels/deployment.svg" align="absmiddle" alt="Deployment · how it ran on Railway"></summary>
<br>

The app ran on **Railway**. Railway built the repository into a container image and ran it as a container. Three small files in the repo were all it needed: `requirements.txt` (Flask and gunicorn), `.python-version` (Python 3.11) and the `Procfile`, whose start command `gunicorn app:app` ran the app with gunicorn instead of Flask's development server.

**The database lived on a volume.** A container's own files are thrown away on every redeploy, and a SQLite file stored there would have gone with them. A Railway volume was mounted into the container instead, with `DB_PATH` pointing to the database file inside it, so the data survived every redeploy.

This setup was one instance by design: one container, one SQLite file on one volume. The app is offline now.
</details>

<details>
<summary><img src="docs/labels/project-structure.svg" align="absmiddle" alt="Project structure · where everything lives"></summary>
<br>

```
fc26-tournament/
├── app.py              ← Flask app: secret key, blueprints, database init
├── auth.py             ← register · login · logout · /api/me (session)
├── routes.py           ← pages + JSON API: tournaments, matches, validation, logs
├── tournament.py       ← round-robin, knockout pairs, aggregate winners, standings
├── teams.py            ← team filters + auto-assign
├── database.py         ← SQLite schema + in-place migrations
├── activity.py         ← event log helper
├── seed_demo.py        ← demo data with invented players
├── data/teams.json     ← 136 FC 26 clubs and national teams
├── scripts/            ← build_teams_json.py (rebuilds teams.json)
├── templates/          ← login · dashboard (Table) · matches · admin (Create) · manage · logs
├── static/             ← style.css · app.js
├── docs/               ← README images
├── run_local.bat       ← Windows one-click start
└── Procfile            ← gunicorn app:app
```
</details>

---

<a name="notes"></a>
<p><img src="docs/zones/notes.svg" alt="Honest notes" width="100%"></p>

<a name="security-scope"></a>
<p><img src="docs/labels/security-scope.svg" alt="Security scope"></p>

I built this for a small group of friends who trust each other. Every player sets their own simple PIN, so everyone has their own profile. It keeps profiles apart; it doesn't keep attackers out. It isn't hardened, so don't deploy it publicly as it is.

<a name="known-limitations"></a>
<p><img src="docs/labels/known-limitations.svg" alt="Known limitations"></p>

- **Race on round advance:** two confirmations at the same moment could create the next knockout round twice (not with the single worker it ran on).
- **User input isn't escaped** when the pages display it.
- **Logins are simple on purpose:** 4-digit PINs, stored in plain text, with no attempt limit.
- **Some bad input returns 500** instead of 400.
- **One SQLite file, one server:** no built-in backup, no running several instances.
- **Knockout Matches page on narrow screens** starts partly off-screen below about 900px.
- **No automated tests:** everything was tested by hand and by playing.

<a name="license"></a>
<p><img src="docs/labels/license.svg" alt="License"></p>

[MIT](LICENSE)

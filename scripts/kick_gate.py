"""Kickoff gate for Fri/Sat (and other non-standard) cron runs.
Reads this week's ESPN schedule and writes run=1 to $GITHUB_OUTPUT only when an
un-started NFL game kicks off within the next 75 minutes (covers the ~60/30/10-min pulls)."""
import json, os, sys, urllib.request
from datetime import datetime, timezone, timedelta
SB = 'https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard'
now = datetime.now(timezone.utc); run = 0; why = 'no kickoff in next 75 min'
try:
    d = json.load(urllib.request.urlopen(urllib.request.Request(SB, headers={'User-Agent': 'Mozilla/5.0'}), timeout=20))
    ev = d.get('events') if isinstance(d, dict) else None
    if not ev:
        run = 1; why = 'ESPN scoreboard has no events; pulling anyway'
    else:
        for e in ev:
            try:
                k = datetime.fromisoformat(e['date'].replace('Z', '+00:00'))
                if k.tzinfo is None: raise ValueError('naive date')
            except Exception as x:
                run = 1; why = f'malformed ESPN event {e.get("shortName") if isinstance(e, dict) else e!r} ({x}); pulling anyway'; break
            if timedelta(0) <= k - now <= timedelta(minutes=75):
                run = 1; why = f"{e.get('shortName')} kicks {k:%Y-%m-%d %H:%MZ}"; break
except Exception as x:
    run = 1; why = f'ESPN schedule unavailable ({x}); pulling anyway'
print(why)
with open(os.environ.get('GITHUB_OUTPUT', os.devnull), 'a') as f: f.write(f'run={run}\n')

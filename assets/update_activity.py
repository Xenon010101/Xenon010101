"""Fetch a GitHub activity snapshot, validate it, then render local profile cards.

Only Python's standard library is needed. Failed fetches or invalid responses
leave the committed snapshot and cards untouched. No tokens are saved or printed.
"""
import argparse
from datetime import date
import json
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from generate import OUT, ROOT, PALETTES, start, end, text

QUERY = '''query ProfileActivity($login: String!) {
  user(login: $login) {
    login
    contributionsCollection {
      startedAt
      endedAt
      totalPullRequestContributions
      totalPullRequestReviewContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}'''
BEGIN = '<!-- ACTIVITY:START -->'
END = '<!-- ACTIVITY:END -->'


def natural(value):
    if type(value) is not int or value < 0:
        raise ValueError('GitHub returned an invalid contribution count.')
    return value


def normalize(response, login):
    if response.get('errors'):
        raise ValueError('GitHub returned GraphQL errors; keeping the saved snapshot.')
    user = response['data']['user']
    if not user or user['login'].lower() != login.lower():
        raise ValueError('GitHub returned no matching user.')
    collection = user['contributionsCollection']
    calendar = collection['contributionCalendar']
    snapshot = {
        'login': user['login'],
        'source': 'https://github.com/' + user['login'],
        'period': 'GitHub past-year contribution window',
        'from': collection['startedAt'][:10],
        'through': collection['endedAt'][:10],
        'updated': date.today().isoformat(),
        'contributions': calendar['totalContributions'],
        'pull_requests': collection['totalPullRequestContributions'],
        'reviews': collection['totalPullRequestReviewContributions'],
        'weeks': [
            [{'date': day['date'], 'count': day['contributionCount']}
             for day in week['contributionDays']]
            for week in calendar['weeks']
        ],
    }
    validate(snapshot)
    return snapshot


def validate(snapshot):
    if not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})', snapshot['login']):
        raise ValueError('Invalid GitHub username.')
    for key in ['contributions', 'pull_requests', 'reviews']:
        natural(snapshot[key])
    first = date.fromisoformat(snapshot['from'])
    last = date.fromisoformat(snapshot['through'])
    date.fromisoformat(snapshot['updated'])
    if not 0 <= (last-first).days <= 371:
        raise ValueError('Unexpected contribution window.')
    weeks = snapshot['weeks']
    if not isinstance(weeks, list) or not 1 <= len(weeks) <= 54:
        raise ValueError('Missing or incomplete contribution calendar.')
    days = []
    total = 0
    for week in weeks:
        if not isinstance(week, list) or not 1 <= len(week) <= 7:
            raise ValueError('Invalid calendar week.')
        for day in week:
            parsed = date.fromisoformat(day['date'])
            if not first <= parsed <= last:
                raise ValueError('Calendar date outside the contribution window.')
            days.append(parsed)
            total += natural(day['count'])
    if len(set(days)) != len(days) or days != sorted(days):
        raise ValueError('Duplicate or out-of-order calendar dates.')
    if len(days) != (days[-1]-days[0]).days+1:
        raise ValueError('The calendar is missing days.')
    if total != snapshot['contributions']:
        raise ValueError('Calendar totals do not match; keeping the saved snapshot.')


def fetch(login):
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if not token:
        raise ValueError('Set GH_TOKEN or run this script through GitHub Actions.')
    request = Request('https://api.github.com/graphql',
        data=json.dumps({'query': QUERY, 'variables': {'login': login}}).encode(),
        headers={'Authorization': 'Bearer ' + token,
                 'User-Agent': 'Xenon-Profile-Activity',
                 'Content-Type': 'application/json'}, method='POST')
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def summary(snapshot):
    return (f"{snapshot['contributions']:,} contributions, "
            f"{snapshot['pull_requests']:,} pull requests opened, "
            f"and {snapshot['reviews']:,} reviews in GitHub's past-year window. "
            f"Updated {snapshot['updated']}.")


def render(snapshot, theme, mobile=False):
    p = PALETTES[theme]
    w, h = (640, 460) if mobile else (1200, 310)
    s = start(w, h, p, 'Open-source activity', summary(snapshot))
    s += f'<rect width="{w}" height="3" fill="url(#spectrum)"/>'
    s += text(32 if mobile else 40, 42, 'OPEN SOURCE / PAST YEAR',
              21 if mobile else 19, p['muted'], mono=True, spacing=1)
    if mobile:
        s += text(28, 142, f"{snapshot['contributions']:,}", 94, p['cyan'], 700, spacing=-4)
        s += text(32, 181, 'Contributions', 28, p['ink'], 500)
        metrics = [(32, 'pull_requests', 'Pull requests opened'),
                   (346, 'reviews', 'Reviews')]
        for x, key, label in metrics:
            s += text(x, 270, f'{snapshot[key]:,}', 60, p['ink'], 650, spacing=-2)
            s += text(x, 306, label, 23, p['muted'])
        chart_x, chart_y, chart_w, chart_h = 32, 392, 576, 46
        footer_y = 434
    else:
        metrics = [(40, 'contributions', 'Contributions'),
                   (454, 'pull_requests', 'Pull requests opened'),
                   (868, 'reviews', 'Reviews')]
        for x, key, label in metrics:
            s += text(x-3, 144, f'{snapshot[key]:,}', 88,
                      p['cyan'] if key == 'contributions' else p['ink'], 650, spacing=-3)
            s += text(x, 182, label, 25, p['muted'])
        for x in [413, 827]:
            s += f'<path d="M{x} 77V184" stroke="{p["line"]}"/>'
        chart_x, chart_y, chart_w, chart_h = 40, 257, 1120, 48
        footer_y = 292
    totals = [sum(day['count'] for day in week) for week in snapshot['weeks']]
    maximum = max(totals) or 1
    step = chart_w / len(totals)
    for i, count in enumerate(totals):
        bar_h = chart_h * count / maximum if count else 2
        s += (f'<rect x="{chart_x+i*step:.2f}" y="{chart_y-bar_h:.2f}" '
              f'width="{max(step-4, 2):.2f}" height="{bar_h:.2f}" rx="2" '
              f'fill="{p["cyan"] if count else p["line"]}" opacity="{.4+.6*count/maximum:.2f}">'
              f'<title>Week of {snapshot["weeks"][i][0]["date"]}: {count:,} contributions</title></rect>')
    s += text(chart_x, footer_y, 'WEEKLY ACTIVITY', 17 if mobile else 18, p['muted'], mono=True)
    s += text(w-32 if mobile else w-40, footer_y,
              'UPDATED ' + snapshot['updated'], 17 if mobile else 18,
              p['muted'], mono=True, extra='text-anchor="end"')
    return s + end(w, h, p)


def markdown(snapshot):
    return f'''{BEGIN}
<p>
<picture>
  <source media="(prefers-color-scheme: dark) and (max-width: 600px)" srcset="assets/activity-mobile-dark.svg">
  <source media="(max-width: 600px)" srcset="assets/activity-mobile-light.svg">
  <source media="(prefers-color-scheme: dark)" srcset="assets/activity-dark.svg">
  <img src="assets/activity-light.svg" width="1200" alt="{summary(snapshot)}">
</picture>
</p>

<sub>GitHub's past-year window · {snapshot['from']} to {snapshot['through']} · <a href="assets/activity.json">Snapshot data</a></sub>
{END}'''


def save(snapshot):
    validate(snapshot)
    readme = ROOT / 'README.md'
    content = readme.read_text(encoding='utf-8')
    if content.count(BEGIN) != 1 or content.count(END) != 1 or content.index(END) < content.index(BEGIN):
        raise ValueError('Activity markers are missing or ambiguous; no files changed.')
    # Prepare every artifact before changing files; a failed fetch never reaches this point.
    files = {OUT / f'activity-{"mobile-" if mobile else ""}{theme}.svg': render(snapshot, theme, mobile)
             for theme in PALETTES for mobile in [False, True]}
    files[OUT / 'activity.json'] = json.dumps(snapshot, indent=2) + '\n'
    files[readme] = content[:content.index(BEGIN)] + markdown(snapshot) + content[content.index(END)+len(END):]
    for path, value in files.items():
        path.write_text(value, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--login', default='Xenon010101')
    source = parser.add_mutually_exclusive_group()
    source.add_argument('--response', type=Path, help='Use a saved GraphQL response instead of the network.')
    source.add_argument('--offline', action='store_true', help='Re-render the existing activity.json without changing its date.')
    args = parser.parse_args()
    try:
        if args.offline:
            snapshot = json.loads((OUT / 'activity.json').read_text(encoding='utf-8'))
        else:
            response = json.loads(args.response.read_text(encoding='utf-8-sig')) if args.response else fetch(args.login)
            snapshot = normalize(response, args.login)
        save(snapshot)
    except (HTTPError, URLError, TimeoutError, OSError, KeyError, TypeError, ValueError) as error:
        # Do not print response bodies or authentication headers.
        print(f'Activity refresh failed ({type(error).__name__}). Existing snapshot retained.', file=sys.stderr)
        return 1
    print(summary(snapshot))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

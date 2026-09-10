"""Validate snapshot handling and ensure failures cannot replace published data."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from xml.etree import ElementTree

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'assets'))
import update_activity as activity


def response():
    return {'data': {'user': {'login': 'Xenon010101', 'contributionsCollection': {
        'startedAt': '2026-09-01T00:00:00Z', 'endedAt': '2026-09-07T23:59:59Z',
        'totalPullRequestContributions': 3, 'totalPullRequestReviewContributions': 1,
        'contributionCalendar': {'totalContributions': 7, 'weeks': [{'contributionDays': [
            {'date': f'2026-09-{day:02}', 'contributionCount': 1} for day in range(1, 8)
        ]}]},
    }}}}


class ActivityTests(unittest.TestCase):
    def test_counts_and_real_weekly_data(self):
        snapshot = activity.normalize(response(), 'Xenon010101')
        self.assertEqual(snapshot['contributions'], 7)
        self.assertEqual(snapshot['pull_requests'], 3)
        self.assertEqual(snapshot['reviews'], 1)
        for theme in activity.PALETTES:
            for mobile in [False, True]:
                svg = activity.render(snapshot, theme, mobile)
                ElementTree.fromstring(svg)
                self.assertIn('Week of 2026-09-01: 7 contributions', svg)

    def test_zero_activity_is_valid(self):
        data = response()
        c = data['data']['user']['contributionsCollection']
        c['totalPullRequestContributions'] = c['totalPullRequestReviewContributions'] = 0
        c['contributionCalendar']['totalContributions'] = 0
        for day in c['contributionCalendar']['weeks'][0]['contributionDays']:
            day['contributionCount'] = 0
        snapshot = activity.normalize(data, 'Xenon010101')
        ElementTree.fromstring(activity.render(snapshot, 'dark', True))
        self.assertEqual(snapshot['contributions'], 0)

    def test_graphql_errors_and_wrong_user_fail(self):
        for data, login in [({'errors': [{'message': 'Rate limited'}]}, 'Xenon010101'),
                            (response(), 'AnotherUser'), ({'data': {'user': None}}, 'Xenon010101')]:
            with self.subTest(login=login, data=data):
                with self.assertRaises(ValueError):
                    activity.normalize(data, login)

    def test_invalid_counts_and_calendar_fail(self):
        valid = activity.normalize(response(), 'Xenon010101')
        for value in [-1, True, '7', None]:
            data = copy.deepcopy(valid)
            data['contributions'] = value
            with self.assertRaises(ValueError):
                activity.validate(data)
        for mutation in [
            lambda s: s.update(contributions=8),
            lambda s: s.update(weeks=[]),
            lambda s: s['weeks'][0][1].update(date='2026-09-01'),
            lambda s: s['weeks'][0].pop(2),
        ]:
            data = copy.deepcopy(valid)
            mutation(data)
            with self.assertRaises(ValueError):
                activity.validate(data)

    def test_save_changes_only_activity_block(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            out = root / 'assets'
            out.mkdir()
            original = f'Keep this introduction.\n{activity.BEGIN}\nold card\n{activity.END}\nKeep this footer.\n'
            (root / 'README.md').write_text(original, encoding='utf-8')
            with patch.object(activity, 'ROOT', root), patch.object(activity, 'OUT', out):
                activity.save(activity.normalize(response(), 'Xenon010101'))
            content = (root / 'README.md').read_text(encoding='utf-8')
            self.assertTrue(content.startswith('Keep this introduction.\n'))
            self.assertTrue(content.endswith('\nKeep this footer.\n'))
            self.assertEqual(len(list(out.iterdir())), 5)

    def test_missing_markers_write_nothing(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            out = root / 'assets'
            out.mkdir()
            (root / 'README.md').write_text('No markers.', encoding='utf-8')
            with patch.object(activity, 'ROOT', root), patch.object(activity, 'OUT', out):
                with self.assertRaises(ValueError):
                    activity.save(activity.normalize(response(), 'Xenon010101'))
            self.assertEqual(list(out.iterdir()), [])
            self.assertEqual((root / 'README.md').read_text(), 'No markers.')

    def test_network_failure_never_calls_save(self):
        with patch.object(sys, 'argv', ['update_activity.py']), \
             patch.object(activity, 'fetch', side_effect=HTTPError('https://api.github.com/graphql', 403, 'Forbidden', {}, None)), \
             patch.object(activity, 'save') as save:
            self.assertEqual(activity.main(), 1)
            save.assert_not_called()

    def test_offline_render_retains_date(self):
        snapshot = activity.normalize(response(), 'Xenon010101')
        snapshot['updated'] = '2026-09-08'
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder)
            (out / 'activity.json').write_text(json.dumps(snapshot), encoding='utf-8')
            with patch.object(sys, 'argv', ['update_activity.py', '--offline']), \
                 patch.object(activity, 'OUT', out), patch.object(activity, 'save') as save:
                self.assertEqual(activity.main(), 0)
                self.assertEqual(save.call_args.args[0]['updated'], '2026-09-08')


if __name__ == '__main__':
    unittest.main()

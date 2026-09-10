#!/usr/bin/env python3
"""Resolve every project in the local manifests against GitHub.

For each <project>, the pinned revision must be a full commit id that exists in
the repository and lies on the branch named by `upstream`. The check also
reports whether that branch has moved past the pin. Exit status is 1 if any
project fails.

Needs an authenticated GitHub CLI, because some repositories are private.
Set GH=/path/to/gh when `gh` is not on PATH.

Usage: python3 check.py [manifest.xml ...]   (default: every *.xml here)
"""
import glob
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

GH = os.environ.get('GH', 'gh')
HERE = os.path.dirname(os.path.abspath(__file__))
SHA = re.compile(r'^[0-9a-f]{40}$')


def api(path):
    r = subprocess.run([GH, 'api', path], capture_output=True, encoding='utf-8')
    return json.loads(r.stdout) if r.returncode == 0 else None


def check(project, remotes):
    path, repo = project.get('path'), project.get('name')
    rev, upstream = project.get('revision', ''), project.get('upstream')
    if remotes.get(project.get('remote')) != 'https://github.com':
        return False, 'remote is not https://github.com, cannot resolve'
    if not SHA.match(rev):
        return False, f'revision {rev!r} is not a full commit id'
    if not upstream:
        return False, 'no upstream branch named'
    commit = api(f'repos/{repo}/commits/{rev}')
    if not commit or commit.get('sha') != rev:
        return False, f'commit {rev[:12]} not found in {repo}'
    # base...head: "identical" or "ahead" means the pin is on the branch.
    cmp = api(f'repos/{repo}/compare/{rev}...{upstream}')
    if not cmp:
        return False, f'branch {upstream!r} not found in {repo}'
    status, ahead = cmp.get('status'), cmp.get('ahead_by', 0)
    if status == 'identical':
        return True, f'{repo}@{rev[:12]} is the tip of {upstream}'
    if status == 'ahead':
        return True, f'{repo}@{rev[:12]} is on {upstream}, which is {ahead} commit(s) ahead'
    return False, f'{repo}@{rev[:12]} is not on {upstream} (compare status {status})'


def main(files):
    failed = 0
    for f in files:
        root = ET.parse(f).getroot()
        remotes = {r.get('name'): r.get('fetch', '').rstrip('/') for r in root.iter('remote')}
        print(os.path.basename(f))
        for project in root.iter('project'):
            ok, message = check(project, remotes)
            failed += not ok
            print(f"  {'OK  ' if ok else 'FAIL'} {project.get('path')}: {message}")
    print('resolved' if not failed else f'{failed} project(s) failed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:] or sorted(glob.glob(os.path.join(HERE, '*.xml')))))

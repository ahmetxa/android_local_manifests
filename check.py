#!/usr/bin/env python3
"""Resolve every project in the local manifests against its host.

For each <project>, the pinned revision must be a full commit id that exists in
the repository and lies on the branch named by `upstream`. GitHub projects
resolve through the GitHub CLI, GitLab projects through GitLab's public API.
The check also reports whether that branch has moved past the pin.

AOSPA's `lunch` runs vendor/aospa/build/tools/barista.py, which writes the
device's beans (vendor/aospa/products/ishtar/beans.xml and its includes) into
.repo/local_manifests/baristablend.xml. Local manifests load in alphabetical
order, so this file loads after it, and:
  - a <project> at a path the beans also define must follow a
    <remove-project path="..." optional="true">, or repo sees the path twice;
  - every <remove-project> must be optional, because baristablend.xml does not
    exist yet at the first sync, and must be followed by a <project> at the
    same path, so no dependency is dropped without a pinned replacement.

Exit status is 1 if anything fails.

Needs an authenticated GitHub CLI, because some repositories are private.
Set GH=/path/to/gh when `gh` is not on PATH. BEANS_REF selects the
AOSPA/android_vendor_aospa revision the beans are read from (default: beryl).

Usage: python3 check.py [manifest.xml ...]   (default: every *.xml here)
"""
import glob
import json
import os
import posixpath
import re
import subprocess
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

GH = os.environ.get('GH', 'gh')
BEANS_REF = os.environ.get('BEANS_REF', 'beryl')
BEANS = 'products/ishtar/beans.xml'
HERE = os.path.dirname(os.path.abspath(__file__))
SHA = re.compile(r'^[0-9a-f]{40}$')


def gh(path, raw=False):
    accept = ['-H', 'Accept: application/vnd.github.raw'] if raw else []
    r = subprocess.run([GH, 'api', path] + accept, capture_output=True, encoding='utf-8')
    if r.returncode != 0:
        return None
    return r.stdout if raw else json.loads(r.stdout)


def gitlab(repo, path):
    url = 'https://gitlab.com/api/v4/projects/' + urllib.parse.quote(repo, safe='') + path
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.load(r)
    except (OSError, ValueError):
        return None


def resolve_github(repo, rev, upstream):
    commit = gh(f'repos/{repo}/commits/{rev}')
    if not commit or commit.get('sha') != rev:
        return False, f'commit {rev[:12]} not found in {repo}'
    # base...head: "identical" or "ahead" means the pin is on the branch.
    cmp = gh(f'repos/{repo}/compare/{rev}...{upstream}')
    if not cmp:
        return False, f'branch {upstream!r} not found in {repo}'
    status, ahead = cmp.get('status'), cmp.get('ahead_by', 0)
    if status == 'identical':
        return True, f'{repo}@{rev[:12]} is the tip of {upstream}'
    if status == 'ahead':
        return True, f'{repo}@{rev[:12]} is on {upstream}, which is {ahead} commit(s) ahead'
    return False, f'{repo}@{rev[:12]} is not on {upstream} (compare status {status})'


def resolve_gitlab(repo, rev, upstream):
    commit = gitlab(repo, f'/repository/commits/{rev}')
    if not commit or commit.get('id') != rev:
        return False, f'commit {rev[:12]} not found in {repo}'
    branch = gitlab(repo, '/repository/branches/' + urllib.parse.quote(upstream, safe=''))
    if not branch:
        return False, f'branch {upstream!r} not found in {repo}'
    if branch.get('commit', {}).get('id') == rev:
        return True, f'{repo}@{rev[:12]} is the tip of {upstream}'
    refs = gitlab(repo, f'/repository/commits/{rev}/refs?type=branch&per_page=100') or []
    if any(ref.get('name') == upstream for ref in refs):
        return True, f'{repo}@{rev[:12]} is on {upstream}, which has moved past it'
    return False, f'{repo}@{rev[:12]} is not on {upstream}'


HOSTS = {'https://github.com': resolve_github, 'https://gitlab.com': resolve_gitlab}


def beans_paths():
    """Every project path barista blends in for ishtar, or None if unreadable."""
    paths, pending, seen = set(), [BEANS], set()
    while pending:
        name = posixpath.normpath(pending.pop())
        if name in seen:
            continue
        seen.add(name)
        text = gh(f'repos/AOSPA/android_vendor_aospa/contents/{name}?ref={BEANS_REF}', raw=True)
        if text is None:
            return None
        root = ET.fromstring(text.encode('utf-8'))
        pending += [posixpath.join(posixpath.dirname(name), i.get('name')) for i in root.iter('include')]
        paths |= {p.get('path', p.get('name')) for p in root.iter('project')}
    return paths


def check_removal(elem, later):
    path = elem.get('path')
    if not path:
        return False, 'remove-project must name a path, not only a name'
    if elem.get('optional') != 'true':
        return False, 'remove-project needs optional="true"; baristablend.xml does not exist at the first sync'
    if not any(e.tag == 'project' and e.get('path') == path for e in later):
        return False, 'removed without a pinned <project> at that path after it'
    return True, "barista's project is replaced below"


def check(project, remotes, removed, beans):
    path, repo = project.get('path'), project.get('name')
    rev, upstream = project.get('revision', ''), project.get('upstream')
    resolve = HOSTS.get(remotes.get(project.get('remote')))
    if not resolve:
        return False, 'remote is neither https://github.com nor https://gitlab.com, cannot resolve'
    if not SHA.match(rev):
        return False, f'revision {rev!r} is not a full commit id'
    if not upstream:
        return False, 'no upstream branch named'
    if path in beans and path not in removed:
        return False, 'barista also blends in this path; put <remove-project path="..." optional="true"> before it'
    return resolve(repo, rev, upstream)


def main(files):
    beans = beans_paths()
    if beans is None:
        print(f'cannot read AOSPA/android_vendor_aospa {BEANS} at {BEANS_REF}')
        return 1
    failed = 0
    for f in files:
        root = ET.parse(f).getroot()
        remotes = {r.get('name'): r.get('fetch', '').rstrip('/') for r in root.iter('remote')}
        print(os.path.basename(f))
        elements = list(root)
        removed, defined = set(), set()
        for i, elem in enumerate(elements):
            path = elem.get('path') or elem.get('name')
            if elem.tag == 'remove-project':
                ok, message = check_removal(elem, elements[i + 1:])
                if ok:
                    removed.add(path)
                label = f'remove {path}'
            elif elem.tag == 'project':
                if path in defined:
                    ok, message = False, 'path is defined twice in this file'
                else:
                    ok, message = check(elem, remotes, removed, beans)
                defined.add(path)
                label = path
            else:
                continue
            failed += not ok
            print(f"  {'OK  ' if ok else 'FAIL'} {label}: {message}")
    print('resolved' if not failed else f'{failed} element(s) failed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:] or sorted(glob.glob(os.path.join(HERE, '*.xml')))))

#!/usr/bin/env python3
"""cykl-lifecycle 3.0.1. Offline, stdlib-only reader and sole lifecycle writer."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import shlex
import sys
import tempfile
import uuid

OUTPUT_CAP = 16384
NOW_CAP = 4096
INDEX_HEADER = '# DECISIONS\n\nid\tkind\tstatus\tscope\tsupersedes\ttext\n'
REVIEW_KEYS = ('active_facts', 'snapshot_ambiguity', 'issue_urls', 'readers', 'writers', 'privacy')
ID = re.compile(r'[OADL]-[A-Za-z0-9][A-Za-z0-9_-]*\Z')
HASH = re.compile(r'[0-9a-f]{64}\Z')
MARKERS = re.compile(r'^(<<<<<<< |=======\s*$|>>>>>>> )', re.M)
SECRET = re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----|(?:gh[pousr]_[A-Za-z0-9]{20,})|(?:AKIA[A-Z0-9]{16})|(?i:password|secret|api_key)\s*[:=]\s*["\']?[^\s"\']{8,}')
FIXED_CAPS = {'PROJECT_CONFIG.md': 2048, 'docs/NOW.md': NOW_CAP,
              'docs/ROADMAP.md': 4096, 'docs/HANDOFF.md': 512,
              'docs/LESSONS_CANON.md': 512}
NOW_FIELDS = {'schema', 'checkpoint', 'previous_sha256', 'content_sha256', 'parents', 'base',
              'repo', 'branch', 'goal', 'position', 'next', 'preserve', 'work', 'risks',
              'references', 'reconciliation'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def dumps(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def loads(text):
    return json.loads(text, object_pairs_hook=unique_pairs)


def resolve_entry_path(root, relative):
    """Resolve existing components to disk spelling, retaining any missing suffix."""
    root = Path(root)
    rel = Path(relative)
    require(not rel.is_absolute() and '..' not in rel.parts and rel.parts, 'escaping/empty path')
    p = root
    require(not root.is_symlink(), 'symlink root')
    for part in rel.parts:
        candidate = p / part
        require(not candidate.is_symlink(), 'symlink on managed path: ' + str(rel))
        if p.is_dir():
            with os.scandir(p) as entries:
                names = {entry.name: entry for entry in entries}
            if part not in names and candidate.exists():
                # Ask the volume which entry aliases this name; casefold alone is not identity.
                identity = candidate.stat(follow_symlinks=False)
                matches = [name for name, entry in names.items()
                           if os.path.samestat(entry.stat(follow_symlinks=False), identity)]
                require(len(matches) == 1, 'ambiguous on-disk path: ' + str(rel))
                candidate = p / matches[0]
        p = candidate
    return p


def safe(root, relative):
    path = resolve_entry_path(root, relative)
    actual = path.relative_to(root).as_posix()
    require(actual == Path(relative).as_posix(),
            'path spelling mismatch: ' + str(relative) + '; on-disk path: ' + actual)
    return path


def bounded(text, cap=OUTPUT_CAP, label='output'):
    require(len(text.encode('utf-8')) <= cap, label + ' cap exceeded')
    return text


def read(root, relative, cap):
    path = safe(root, relative)
    require(path.is_file(), 'missing file: ' + relative)
    with path.open('rb') as handle:
        raw = handle.read(cap + 1)
    require(len(raw) <= cap, relative + ' cap exceeded')
    return raw.decode('utf-8')


def file_hash(path):
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(65536), b''):
            digest.update(chunk)
    return digest.hexdigest()


def cap_for(rel):
    if rel in FIXED_CAPS:
        return FIXED_CAPS[rel]
    if Path(rel).name in ('AGENTS.md', 'CLAUDE.md'):
        return 4096
    if re.fullmatch(r'docs/queue/T-[\w-]+\.json', rel):
        return 8192
    if re.fullmatch(r'docs/queue/attempts/A-[\w-]+\.json', rel):
        return 2048
    if re.fullmatch(r'docs/queue/results/[\w-]+\.md', rel):
        return 2048
    if rel == 'docs/sync/status.json' or re.fullmatch(r'docs/sync/outbox/[\w-]+\.json', rel):
        return 2048
    if re.fullmatch(r'docs/(?:issues|decisions)/[\w-]+\.md', rel):
        return 8192
    return None


def managed(root):
    """Enumerate only lifecycle surfaces; do not scan product fixtures for markers."""
    paths = set(FIXED_CAPS) | {'docs/DECISIONS.md'}
    root = Path(root)
    for folder in ('docs/queue', 'docs/sync', 'docs/issues', 'docs/decisions', 'docs/archive'):
        if not exact_path_exists(root, folder):
            continue
        directory = safe(root, folder)
        if directory.exists():
            for path in directory.rglob('*'):
                rel = path.relative_to(root).as_posix()
                safe(root, rel)
                if path.is_file():
                    paths.add(rel)
    for name in ('AGENTS.md', 'CLAUDE.md'):
        for path in root.rglob(name):
            rel = path.relative_to(root).as_posix()
            if path.name == name and not any(part in ('.git', '.cykl', 'node_modules', '.venv') for part in path.relative_to(root).parts):
                paths.add(rel)
    return sorted(rel for rel in paths if exact_path_exists(root, rel))


def render_now(state):
    def render():
        return '# NOW\n\n```json\n' + json.dumps(state, ensure_ascii=False, indent=2) + '\n```\n'
    state = dict(state)
    state['content_sha256'] = ''
    raw = render()
    state['content_sha256'] = sha(''.join(line for line in raw.splitlines(True)
                                        if not line.startswith('  "content_sha256":')).encode())
    return render()


def parse_now(text):
    require(text.startswith('# NOW\n\n```json\n') and text.endswith('\n```\n'), 'NOW shape')
    data = loads(text[len('# NOW\n\n```json\n'):-len('\n```\n')])
    require(isinstance(data, dict) and set(data) == NOW_FIELDS, 'NOW fields')
    require(data['schema'] == 3, 'schema must be 3')
    require(str(uuid.UUID(data['checkpoint'])) == data['checkpoint'], 'checkpoint UUID')
    for name in ('repo', 'branch', 'goal', 'position', 'next'):
        require(isinstance(data[name], str) and data[name].strip(), 'NOW string: ' + name)
    require(data['previous_sha256'] is None or HASH.fullmatch(data['previous_sha256']), 'previous hash')
    require(isinstance(data['parents'], list) and len(data['parents']) <= 2, 'parent shape')
    for value in data['parents'] + ([data['base']] if data['base'] else []):
        require(str(uuid.UUID(value)) == value, 'parent/base UUID')
    for name in ('preserve', 'risks', 'references'):
        require(isinstance(data[name], list) and all(isinstance(v, str) and v for v in data[name]), name + ' shape')
    require(len(data['preserve']) <= 10, 'Preserve cap')
    require(isinstance(data['work'], dict), 'work shape')
    for key, value in data['work'].items():
        require(ID.fullmatch(key) and key[0] in 'OA' and isinstance(value, str) and value, 'work ID/text')
    require(isinstance(data['reconciliation'], dict), 'reconciliation shape')
    for key, entry in data['reconciliation'].items():
        require(ID.fullmatch(key) and isinstance(entry, dict), 'reconciliation ID')
        require(set(entry) <= {'sources', 'action', 'reason', 'successor'}, 'reconciliation keys')
        require(entry.get('action') in ('keep', 'update', 'close', 'supersede'), 'reconciliation action')
        require(isinstance(entry.get('reason'), str) and entry['reason'].strip() and entry['reason'] != 'REVIEW REQUIRED', 'reconciliation reason requires review')
        # Older checkpoints carry historical hashes; accept their shape, never compare them.
        if 'sources' in entry:
            require(isinstance(entry['sources'], list) and all(isinstance(h, str) and HASH.fullmatch(h) for h in entry['sources']), 'reconciliation sources')
    require(render_now(data) == text, 'NOW canonical form/hash mismatch')
    return data


def render_decisions(rows):
    return INDEX_HEADER + ''.join('\t'.join([row['id'], row['kind'], row['status'],
        row['scope'], row.get('supersedes', '-'), json.dumps(row['text'], ensure_ascii=False)]) + '\n' for row in rows)


def decision_rows(root):
    path = safe(root, 'docs/DECISIONS.md')
    require(path.is_file(), 'missing decision index')
    rows = {}
    with path.open('r', encoding='utf-8', newline='') as handle:
        require(''.join(handle.readline() for _ in range(3)) == INDEX_HEADER, 'decision index header')
        while True:
            line = handle.readline(2049)
            if not line:
                break
            bounded(line, 2048, 'decision row')
            require(line.endswith('\n'), 'decision row newline')
            fields = line.rstrip('\n').split('\t')
            require(len(fields) == 6, 'decision row fields')
            key, kind, status, scope, supersedes, text = fields
            require(ID.fullmatch(key) and key[0] in 'DL' and key not in rows, 'decision ID duplicate/shape')
            require(kind == ('decision' if key[0] == 'D' else 'lesson'), 'decision kind')
            require(status in ('proposed', 'accepted', 'retired', 'superseded'), 'decision status')
            require(scope in ('project', 'archived') or re.fullmatch(r'task:[\w-]+', scope), 'decision scope')
            text = loads(text)
            require(isinstance(text, str) and text, 'decision text')
            rows[key] = dict(id=key, kind=kind, status=status, scope=scope, supersedes=supersedes, text=text)
    for key, row in rows.items():
        seen = {key}
        target = row['supersedes']
        while target != '-':
            require(target in rows, 'missing supersedes target')
            require(target not in seen, 'decision cycle')
            seen.add(target)
            target = rows[target]['supersedes']
    return rows


def record_ids(root, state=None):
    state = state or parse_now(read(root, 'docs/NOW.md', NOW_CAP))
    return set(state['work']) | set(decision_rows(root))


def closed_ids(state):
    return {key for key, entry in state['reconciliation'].items()
            if entry['action'] in ('close', 'supersede')}


def source_union(parents, base):
    union, ids = set(), []
    for root in list(parents) + [base]:
        require(root is not None, 'missing merge-base')
        root = Path(root)
        require(root.is_dir(), 'missing parent/base tree')
        if not safe(root, 'docs/NOW.md').exists():
            config = safe(root, 'PROJECT_CONFIG.md')
            if config.exists():
                with config.open(encoding='utf-8') as handle:
                    require(not any(line.strip() == 'CYKL_SCHEMA=3' for line in handle), 'missing parent NOW')
            ids.append(None)
            continue
        state = check(root)
        ids.append(state['checkpoint'])
        union.update(record_ids(root, state))
    return union, ids


def reconciliation_template(parents, base):
    require(len(parents) == 2, 'exactly two parents required')
    union, ids = source_union(parents, base)
    return dict(parents=[v for v in ids[:2] if v], base=ids[2], reconciliation={
        key: dict(action='close', reason='REVIEW REQUIRED') for key in sorted(union)})


def account(current, rec, sources):
    for key in sorted(sources - current):
        entry = rec.get(key)
        require(entry is not None, 'missing reconciliation: ' + key)
        require(entry['action'] in ('close', 'supersede'), 'missing closing line: ' + key)


def check(root, parents=None, base=None, unlocked=False, merge_result=False):
    root = Path(root)
    require(not merge_result or parents is not None, 'merge-result requires both parents and merge-base')
    require(unlocked or not safe(root, '.cykl/lock').exists(), 'writer lock present; inspect/recover first')
    config = read(root, 'PROJECT_CONFIG.md', 2048)
    require(config.splitlines().count('CYKL_SCHEMA=3') == 1, 'missing/downgraded schema')
    state = parse_now(read(root, 'docs/NOW.md', NOW_CAP))
    rows = decision_rows(root)
    closed = closed_ids(state)
    for key in closed:
        require(key not in state['work'] and key not in rows, 'closed ID still active')
        entry = state['reconciliation'][key]
        if entry['action'] == 'supersede':
            require(entry.get('successor') in set(state['work']) | set(rows), 'invalid successor')
    require(all(ref in rows for ref in state['references']), 'missing decision reference')
    for rel in managed(root):
        if rel == 'docs/DECISIONS.md' or rel == 'docs/archive/migration.jsonl':
            continue
        if rel.startswith('docs/archive/'):
            read(root, rel, 65536)
            continue
        cap = cap_for(rel)
        require(cap is not None, 'unexpected managed state: ' + rel)
        text = read(root, rel, cap)
        require(not MARKERS.search(text), 'conflict marker: ' + rel)
        if '/results/' in rel:
            require(len(text.splitlines()) <= 15, 'result line cap')
        if rel.endswith('.json'):
            data = loads(text)
            require(isinstance(data, dict), 'JSON record shape')
            if rel.startswith('docs/queue/T-'):
                require(all(key in data for key in ('attempt', 'issue_url', 'revision', 'base', 'allowed_paths', 'excluded_paths', 'acceptance', 'offline', 'task_budget_bytes')), 'packet fields')
                require(type(data['task_budget_bytes']) is int and 0 < data['task_budget_bytes'] <= 65536, 'packet budget')
                require(data['offline'] is True and data['attempt'] in set(state['work']) | closed, 'packet offline/attempt')
                for field in ('allowed_paths', 'excluded_paths'):
                    require(isinstance(data[field], list) and all(isinstance(p, str) for p in data[field]), 'packet paths')
                    for path in data[field]:
                        require(not Path(path).is_absolute() and '..' not in Path(path).parts, 'packet escaping path')
                exclusions = {Path(p).as_posix() for p in data['excluded_paths']}
                require({'docs/archive', 'docs/DECISIONS.md'} <= exclusions, 'packet history exclusions required')
            if '/attempts/' in rel:
                require(data.get('status') in ('running', 'paused', 'result-ready', 'integrated', 'abandoned'), 'attempt status')
                require(Path(rel).stem in set(state['work']) | closed, 'attempt unreachable')
                if Path(rel).stem in closed:
                    require(data['status'] in ('integrated', 'abandoned'), 'cannot close live attempt')
                require(isinstance(data.get('packet'), str) and re.fullmatch(r'docs/queue/T-[\w-]+\.json', data['packet']), 'attempt packet')
                packet = loads(read(root, data['packet'], 8192))
                require(packet['attempt'] == Path(rel).stem, 'attempt packet mismatch')
    for key in state['work']:
        if key.startswith('A-'):
            require(safe(root, 'docs/queue/attempts/' + key + '.json').exists(), 'missing attempt record')
    manifest = safe(root, 'docs/archive/migration.jsonl')
    if manifest.exists():
        verify_archive(root)
    if parents is not None:
        require(len(parents) == 2 and base is not None, 'both parents and merge-base required')
        union, ids = source_union(parents, base)
        # GitHub inherits NOW from the merged trees; no writer runs on its synthetic commit.
        if not merge_result:
            require(state['parents'] == [v for v in ids[:2] if v] and state['base'] == ids[2], 'parent/base checkpoint reconciliation required')
        account(record_ids(root, state), state['reconciliation'], union)
        for source in list(parents) + [base]:
            for rel in managed(source):
                if rel.startswith('docs/archive/'):
                    original_hash = file_hash(safe(source, rel))
                    retained = file_hash(safe(root, rel)) == original_hash
                    if not retained and not safe(source, 'docs/NOW.md').exists() and manifest.exists():
                        retained = any(row.get('source') == rel and row.get('sha256') == original_hash
                                       for row in manifest_rows(root))
                    require(retained, 'archive changed/deleted without reconstruction: ' + rel)
    return state


def check_workflow(root, trusted):
    rel = '.github/workflows/lifecycle-integrity.yml'
    expected = file_hash(safe(trusted, rel))
    require(expected is not None, 'missing trusted workflow')
    require(file_hash(safe(root, rel)) == expected, 'workflow differs from trusted version')


def package_check(root=None):
    skills = Path(root) / 'skills' if root is not None else Path(__file__).resolve().parents[2]
    require(not skills.is_symlink(), 'symlink package skills')
    found = sorted(skills.glob('cykl-*/SKILL.md'))
    require(len(found) == 7, 'package must contain seven skills')
    for skill in found:
        for path in [skill] + list(skill.parent.glob('assets/*.md')) + list(skill.parent.glob('references/*.md')):
            text = read(skills, path.relative_to(skills).as_posix(), 4096)
            require(not re.search(r'docs/(?:archive|log)|gh issue view', text), 'raw history/issue read in skill/template')
        text = skill.read_text()
        desc = re.search(r'^description: (.+)$', text, re.M)
        require(desc is not None, 'skill description missing')
        bounded(desc[1], 512, 'description')
        require('<!-- cykl-lifecycle v3.0.1 -->' in text, 'skill version')
    return found


def context(root, skill='cykl-start', task=None, files=None):
    state = check(root)
    found = package_check()
    require(skill in [p.parent.name for p in found], 'unknown skill')
    pieces = []
    for path in found:
        text = path.read_text()
        pieces.append(text if path.parent.name == skill else re.search(r'^description: (.+)$', text, re.M)[0])
    for rel in ('AGENTS.md', 'CLAUDE.md', 'PROJECT_CONFIG.md', 'docs/NOW.md', 'docs/ROADMAP.md'):
        if exact_path_exists(root, rel):
            pieces.append(read(root, rel, cap_for(rel)))
    for row in decision_rows(root).values():
        if row['id'] in state['references'] or (row['status'] == 'accepted' and row['scope'] in ('project', 'task:' + str(task))):
            pieces.append(dumps(row))
    exclusions = set()
    for key in state['work']:
        if key.startswith('A-'):
            attempt = read(root, 'docs/queue/attempts/' + key + '.json', 2048)
            pieces.append(attempt)
            packet = loads(read(root, loads(attempt)['packet'], 8192))
            exclusions.update(Path(p).as_posix() for p in packet['excluded_paths'])
    outbox = sorted(safe(root, 'docs/sync/outbox').glob('*.json'))
    pieces.append(dumps({'pending_count': len(outbox), 'oldest_id': outbox[0].stem if outbox else None}))
    if safe(root, 'docs/sync/status.json').exists():
        pieces.append(read(root, 'docs/sync/status.json', 2048))
    for rel in files or []:
        safe(root, rel)
        rel = Path(rel).as_posix()
        require(not rel.startswith(('docs/archive/', 'docs/log/')) and rel != 'docs/DECISIONS.md', 'use bounded archive/index projection')
        require(not rel.startswith('docs/decisions/') or Path(rel).stem in state['references'], 'unlisted decision body; use index projection')
        require(not any(rel == path or rel.startswith(path + '/') or path == '.' for path in exclusions), 'packet excluded path')
        pieces.append(read(root, rel, min(cap_for(rel) or 8192, 8192)))
    return bounded('\n\n'.join(pieces) + '\n')


def durable(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix='.lifecycle-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def promote(root, changes, preflight):
    root = Path(root)
    lock = safe(root, '.cykl/lock')
    lock.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise ValueError('writer lock present; inspect/recover first') from None
    with os.fdopen(fd, 'w') as handle:
        handle.write(dumps({'pid': os.getpid()}))
        handle.flush()
        os.fsync(handle.fileno())
    stage = safe(root, '.cykl/stage')
    descriptor = safe(root, '.cykl/recovery.json')
    promoting = False
    prepared = False
    try:
        require(not descriptor.exists() and not stage.exists(), 'recovery material already exists')
        prepared = True
        preflight()
        if callable(changes):
            changes = changes()
        for rel, raw in changes.items():
            if rel.startswith('docs/archive/') and safe(root, 'docs/archive/migration.jsonl').exists() and safe(root, rel).exists():
                require(file_hash(safe(root, rel)) == sha(raw), 'archive overwrite forbidden')
        stage.mkdir()
        for rel in managed(root):
            path = safe(stage, rel)
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(safe(root, rel), path)
        for rel, raw in changes.items():
            durable(safe(stage, rel), raw)
        check(stage)
        desc = {'changes': {rel: {'before': file_hash(safe(root, rel)), 'after': sha(raw)} for rel, raw in changes.items()}}
        durable(descriptor, dumps(desc).encode())
        promoting = True
        finish_promotion(root, desc)
    finally:
        if not promoting:
            if prepared and stage.exists():
                shutil.rmtree(stage)
            if prepared and descriptor.exists():
                descriptor.unlink()
            lock.unlink()


def finish_promotion(root, desc):
    stage = safe(root, '.cykl/stage')
    check(stage)
    for rel, hashes in desc['changes'].items():
        require(file_hash(safe(stage, rel)) == hashes['after'], 'recovery candidate changed')
        require(file_hash(safe(root, rel)) in (hashes['before'], hashes['after']), 'recovery target changed')
    for rel in sorted(desc['changes'], key=lambda rel: (rel == 'docs/NOW.md', rel)):
        durable(safe(root, rel), safe(stage, rel).read_bytes())
    check(root, unlocked=True)
    shutil.rmtree(stage)
    safe(root, '.cykl/recovery.json').unlink()
    safe(root, '.cykl/lock').unlink()


def recover(root):
    guard = safe(root, '.cykl/recover.lock')
    try:
        fd = os.open(guard, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise ValueError('recovery already owned; inspect stale recovery guard manually') from None
    try:
        with os.fdopen(fd, 'w') as handle:
            handle.write(str(os.getpid()))
            handle.flush()
            os.fsync(handle.fileno())
        data = loads(read(root, '.cykl/lock', 2048))
        pid = data.get('pid')
        require(type(pid) is int and pid > 0, 'invalid lock; inspect manually')
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            pass
        else:
            raise ValueError('writer pid is alive; recovery refused')
        descriptor = safe(root, '.cykl/recovery.json')
        require(descriptor.exists(), 'no verified promotion; inspect stage and remove stale lock manually')
        finish_promotion(Path(root), loads(descriptor.read_text()))
        return 'Recovered verified checkpoint\n'
    finally:
        guard.unlink()


def draft_changes(root, draft, expected):
    require(isinstance(draft, dict), 'draft object required')
    allowed = NOW_FIELDS - {'schema', 'checkpoint', 'previous_sha256', 'content_sha256'} | {'files', 'decisions'}
    require(set(draft) <= allowed, 'unknown draft fields')
    old = None
    if safe(root, 'docs/NOW.md').exists():
        old = parse_now(read(root, 'docs/NOW.md', NOW_CAP))
    require(expected == (old['content_sha256'] if old else 'absent'), 'expected checkpoint hash mismatch')
    if not old:
        require(not safe(root, 'PROJECT_CONFIG.md').exists() and not safe(root, 'docs/HANDOFF.md').exists(), 'legacy project requires migrate')
    state = {key: draft[key] for key in ('repo', 'branch', 'goal', 'position', 'next', 'preserve', 'work', 'risks', 'references')}
    state['work'] = dict(state['work'])
    preserve = state['preserve']
    for item in preserve[10:]:
        key = 'O-preserve-' + sha(item.encode())[:12]
        require(key not in state['work'] or state['work'][key] == item, 'spill ID collision')
        state['work'][key] = item
    state['preserve'] = preserve[:10]
    state.update(schema=3, checkpoint=str(uuid.uuid4()), previous_sha256=old['content_sha256'] if old else None,
                 content_sha256='', parents=draft.get('parents', []), base=draft.get('base'),
                 reconciliation=draft.get('reconciliation', old['reconciliation'] if old else {}))
    text = bounded(render_now(state), NOW_CAP, 'NOW')
    state = parse_now(text)
    changes = {}
    for rel, content in draft.get('files', {}).items():
        safe(root, rel)
        cap = cap_for(rel)
        require(cap is not None and rel not in ('docs/NOW.md',), 'unsupported checkpoint write')
        changes[rel] = bounded(content, cap, rel).encode()
    changes['docs/NOW.md'] = text.encode()
    if 'decisions' in draft:
        changes['docs/DECISIONS.md'] = draft['decisions'].encode()
    elif not old:
        changes['docs/DECISIONS.md'] = INDEX_HEADER.encode()
    if not old:
        changes.setdefault('PROJECT_CONFIG.md', b'CYKL_SCHEMA=3\nMIRROR=disabled\nMERGE_PROTECTION=merge protection unverified\n')
    return changes, acknowledgement(root, state), old


def acknowledgement(root, state):
    return bounded(dumps(dict(repo=state['repo'], branch=state['branch'], path='docs/NOW.md',
        checkpoint=state['checkpoint'], hash=state['content_sha256'], preserve=state['preserve'],
        worktree=str(root.resolve()), goal=state['goal'], next=state['next'],
        work_ids=list(state['work']), reload='python3 ' + shlex.quote(str(Path(__file__).resolve())) +
        ' context --root ' + shlex.quote(str(root.resolve())) + ' --skill cykl-start')) + '\n')


def saved_card(root, changes):
    text = read(root, 'docs/NOW.md', NOW_CAP)
    require(text.encode() == changes['docs/NOW.md'], 'NOW changed after promotion')
    return acknowledgement(Path(root), parse_now(text))


def checkpoint(root, draft, expected):
    root = Path(root)
    require(not safe(root, '.cykl/lock').exists() and not safe(root, '.cykl/recover.lock').exists(), 'writer/recovery lock present')
    changes, card, old = draft_changes(root, draft, expected)
    def preflight():
        if old:
            require(parse_now(read(root, 'docs/NOW.md', NOW_CAP))['content_sha256'] == expected, 'expected hash changed')
            # Preserve removed obligations and decision IDs, including previous closures.
            with tempfile.TemporaryDirectory() as temp:
                stage = Path(temp)
                for rel in set(managed(root)) | set(changes):
                    path = safe(stage, rel)
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(changes[rel] if rel in changes else safe(root, rel).read_bytes())
                current = record_ids(stage)
            sources = record_ids(root, old) | closed_ids(old)
            account(current, parse_now(changes['docs/NOW.md'].decode())['reconciliation'], sources)
        else:
            require(not safe(root, 'docs/NOW.md').exists(), 'expected absent changed')
    promote(root, changes, preflight)
    return saved_card(root, changes)


def decisions_add(root, row, expected):
    root = Path(root)
    require(isinstance(row, dict) and set(row) == {'id', 'kind', 'status', 'scope', 'supersedes', 'text'}, 'decision row fields')
    line = bounded(render_decisions([row])[len(INDEX_HEADER):], 2048, 'decision row')
    changes = {}
    def prepare():
        old = check(root, unlocked=True)
        require(old['content_sha256'] == expected, 'expected checkpoint hash mismatch')
        require(row['id'] not in record_ids(root, old) | closed_ids(old), 'decision ID already used')
        draft = {key: value for key, value in old.items()
                 if key not in {'schema', 'checkpoint', 'previous_sha256', 'content_sha256'}}
        generated, card, _ = draft_changes(root, draft, expected)
        bounded(card + line)
        # Only the writer reads history; keep every existing index byte intact.
        generated['docs/DECISIONS.md'] = safe(root, 'docs/DECISIONS.md').read_bytes() + line.encode()
        changes.update(generated)
        return changes
    require(not safe(root, '.cykl/recover.lock').exists(), 'recovery lock present')
    promote(root, prepare, lambda: None)
    return bounded(saved_card(root, changes) + line)


# v2 e285f95: porzadek.py:36 and kickoff references/struktura-projektu.md:35-42.
# ADRs/registers are knowledge documents (same reference:46-53), not state files.
LEGACY_STATE_PATHS = ('PROJECT_CONFIG.md', 'docs/HANDOFF.md', 'docs/ROADMAP.md',
                      'docs/LESSONS_CANON.md')


def exact_path_exists(root, relative):
    path = resolve_entry_path(root, relative)
    return path.relative_to(root).as_posix() == Path(relative).as_posix() and path.exists()


def source_paths(root):
    return sorted(rel for rel in LEGACY_STATE_PATHS if exact_path_exists(root, rel))


def keep_paths(root, sources):
    root = Path(root)
    paths = {path.name for path in root.iterdir() if path.is_file() or path.is_symlink()}
    for docs in root.iterdir():
        if docs.name.casefold() == 'docs' and docs.is_dir() and not docs.is_symlink():
            paths.update(path.relative_to(root).as_posix() for path in docs.rglob('*')
                         if path.is_file() or path.is_symlink())
    return sorted(paths - set(sources))


def path_summary(paths):
    paths = sorted(paths)
    # Full names live in the external plan; previews stay bounded even for huge trees.
    preview = [path[:160] for path in paths[:8]]
    return dict(count=len(paths), paths=preview,
                truncated=len(paths) > 8 or any(len(path) > 160 for path in paths[:8]))


def migrated_config(raw, schema):
    # v2 kickoff template:26-40 owns Current Sprint; preserve every other section.
    lines = raw.decode('utf-8').splitlines(keepends=True)
    result, current, notes = [], False, False
    for line in lines:
        if re.match(r'^## Current Sprint(?:\s|$)', line):
            current = True
            notes = False
            result.append('## Lifecycle state\nUse lifecycle.py context for current state.\n')
        elif re.match(r'^#{1,2} ', line):
            current = False
            notes = False
            result.append(line)
        else:
            if re.match(r'^#{1,6}\s', line) or re.match(r'^[A-Za-z_][A-Za-z0-9_]*=', line):
                notes = line.startswith('REPO_NOTES=')
            if not current or notes:
                result.append(line)
    retained = ''.join(result).encode()
    return retained + (b'\n' if retained and not retained.endswith(b'\n') else b'') + schema


def source_data(root, rel):
    raw = safe(root, rel).read_bytes()
    text = raw.decode('utf-8')
    lines = text.splitlines(keepends=True)
    require(''.join(lines).encode() == raw, 'source UTF-8 reconstruction')
    hits = [str(i) for i, line in enumerate(lines, 1) if SECRET.search(line)]
    return raw, lines, hits


def migration_plan(root, extra_sources=()):
    require(not safe(root, '.cykl/lock').exists(), 'writer lock present')
    require(not safe(root, 'docs/NOW.md').exists(), 'already v3; use original approved plan for retry')
    sources = {}
    for rel in sorted(set(source_paths(root)) | set(extra_sources)):
        require(Path(rel).as_posix() == rel and not any(p.startswith('.') for p in Path(rel).parts),
                'noncanonical/hidden migration source forbidden')
        raw, lines, hits = source_data(root, rel)
        sources[rel] = dict(sha256=sha(raw), bytes=len(raw), lines=len(lines), secret_hits=hits,
            acknowledgements={}, ranges=[dict(start=1, end=len(lines), disposition='unresolved', reason='')] if lines else [])
    require(sources, 'no legacy sources')
    plan = dict(schema=3, extra_sources=sorted(set(extra_sources)), keep=keep_paths(root, sources),
                review={key: '' for key in REVIEW_KEYS}, sources=sources,
                draft=dict(repo='example/project', branch='UNKNOWN', goal='REVIEW REQUIRED', position='Offline migration',
                           next='Review migrated facts', preserve=[], work={}, risks=[], references=[]), replacements={})
    # Unresolved ranges assume archiving; reviewers must update change after range edits.
    paths = set(sources) | {'PROJECT_CONFIG.md', 'docs/NOW.md', 'docs/DECISIONS.md',
                            'docs/archive/migration.jsonl'}
    for rel, spec in sources.items():
        _, lines, _ = source_data(root, rel)
        for entry in spec['ranges']:
            paths.update(part['path'] for part, _ in archive_chunks(rel, lines, entry))
    migration_write_set(root, paths, set(sources))
    plan['change'] = sorted(paths)
    return plan


def archive_chunks(rel, lines, entry):
    start, end = entry['start'], entry['end']
    chunk, first = '', start
    for number in range(start, end + 1):
        line = lines[number - 1]
        bounded(line, 65536, 'archive source line')
        if chunk and len((chunk + line).encode()) > 65536:
            path = 'docs/archive/' + sha(rel.encode())[:16] + '-' + str(first) + '.txt'
            yield dict(start=first, end=number - 1, path=path, sha256=sha(chunk.encode()),
                       reason=entry['reason']), chunk.encode()
            chunk, first = '', number
        chunk += line
    path = 'docs/archive/' + sha(rel.encode())[:16] + '-' + str(first) + '.txt'
    yield dict(start=first, end=end, path=path, sha256=sha(chunk.encode()),
               reason=entry['reason']), chunk.encode()


def migration_write_set(root, paths, selected):
    for rel in paths:
        path = safe(root, rel)
        for parent in Path(rel).parents:
            ancestor = Path(root) / parent
            require(not ancestor.exists() or ancestor.is_dir(),
                    'non-directory ancestor of migration write: ' + parent.as_posix())
        require(rel in selected or rel in ('PROJECT_CONFIG.md', 'docs/NOW.md', 'docs/DECISIONS.md')
                or rel.startswith('docs/archive/'), 'unselected migration write: ' + rel)
        require(rel in selected or not path.exists(),
                'unselected file would change; explicit opt-in required: ' + rel)


def manifest_rows(root):
    path = safe(root, 'docs/archive/migration.jsonl')
    require(path.is_file(), 'missing migration manifest')
    with path.open(encoding='utf-8') as handle:
        for line in handle:
            yield loads(line)


def reconstruct(root, row):
    parts = []
    cursor = 1
    for part in row['parts']:
        require(part['start'] == cursor, 'archive range coverage')
        if 'text' in part:
            text = part['text']
        else:
            text = read(root, part['path'], 65536)
        require(sha(text.encode()) == part['sha256'], 'archive chunk hash')
        require(len(text.splitlines(keepends=True)) == part['end'] - part['start'] + 1, 'archive line count')
        cursor = part['end'] + 1
        parts.append(text)
    raw = ''.join(parts).encode()
    require(cursor == row['lines'] + 1 and len(raw) == row['bytes'] and sha(raw) == row['sha256'], 'archive reconstruction hash')
    return raw


def verify_archive(root):
    for row in manifest_rows(root):
        if row['type'] == 'source':
            reconstruct(root, row)


def archive_show(root, source, start, end):
    require(not safe(root, '.cykl/lock').exists(), 'writer lock present')
    require(1 <= start <= end, 'invalid line range')
    for row in manifest_rows(root):
        if row.get('source') == source:
            text = reconstruct(root, row).decode()
            require(end <= row['lines'], 'line range beyond source')
            return bounded(''.join(text.splitlines(keepends=True)[start - 1:end]))
    raise ValueError('source not found')


def external_destination(root, destination):
    destination = Path(destination).absolute()
    safe(Path(destination.anchor), destination.relative_to(destination.anchor).as_posix())
    root = Path(root).resolve()
    require(destination != root and root not in destination.parents and destination not in root.parents,
            'destination must be separate from the live tree')
    require(not destination.exists(), 'destination already exists')
    require(destination.parent.is_dir(), 'destination parent must exist')
    return destination


def write_migration_plan(root, output=None, extra_sources=()):
    plan = migration_plan(root, extra_sources)
    raw = (dumps(plan) + '\n').encode()
    output = output or Path(tempfile.gettempdir()).resolve() / ('cykl-plan-' + str(uuid.uuid4()) + '.json')
    output = external_destination(root, output)
    result = bounded(dumps(dict(plan=str(output), sha256=sha(raw), sources=len(plan['sources']),
        change=path_summary(plan['change']),
        keep=path_summary(plan['keep']))) + '\n')
    # Exclusive creation preserves an existing reviewed plan even if another writer races us.
    with output.open('xb') as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    return result


def rollback(root, destination):
    root = Path(root)
    check(root)
    destination = external_destination(root, destination)
    with tempfile.TemporaryDirectory(dir=destination.parent, prefix='.cykl-restore-') as temp:
        stage = Path(temp)
        count = 0
        for row in manifest_rows(root):
            if row['type'] == 'source':
                safe(root, row['source'])
                path = safe(stage, row['source'])
                require(not path.exists(), 'duplicate rollback source')
                durable(path, reconstruct(root, row))
                count += 1
        require(count > 0, 'no migration sources to restore')
        result = bounded(dumps(dict(status='restored migration sources', dest=str(destination), sources=count)) + '\n')
        # Reserve the destination atomically: rename alone can replace an existing directory.
        destination.mkdir(mode=0o700)
        try:
            for path in stage.iterdir():
                shutil.move(str(path), str(destination / path.name))
        except OSError:
            shutil.rmtree(destination)
            raise
    return result


def migrate(root, plan=None, apply=False):
    root = Path(root)
    if plan is None:
        require(not apply, '--apply requires reviewed --plan')
        return migration_plan(root)
    plan_hash = sha(dumps(plan).encode())
    if safe(root, 'docs/archive/migration.jsonl').exists():
        receipt = next(manifest_rows(root))
        require(receipt['plan_sha256'] == plan_hash, 'migration plan changed')
        check(root)
        return {'status': 'already applied', 'plan_sha256': plan_hash}
    require(plan.get('schema') == 3, 'migration schema')
    require(all(isinstance(plan.get('review', {}).get(key), str) and plan['review'][key].strip() for key in REVIEW_KEYS), 'review checklist incomplete')
    selected = set(plan['sources'])
    extras = plan.get('extra_sources', [])
    require(isinstance(extras, list) and all(isinstance(rel, str) for rel in extras), 'extra_sources list required')
    replacements = plan.get('replacements', {})
    for rel in selected | set(extras) | set(replacements) | set(plan['draft'].get('files', {})):
        safe(root, rel)
    require(set(replacements) <= selected, 'replacement requires reviewed source')
    require(set(source_paths(root)) <= selected, 'source inventory incomplete')
    require(set(extras) <= selected, 'extra source missing review')
    require(selected <= set(source_paths(root)) | set(extras) | set(replacements),
            'non-state source requires explicit per-file opt-in')
    declared = plan.get('change')
    require(isinstance(declared, list) and all(isinstance(rel, str) for rel in declared),
            'plan change must be a full path list')
    for rel in declared:
        safe(root, rel)
        require(Path(rel).as_posix() == rel, 'noncanonical plan change path')
    files = {rel: content for rel, content in plan['draft'].get('files', {}).items()
             if rel not in LEGACY_STATE_PATHS}
    require(set(files) <= selected, 'unselected draft.files write requires explicit opt-in')
    for rel in set(files) & set(replacements):
        require(files[rel].encode() == replacements[rel].encode(),
                'draft.files conflicts with reviewed replacement: ' + rel)
    changes, rows, work, ids = {}, [], dict(plan['draft']['work']), set(plan['draft']['work'])
    manifest = [dict(type='migration', plan_sha256=plan_hash, review=plan['review'])]
    for rel, spec in plan['sources'].items():
        require(Path(rel).as_posix() == rel and not any(part.startswith('.') for part in Path(rel).parts),
                'noncanonical/hidden migration source forbidden')
        raw, lines, hits = source_data(root, rel)
        require(sha(raw) == spec['sha256'] and len(raw) == spec['bytes'] and len(lines) == spec['lines'], 'source hash changed: ' + rel)
        for hit in hits:
            require(re.fullmatch(r'ACK-[\w-]+', spec.get('acknowledgements', {}).get(hit, '')), 'secret hit requires acknowledgement: ' + rel + ':' + hit)
        cursor, parts = 1, []
        for entry in spec['ranges']:
            start, end = entry['start'], entry['end']
            require(type(start) is int and type(end) is int and start == cursor and start <= end <= len(lines), 'source range coverage')
            require(isinstance(entry.get('reason'), str) and entry['reason'].strip(), 'range review reason missing')
            text = ''.join(lines[start - 1:end])
            part = dict(start=start, end=end, sha256=sha(text.encode()), reason=entry['reason'])
            disposition = entry['disposition']
            if disposition == 'active':
                key = entry.get('id', '')
                require(ID.fullmatch(key) and key not in ids, 'active fact ID duplicate/invalid')
                ids.add(key)
                part.update(id=key, text=text)
                if key[0] in 'OA':
                    work[key] = text
                else:
                    rows.append(dict(id=key, kind='decision' if key[0] == 'D' else 'lesson', status='accepted',
                                     scope=entry.get('scope', 'archived'), supersedes='-', text=text))
                parts.append(part)
            elif disposition == 'archived':
                for part, raw_chunk in archive_chunks(rel, lines, entry):
                    changes[part['path']] = raw_chunk
                    parts.append(part)
            else:
                raise ValueError('unresolved range disposition')
            cursor = end + 1
        require(cursor == len(lines) + 1, 'source range coverage incomplete')
        manifest.append(dict(type='source', source=rel, sha256=sha(raw), bytes=len(raw), lines=len(lines),
                             acknowledgements=spec.get('acknowledgements', {}), parts=parts))
        replacement = replacements.get(rel)
        if Path(rel).name in ('AGENTS.md', 'CLAUDE.md'):
            require(replacement, 'instruction replacement required: ' + rel)
        changes[rel] = (replacement if replacement is not None else '# Migrated\n\nUse lifecycle.py context for current state; archive show for original lines.\n').encode()
    draft = dict(plan['draft'], files=files, work=work, decisions=render_decisions(rows))
    # Use a clean root solely to render the initial checkpoint; never parse legacy state as v3.
    with tempfile.TemporaryDirectory() as temp:
        generated, card, _ = draft_changes(Path(temp), draft, 'absent')
    if 'PROJECT_CONFIG.md' in selected:
        generated['PROJECT_CONFIG.md'] = (replacements['PROJECT_CONFIG.md'].encode()
            if 'PROJECT_CONFIG.md' in replacements else
            migrated_config(safe(root, 'PROJECT_CONFIG.md').read_bytes(), generated['PROJECT_CONFIG.md']))
    for rel in generated:
        if Path(rel).name in ('AGENTS.md', 'CLAUDE.md'):
            require(rel in replacements and generated[rel] == replacements[rel].encode(),
                    'instruction replacement required: ' + rel)
    changes.update(generated)
    changes['docs/archive/migration.jsonl'] = ''.join(dumps(row) + '\n' for row in manifest).encode()
    def preflight():
        require(set(declared) == set(changes),
                'plan change does not match actual write set; review full change list after range edits')
        require(set(source_paths(root)) <= selected, 'source inventory changed')
        migration_write_set(root, changes, selected)
        for rel, spec in plan['sources'].items():
            require(file_hash(safe(root, rel)) == spec['sha256'], 'source hash changed: ' + rel)
    preflight()
    with tempfile.TemporaryDirectory() as temp:
        stage = Path(temp)
        for rel, raw in changes.items():
            durable(safe(stage, rel), raw)
        state = check(stage)
        for row in manifest[1:]:
            for part in row['parts']:
                if 'id' in part:
                    target = state['work'].get(part['id']) if part['id'][0] in 'OA' else decision_rows(stage)[part['id']]['text']
                    require(target == part['text'], 'active extraction mismatch')
    result = {'status': 'applied' if apply else 'verified dry-run', 'plan_sha256': plan_hash,
              'sources': len(plan['sources']), 'active_facts': len(ids), 'review': plan['review'],
              'change': path_summary(changes), 'keep': path_summary(keep_paths(root, changes))}
    bounded(dumps(result) + '\n')
    if apply:
        promote(root, changes, preflight)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('check', 'context', 'checkpoint', 'decisions', 'migrate', 'recover', 'archive'):
        p = sub.add_parser(name)
        if name == 'archive':
            p.add_argument('action', choices=['show'])
        p.add_argument('--root', type=Path, default=Path('.'))
        if name == 'check':
            p.add_argument('--package', action='store_true')
            p.add_argument('--merge-result', action='store_true')
            p.add_argument('--trusted-root', type=Path)
            p.add_argument('--reconcile-template', action='store_true')
            p.add_argument('--parent', type=Path, action='append')
            p.add_argument('--base', type=Path)
        elif name == 'context':
            p.add_argument('--skill', default='cykl-start')
            p.add_argument('--task')
            p.add_argument('--file', action='append')
        elif name == 'checkpoint':
            p.add_argument('--input', type=Path, required=True)
            p.add_argument('--expected', required=True)
        elif name == 'decisions':
            p.add_argument('action', nargs='?', choices=['add'])
            p.add_argument('--input', type=Path)
            p.add_argument('--expected')
        elif name == 'migrate':
            p.add_argument('--plan', type=Path)
            p.add_argument('--output', type=Path)
            p.add_argument('--extra-source', action='append', default=[])
            p.add_argument('--dest', type=Path)
            group = p.add_mutually_exclusive_group()
            group.add_argument('--apply', action='store_true')
            group.add_argument('--dry-run', action='store_true')
            group.add_argument('--rollback', action='store_true')
        elif name == 'archive':
            p.add_argument('--source', required=True)
            p.add_argument('--lines', required=True)
    args = parser.parse_args()
    try:
        if args.command == 'check':
            require(not args.base or args.parent, '--base requires both parents')
            require(not args.merge_result or (args.parent and args.base and not args.package and not args.reconcile_template),
                    '--merge-result requires parents/base, not package/template')
            if args.trusted_root:
                check_workflow(args.root, args.trusted_root)
            if args.reconcile_template:
                require(args.parent and args.base and not args.package, 'template requires parents/base, not package')
                template = reconciliation_template(args.parent, args.base)
                state = check(args.root)
                current = record_ids(args.root, state) | closed_ids(state)
                template['reconciliation'] = {key: entry for key, entry in template['reconciliation'].items()
                    if key not in current}
                result = dumps(template) + '\n'
            elif args.package:
                require(not args.parent and not args.base, 'package mode does not accept ancestry')
                package_check(args.root)
                result = 'Package OK\n'
            else:
                check(args.root, args.parent, args.base, merge_result=args.merge_result)
                result = 'Lifecycle OK\n'
        elif args.command == 'context':
            result = context(args.root, args.skill, args.task, args.file)
        elif args.command == 'checkpoint':
            result = checkpoint(args.root, loads(args.input.read_text()), args.expected)
        elif args.command == 'decisions':
            if args.action == 'add':
                require(args.input and args.expected, 'decisions add requires --input and --expected')
                row = loads(read(args.input.parent, args.input.name, 8192))
                result = decisions_add(args.root, row, args.expected)
            else:
                require(not args.input and not args.expected, 'use decisions add for writes')
                require(not safe(args.root, '.cykl/lock').exists(), 'writer lock present')
                result = dumps({'decisions': len(decision_rows(args.root))}) + '\n'
        elif args.command == 'migrate':
            if args.rollback:
                require(args.dest and not args.plan and not args.output and not args.extra_source, '--rollback requires --dest only')
                result = rollback(args.root, args.dest)
            else:
                require(not args.dest, '--dest requires --rollback')
                if args.plan:
                    require(not args.output and not args.extra_source, '--output/--extra-source are only for inventory')
                    result = dumps(migrate(args.root, loads(args.plan.read_text()), args.apply)) + '\n'
                else:
                    require(not args.apply, '--apply requires reviewed --plan')
                    result = write_migration_plan(args.root, args.output, args.extra_source)
        elif args.command == 'recover':
            result = recover(args.root)
        else:
            first, last = map(int, args.lines.split('-'))
            result = archive_show(args.root, args.source, first, last)
        sys.stdout.write(bounded(result))
        return 0
    except (ValueError, OSError, KeyError, TypeError, StopIteration) as exc:
        message = ('lifecycle: ' + str(exc)).encode('utf-8')[:1000].decode('utf-8', errors='ignore')
        sys.stderr.write(message + '\n')
        return 1


if __name__ == '__main__':
    sys.exit(main())

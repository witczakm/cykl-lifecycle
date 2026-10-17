import importlib.util
import json
import re
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/cykl-start/scripts/lifecycle.py'

REPO = Path(__file__).resolve().parents[1]
CONFIG = 'CYKL_SCHEMA=3\nMIRROR=disabled\n'
ROADMAP = '# ROADMAP\n\n- T-1 open First\n- T-2 done Second\n'


class LifecycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SCRIPT.exists():
            return
        spec = importlib.util.spec_from_file_location('lifecycle', SCRIPT)
        cls.lc = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.lc)

    def setUp(self):
        self.assertTrue(SCRIPT.exists(), 'lifecycle.py implementation is missing')
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()

    def draft(self, **kw):
        d = dict(repo='example/project', branch='work', goal='Deliver a change',
                 position='Offline observation', next='Run checks', preserve=[],
                 work={}, risks=[], references=[])
        d.update(kw)
        return d

    def init(self, name='result', **kw):
        root = self.root / name
        root.mkdir()
        self.lc.checkpoint(root, self.draft(**kw), 'absent')
        return root

    def test_checkpoint_is_hashed_and_rewrites(self):
        root = self.init(work={'O-1': 'Keep evidence'})
        old = self.lc.check(root)
        card = self.lc.checkpoint(root, self.draft(work=old['work']), old['content_sha256'])
        self.assertIn('checkpoint', card)
        self.assertEqual(self.lc.check(root)['previous_sha256'], old['content_sha256'])
        self.assertLessEqual((root / 'docs/NOW.md').stat().st_size, 4096)

    def test_two_valid_parents_cannot_drop_obligation(self):
        base = self.init('base')
        left = self.init('left', work={'O-left': 'Keep left'})
        right = self.init('right', work={'O-right': 'Keep right'})
        draft = self.draft(work={'O-left': 'Keep left'})
        draft.update(self.lc.reconciliation_template([left, right], base))
        draft['reconciliation'] = {}
        result = self.init(**draft)
        with self.assertRaisesRegex(ValueError, 'missing reconciliation: O-right'):
            self.lc.check(result, [left, right], base)

    def test_synthetic_merge_with_one_sided_now_change_passes(self):
        base = self.init('base', work={'O-base': 'Keep base'})
        left = self.root / 'left'
        right = self.root / 'right'
        shutil.copytree(base, left)
        shutil.copytree(base, right)
        self.lc.checkpoint(right, self.draft(next='New action', work={
            'O-base': 'Updated base duty', 'O-head': 'Keep head'}), self.lc.check(right)['content_sha256'])
        result = self.root / 'result'
        shutil.copytree(right, result)  # GitHub inherits the head NOW byte-for-byte.
        proc = subprocess.run([sys.executable, '-B', str(SCRIPT), 'check', '--merge-result',
            '--root', str(result), '--parent', str(left), '--parent', str(right), '--base', str(base)],
            capture_output=True)
        self.assertEqual(proc.returncode, 0, proc.stderr.decode())

    def test_synthetic_merge_unchanged_now_passes(self):
        base = self.init('base', work={'O-base': 'Keep base'})
        self.lc.check(base, [base, base], base, merge_result=True)

    def test_synthetic_merge_both_changed_cannot_drop_obligations(self):
        base = self.init('base', work={'O-base': 'Keep base'})
        left, right = self.root / 'left', self.root / 'right'
        for tree, key in ((left, 'O-left'), (right, 'O-right')):
            shutil.copytree(base, tree)
            self.lc.checkpoint(tree, self.draft(work={'O-base': 'Keep base', key: key}),
                               self.lc.check(tree)['content_sha256'])
        result = self.root / 'result'
        shutil.copytree(right, result)
        with self.assertRaisesRegex(ValueError, 'missing reconciliation: O-left'):
            self.lc.check(result, [left, right], base, merge_result=True)

    def test_synthetic_merge_both_sides_changed_with_union_kept_passes(self):
        base = self.init('base')
        left = self.init('left', work={'O-1': 'left', 'O-left': 'Keep left'})
        right = self.init('right', work={'O-1': 'right', 'O-right': 'Keep right'})
        draft = self.draft(work={'O-right': 'Keep right', 'O-1': 'settled', 'O-left': 'Keep left'})
        self.lc.checkpoint(right, draft, self.lc.check(right)['content_sha256'])
        result = self.root / 'result'
        shutil.copytree(right, result)
        self.lc.check(result, [left, right], base, merge_result=True)

    def test_second_pr_after_settled_update_with_unchanged_now_passes(self):
        base = self.init('base', work={'O-1': 'Original duty'})
        left = self.init('left', work={'O-1': 'Left duty'})
        right = self.init('right', work={'O-1': 'Right duty'})
        # Historical hashes from a previously valid update, including the settled value.
        hashes = [self.lc.sha(self.lc.dumps({'text': text}).encode())
                  for text in ('Original duty', 'Left duty', 'Settled duty')]
        draft = self.draft(work={'O-1': 'Settled duty'}, reconciliation={'O-1': dict(
            sources=hashes, action='update', reason='Reviewed both variants')})
        self.lc.checkpoint(right, draft, self.lc.check(right)['content_sha256'])
        self.lc.check(right, [left, right], base, merge_result=True)
        second_left, second_right = self.root / 'second-left', self.root / 'second-right'
        shutil.copytree(right, second_left)
        shutil.copytree(right, second_right)
        before = (second_right / 'docs/NOW.md').read_bytes()
        self.lc.check(second_right, [second_left, second_right], right, merge_result=True)
        self.assertEqual((second_right / 'docs/NOW.md').read_bytes(), before)

    def test_synthetic_merge_metadata_only_after_settled_update_passes(self):
        base = self.init('base', work={'O-1': 'Settled duty'}, reconciliation={'O-1': dict(
            sources=['0' * 64, '1' * 64], action='update', reason='Earlier settlement')})
        right = self.root / 'right'
        shutil.copytree(base, right)
        self.lc.checkpoint(right, self.draft(next='New action', position='Review',
            work={'O-1': 'Settled duty'}), self.lc.check(right)['content_sha256'])
        self.lc.check(right, [base, right], base, merge_result=True)

    def test_synthetic_merge_closed_obligation_with_reason_passes(self):
        base = self.init('base', work={'O-1': 'Complete review'})
        result = self.init(reconciliation={'O-1': dict(action='close', reason='Review completed')})
        self.lc.check(result, [base, base], base, merge_result=True)

    def test_synthetic_merge_missing_closure_reason_fails(self):
        base = self.init('base', work={'O-1': 'Complete review'})
        result = self.init()
        state = self.lc.check(result)
        for reason in ('', ' ', 'REVIEW REQUIRED'):
            with self.subTest(reason=reason):
                state['reconciliation'] = {'O-1': dict(sources=[], action='close', reason=reason)}
                (result / 'docs/NOW.md').write_text(self.lc.render_now(state))
                with self.assertRaisesRegex(ValueError, 'reason'):
                    self.lc.check(result, [base, base], base, merge_result=True)

    def test_synthetic_merge_update_row_cannot_excuse_dropped_obligation(self):
        base = self.init('base', work={'O-1': 'Keep duty'})
        result = self.init(reconciliation={'O-1': dict(
            sources=['0' * 64], action='update', reason='Earlier settlement')})
        with self.assertRaisesRegex(ValueError, 'O-1'):
            self.lc.check(result, [base, base], base, merge_result=True)

    def test_synthetic_merge_base_only_obligation_cannot_disappear(self):
        base = self.init('base', work={'O-base': 'Base duty'})
        left, right, result = self.init('left'), self.init('right'), self.init()
        with self.assertRaisesRegex(ValueError, 'O-base'):
            self.lc.check(result, [left, right], base, merge_result=True)

    def test_synthetic_merge_settled_rows_are_not_source_obligations(self):
        base = self.init('base', reconciliation={'O-old': dict(
            sources=['0' * 64], action='close', reason='Completed earlier')})
        result = self.init()
        self.lc.check(result, [base, base], base, merge_result=True)

    def test_merge_template_requests_only_missing_ids_without_hashes(self):
        base = self.init('base', work={'O-kept': 'Original', 'O-closed': 'Finish', 'O-lost': 'Keep'})
        result = self.init(work={'O-kept': 'Edited'}, reconciliation={
            'O-closed': dict(action='close', reason='Finished')})
        proc = subprocess.run([sys.executable, '-B', str(SCRIPT), 'check', '--reconcile-template',
            '--root', str(result), '--parent', str(base), '--parent', str(base), '--base', str(base)],
            capture_output=True)
        self.assertEqual(proc.returncode, 0, proc.stderr.decode())
        template = json.loads(proc.stdout)
        self.assertEqual(template['reconciliation'], {
            'O-lost': dict(action='close', reason='REVIEW REQUIRED')})
        template['reconciliation']['O-lost']['reason'] = 'Review completed'
        template['reconciliation']['O-closed'] = dict(action='close', reason='Finished')
        self.lc.checkpoint(result, self.draft(work={'O-kept': 'Edited'}, **template),
                           self.lc.check(result)['content_sha256'])
        self.lc.check(result, [base, base], base, merge_result=True)

    def test_synthetic_merge_decision_and_lesson_drops_need_closing_lines(self):
        for key, kind in (('D-1', 'decision'), ('L-1', 'lesson')):
            with self.subTest(key=key):
                base = self.init('base-' + key, decisions=self.lc.render_decisions([
                    dict(id=key, kind=kind, status='accepted', scope='project',
                         supersedes='-', text='Keep rule')]))
                result = self.init('result-' + key)
                with self.assertRaisesRegex(ValueError, key):
                    self.lc.check(result, [base, base], base, merge_result=True)
                self.lc.checkpoint(result, self.draft(reconciliation={key: dict(
                    action='close', reason='Rule retired')}), self.lc.check(result)['content_sha256'])
                self.lc.check(result, [base, base], base, merge_result=True)

    def test_parent_union_reconciliation_and_base_only(self):
        base = self.init('base', work={'O-base': 'Base duty'})
        left = self.init('left', work={'O-left': 'Left duty'})
        right = self.init('right', work={'O-right': 'Right duty'})
        d = self.draft(work={'O-base': 'Base duty', 'O-left': 'Left duty', 'O-right': 'Right duty'})
        d.update(self.lc.reconciliation_template([left, right], base))
        for r in d['reconciliation'].values():
            r.update(action='keep', reason='Reviewed retained source')
        result = self.root / 'result'
        result.mkdir()
        self.lc.checkpoint(result, d, 'absent')
        self.lc.check(result, [left, right], base)
    def test_same_id_changed_text_needs_no_variant_accounting(self):
        base = self.init('base')
        left = self.init('left', work={'O-1': 'left'})
        right = self.init('right', work={'O-1': 'right'})
        d = self.draft(work={'O-1': 'left'})
        d.update(self.lc.reconciliation_template([left, right], base))
        d['reconciliation']['O-1'].update(action='keep', reason='Selected left')
        result = self.root / 'result'
        result.mkdir()
        self.lc.checkpoint(result, d, 'absent')
        self.lc.check(result, [left, right], base)

    def test_caps_and_synthetic_resurrection(self):
        root = self.init()
        handoff = root / 'docs/HANDOFF.md'
        handoff.write_bytes(b'x' * 512)
        self.lc.check(root)
        handoff.write_bytes(b'x' * 513)
        with self.assertRaisesRegex(ValueError, 'cap'):
            self.lc.check(root)
        marker = b'SYNTHETIC-HANDOFF\n'
        data = (marker * (420976 // len(marker) + 1))[:420976]
        self.assertTrue(data.startswith(marker))
        self.assertEqual(len(data), 420976)
        handoff.write_bytes(data)
        with self.assertRaisesRegex(ValueError, 'cap'):
            self.lc.check(root)

    def test_issue_and_extra_file_caps(self):
        root = self.init()
        issue = root / 'docs/issues/pinned.md'
        issue.parent.mkdir()
        issue.write_text('x' * 8193)
        with self.assertRaisesRegex(ValueError, 'cap'):
            self.lc.check(root)
        issue.unlink()
        (root / 'extra.md').write_text('x' * 8193)
        with self.assertRaisesRegex(ValueError, 'cap'):
            self.lc.context(root, files=['extra.md'])

    def test_checkpoint_failure_does_not_acknowledge_or_write(self):
        root = self.init()
        before = (root / 'docs/NOW.md').read_bytes()
        with self.assertRaises(ValueError):
            self.lc.checkpoint(root, self.draft(goal='x' * 4096), self.lc.check(root)['content_sha256'])
        self.assertEqual(before, (root / 'docs/NOW.md').read_bytes())
        with self.assertRaisesRegex(ValueError, 'expected'):
            self.lc.checkpoint(root, self.draft(), '0' * 64)

    def test_preserve_overflow_spills_to_named_work(self):
        root = self.init(preserve=['constraint ' + str(i) for i in range(11)])
        state = self.lc.check(root)
        self.assertEqual(len(state['preserve']), 10)
        self.assertIn('constraint 10', state['work'].values())

    def migration_plan(self):
        root = self.root / 'legacy'
        (root / 'docs').mkdir(parents=True)
        source = b'Active constraint\r\nOld history\r\nDecision: keep Unicode \xc5\xbc'
        (root / 'docs/HANDOFF.md').write_bytes(source)
        plan = self.lc.migration_plan(root)
        plan['review'] = {key: 'reviewed fixture' for key in self.lc.REVIEW_KEYS}
        plan['draft'] = self.draft()
        plan['sources']['docs/HANDOFF.md']['ranges'] = [
            dict(start=1, end=1, disposition='active', id='O-1', reason='still required'),
            dict(start=2, end=2, disposition='archived', reason='historical'),
            dict(start=3, end=3, disposition='active', id='D-1', reason='binding', scope='project')]
        prefix = 'docs/archive/' + self.lc.sha(b'docs/HANDOFF.md')[:16]
        plan['change'].remove(prefix + '-1.txt')
        plan['change'].append(prefix + '-2.txt')
        return root, source, plan

    def test_migration_extracts_active_facts_and_reconstructs(self):
        root, source, plan = self.migration_plan()
        before = sorted(p.relative_to(root) for p in root.rglob('*'))
        self.lc.migrate(root, plan, apply=False)
        self.assertEqual(before, sorted(p.relative_to(root) for p in root.rglob('*')))
        self.lc.migrate(root, plan, apply=True)
        self.assertEqual(self.lc.check(root)['work']['O-1'], 'Active constraint\r\n')
        self.assertEqual(self.lc.decision_rows(root)['D-1']['text'], 'Decision: keep Unicode ż')
        self.assertEqual(self.lc.archive_show(root, 'docs/HANDOFF.md', 1, 3).encode(), source)
        chunks = list((root / 'docs/archive').glob('*.txt'))
        self.assertEqual(b''.join(p.read_bytes() for p in chunks), b'Old history\r\n')
        snapshot = (root / 'docs/NOW.md').read_bytes()
        self.lc.migrate(root, plan, apply=True)
        self.assertEqual(snapshot, (root / 'docs/NOW.md').read_bytes())

    def test_migration_keeps_ordinary_docs_and_restores_only_selected_sources(self):
        root, source, _ = self.migration_plan()
        notes = b'REPO_NOTES=Keep this note\r\n  wrapped detail with Unicode \xc5\xbc\r\n\r\n'
        states = {
            'PROJECT_CONFIG.md': b'## Identity\r\nOWNER_NAME=Owner\r\n## Current Sprint (live state)\r\n' + notes + b'CURRENT_SPRINT=old\r\nDiscard sprint continuation\r\n## Privacy\r\nKeep local\r\n',
            'docs/HANDOFF.md': source,
            'docs/ROADMAP.md': b'Old roadmap\n',
            'docs/LESSONS_CANON.md': b'Old lesson\n',
        }
        for rel, raw in states.items():
            (root / rel).write_bytes(raw)
        for i in range(120):
            rel = 'docs/' + ('reports', 'specs', 'adr', 'runbooks')[i % 4] + '/' + str(i) + '.md'
            (root / rel).parent.mkdir(exist_ok=True)
            (root / rel).write_bytes(('Ordinary document %d\r\n' % i).encode())
        for rel in ('AGENTS.md', 'CLAUDE.md', 'docs/journal.jsonl', 'docs/register.tsv', 'docs/notes.txt'):
            (root / rel).write_bytes(b'Keep exactly\r\n')
        (root / 'docs/binary.dat').write_bytes(b'\xff\x00')
        before = {p.relative_to(root).as_posix(): self.lc.sha(p.read_bytes())
                  for p in root.rglob('*') if p.is_file() and p.relative_to(root).as_posix() not in states}
        plan = self.lc.migration_plan(root)
        self.assertEqual(set(plan['sources']), set(states))
        self.assertEqual(set(plan['keep']), set(before))
        plan['review'] = {key: 'reviewed fixture' for key in self.lc.REVIEW_KEYS}
        plan['draft'] = self.draft()
        for spec in plan['sources'].values():
            for entry in spec['ranges']:
                entry.update(disposition='archived', reason='reviewed history')
        # Kept files are informational, never a mandatory source inventory.
        plan.pop('keep')
        (root / 'docs/new-report.md').write_bytes(b'Created after inventory')
        before['docs/new-report.md'] = self.lc.sha(b'Created after inventory')
        reviewed = self.root / 'reviewed.json'
        reviewed.write_text(json.dumps(plan))
        proc = subprocess.run([sys.executable, '-B', str(SCRIPT), 'migrate', '--root', str(root),
                               '--plan', str(reviewed), '--apply'], capture_output=True)
        self.assertEqual(proc.returncode, 0, proc.stderr.decode())
        result = json.loads(proc.stdout)
        self.assertEqual(result['keep']['count'], len(before))
        self.assertIn('docs/HANDOFF.md', result['change']['paths'])
        self.assertEqual(before, {rel: self.lc.sha((root / rel).read_bytes()) for rel in before})
        config = (root / 'PROJECT_CONFIG.md').read_bytes()
        self.assertTrue(config.startswith(b'## Identity\r\nOWNER_NAME=Owner\r\n'))
        self.assertIn(b'## Privacy\r\nKeep local\r\n', config)
        self.assertNotIn(b'CURRENT_SPRINT=old', config)
        self.assertIn(b'CYKL_SCHEMA=3', config)
        self.assertIn(notes, config)
        self.assertNotIn(b'Discard sprint continuation', config)
        after_paths = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
        new_paths = after_paths - set(before) - set(states)
        self.assertTrue({'docs/NOW.md', 'docs/DECISIONS.md'} <= new_paths)
        self.assertTrue(all(rel in {'docs/NOW.md', 'docs/DECISIONS.md'}
                            or rel.startswith('docs/archive/') for rel in new_paths), new_paths)
        for rel in states.keys() - {'PROJECT_CONFIG.md'}:
            self.assertTrue((root / rel).read_bytes().startswith(b'# Migrated'))
        rows = [row for row in self.lc.manifest_rows(root) if row['type'] == 'source']
        self.assertEqual({row['source'] for row in rows}, set(states))
        dest = self.root / 'restored'
        self.lc.rollback(root, dest)
        self.assertEqual({p.relative_to(dest).as_posix(): p.read_bytes()
                          for p in dest.rglob('*') if p.is_file()}, states)
        self.assertEqual(before, {rel: self.lc.sha((root / rel).read_bytes()) for rel in before})

    def test_migration_case_variant_documents_are_kept_after_cli_apply(self):
        for variant in ('docs/handoff.md', 'docs/Handoff.md', 'docs/roadmap.md',
                        'docs/Lessons_Canon.md', 'Docs/HANDOFF.md'):
            with self.subTest(variant=variant), tempfile.TemporaryDirectory(dir=self.root) as temp:
                root = Path(temp)
                (root / variant).parent.mkdir(parents=True, exist_ok=True)
                original = b'Ordinary case-variant document\r\n'
                (root / variant).write_bytes(original)
                (root / 'PROJECT_CONFIG.md').write_text('OWNER_NAME=Owner\n')
                if variant == 'Docs/HANDOFF.md' and (root / 'docs').exists():
                    with self.assertRaisesRegex(ValueError, 'on-disk.*Docs/'):
                        self.lc.migration_plan(root)
                    self.assertEqual((root / variant).read_bytes(), original)
                    self.assertEqual(self.lc.sha((root / variant).read_bytes()), self.lc.sha(original))
                    self.assertEqual(self.lc.source_paths(root), ['PROJECT_CONFIG.md'])
                    self.assertIn(variant, self.lc.keep_paths(root, ['PROJECT_CONFIG.md']))
                    continue
                plan = self.lc.migration_plan(root)
                self.assertEqual(set(plan['sources']), {'PROJECT_CONFIG.md'})
                self.assertIn(variant, plan['keep'])
                plan['review'] = {key: 'reviewed' for key in self.lc.REVIEW_KEYS}
                for spec in plan['sources'].values():
                    for entry in spec['ranges']:
                        entry.update(disposition='archived', reason='history')
                reviewed = self.root / 'reviewed-case.json'
                reviewed.write_text(json.dumps(plan))
                proc = subprocess.run([sys.executable, '-B', str(SCRIPT), 'migrate',
                    '--root', str(root), '--plan', str(reviewed), '--apply'], capture_output=True)
                self.assertEqual(proc.returncode, 0, proc.stderr.decode())
                self.assertEqual((root / variant).read_bytes(), original)
                self.assertEqual(self.lc.sha((root / variant).read_bytes()), self.lc.sha(original))
                self.assertIn(variant, json.loads(proc.stdout)['keep']['paths'])

    def test_migration_case_variant_config_is_not_a_source_or_overwritten(self):
        root, _, plan = self.migration_plan()
        original = b'Ordinary config-named document\r\n'
        (root / 'project_config.md').write_bytes(original)
        self.assertEqual(self.lc.source_paths(root), ['docs/HANDOFF.md'])
        self.assertIn('project_config.md', self.lc.keep_paths(root, plan['sources']))
        if (root / 'PROJECT_CONFIG.md').exists():
            with self.assertRaisesRegex(ValueError, 'on-disk.*project_config.md'):
                self.lc.migration_plan(root)
            with self.assertRaisesRegex(ValueError, 'on-disk.*project_config.md'):
                self.lc.migrate(root, plan, apply=True)
        else:
            self.lc.migrate(root, plan, apply=True)
        self.assertEqual((root / 'project_config.md').read_bytes(), original)

    def test_migration_rejects_unselected_new_draft_paths(self):
        template, _, plan = self.migration_plan()
        for files in ({'docs/issues/x.md': 'Issue'}, {'docs/decisions/x.md': 'Decision'},
                      self.attempt_files(), {'docs/queue/results/x.md': 'Result'},
                      {'docs/sync/status.json': '{}'}, {'docs/sync/outbox/x.json': '{}'}):
            with self.subTest(paths=list(files)), tempfile.TemporaryDirectory(dir=self.root) as temp:
                root = Path(temp) / 'case'
                shutil.copytree(template, root)
                before = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
                plan['draft']['files'] = files
                plan['draft']['work'] = {'A-1': 'Task'} if 'docs/queue/T-1.json' in files else {}
                with self.assertRaisesRegex(ValueError, 'unselected'):
                    self.lc.migrate(root, plan, apply=True)
                self.assertEqual(before, {p.relative_to(root): p.read_bytes()
                                         for p in root.rglob('*') if p.is_file()})

    def test_migration_canonical_extra_source_cannot_select_case_variant(self):
        for canonical, variant in (('PROJECT_CONFIG.md', 'project_config.md'),
                                   ('docs/DECISIONS.md', 'docs/decisions.md'),
                                   ('docs/HANDOFF.md', 'docs/handoff.md'),
                                   ('docs/ROADMAP.md', 'docs/roadmap.md')):
            with self.subTest(path=variant), tempfile.TemporaryDirectory(dir=self.root) as temp:
                root = Path(temp) / 'legacy'
                (root / 'docs').mkdir(parents=True)
                state = 'PROJECT_CONFIG.md' if canonical == 'docs/HANDOFF.md' else 'docs/HANDOFF.md'
                (root / state).write_text('Legacy state\n')
                (root / variant).write_bytes(b'Ordinary document\r\n')
                before = {p.relative_to(root): self.lc.sha(p.read_bytes())
                          for p in root.rglob('*') if p.is_file()}
                output = Path(temp) / 'plan.json'
                proc = subprocess.run([sys.executable, '-B', str(SCRIPT), 'migrate',
                    '--root', str(root), '--output', str(output), '--extra-source', canonical],
                    capture_output=True)
                self.assertNotEqual(proc.returncode, 0)
                self.assertFalse(output.exists())
                if (root / canonical).exists():
                    self.assertIn(variant, proc.stderr.decode())
                    self.assertNotIn('explicit opt-in required: ' + canonical, proc.stderr.decode())
                self.assertEqual(before, {p.relative_to(root): self.lc.sha(p.read_bytes())
                                         for p in root.rglob('*') if p.is_file()})

    def test_migration_plan_rejects_sources_renamed_to_case_variants(self):
        for canonical, variant in (('PROJECT_CONFIG.md', 'project_config.md'),
                                   ('docs/DECISIONS.md', 'docs/decisions.md'),
                                   ('docs/HANDOFF.md', 'docs/handoff.md')):
            for authority in ('extra_sources', 'replacements'):
                with self.subTest(path=variant, authority=authority), tempfile.TemporaryDirectory(dir=self.root) as temp:
                    root = Path(temp)
                    (root / 'docs').mkdir()
                    (root / 'docs/HANDOFF.md').write_text('Legacy state\n')
                    (root / canonical).write_text('Reviewed source\n')
                    plan = self.lc.migration_plan(root, extra_sources=[canonical])
                    plan['review'] = {key: 'reviewed' for key in self.lc.REVIEW_KEYS}
                    for spec in plan['sources'].values():
                        for entry in spec['ranges']:
                            entry.update(disposition='archived', reason='history')
                    if authority == 'replacements':
                        plan['extra_sources'] = []
                        plan['replacements'][canonical] = ('CYKL_SCHEMA=3\n' if canonical == 'PROJECT_CONFIG.md'
                                                           else self.lc.INDEX_HEADER)
                    (root / canonical).rename(root / variant)
                    before = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
                    for apply in (False, True):
                        with self.assertRaises((ValueError, FileNotFoundError)):
                            self.lc.migrate(root, plan, apply=apply)
                        self.assertEqual(before, {p.relative_to(root): p.read_bytes()
                                                 for p in root.rglob('*') if p.is_file()})

    def test_migration_case_variants_are_not_managed_or_capped(self):
        root = self.root / 'legacy'
        (root / 'docs').mkdir(parents=True)
        (root / 'PROJECT_CONFIG.md').write_text('OWNER_NAME=Owner\n')
        kept = {'docs/handoff.md': b'x' * 1024,
                'docs/roadmap.md': b'x' * 8192,
                'docs/lessons_canon.md': b'<<<<<<< ordinary example\n=======\n>>>>>>> example\n'}
        for rel, raw in kept.items():
            (root / rel).write_bytes(raw)
        self.assertEqual(self.lc.managed(root), ['PROJECT_CONFIG.md'])
        plan = self.lc.migration_plan(root)
        plan['review'] = {key: 'reviewed' for key in self.lc.REVIEW_KEYS}
        for entry in plan['sources']['PROJECT_CONFIG.md']['ranges']:
            entry.update(disposition='archived', reason='history')
        reviewed = self.root / 'plan.json'
        command = [sys.executable, '-B', str(SCRIPT), 'migrate', '--root', str(root),
                   '--plan', str(reviewed), '--apply']
        plan['draft']['goal'] = 'x' * 4096
        reviewed.write_text(json.dumps(plan))
        failed = subprocess.run(command, capture_output=True)
        self.assertNotEqual(failed.returncode, 0)
        self.assertEqual({rel: self.lc.sha(raw) for rel, raw in kept.items()},
                         {rel: self.lc.sha((root / rel).read_bytes()) for rel in kept})
        plan['draft']['goal'] = 'Reviewed migration'
        reviewed.write_text(json.dumps(plan))
        applied = subprocess.run(command, capture_output=True)
        self.assertEqual(applied.returncode, 0, applied.stderr.decode())
        self.lc.check(root)
        self.lc.context(root)
        self.assertEqual({rel: self.lc.sha(raw) for rel, raw in kept.items()},
                         {rel: self.lc.sha((root / rel).read_bytes()) for rel in kept})
        self.assertTrue(set(kept) <= set(self.lc.keep_paths(root, plan['sources'])))

    def test_migration_change_set_must_match_edited_ranges(self):
        root, source, plan = self.migration_plan()
        plan['sources']['docs/HANDOFF.md']['ranges'] = [
            dict(start=1, end=1, disposition='archived', reason='first'),
            dict(start=2, end=3, disposition='archived', reason='rest')]
        before = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
        for apply in (False, True):
            with self.subTest(apply=apply), self.assertRaisesRegex(ValueError, 'change.*write set'):
                self.lc.migrate(root, plan, apply=apply)
            self.assertEqual(before, {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()})
        first = 'docs/archive/' + self.lc.sha(b'docs/HANDOFF.md')[:16] + '-1.txt'
        plan['change'].append(first)
        self.lc.migrate(root, plan, apply=True)
        self.assertEqual(set(plan['change']), {p.relative_to(root).as_posix()
                                             for p in root.rglob('*') if p.is_file()})
        self.assertEqual(self.lc.archive_show(root, 'docs/HANDOFF.md', 1, 3).encode(), source)

    def test_migration_change_set_rejects_missing_extra_and_invalid_declarations(self):
        root, _, plan = self.migration_plan()
        before = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
        for declared in (None, 'docs/HANDOFF.md', [], plan['change'] + ['docs/unused.md'],
                         plan['change'][:-1], plan['change'] + [123]):
            for apply in (False, True):
                with self.subTest(declared=declared, apply=apply), self.assertRaisesRegex(ValueError, 'change'):
                    self.lc.migrate(root, dict(plan, change=declared), apply=apply)
                self.assertEqual(before, {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()})

    def test_migration_draft_and_replacement_must_agree(self):
        root, _, _ = self.migration_plan()
        rel = 'docs/issues/journal.md'
        (root / rel).parent.mkdir()
        (root / rel).write_text('Original journal\n')
        plan = self.lc.migration_plan(root, extra_sources=[rel])
        plan['review'] = {key: 'reviewed' for key in self.lc.REVIEW_KEYS}
        for spec in plan['sources'].values():
            for entry in spec['ranges']:
                entry.update(disposition='archived', reason='history')
        plan['replacements'][rel] = 'Reviewed replacement\n'
        plan['draft']['files'] = {rel: 'Different draft\n'}
        before = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
        for apply in (False, True):
            with self.assertRaisesRegex(ValueError, 'draft.*replacement'):
                self.lc.migrate(root, plan, apply=apply)
            self.assertEqual(before, {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()})
        plan['draft']['files'][rel] = plan['replacements'][rel]
        self.lc.migrate(root, plan, apply=True)
        self.assertEqual((root / rel).read_text(), plan['replacements'][rel])

    def test_checkpoint_draft_cannot_write_through_case_alias(self):
        root = self.init()
        (root / 'docs/handoff.md').write_bytes(b'Ordinary kept document\n')
        before = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
        state = self.lc.check(root)
        if (root / 'docs/HANDOFF.md').exists():
            with self.assertRaisesRegex(ValueError, 'on-disk.*docs/handoff.md'):
                self.lc.checkpoint(root, self.draft(files={'docs/HANDOFF.md': 'overwrite'}), state['content_sha256'])
            self.assertEqual(before, {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()})

    def test_path_resolution_ignores_unrelated_symlinks(self):
        root = self.root / 'paths'
        (root / 'docs').mkdir(parents=True)
        (root / 'docs/handoff.md').write_text('Ordinary document')
        (root / 'alias').symlink_to(root / 'docs', target_is_directory=True)
        (root / 'dangling').symlink_to(root / 'absent')
        if (root / 'DOCS/HANDOFF.md').exists():
            self.assertEqual(self.lc.resolve_entry_path(root, 'DOCS/HANDOFF.md'), root / 'docs/handoff.md')
            with self.assertRaisesRegex(ValueError, 'on-disk.*docs/handoff.md'):
                self.lc.safe(root, 'DOCS/HANDOFF.md')
        with self.assertRaisesRegex(ValueError, 'symlink'):
            self.lc.resolve_entry_path(root, 'alias/handoff.md')

    def test_migration_validates_case_identity_in_every_plan_path_field(self):
        root, _, original = self.migration_plan()
        (root / 'docs/roadmap.md').write_text('Ordinary roadmap\n')
        before = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
        if (root / 'docs/ROADMAP.md').exists():
            for field in ('extra_sources', 'replacements', 'change', 'files'):
                with self.subTest(field=field):
                    plan = json.loads(json.dumps(original))
                    if field == 'files':
                        plan['draft']['files'] = {'docs/ROADMAP.md': 'Ignored state draft'}
                    elif field == 'replacements':
                        plan[field]['docs/ROADMAP.md'] = 'Unreviewed replacement'
                    else:
                        plan[field].append('docs/ROADMAP.md')
                    for apply in (False, True):
                        with self.assertRaisesRegex(ValueError, 'on-disk.*docs/roadmap.md'):
                            self.lc.migrate(root, plan, apply=apply)
                        self.assertEqual(before, {p.relative_to(root): p.read_bytes()
                                                 for p in root.rglob('*') if p.is_file()})

    def test_migration_rechecks_case_alias_outputs_under_writer_lock(self):
        root, source, plan = self.migration_plan()
        promote = self.lc.promote
        def introduce_alias(*args):
            (root / 'docs/decisions.md').write_text('New kept document\n')
            return promote(*args)
        probe = self.root / 'CaseProbe'
        probe.write_text('probe')
        if (self.root / 'caseprobe').exists():
            with patch.object(self.lc, 'promote', side_effect=introduce_alias):
                with self.assertRaisesRegex(ValueError, 'on-disk.*docs/decisions.md'):
                    self.lc.migrate(root, plan, apply=True)
            self.assertEqual((root / 'docs/decisions.md').read_text(), 'New kept document\n')
            self.assertEqual((root / 'docs/HANDOFF.md').read_bytes(), source)
            self.assertFalse((root / 'docs/NOW.md').exists())
            self.assertFalse((root / '.cykl/lock').exists())

    def test_migration_exact_case_variant_opt_in_preserves_rollback_spelling(self):
        root, _, _ = self.migration_plan()
        (root / 'docs/HANDOFF.md').rename(root / 'docs/handoff.md')
        original = (root / 'docs/handoff.md').read_bytes()
        plan = self.lc.migration_plan(root, extra_sources=['docs/handoff.md'])
        self.assertNotIn('docs/handoff.md', plan['keep'])
        plan['review'] = {key: 'reviewed' for key in self.lc.REVIEW_KEYS}
        for entry in plan['sources']['docs/handoff.md']['ranges']:
            entry.update(disposition='archived', reason='history')
        self.lc.migrate(root, plan, apply=True)
        destination = self.root / 'restore'
        self.lc.rollback(root, destination)
        self.assertEqual({p.relative_to(destination).as_posix(): p.read_bytes()
                          for p in destination.rglob('*') if p.is_file()}, {'docs/handoff.md': original})
        manifest = root / 'docs/archive/migration.jsonl'
        rows = [json.loads(line) for line in manifest.read_text().splitlines()]
        rows[1]['source'] = 'docs/HANDOFF.md'
        manifest.write_text(''.join(json.dumps(row) + '\n' for row in rows))
        if (root / 'docs/HANDOFF.md').exists():
            with self.assertRaisesRegex(ValueError, 'on-disk.*docs/handoff.md'):
                self.lc.rollback(root, self.root / 'bad-restore')
            self.assertFalse((self.root / 'bad-restore').exists())

    def test_migration_ignores_state_draft_files_and_honors_replacements(self):
        root, _, _ = self.migration_plan()
        (root / 'PROJECT_CONFIG.md').write_text('OWNER_NAME=Owner\n')
        (root / 'docs/ROADMAP.md').write_text('Roadmap\n')
        (root / 'docs/LESSONS_CANON.md').write_text('Lessons\n')
        plan = self.lc.migration_plan(root)
        plan['review'] = {key: 'reviewed' for key in self.lc.REVIEW_KEYS}
        for spec in plan['sources'].values():
            for entry in spec['ranges']:
                entry.update(disposition='archived', reason='history')
        plan['draft']['files'] = {rel: 'UNREVIEWED\n' for rel in (
            'PROJECT_CONFIG.md', 'docs/HANDOFF.md', 'docs/ROADMAP.md', 'docs/LESSONS_CANON.md')}
        plan['draft']['files']['PROJECT_CONFIG.md'] = 'CYKL_SCHEMA=3\nUNREVIEWED\n'
        plan['replacements'] = {'docs/ROADMAP.md': 'Reviewed roadmap\n'}
        self.lc.migrate(root, plan, apply=True)
        self.assertTrue((root / 'docs/HANDOFF.md').read_text().startswith('# Migrated'))
        self.assertTrue((root / 'docs/LESSONS_CANON.md').read_text().startswith('# Migrated'))
        self.assertEqual((root / 'docs/ROADMAP.md').read_text(), 'Reviewed roadmap\n')
        self.assertIn('OWNER_NAME=Owner', (root / 'PROJECT_CONFIG.md').read_text())
        self.assertNotIn('UNREVIEWED', (root / 'PROJECT_CONFIG.md').read_text())

    def test_migration_state_draft_files_cannot_create_missing_stubs(self):
        root, _, plan = self.migration_plan()
        plan['draft']['files'] = {'docs/ROADMAP.md': 'Injected roadmap',
                                  'docs/LESSONS_CANON.md': 'Injected lesson',
                                  'PROJECT_CONFIG.md': 'CYKL_SCHEMA=3\nINJECTED=1\n'}
        self.lc.migrate(root, plan, apply=True)
        self.assertFalse((root / 'docs/ROADMAP.md').exists())
        self.assertFalse((root / 'docs/LESSONS_CANON.md').exists())
        self.assertIn('CYKL_SCHEMA=3', (root / 'PROJECT_CONFIG.md').read_text())
        self.assertNotIn('INJECTED=1', (root / 'PROJECT_CONFIG.md').read_text())

    def test_migration_repo_notes_stop_at_keys_and_headings(self):
        root, _, _ = self.migration_plan()
        notes = b'REPO_NOTES=Keep first\r\nwrapped first\r\n'
        more_notes = b'REPO_NOTES=Keep second\r\nwrapped second\r\n'
        raw = (b'## Current Sprint\r\n' + notes + b'REPO_STATE=old\r\ndrop state detail\r\n'
               + more_notes + b'### Sprint detail\r\ndrop heading detail\r\n'
               b'## Last Completed Sprint\r\nKEEP_HISTORY=1\r\nGLOBAL_LESSONS_BASELINE=42\r\n')
        (root / 'PROJECT_CONFIG.md').write_bytes(raw)
        plan = self.lc.migration_plan(root)
        plan['review'] = {key: 'reviewed' for key in self.lc.REVIEW_KEYS}
        for spec in plan['sources'].values():
            for entry in spec['ranges']:
                entry.update(disposition='archived', reason='history')
        self.lc.migrate(root, plan, apply=True)
        config = (root / 'PROJECT_CONFIG.md').read_bytes()
        self.assertIn(notes, config)
        self.assertIn(more_notes, config)
        self.assertNotIn(b'drop state detail', config)
        self.assertNotIn(b'drop heading detail', config)
        self.assertIn(b'## Last Completed Sprint\r\nKEEP_HISTORY=1\r\nGLOBAL_LESSONS_BASELINE=42\r\n', config)
        dest = self.root / 'restored-notes'
        self.lc.rollback(root, dest)
        self.assertEqual((dest / 'PROJECT_CONFIG.md').read_bytes(), raw)

    def test_migration_selected_draft_file_remains_supported(self):
        root, _, _ = self.migration_plan()
        rel = 'docs/issues/x.md'
        (root / rel).parent.mkdir()
        (root / rel).write_text('Reviewed source\n')
        plan = self.lc.migration_plan(root, extra_sources=[rel])
        plan['review'] = {key: 'reviewed' for key in self.lc.REVIEW_KEYS}
        for spec in plan['sources'].values():
            for entry in spec['ranges']:
                entry.update(disposition='archived', reason='history')
        plan['draft']['files'] = {rel: 'Reviewed live issue\n'}
        self.lc.migrate(root, plan, apply=True)
        self.assertEqual((root / rel).read_text(), 'Reviewed live issue\n')

    def test_migration_inventory_refuses_unselected_output_collision(self):
        template, _, _ = self.migration_plan()
        for rel in ('docs/DECISIONS.md', 'docs/archive/migration.jsonl',
                    'docs/archive/' + self.lc.sha(b'docs/HANDOFF.md')[:16] + '-1.txt'):
            with self.subTest(path=rel), tempfile.TemporaryDirectory(dir=self.root) as temp:
                root = Path(temp) / 'case'
                shutil.copytree(template, root)
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b'Ordinary existing document')
                output = Path(temp) / 'collision-plan.json'
                with self.assertRaisesRegex(ValueError, 'unselected'):
                    self.lc.write_migration_plan(root, output)
                self.assertFalse(output.exists())
                self.assertEqual(path.read_bytes(), b'Ordinary existing document')
                path.unlink()

    def test_migration_refuses_non_directory_ancestors_without_writes(self):
        for blocker in ('docs/archive', 'docs'):
            for operation in ('inventory', 'dry-run', 'apply'):
                with self.subTest(blocker=blocker, operation=operation), tempfile.TemporaryDirectory(dir=self.root) as temp:
                    root = Path(temp)
                    (root / 'PROJECT_CONFIG.md').write_bytes(b'OWNER_NAME=Owner\r\n')
                    if blocker == 'docs/archive':
                        (root / 'docs').mkdir()
                        (root / 'docs/HANDOFF.md').write_bytes(b'Legacy handoff\r\n')
                    plan = self.lc.migration_plan(root)
                    plan['review'] = {key: 'reviewed' for key in self.lc.REVIEW_KEYS}
                    for spec in plan['sources'].values():
                        for entry in spec['ranges']:
                            entry.update(disposition='archived', reason='history')
                    (root / blocker).write_bytes(b'Keep this ordinary file\r\n')
                    before = {p.relative_to(root): self.lc.sha(p.read_bytes())
                              for p in root.rglob('*') if p.is_file()}
                    with self.assertRaisesRegex(ValueError, 'non-directory ancestor.*' + blocker):
                        if operation == 'inventory':
                            self.lc.migration_plan(root)
                        else:
                            self.lc.migrate(root, plan, apply=operation == 'apply')
                    self.assertEqual(before, {p.relative_to(root): self.lc.sha(p.read_bytes())
                                              for p in root.rglob('*') if p.is_file()})
                    self.assertFalse((root / '.cykl/lock').exists())
                    self.assertFalse((root / '.cykl/stage').exists())
                    self.assertFalse((root / '.cykl/recovery.json').exists())

    def test_migration_rechecks_non_directory_ancestors_under_writer_lock(self):
        root, source, plan = self.migration_plan()
        promote = self.lc.promote
        def introduce_blocker(*args):
            (root / 'docs/archive').write_bytes(b'Keep this ordinary file')
            return promote(*args)
        with patch.object(self.lc, 'promote', side_effect=introduce_blocker):
            with self.assertRaisesRegex(ValueError, 'non-directory ancestor.*docs/archive'):
                self.lc.migrate(root, plan, apply=True)
        self.assertEqual((root / 'docs/HANDOFF.md').read_bytes(), source)
        self.assertEqual((root / 'docs/archive').read_bytes(), b'Keep this ordinary file')
        self.assertFalse((root / 'PROJECT_CONFIG.md').exists())
        self.assertFalse((root / 'docs/NOW.md').exists())
        for rel in ('.cykl/lock', '.cykl/stage', '.cykl/recovery.json'):
            self.assertFalse((root / rel).exists())

    def test_migration_mid_promotion_failure_recovers_and_restores_originals(self):
        root, source, _ = self.migration_plan()
        originals = {'PROJECT_CONFIG.md': b'OWNER_NAME=Owner\r\nCURRENT_SPRINT=old\r\n',
                     'docs/HANDOFF.md': source, 'docs/ROADMAP.md': b'Old roadmap\r\n',
                     'docs/LESSONS_CANON.md': b'Old lessons\r\n'}
        for rel, raw in originals.items():
            (root / rel).write_bytes(raw)
        plan = self.lc.migration_plan(root)
        plan['review'] = {key: 'reviewed' for key in self.lc.REVIEW_KEYS}
        for spec in plan['sources'].values():
            for entry in spec['ranges']:
                entry.update(disposition='archived', reason='history')
        durable = self.lc.durable
        def crash(path, raw):
            if path.parent == root / 'docs/archive':
                raise OSError('simulated promotion failure')
            return durable(path, raw)
        with patch.object(self.lc, 'durable', side_effect=crash):
            with self.assertRaisesRegex(OSError, 'simulated promotion failure'):
                self.lc.migrate(root, plan, apply=True)
        for rel, raw in originals.items():
            self.assertNotEqual((root / rel).read_bytes(), raw)
        self.assertFalse((root / 'docs/NOW.md').exists())
        self.assertTrue((root / '.cykl/lock').exists())
        with patch.object(self.lc.os, 'kill', side_effect=ProcessLookupError):
            self.lc.recover(root)
        self.lc.check(root)
        for rel in ('.cykl/lock', '.cykl/recover.lock', '.cykl/stage', '.cykl/recovery.json'):
            self.assertFalse((root / rel).exists())
        live = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
        destination = self.root / 'restored'
        self.lc.rollback(root, destination)
        self.assertEqual(originals, {p.relative_to(destination).as_posix(): p.read_bytes()
                                    for p in destination.rglob('*') if p.is_file()})
        self.assertEqual(live, {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()})
        self.assertFalse((root / '.cykl/lock').exists())

    def test_migration_inventory_lists_archive_chunks_and_actual_write_set(self):
        root, _, _ = self.migration_plan()
        (root / 'docs/HANDOFF.md').write_text(('x' * 40000 + '\n') * 3)
        before = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
        output = self.root / 'inventory.json'
        summary = json.loads(self.lc.write_migration_plan(root, output))
        plan = json.loads(output.read_text())
        prefix = 'docs/archive/' + self.lc.sha(b'docs/HANDOFF.md')[:16]
        expected = {'PROJECT_CONFIG.md', 'docs/HANDOFF.md', 'docs/NOW.md', 'docs/DECISIONS.md',
                    'docs/archive/migration.jsonl', prefix + '-1.txt', prefix + '-2.txt', prefix + '-3.txt'}
        self.assertEqual(set(plan.get('change', [])), expected)
        self.assertEqual(set(summary['change']['paths']), expected)
        self.assertFalse(set(plan['change']) & set(plan['keep']))
        plan['review'] = {key: 'reviewed' for key in self.lc.REVIEW_KEYS}
        for spec in plan['sources'].values():
            for entry in spec['ranges']:
                entry.update(disposition='archived', reason='history')
        result = self.lc.migrate(root, plan, apply=True)
        self.assertEqual(set(result['change']['paths']), expected)
        after = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
        self.assertEqual(after - before, expected - before)

    def test_migration_extra_source_requires_opt_in_and_reconstructs(self):
        root, _, _ = self.migration_plan()
        rel = 'docs/reports/selected.txt'
        (root / rel).parent.mkdir()
        raw = b'Explicit historical source\r\n'
        (root / rel).write_bytes(raw)
        plan = self.lc.migration_plan(root, extra_sources=[rel])
        self.assertNotIn(rel, plan['keep'])
        plan['review'] = {key: 'reviewed' for key in self.lc.REVIEW_KEYS}
        plan['draft'] = self.draft()
        for spec in plan['sources'].values():
            for entry in spec['ranges']:
                entry.update(disposition='archived', reason='historical')
        plan['extra_sources'] = []
        with self.assertRaisesRegex(ValueError, 'opt-in'):
            self.lc.migrate(root, plan, apply=True)
        self.assertEqual((root / rel).read_bytes(), raw)
        plan['extra_sources'] = [rel]
        self.lc.migrate(root, plan, apply=True)
        self.assertTrue((root / rel).read_text().startswith('# Migrated'))
        dest = self.root / 'restored'
        self.lc.rollback(root, dest)
        self.assertEqual((dest / rel).read_bytes(), raw)

    def test_migration_instructions_require_explicit_replacement(self):
        root, _, _ = self.migration_plan()
        (root / 'AGENTS.md').write_bytes(b'Original instructions\r\n')
        plan = self.lc.migration_plan(root, extra_sources=['AGENTS.md'])
        plan['review'] = {key: 'reviewed' for key in self.lc.REVIEW_KEYS}
        plan['draft'] = self.draft()
        for spec in plan['sources'].values():
            for entry in spec['ranges']:
                entry.update(disposition='archived', reason='reviewed')
        with self.assertRaisesRegex(ValueError, 'instruction replacement'):
            self.lc.migrate(root, plan, apply=True)
        plan['replacements'] = {'AGENTS.md': 'Reviewed instructions\n'}
        self.lc.migrate(root, plan, apply=True)
        self.assertEqual((root / 'AGENTS.md').read_text(), 'Reviewed instructions\n')
        dest = self.root / 'restored'
        self.lc.rollback(root, dest)
        self.assertEqual((dest / 'AGENTS.md').read_bytes(), b'Original instructions\r\n')

    def test_migration_oversized_static_config_requires_reviewed_replacement(self):
        root, _, _ = self.migration_plan()
        raw = b'## Identity\n' + b'Keep static configuration\n' * 150
        (root / 'PROJECT_CONFIG.md').write_bytes(raw)
        plan = self.lc.migration_plan(root)
        plan['review'] = {key: 'reviewed' for key in self.lc.REVIEW_KEYS}
        plan['draft'] = self.draft()
        for spec in plan['sources'].values():
            for entry in spec['ranges']:
                entry.update(disposition='archived', reason='reviewed')
        with self.assertRaisesRegex(ValueError, 'PROJECT_CONFIG.md cap'):
            self.lc.migrate(root, plan, apply=True)
        self.assertEqual((root / 'PROJECT_CONFIG.md').read_bytes(), raw)
        plan['replacements']['PROJECT_CONFIG.md'] = 'CYKL_SCHEMA=3\nOWNER_NAME=Owner\n'
        self.lc.migrate(root, plan, apply=True)
        self.assertEqual((root / 'PROJECT_CONFIG.md').read_text(), plan['replacements']['PROJECT_CONFIG.md'])
        dest = self.root / 'restored'
        self.lc.rollback(root, dest)
        self.assertEqual((dest / 'PROJECT_CONFIG.md').read_bytes(), raw)

    def test_migration_cli_explicit_extra_source_inventory(self):
        root, _, _ = self.migration_plan()
        (root / 'docs/journal.txt').write_text('Opt in this journal\n')
        output = self.root / 'plan.json'
        proc = subprocess.run([sys.executable, '-B', str(SCRIPT), 'migrate', '--root', str(root),
                               '--output', str(output), '--extra-source', 'docs/journal.txt'], capture_output=True)
        self.assertEqual(proc.returncode, 0, proc.stderr.decode())
        plan = json.loads(output.read_text())
        self.assertEqual(plan['extra_sources'], ['docs/journal.txt'])
        self.assertIn('docs/journal.txt', plan['sources'])
        self.assertNotIn('docs/journal.txt', plan['keep'])

    def test_migration_generated_files_cannot_overwrite_kept_documents(self):
        root, _, plan = self.migration_plan()
        (root / 'docs/DECISIONS.md').write_bytes(b'Ordinary decision register')
        with self.assertRaisesRegex(ValueError, 'opt-in|unselected'):
            self.lc.migrate(root, plan, apply=True)
        self.assertEqual((root / 'docs/DECISIONS.md').read_bytes(), b'Ordinary decision register')
        (root / 'docs/DECISIONS.md').unlink()
        (root / 'AGENTS.md').write_bytes(b'Keep instructions')
        plan['draft']['files'] = {'AGENTS.md': 'Bypass replacement review'}
        with self.assertRaisesRegex(ValueError, 'replacement|unselected'):
            self.lc.migrate(root, plan, apply=True)
        self.assertEqual((root / 'AGENTS.md').read_bytes(), b'Keep instructions')

    def test_migration_requires_complete_review_and_source_hash(self):
        root, source, plan = self.migration_plan()
        plan['sources']['docs/HANDOFF.md']['ranges'].pop()
        with self.assertRaisesRegex(ValueError, 'coverage|range'):
            self.lc.migrate(root, plan, apply=True)
        self.assertEqual((root / 'docs/HANDOFF.md').read_bytes(), source)
        (root / 'docs/HANDOFF.md').write_bytes(source + b'drift')
        with self.assertRaisesRegex(ValueError, 'hash|changed'):
            self.lc.migrate(root, plan, apply=True)

    def test_symlink_and_lock_block_reads(self):
        root = self.init()
        (root / '.cykl/lock').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'lock'):
            self.lc.check(root)
        (root / '.cykl/lock').unlink()
        (root / 'docs/HANDOFF.md').symlink_to(self.root / 'outside')
        with self.assertRaisesRegex(ValueError, 'symlink'):
            self.lc.check(root)

    def test_decision_cycle_rejected(self):
        root = self.init()
        rows = [dict(id='D-1', kind='decision', status='superseded', scope='archived', supersedes='D-2', text='one'),
                dict(id='D-2', kind='decision', status='superseded', scope='archived', supersedes='D-1', text='two')]
        (root / 'docs/DECISIONS.md').write_text(self.lc.render_decisions(rows))
        with self.assertRaisesRegex(ValueError, 'cycle'):
            self.lc.decision_rows(root)

    def test_refusal_preserves_existing_recovery_evidence(self):
        root = self.init()
        stage = root / '.cykl/stage'
        stage.mkdir()
        (stage / 'evidence').write_text('must survive')
        descriptor = root / '.cykl/recovery.json'
        descriptor.write_text('review me')
        with self.assertRaisesRegex(ValueError, 'recovery material'):
            self.lc.checkpoint(root, self.draft(), self.lc.check(root)['content_sha256'])
        self.assertEqual((stage / 'evidence').read_text(), 'must survive')
        self.assertEqual(descriptor.read_text(), 'review me')

    def attempt_files(self, status='running'):
        return {
            'docs/queue/T-1.json': json.dumps(dict(attempt='A-1', issue_url='https://example.invalid/issues/1',
                revision='observed', base='code-base', allowed_paths=['src/'],
                excluded_paths=['docs/archive/', 'docs/DECISIONS.md'],
                acceptance='Tests pass', offline=True, task_budget_bytes=1000)),
            'docs/queue/attempts/A-1.json': json.dumps(dict(status=status, packet='docs/queue/T-1.json'))}

    def test_completed_attempt_can_leave_now_with_closure(self):
        root = self.init(work={'A-1': 'Deliver task'}, files=self.attempt_files('integrated'))
        old = self.lc.check(root)
        draft = self.draft(reconciliation={'A-1': dict(
            action='close', reason='Accepted test evidence')})
        self.lc.checkpoint(root, draft, old['content_sha256'])
        self.assertNotIn('A-1', self.lc.check(root)['work'])

    def test_recovery_ownership_is_exclusive(self):
        root = self.init()
        (root / '.cykl/recover.lock').write_text('other recovery owns promotion')
        with self.assertRaisesRegex(ValueError, 'recover'):
            self.lc.recover(root)
        self.assertTrue((root / '.cykl/recover.lock').exists())

    def test_interrupted_promotion_requires_verified_recovery(self):
        root = self.init()
        old = self.lc.check(root)
        original = self.lc.durable
        def crash(path, data):
            if path == root / 'docs/NOW.md':
                raise OSError('simulated power loss')
            return original(path, data)
        with patch.object(self.lc, 'durable', side_effect=crash):
            with self.assertRaisesRegex(OSError, 'simulated'):
                self.lc.checkpoint(root, self.draft(next='New action'), old['content_sha256'])
        with self.assertRaisesRegex(ValueError, 'lock'):
            self.lc.check(root)
        with patch.object(self.lc.os, 'kill', side_effect=ProcessLookupError):
            self.lc.recover(root)
        self.assertEqual(self.lc.check(root)['next'], 'New action')

    def test_recovery_refuses_unrelated_changed_target(self):
        root = self.init()
        old = self.lc.check(root)
        with patch.object(self.lc, 'finish_promotion', side_effect=OSError('stop')):
            with self.assertRaises(OSError):
                self.lc.checkpoint(root, self.draft(), old['content_sha256'])
        (root / 'docs/NOW.md').write_text('unrelated edit')
        with patch.object(self.lc.os, 'kill', side_effect=ProcessLookupError):
            with self.assertRaisesRegex(ValueError, 'target changed'):
                self.lc.recover(root)
        self.assertEqual((root / 'docs/NOW.md').read_text(), 'unrelated edit')

    def test_local_drop_requires_closure_with_reason(self):
        root = self.init(work={'O-1': 'Keep this obligation'})
        old = self.lc.check(root)
        with self.assertRaisesRegex(ValueError, 'O-1'):
            self.lc.checkpoint(root, self.draft(), old['content_sha256'])
        self.lc.checkpoint(root, self.draft(reconciliation={'O-1': dict(
            action='close', reason='Completed review')}), old['content_sha256'])
        self.assertNotIn('O-1', self.lc.check(root)['work'])

    def test_secret_hits_need_acknowledgement_and_archive_is_immutable(self):
        root, source, plan = self.migration_plan()
        path = root / 'docs/HANDOFF.md'
        path.write_bytes(source.replace(b'Old history', b'password=synthetic-value'))
        spec = plan['sources']['docs/HANDOFF.md']
        spec.update(sha256=self.lc.sha(path.read_bytes()), bytes=path.stat().st_size)
        with self.assertRaisesRegex(ValueError, 'acknowledgement'):
            self.lc.migrate(root, plan, apply=True)
        spec['acknowledgements'] = {'2': 'ACK-synthetic-review'}
        self.lc.migrate(root, plan, apply=True)
        chunk = next((root / 'docs/archive').glob('*.txt'))
        chunk.write_text('altered')
        with self.assertRaisesRegex(ValueError, 'hash'):
            self.lc.check(root)

    def test_context_budget_no_partial_output_and_history_projection(self):
        root = self.init()
        payload = self.lc.context(root)
        self.assertLessEqual(len(payload.encode()), 16384)
        rows = [dict(id='D-' + str(i), kind='decision', status='retired', scope='archived',
                     supersedes='-', text='Old history ' * 100) for i in range(1000)]
        (root / 'docs/DECISIONS.md').write_text(self.lc.render_decisions(rows))
        self.assertEqual(self.lc.context(root), payload)
        (root / 'extra1').write_text('x' * 8192)
        (root / 'extra2').write_text('x' * 8192)
        proc = subprocess.run([sys.executable, '-B', str(SCRIPT), 'context', '--root', str(root),
                               '--file', 'extra1', '--file', 'extra2'], capture_output=True)
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(proc.stdout, b'')
        self.assertLessEqual(len(proc.stderr), 1024)

    def test_context_many_long_rows_fail_soft_index(self):
        root = self.init()
        rows = [dict(id=('D-' if i % 2 else 'L-') + 'row%03d' % i, kind='decision' if i % 2 else 'lesson',
                     status='accepted', scope='project', supersedes='-',
                     text='First sentence %d. ' % i + 'Long body text. ' * 100) for i in range(300)]
        (root / 'docs/DECISIONS.md').write_text(self.lc.render_decisions(rows))
        (root / 'CLAUDE.md').write_text('c' * 4000)
        proc = subprocess.run([sys.executable, '-B', str(SCRIPT), 'context', '--root', str(root)], capture_output=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = proc.stdout.decode()
        self.assertLessEqual(len(proc.stdout), 16384)
        self.assertIn('[... truncated', out)
        shown = sum(1 for r in rows if r['id'] + ' ' in out)
        self.assertRegex(out, r'\[\.\.\. (\d+) more')
        self.assertEqual(shown + int(re.search(r'\[\.\.\. (\d+) more', out)[1]), 300)
        self.assertIn('First sentence 0.', out)
        self.assertNotIn('Long body text.', out)

    def test_preexisting_large_archive_is_kept_but_owned_chunk_cap_holds(self):
        root, _, plan = self.migration_plan()
        (root / 'docs/archive').mkdir()
        big = root / 'docs/archive/legacy-v2.txt'
        big.write_bytes(b'x' * 412519)
        self.lc.migrate(root, plan, apply=True)
        self.assertEqual(big.read_bytes(), b'x' * 412519)
        self.lc.check(root)
        chunk = next((root / 'docs/archive').glob('*-2.txt'))
        chunk.write_bytes(b'y' * 65537)
        with self.assertRaisesRegex(ValueError, 'cap exceeded'):
            self.lc.check(root)

    def test_manifest_row_deletion_or_planted_chunk_fails_check(self):
        root, _, plan = self.migration_plan()
        self.lc.migrate(root, plan, apply=True)
        manifest = root / 'docs/archive/migration.jsonl'
        original = manifest.read_text()
        lines = original.splitlines(keepends=True)
        sources = [i for i, l in enumerate(lines) if '"type": "source"' in l or '"type":"source"' in l]
        self.assertTrue(sources)
        manifest.write_text(''.join(l for i, l in enumerate(lines) if i != sources[0]))
        with self.assertRaisesRegex(ValueError, 'unlisted archive chunk'):
            self.lc.check(root)
        with self.assertRaisesRegex(ValueError, 'unlisted archive chunk'):
            self.lc.rollback(root, self.root / 'restored-deleted-row')
        manifest.write_text(original)
        self.lc.check(root)
        (root / 'docs/archive' / ('0' * 16 + '-1.txt')).write_text('planted')
        with self.assertRaisesRegex(ValueError, 'unlisted archive chunk'):
            self.lc.check(root)

    def test_row_text_cannot_forge_omitted_marker(self):
        row = dict(id='D-001', kind='decision', status='accepted', scope='project',
                   text='x [... 9 more selected rows not shown] y')
        self.assertNotIn('more selected rows not shown', self.lc.row_line(row))

    def test_context_rows_never_exceed_budget_and_count_is_exact(self):
        rows = [dict(id='D-%03d' % i, kind='decision', status='accepted', scope='project',
                     text='[... 0 more. body') for i in range(50)]
        for budget in range(0, 400):
            out = self.lc.context_rows(rows, budget)
            self.assertLessEqual(len(out.encode()), budget)
        out = self.lc.context_rows(rows, 600)
        shown = sum(1 for r in rows if r['id'] + ' ' in out)
        self.assertEqual(shown + int(re.findall(r'\[\.\.\. (\d+) more selected', out)[-1]), 50)
        self.assertNotIn('grep -c', out)
        root = self.init()
        (root / 'docs/DECISIONS.md').write_text(self.lc.render_decisions(rows))
        (root / 'CLAUDE.md').write_text('c' * 4000)
        (root / 'x1').write_text('x' * 5000)
        (root / 'x2').write_text('x' * 1000)
        self.lc.context(root, files=['x1', 'x2'])

    def test_package_templates_and_descriptions_are_capped(self):
        self.assertEqual(len(self.lc.package_check()), 8)

    def test_merge_of_migration_with_large_v2_config(self):
        base = self.root / 'base'
        base.mkdir()
        (base / 'PROJECT_CONFIG.md').write_text('Legacy configuration\n' * 500)
        left = self.init('left')
        right = self.root / 'right'
        right.mkdir()
        (right / 'PROJECT_CONFIG.md').write_text('Legacy configuration\n' * 500)
        (right / 'docs/archive').mkdir(parents=True)
        (right / 'docs/archive/legacy.txt').write_text('Old v2 archive')
        result = self.root / 'result'
        (result / 'docs/archive').mkdir(parents=True)
        (result / 'PROJECT_CONFIG.md').write_bytes((right / 'PROJECT_CONFIG.md').read_bytes())
        (result / 'docs/archive/legacy.txt').write_text('Old v2 archive')
        plan = self.lc.migration_plan(result)
        plan['review'] = {key: 'reviewed' for key in self.lc.REVIEW_KEYS}
        plan['draft'] = self.draft()
        plan['draft'].update(self.lc.reconciliation_template([left, right], base))
        # Whole-file replacement of oversized unstructured config now needs explicit review.
        plan['replacements']['PROJECT_CONFIG.md'] = 'CYKL_SCHEMA=3\nMIRROR=disabled\n'
        for source in plan['sources'].values():
            for entry in source['ranges']:
                entry.update(disposition='archived', reason='historical fixture')
        self.lc.migrate(result, plan, apply=True)
        self.lc.check(result, [left, right], base)
        (right / 'docs/archive/legacy.txt').write_text('Changed legacy bytes')
        with self.assertRaisesRegex(ValueError, 'archive'):
            self.lc.check(result, [left, right], base)

    def test_merge_resurrected_420kb_file_and_schema_deletion_fail(self):
        base = self.init('base')
        left = self.init('left')
        right = self.init('right')
        draft = self.draft()
        draft.update(self.lc.reconciliation_template([left, right], base))
        result = self.root / 'result'
        result.mkdir()
        self.lc.checkpoint(result, draft, 'absent')
        self.lc.check(result, [left, right], base)
        marker = b'SYNTHETIC-HANDOFF\n'
        (result / 'docs/HANDOFF.md').write_bytes((marker * 30000)[:420976])
        with self.assertRaisesRegex(ValueError, 'cap'):
            self.lc.check(result, [left, right], base)
        (result / 'docs/HANDOFF.md').unlink()
        (result / 'PROJECT_CONFIG.md').unlink()
        with self.assertRaisesRegex(ValueError, 'missing'):
            self.lc.check(result, [left, right], base)

    def test_attempt_status_change_needs_no_variant_accounting(self):
        base = self.init('base')
        left = self.init('left', work={'A-1': 'Task'}, files=self.attempt_files())
        right_files = self.attempt_files('paused')
        attempt_path = 'docs/queue/attempts/A-1.json'
        right_files[attempt_path] = json.dumps(dict(json.loads(right_files[attempt_path]),
            updated_at='2026-10-17T10:00:00Z'))
        right = self.init('right', work={'A-1': 'Task'}, files=right_files)
        result = self.root / 'result'
        result.mkdir()
        draft = self.draft(work={'A-1': 'Task'}, files=self.attempt_files())
        draft.update(self.lc.reconciliation_template([left, right], base))
        draft['reconciliation']['A-1'].update(action='keep', reason='Retain attempt')
        self.lc.checkpoint(result, draft, 'absent')
        self.lc.check(result, [left, right], base, merge_result=True)

    def test_live_attempt_cannot_be_closed(self):
        root = self.init(work={'A-1': 'Task'}, files=self.attempt_files())
        old = self.lc.check(root)
        draft = self.draft(reconciliation={'A-1': dict(
              action='close', reason='Premature closure')})
        with self.assertRaisesRegex(ValueError, 'live attempt'):
            self.lc.checkpoint(root, draft, old['content_sha256'])

    def test_large_acknowledgement_does_not_apply_before_output_failure(self):
        root, source, plan = self.migration_plan()
        plan['review']['privacy'] = 'x' * 16384
        with self.assertRaisesRegex(ValueError, 'cap'):
            self.lc.migrate(root, plan, apply=True)
        self.assertEqual((root / 'docs/HANDOFF.md').read_bytes(), source)
        self.assertFalse((root / 'docs/NOW.md').exists())

    def test_multibyte_now_cap_and_nested_instruction_cap(self):
        with self.assertRaisesRegex(ValueError, 'cap'):
            self.init(goal='ż' * 2048)
        root = self.init('other')
        (root / 'src').mkdir()
        (root / 'src/AGENTS.md').write_bytes(b'x' * 4097)
        with self.assertRaisesRegex(ValueError, 'cap'):
            self.lc.check(root)

    def test_legacy_cli_never_writes(self):
        root = self.init()
        old = (root / 'docs/NOW.md').read_bytes()
        proc = subprocess.run([sys.executable, str(SCRIPT.with_name('porzadek.py')), '--wykonaj', str(root)], capture_output=True)
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(old, (root / 'docs/NOW.md').read_bytes())

    def test_packet_requires_history_exclusions(self):
        for excluded in ([], ['docs/archive/'], ['docs/DECISIONS.md']):
            with self.subTest(excluded=excluded):
                files = self.attempt_files()
                packet = json.loads(files['docs/queue/T-1.json'])
                packet['excluded_paths'] = excluded
                files['docs/queue/T-1.json'] = json.dumps(packet)
                with self.assertRaisesRegex(ValueError, 'exclusions'):
                    self.init('case-' + str(len(excluded)) + str(len(str(excluded))),
                              work={'A-1': 'Task'}, files=files)

    def test_context_rejects_normalized_history_and_unlisted_decision_bodies(self):
        root = self.init()
        (root / 'docs/archive').mkdir()
        (root / 'docs/archive/old.txt').write_text('history')
        (root / 'docs/decisions').mkdir()
        (root / 'docs/decisions/D-hidden.md').write_text('unlisted history')
        for rel in ('./docs/archive/old.txt', 'docs//archive/old.txt',
                    './docs/DECISIONS.md', 'docs/decisions/D-hidden.md'):
            with self.subTest(path=rel), self.assertRaisesRegex(ValueError, 'projection|unlisted'):
                self.lc.context(root, files=[rel])

    def test_nested_git_checkouts_are_not_scanned(self):
        root = self.init()
        nested = root / '_worktrees/x'
        nested.mkdir(parents=True)
        (nested / '.git').write_text('gitdir: elsewhere')
        (nested / 'CLAUDE.md').write_text('x' * 21000)
        self.lc.check(root)
        self.lc.context(root)
        plain = root / 'sub'
        plain.mkdir()
        (plain / 'CLAUDE.md').write_text('x' * 21000)
        with self.assertRaises(ValueError):
            self.lc.check(root)

    def test_context_applies_active_packet_exclusions(self):
        files = self.attempt_files()
        packet = json.loads(files['docs/queue/T-1.json'])
        packet['excluded_paths'].append('restricted/')
        files['docs/queue/T-1.json'] = json.dumps(packet)
        root = self.init(work={'A-1': 'Task'}, files=files)
        (root / 'restricted').mkdir()
        (root / 'restricted/data.txt').write_text('excluded fixture')
        with self.assertRaisesRegex(ValueError, 'excluded'):
            self.lc.context(root, files=['./restricted/data.txt'])

    def test_decisions_add_preserves_large_index_without_returning_history(self):
        root = self.init()
        rows = [dict(id='L-' + str(i), kind='lesson', status='retired', scope='archived',
                     supersedes='-', text='SYNTHETIC HISTORY ' * 50) for i in range(200)]
        index = root / 'docs/DECISIONS.md'
        index.write_text(self.lc.render_decisions(rows))
        before = index.read_bytes()
        row = dict(id='L-new', kind='lesson', status='accepted', scope='project',
                   supersedes='-', text='New rule; precedent; operational test')
        path = self.root / 'row.json'
        path.write_text(json.dumps(row))
        old_hash = self.lc.check(root)['content_sha256']
        command = [sys.executable, '-B', str(SCRIPT), 'decisions', 'add', '--root', str(root),
                   '--input', str(path), '--expected', old_hash]
        proc = subprocess.run(command, capture_output=True)
        self.assertEqual(proc.returncode, 0, proc.stderr.decode())
        self.assertTrue(index.read_bytes().startswith(before))
        self.assertEqual(len(self.lc.decision_rows(root)), 201)
        self.assertIn(b'L-new', proc.stdout)
        self.assertNotIn(b'SYNTHETIC HISTORY', proc.stdout)
        self.assertLessEqual(len(proc.stdout), 16384)
        self.assertEqual(self.lc.check(root)['previous_sha256'], old_hash)
        self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)

    def test_migration_cli_plan_is_file_with_bounded_summary(self):
        root = self.root / 'legacy'
        (root / 'docs').mkdir(parents=True)
        (root / 'docs/HANDOFF.md').write_text('Synthetic state\n')
        for i in range(120):
            (root / ('docs/journal-' + str(i) + '-' + 'x' * 140 + '.md')).write_text('Synthetic journal\n')
        before = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
        output = self.root / 'plan.json'
        proc = subprocess.run([sys.executable, '-B', str(SCRIPT), 'migrate', '--root', str(root),
                               '--output', str(output)], capture_output=True)
        self.assertEqual(proc.returncode, 0, proc.stderr.decode())
        summary = json.loads(proc.stdout)
        self.assertEqual(summary['sources'], 1)
        self.assertEqual(summary['keep']['count'], 120)
        self.assertTrue(summary['keep']['truncated'])
        self.assertIn('docs/HANDOFF.md', summary['change']['paths'])
        self.assertEqual(summary['sha256'], self.lc.sha(output.read_bytes()))
        self.assertGreater(output.stat().st_size, 16384)
        self.assertLessEqual(len(proc.stdout), 16384)
        self.assertEqual(len(json.loads(output.read_text())['sources']), 1)
        self.assertEqual(len(json.loads(output.read_text())['keep']), 120)
        self.assertEqual(before, {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()})

    def test_rollback_cli_restores_exact_bytes_outside_live_tree(self):
        root, source, plan = self.migration_plan()
        self.lc.migrate(root, plan, apply=True)
        before = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
        dest = self.root / 'restored'
        command = [sys.executable, '-B', str(SCRIPT), 'migrate', '--root', str(root), '--rollback', '--dest']
        proc = subprocess.run(command + [str(dest)], capture_output=True)
        self.assertEqual(proc.returncode, 0, proc.stderr.decode())
        self.assertEqual((dest / 'docs/HANDOFF.md').read_bytes(), source)
        self.assertEqual(before, {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()})
        for bad in (root, root / 'nested', dest):
            with self.subTest(dest=bad):
                self.assertNotEqual(subprocess.run(command + [str(bad)], capture_output=True).returncode, 0)

    def test_workflow_replacement_or_deletion_fails_trusted_check(self):
        trusted = self.root / 'trusted'
        path = '.github/workflows/lifecycle-integrity.yml'
        (trusted / path).parent.mkdir(parents=True)
        (trusted / path).write_text('reviewed workflow fixture\n')
        for package in (False, True):
            root = self.init('candidate-' + str(package))
            if package:
                shutil.copytree(SCRIPT.parents[2], root / 'skills')
            (root / path).parent.mkdir(parents=True)
            (root / path).write_bytes((trusted / path).read_bytes())
            command = [sys.executable, '-B', str(SCRIPT), 'check', '--root', str(root),
                       '--trusted-root', str(trusted)] + (['--package'] if package else [])
            proc = subprocess.run(command, capture_output=True)
            self.assertEqual(proc.returncode, 0, proc.stderr.decode())
            (root / path).write_text('name: lifecycle-integrity\nrun: true\n')
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
            (root / path).unlink()
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)

    def test_checkpoint_acknowledgement_rereads_promoted_now(self):
        root = self.init()
        promote = self.lc.promote
        def corrupt_after_promotion(*args):
            promote(*args)
            (root / 'docs/NOW.md').write_text('changed after promotion')
        with patch.object(self.lc, 'promote', side_effect=corrupt_after_promotion):
            with self.assertRaisesRegex(ValueError, 'NOW'):
                self.lc.checkpoint(root, self.draft(), self.lc.check(root)['content_sha256'])

    def test_build_rejects_manifest_skill_version_mismatch(self):
        repo = SCRIPT.parents[3]
        root = self.root / 'package'
        root.mkdir()
        for name in ('skills', 'packaging', '.claude-plugin'):
            shutil.copytree(repo / name, root / name)
        shutil.copyfile(repo / 'build-plugin.sh', root / 'build-plugin.sh')
        manifest = root / '.claude-plugin/plugin.json'
        data = json.loads(manifest.read_text())
        data['version'] = '0.0.0'
        manifest.write_text(json.dumps(data))
        proc = subprocess.run(['bash', str(root / 'build-plugin.sh')], capture_output=True)
        self.assertNotEqual(proc.returncode, 0, proc.stdout.decode())
        self.assertIn(b'version', proc.stdout + proc.stderr)

    def test_decisions_add_refuses_duplicate_closed_id_and_oversized_row(self):
        root = self.init(work={'O-1': 'Keep'})
        row = dict(id='L-new', kind='lesson', status='accepted', scope='archived',
                   supersedes='-', text='Rule')
        self.lc.decisions_add(root, row, self.lc.check(root)['content_sha256'])
        before = (root / 'docs/DECISIONS.md').read_bytes()
        state = self.lc.check(root)
        with self.assertRaisesRegex(ValueError, 'already used'):
            self.lc.decisions_add(root, row, state['content_sha256'])
        with self.assertRaisesRegex(ValueError, 'cap'):
            self.lc.decisions_add(root, dict(row, id='L-big', text='x' * 2048), state['content_sha256'])
        self.assertEqual((root / 'docs/DECISIONS.md').read_bytes(), before)
        self.assertEqual(self.lc.check(root), state)
        draft = self.draft(work=state['work'], decisions=self.lc.INDEX_HEADER,
            reconciliation={'L-new': dict(action='close', reason='Retired rule')})
        self.lc.checkpoint(root, draft, state['content_sha256'])
        with self.assertRaisesRegex(ValueError, 'already used'):
            self.lc.decisions_add(root, row, self.lc.check(root)['content_sha256'])

    def test_decisions_add_obeys_writer_lock(self):
        root = self.init()
        state = self.lc.check(root)
        before = (root / 'docs/DECISIONS.md').read_bytes()
        (root / '.cykl/lock').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'lock'):
            self.lc.decisions_add(root, dict(id='L-new', kind='lesson', status='accepted',
                scope='project', supersedes='-', text='Rule'), state['content_sha256'])
        self.assertEqual((root / 'docs/DECISIONS.md').read_bytes(), before)
        self.assertEqual((root / '.cykl/lock').read_text(), '{}')

    def test_migration_plan_refuses_existing_live_and_symlink_outputs(self):
        root, _, _ = self.migration_plan()
        existing = self.root / 'reviewed.json'
        existing.write_bytes(b'keep reviewed plan')
        alias = self.root / 'alias'
        alias.symlink_to(root, target_is_directory=True)
        for output in (existing, root / 'plan.json', alias / 'plan.json'):
            with self.subTest(path=output), self.assertRaises((ValueError, OSError)):
                self.lc.write_migration_plan(root, output)
        self.assertEqual(existing.read_bytes(), b'keep reviewed plan')
        self.assertFalse((root / 'plan.json').exists())

    def test_rollback_large_source_and_corrupt_archive(self):
        root = self.root / 'legacy'
        (root / 'docs').mkdir(parents=True)
        source = ('SYNTHETIC ż history\r\n' * 5000).encode()
        (root / 'docs/HANDOFF.md').write_bytes(source)
        plan = self.lc.migration_plan(root)
        plan['review'] = {key: 'synthetic review' for key in self.lc.REVIEW_KEYS}
        plan['draft'] = self.draft()
        for entry in plan['sources']['docs/HANDOFF.md']['ranges']:
            entry.update(disposition='archived', reason='historical fixture')
        self.lc.migrate(root, plan, apply=True)
        dest = self.root / 'restore'
        result = self.lc.rollback(root, dest)
        self.assertLessEqual(len(result.encode()), 16384)
        self.assertEqual((dest / 'docs/HANDOFF.md').read_bytes(), source)
        next((root / 'docs/archive').glob('*.txt')).write_text('corrupted archive')
        with self.assertRaisesRegex(ValueError, 'hash'):
            self.lc.rollback(root, self.root / 'corrupt-restore')
        self.assertFalse((self.root / 'corrupt-restore').exists())

    def test_rollback_rejects_ancestor_symlink_and_destination_race(self):
        root, _, plan = self.migration_plan()
        self.lc.migrate(root, plan, apply=True)
        alias = self.root / 'alias'
        alias.symlink_to(self.root, target_is_directory=True)
        for dest in (self.root, alias / 'restore'):
            with self.subTest(path=dest), self.assertRaises(ValueError):
                self.lc.rollback(root, dest)
        dest = self.root / 'raced'
        original = self.lc.reconstruct
        calls = 0
        def race(*args):
            nonlocal calls
            calls += 1
            data = original(*args)
            if calls == 2:  # After live-tree validation and destination preflight.
                dest.mkdir()
                (dest / 'keep').write_text('other writer')
            return data
        with patch.object(self.lc, 'reconstruct', side_effect=race):
            with self.assertRaises((ValueError, FileExistsError)):
                self.lc.rollback(root, dest)
        self.assertEqual((dest / 'keep').read_text(), 'other writer')


    # Local edition, lead surfaces, package and installer (added in 3.1.0).
    def local(self, name='local', roadmap=ROADMAP, files=None, **kw):
        files = {'PROJECT_CONFIG.md': CONFIG + 'TASKS=local\n', 'docs/ROADMAP.md': roadmap,
                 'docs/issues/T-1.md': 'Body', **(files or {})}
        return self.init(name, files=files, **kw)

    def lead(self, name='lead', files=None, **kw):
        files = {'docs/lead/LEAD.md': '# LEAD\n', **(files or {})}
        return self.init(name, files=files, **kw)

    def test_tasks_absent_is_github_and_bogus_fails(self):
        root = self.init()
        self.assertIsNone(self.lc.config_value(root, 'TASKS'))
        self.lc.check(root)
        (root / 'PROJECT_CONFIG.md').write_text(CONFIG + 'TASKS=bogus\n')
        with self.assertRaisesRegex(ValueError, 'TASKS must be'):
            self.lc.check(root)

    def test_local_tasks_valid_and_roadmap_projected(self):
        root = self.local()
        self.lc.check(root)
        self.assertIn('- T-1 open First', self.lc.context(root))

    def test_local_tasks_reject_bad_roadmaps(self):
        cases = {'duplicate': '- T-1 open A\n- T-1 done B\n', 'status': '- T-1 started A\n',
                 'no title': '- T-1 open\n', 'missing file': '- T-1 open A\n- T-3 doing C\n'}
        for label, roadmap in cases.items():
            with self.subTest(label):
                with self.assertRaisesRegex(ValueError, 'ROADMAP task line|missing task file'):
                    self.lc.check(self.local('r-' + label.replace(' ', '-'), roadmap=roadmap))

    def test_local_packet_issue_url_must_be_task_file(self):
        files = self.attempt_files()
        with self.assertRaisesRegex(ValueError, 'local packet issue_url'):
            self.local('bad', work={'A-1': 'Deliver'}, files=files)
        packet = json.loads(files['docs/queue/T-1.json'])
        packet['issue_url'] = 'docs/issues/T-1.md'
        files['docs/queue/T-1.json'] = json.dumps(packet)
        self.lc.check(self.local('good', work={'A-1': 'Deliver'}, files=files))

    def test_threads_projected_capped_and_serialized(self):
        root = self.lead(files={'docs/lead/THREADS.md': '# THREADS\nlead-1 | lead | active\n'})
        self.assertIn('lead-1 | lead | active', self.lc.context(root))
        old = self.lc.check(root)
        for text, message in (('x' * 2049, 'cap exceeded'), ('<<<<<<< a\nb\n=======\nc\n>>>>>>> d\n', 'conflict marker')):
            with self.assertRaisesRegex(ValueError, message):
                self.lc.checkpoint(root, self.draft(files={'docs/lead/THREADS.md': text}), old['content_sha256'])
        self.lc.checkpoint(root, self.draft(files={'docs/lead/THREADS.md': '# THREADS\nlead-2\n'}), old['content_sha256'])
        with self.assertRaisesRegex(ValueError, 'expected checkpoint hash mismatch'):
            self.lc.checkpoint(root, self.draft(files={'docs/lead/THREADS.md': '# THREADS\nlead-3\n'}), old['content_sha256'])

    def test_lead_requires_model_reason_only_with_lead_profile(self):
        files = self.attempt_files()
        packet = json.loads(files['docs/queue/T-1.json'])
        packet['model'] = 'example-model'
        files['docs/queue/T-1.json'] = json.dumps(packet)
        self.init('plain', work={'A-1': 'Deliver'}, files=files)
        with self.assertRaisesRegex(ValueError, 'model_reason required'):
            self.lead(work={'A-1': 'Deliver'}, files=files)
        packet['model_reason'] = 'Fits the task'
        files['docs/queue/T-1.json'] = json.dumps(packet)
        self.lead('lead-ok', work={'A-1': 'Deliver'}, files=files)

    def test_lead_results_need_short_block_only_with_lead_profile(self):
        files = {'docs/queue/results/A-1.md': 'free text report'}
        self.init('plain', files=files)
        with self.assertRaisesRegex(ValueError, 'SHORT block'):
            self.lead(files=files)
        long = '=== SHORT ===\n' + '\n'.join('l' * 3 for _ in range(9))
        with self.assertRaisesRegex(ValueError, 'SHORT block'):
            self.lead('long', files={'docs/queue/results/A-1.md': long})
        self.lead('ok', files={'docs/queue/results/A-1.md': '=== SHORT ===\n' + 'ok\n' * 8})

    def package(self, extra=(), drop=()):
        skills = self.root / 'pkg/skills'
        shutil.copytree(REPO / 'skills', skills)
        for name in drop:
            shutil.rmtree(skills / name)
        for name in extra:
            (skills / name).mkdir()
            (skills / name / 'SKILL.md').write_text(
                '---\nname: x\ndescription: "x"\n---\n<!-- cykl-lifecycle v%s -->\n' % self.lc.VERSION)
        return self.root / 'pkg'

    def test_package_accepts_core_plus_optional_lead_only(self):
        self.assertEqual(len(self.lc.package_check(self.package())), 8)
        shutil.rmtree(self.root / 'pkg')
        self.assertEqual(len(self.lc.package_check(self.package(drop=['cykl-prowadzacy']))), 7)
        shutil.rmtree(self.root / 'pkg')
        with self.assertRaisesRegex(ValueError, 'seven core'):
            self.lc.package_check(self.package(drop=['cykl-roadmap']))
        shutil.rmtree(self.root / 'pkg')
        with self.assertRaisesRegex(ValueError, 'seven core'):
            self.lc.package_check(self.package(extra=['cykl-extra']))

    def test_lead_skill_and_templates_are_capped_and_brief_is_valid(self):
        lead = REPO / 'skills/cykl-prowadzacy'
        for path in [lead / 'SKILL.md'] + list((lead / 'assets').iterdir()):
            self.assertLessEqual(path.stat().st_size, 4096, path.name)
        brief = json.loads((lead / 'assets/BRIEF.template.json').read_text())
        files = {'docs/queue/T-1.json': json.dumps(brief),
                 'docs/queue/attempts/A-1.json': json.dumps(dict(status='running', packet='docs/queue/T-1.json')),
                 'docs/queue/results/A-1.md': '=== SHORT ===\nDone'}
        self.lead(work={'A-1': 'Deliver'}, files=files)

    def test_public_texts_carry_no_private_markers(self):
        pattern = re.compile(r'bidsentinel|northstar|przetarg|witczak|micha[lł]|/users/|\bO\d{2,}\b|\bD\d{3,}\b', re.I)
        paths = [REPO / 'README.md'] + [p for d in ('docs', 'skills') for p in (REPO / d).rglob('*') if p.is_file() and p.suffix in ('.md', '.json', '.py', '.txt')]
        for path in paths:
            if 'reports' in path.parts or path.name.startswith('test_'):
                continue
            self.assertIsNone(pattern.search(path.read_text().replace('witczakm/cykl-lifecycle', '').replace('Michał — personal plugins', '')), str(path))  # marketplace name kept: shipped since 2.4.0

    def test_version_stamped_consistently(self):
        version = self.lc.VERSION
        for rel in ('.claude-plugin/plugin.json', '.codex-plugin/plugin.json'):
            self.assertEqual(json.loads((REPO / rel).read_text())['version'], version)
        market = json.loads((REPO / 'marketplace.json').read_text())
        self.assertEqual(market['plugins'][0]['version'], version)
        self.assertTrue((REPO / 'README.md').read_text().startswith('# cykl-lifecycle ' + version))
        self.assertIn('## [' + version + ']', (REPO / 'CHANGELOG.md').read_text())

    def test_forward_compat_with_previous_validator(self):
        proc = subprocess.run(['git', '-C', str(REPO), 'show', 'v3.0.1:skills/cykl-start/scripts/lifecycle.py'],
                              capture_output=True)
        self.assertEqual(proc.returncode, 0, 'v3.0.1 tag required')
        old = self.root / 'old_lifecycle.py'
        old.write_bytes(proc.stdout)
        root = self.local('compat', files={'docs/lead/LEAD.md': '# LEAD\n', 'docs/lead/THREADS.md': '# THREADS\n'})
        run = subprocess.run([sys.executable, '-B', str(old), 'check', '--root', str(root)], capture_output=True)
        self.assertEqual(run.returncode, 0, run.stderr.decode())

    def test_installer_editions_from_local_skills(self):
        for edition, count in (('core', 7), ('multi', 8)):
            home = self.root / ('home-' + edition)
            (home / '.claude/skills/cykl-stale').mkdir(parents=True)
            run = subprocess.run(['bash', str(REPO / 'install.sh'), 'claude', '--edition', edition],
                                 capture_output=True, env={'HOME': str(home), 'PATH': '/usr/bin:/bin',
                                 'CYKL_SKILLS_DIR': str(REPO / 'skills')})
            self.assertEqual(run.returncode, 0, run.stderr.decode())
            installed = sorted((home / '.claude/skills').glob('cykl-*'))
            self.assertEqual(len(installed), count)
            self.assertFalse((home / '.claude/skills/cykl-stale').exists())


if __name__ == '__main__':
    unittest.main()

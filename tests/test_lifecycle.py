import importlib.util
import json
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/cykl-start/scripts/lifecycle.py'


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

    def test_package_templates_and_descriptions_are_capped(self):
        self.assertEqual(len(self.lc.package_check()), 7)

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
        for i in range(120):
            (root / ('docs/journal-' + str(i) + '.md')).write_text('Synthetic journal\n')
        before = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
        output = self.root / 'plan.json'
        proc = subprocess.run([sys.executable, '-B', str(SCRIPT), 'migrate', '--root', str(root),
                               '--output', str(output)], capture_output=True)
        self.assertEqual(proc.returncode, 0, proc.stderr.decode())
        summary = json.loads(proc.stdout)
        self.assertEqual(summary['sources'], 120)
        self.assertEqual(summary['sha256'], self.lc.sha(output.read_bytes()))
        self.assertGreater(output.stat().st_size, 16384)
        self.assertLessEqual(len(proc.stdout), 16384)
        self.assertEqual(len(json.loads(output.read_text())['sources']), 120)
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


if __name__ == '__main__':
    unittest.main()

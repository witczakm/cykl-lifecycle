# Merge protection (GitHub and GitHub + multi-agent editions)
**English** · [Polski](MERGE-PROTECTION.pl.md)

[Hook sample](../hooks/pre-commit.sample) checks the complete staged tree, not the worktree.
It can be bypassed and does not replace [lifecycle-integrity](../.github/workflows/lifecycle-integrity.yml).
The Action uses a trusted validator and checks the test merge against **both parents and
merge-base**, including decisions, obligations, explicit closures and immutable archives.
The Action uses `--merge-result`: it validates the union of both parents and merge-base
without requiring NOW to name GitHub's synthetic commit parents. Every O/A/D/L ID in
either parent or merge-base must remain in work/DECISIONS or have an explicit closing
line in merged NOW (ID, close/supersede action and reason). Record text, metadata,
ordering, timestamps, settled rows and historical source hashes are not compared.
One-sided changes and changes on both sides pass when the ID union is retained or closed,
as does a later PR after a settled update. Silently dropping another side's obligation fails.
Without `--merge-result`, explicit parent/base UUID checks remain available for a
separately authored reconciliation checkpoint against its source snapshots.

For each adopting repository: install the validator at the same path, bootstrap a reviewed
trusted revision (optionally `LIFECYCLE_VALIDATOR_REF` repository variable), require the
`lifecycle-integrity` check, prohibit ordinary bypass/direct pushes, require up-to-date PRs
or merge queue. `--trusted-root` compares the candidate workflow's SHA-256 with the
trusted checkout and rejects replacement or deletion in project and package checks.
Bootstrap workflow and validator together; a workflow upgrade requires an authorized
update of the trusted version, not a PR-provided expected hash.

**External enforcement is required:** configure a required workflow whose definition
and revision are controlled outside the PR. If that policy is unavailable, require
CODEOWNERS approval for `.github/workflows/**`, `.github/CODEOWNERS`, and the trusted
validator path, dismiss stale approvals after new commits, and disallow ordinary bypass.
Protect changes to `LIFECYCLE_VALIDATOR_REF` as well. A same-name no-op job can remove
its own hash check; the hash comparison alone cannot prevent that attack.
Test canaries that replace/delete the workflow and restore HANDOFF over 512 bytes;
verify a non-admin cannot merge them. Record ruleset ID and canary evidence in
PROJECT_CONFIG. Until then report **merge protection unverified**. This offline release
has not configured any remote repository or tested GitHub event execution.

Local tree checks need no git inside Python:

```sh
python3 "$LIFECYCLE" check --merge-result --root result --parent left --parent right --base merge-base
```

To prepare parent/base identity and closure entries for missing IDs, replace
`--merge-result` with `--reconcile-template`. Merge its JSON into a checkpoint draft;
restore each missing ID or replace its REVIEW REQUIRED reason with the reason for closure.
No source hashes are needed. Existing hash lists are accepted without comparison.
Terminal attempts may leave NOW only after integrated/abandoned status and explicit closure.

The caller must export the real tested trees; arbitrary directories are not proof of ancestry.

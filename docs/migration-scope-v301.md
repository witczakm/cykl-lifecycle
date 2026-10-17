# Migration scope in 3.0.1

The default list is closed, derived from v2 commit
`e285f95e8161b7cc47ec2dd9af60a3b2985106d6` (v2.8.2). The snapshot was read locally;
no git command or network access was used for this patch.

The authoritative enumeration is
[`skills/cykl-start/scripts/porzadek.py:36`](https://github.com/witczakm/cykl-lifecycle/blob/e285f95e8161b7cc47ec2dd9af60a3b2985106d6/skills/cykl-start/scripts/porzadek.py#L36):
`DOKUMENTY = ["PROJECT_CONFIG.md", "docs/HANDOFF.md", "docs/ROADMAP.md", "docs/LESSONS_CANON.md"]`.
The v2 kickoff structure independently names exactly these four state files at
[`references/struktura-projektu.md:35–42`](https://github.com/witczakm/cykl-lifecycle/blob/e285f95e8161b7cc47ec2dd9af60a3b2985106d6/skills/cykl-kickoff/references/struktura-projektu.md#L35).

| Default source | Specific v2 evidence | 3.0.1 treatment |
|---|---|---|
| `PROJECT_CONFIG.md` | [`cykl-migawka/SKILL.md:24–25`](https://github.com/witczakm/cykl-lifecycle/blob/e285f95e8161b7cc47ec2dd9af60a3b2985106d6/skills/cykl-migawka/SKILL.md#L24); [`PROJECT_CONFIG.template.md:26–40`](https://github.com/witczakm/cykl-lifecycle/blob/e285f95e8161b7cc47ec2dd9af60a3b2985106d6/skills/cykl-kickoff/assets/PROJECT_CONFIG.template.md#L26) | Replace Current Sprint section; preserve static sections and `REPO_NOTES=`. Append v3 schema fields. Review the whole source for reconstruction. |
| `docs/HANDOFF.md` | [`cykl-migawka/SKILL.md:22`](https://github.com/witczakm/cykl-lifecycle/blob/e285f95e8161b7cc47ec2dd9af60a3b2985106d6/skills/cykl-migawka/SKILL.md#L22) defines the overwritten Snapshot | Reviewed extraction/archive, then pointer stub or explicit replacement. |
| `docs/ROADMAP.md` | [`cykl-migawka/SKILL.md:23`](https://github.com/witczakm/cykl-lifecycle/blob/e285f95e8161b7cc47ec2dd9af60a3b2985106d6/skills/cykl-migawka/SKILL.md#L23); [`cykl-zamknij/SKILL.md:58`](https://github.com/witczakm/cykl-lifecycle/blob/e285f95e8161b7cc47ec2dd9af60a3b2985106d6/skills/cykl-zamknij/SKILL.md#L58) | Reviewed extraction/archive, then pointer stub or explicit replacement. |
| `docs/LESSONS_CANON.md` | [`cykl-lekcja/SKILL.md:30–35`](https://github.com/witczakm/cykl-lifecycle/blob/e285f95e8161b7cc47ec2dd9af60a3b2985106d6/skills/cykl-lekcja/SKILL.md#L30) defines lesson insertion and changelog updates | Reviewed extraction/archive, then pointer stub or explicit replacement. |

No separate decision-register or journal filename is defined as lifecycle state in
this snapshot. Decisions and intermediate history reside in the state files or their
changelogs. The v2 structure explicitly distinguishes state from knowledge documents:
[`struktura-projektu.md:46–53`](https://github.com/witczakm/cykl-lifecycle/blob/e285f95e8161b7cc47ec2dd9af60a3b2985106d6/skills/cykl-kickoff/references/struktura-projektu.md#L46)
places ADRs under `docs/adr/`, registers under `docs/specs/`, and runbooks/reports in
their own directories. These are KEEP, as are project-specific journals and prior
archives. No filename pattern such as `*decision*`, `*journal*` or recursive suffix
scan grants migration authority. Root AGENTS/CLAUDE are also KEEP.

Each component of every selected or written path must match the directory-entry
spelling exactly, including on case-insensitive volumes. One shared resolver walks
the components with `scandir`; default selection, opt-ins, plan validation, managed
file caps, draft writes, promotion and rollback all use that identity. Case variants
are ordinary kept documents and do not inherit state-file caps or marker checks.
If `project_config.md` aliases the required `PROJECT_CONFIG.md`, inventory/apply
refuses without changing it and reports the on-disk spelling. Opting into the
canonical spelling cannot authorize that alias. The same rule applies to output
collisions such as `docs/decisions.md` and parent directories such as `Docs/`.
Resolve such collisions outside migration before generating a new plan.

Use `--extra-source PATH` when generating a plan to add an exact path to
`extra_sources` and obtain its review metadata in `sources`. Each selected source
needs complete reviewed ranges and a matching hash. An explicit `replacements[PATH]`
also authorizes that source, but does not waive its metadata/range review. Instructions
always need a replacement. Every selected source retains exact reconstruction and
rollback, including extras and replaced instructions. Kept files are neither archived
nor rewritten and need not be listed in the reviewed plan.

Migration ignores `draft.files` entries for all four legacy state paths; their
live content comes only from the migration projection/stub or `replacements`.
Every other `draft.files` key must name a selected, reviewed source. New persistent
files are limited to `docs/NOW.md`, `docs/DECISIONS.md`, `docs/archive/*`, and a
missing `PROJECT_CONFIG.md`. Checkpoint's broader write support grants no extra
authority to migration. If a non-state source has both a draft file and a replacement,
their UTF-8 bytes must agree; otherwise dry-run and apply refuse.

CONFIG's complete original bytes are recorded for rollback, even though its static
sections remain in place. If preserving them exceeds v3's existing 2 KB cap, apply
fails before promotion; only an explicit bounded replacement can resolve that case.
The patch does not expand v3 validation caps or guess unrecognized state sections.
Within Current Sprint, `REPO_NOTES=` and its following lines are retained byte for
byte until the next `KEY=` line or Markdown heading.

The plan contains full `sources`, `change`, and informational `keep` paths. Inventory and
validation/apply stdout contain change/keep counts and previews (eight paths, each
up to 160 characters, with `truncated` flags). Inventory includes manifest and archive
chunk paths, assuming unresolved ranges will be archived. After editing ranges or
dispositions, reviewers must update the full `change` list in the plan they approve.
Dry-run and apply recompute the actual write set and refuse unless it equals
`set(plan['change'])`, including archive chunks and the manifest. Chunk names are
`docs/archive/<first 16 hex digits of SHA-256 of the exact source path>-<first line>.txt`;
archived ranges split into chunks of at most 65,536 UTF-8 bytes. Active ranges create
no archive chunk. Neither a missing nor an extra declared path is accepted. Existing output
collisions are rejected during inventory, before apply, and again under the writer
lock. Old broad plans must be
regenerated or explicitly narrowed; their ordinary source entries alone grant no
permission to rewrite documentation.

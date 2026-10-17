# Implementation-review repair pre-check

Question: distinguish synthetic merge validation from checkpoint ancestry, and repair
the workflow trust and operator contracts with the smallest local changes.
Existing evidence: lifecycle.py, the workflow, synthetic tests, and the supplied review.
Owner constraints: fix all findings; stdlib only; no Git, network or private fixtures.
Source quantities: two parents and one base; stdout cap 16,384 bytes; index row cap
2,048 bytes, all taken from the existing contract. No speculative measurements used.

The isolated marshal selected a lifecycle invariant architect, a CI trust-boundary
adversary, and a recovery/operator reviewer. Each answered independently and then ranked
anonymized peer findings. All actual model identifiers were reported as unknown; this
is an advisory panel within one provider, not an independent cross-model approval.
Confidence judgments were 94/100, 97/100 and 90/100 respectively, not measured accuracy.

Recommendation: use explicit synthetic-merge mode to skip only tip UUID equality,
retain union accounting and archive immutability, compare workflow hashes to a trusted
tree, and require externally enforced workflow/ownership policy. Add a locked row append,
external plan file, and executable exact-byte source reconstruction into a new directory.

Dissent and tradeoffs: the architect favors minimal validator changes; the adversary
rejects treating any editable workflow self-check as protection against its replacement.
This is a trust-boundary error caught by the adversary, not a claim that the hash comparison
is useless. There is also a compatibility-versus-preservation tension: a one-sided
metadata edit or added ID can pass, while changed record text still needs reconciliation.
We preserve that stricter accounting contract instead of adding an implicit three-way
semantic merge. The recovery reviewer identified a destination race in ordinary rename;
the implementation must reserve a new destination exclusively.

Unknowns: external ruleset configuration, GitHub event execution and blocked canaries
cannot be verified under the offline constraint. Restoring migration sources is not a
complete historical checkout rollback. Abrupt termination may leave a partial export
directory; it must never overwrite the live tree or an existing recovery directory.

Next action: implement the local checks and run synthetic regressions plus package build.
Wynik po fakcie: 46 unittest cases passed; the named drop test caught an in-memory
mutation disabling missing-ID accounting. Package lint and build passed; nine archives
matched their sources and version markers. Remote protection remains unverified.

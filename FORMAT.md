# Spec format

The contract for this repository is written in plain English and edited by hand. `SPEC.md` at the
repository root is its index. The goal and the constraints live in `AGENTS.md`, because every
agent loads that file at session start. Everything else lives in `spec/`, one file per topic.

`tests/test_spec_hygiene.py` parses these files by their entry headings. An entry the test cannot
parse is invisible to it, so the formats below are rules.

## Files

| File | Holds | Entry heading |
|---|---|---|
| `AGENTS.md` | goal (§G) and constraints (`- C<n>: …` bullets under `## Constraints`) | none |
| `spec/invariants/<area>.md` | testable invariants for one area | `### V<n> — <claim>` |
| `spec/bugs.md` | the bug log | `### B<n> — <title>` |
| `spec/data-model.md` (full form) | the data model | `### D.<n> — <title>` |
| `spec/interfaces.md` (full form) | commands, protocols, entry points, files | `### I.<n> — <title>` |
| `spec/tasks.md` (full form) | the build order | `### T<n> — <title>` |
| `spec/open-questions.md` (full form) | questions awaiting a maintainer decision | `### O<n> — <title>` |

The heading separator is an em dash with a space on each side (` — `).

## Entries

**Invariant.** One testable claim, with its reasoning only where applying the claim needs it. End
with `Test: tests/<file>::<test>` where a test exists. At most 1,200 characters, heading included.
Every invariant must be cited from a file under `tests/` (as `§V.<n>`), or be listed in
`UNTESTED_INVARIANTS` with a written reason. A new area file must be linked from `SPEC.md`.

**Task.** The heading, then:

```
**Status:** to do | in progress | done
**Refs:** V12,T13,B4
```

and a paragraph. Open tasks sit under `## Open` and done tasks under `## Done`, each in id order. A
done task keeps its claim, its key numbers and a pointer to `notes/` or the commit; it is at most 900
characters. Every id in **Refs** must exist.

**Bug.** The heading, then `**Date:** YYYY-MM-DD · **Status:** fixed | open · **Caught by:** V12`,
then the cause and the transferable rule. **Caught by** must name at least one existing invariant:
the invariant that catches recurrence is the purpose of the entry. At most 1,300 characters; the
reproduction belongs in the fixing commit.

**Open question.** The heading and a paragraph. An answered question leaves the file: its answer
lands in the contract if it changed the contract, or in `notes/` if it is a finding. Its id joins the
`Retired so far — O1, O2.` sentence in the file's introduction and is never reused.

## Ids

- Ids are never reused and never renumbered. Each is defined in exactly one place.
- Cite them as `§V.14`, `§T.7`, `§D.2`, `§C.12`, `§B.31`, `§O.49` in code comments, tests, docs,
  commits and PRs.

## Where text that does not belong here goes

| Place | Owns |
|---|---|
| `spec/`, `AGENTS.md` | the contract and the live worklist |
| `notes/*.md` | the narrative: what was measured, what it means, how the code works |
| `git log` | the reasons: the commit that closed a task is that task's record |

The size limits in `tests/test_spec_hygiene.py` keep history out of the specification. In the full
form, the contract (data model, interfaces, and invariants) must also stay above
`MIN_CONTRACT_SHARE` of `spec/`, so that tasks, questions, and bugs cannot bury it. Raising a limit
is allowed; raise it with a dated reason beside the constant.

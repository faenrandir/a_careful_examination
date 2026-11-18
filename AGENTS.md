# A Careful Examination

## Goal

A low-key, as-unbiased-as-possible collection of links, notes, and essays that examine the truth
claims of The Church of Jesus Christ of Latter-day Saints, published as a static website.

## Constraints

- C1: The site is built with Zola 0.23 and served by GitHub Pages from `docs/` on the `main`
  branch, under the base URL `/a_careful_examination`. `docs/` is generated output; never edit
  it by hand.
- C2: Published URLs are permanent. A page's `path`, `/categories/<slug>/`, and `/tags/<slug>/`
  must keep resolving.
- C3: The site is released only through `scripts/release.py`, which commits and pushes as the
  `faenrandir` account. Local previews use `scripts/serve.py`.
- C4: Reading works without JavaScript. Scripts only add search, sorting, and lists.
- C5: Every color and size comes from `sass/_tokens.scss`. The site has a light theme only.
- C6: Scripts target Python 3.12 and the standard library. `scripts/serve.py` may also use
  `livereload`, and the tests use `pytest`.
- C7: Code is under the MIT license. Content written by faenrandir is CC0. Copies of others'
  content remain theirs.

## The spec

`SPEC.md` is the index to this project's contract. The contract itself is plain English in
`spec/`, split by topic and edited by hand (format: `FORMAT.md`). Cite ids as `§V.14`, `§T.7`,
`§B.3`, `§C.2` in code comments, test docstrings, notes, and commit subjects. Do not use the
cavekit skills (`/spec`, `/build`, `/check`, `/backprop`) or caveman encoding here.

`docs/` is the generated site, so narrative documents go in `notes/`.

Read what the task touches:

| before changing | read |
|---|---|
| `scripts/` | `spec/invariants/build.md`, `spec/interfaces.md` |
| `content/` front matter, URLs, `templates/browse.html`, `templates/categories/` | `spec/invariants/urls.md`, `spec/data-model.md` |
| `sass/`, other `templates/` | `spec/invariants/presentation.md` |
| choosing what to work on | `spec/tasks.md` (open first), `spec/open-questions.md` |

Rules:

1. **Invariants are testable claims.** New or changed behaviour adds an invariant or cites an
   existing one, and a test cites it in its docstring, for example `"""§V.6: topic links point
   at /tags/."""`.
2. **Every bug names the invariant that catches it again.** When a test fails or a bug is found:
   find the cause; identify the invariant whose test would have caught it, and if none exists,
   write one with a test that fails on the defective code; add an entry to `spec/bugs.md` with
   status `open`; fix the code; set the status to `fixed`; put the reproduction in the commit
   message and cite `§B.<n>` and `§V.<n>` in its subject.
3. **Open questions are not yours to resolve.** Raise them and stop work on any task they block.
   After the maintainer answers, move the answer into the contract or `notes/`, delete the
   question, and add its id to the "Retired so far" sentence.
4. **Tasks are the build order.** Take the first open task that no open question blocks and keep
   its **Status** line current. A done task moves under `## Done` and shrinks to its claim, its
   numbers, and a pointer; cite `§T.<n>` in the closing commit.
5. **The maintainer owns the wording.** Propose spec changes as ordinary edits in the same commit
   as the code.
6. **The spec does not carry its own history.** Narrative goes in `notes/`, reasons in commit
   messages (`git log --grep '§T.12'`). Ids are never reused or renumbered.
7. Where a document under `notes/` and the spec disagree, the document is wrong.

`tests/test_spec_hygiene.py` enforces the format: every invariant cited by a test, every bug
naming an invariant, ids defined once, and size limits. Run the whole suite with `pytest`; it
rebuilds `docs/` once through `scripts/build.py`.

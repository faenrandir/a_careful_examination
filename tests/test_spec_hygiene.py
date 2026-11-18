"""The spec's hygiene is machine-checked rather than maintained by habit.

The property this file protects is that every invariant is cited by a test, so that an invariant
cannot quietly stop being true. The other checks keep the spec parseable (ids defined once, every
bug tied to an invariant, tasks under the heading their status names) and keep history out of it
(size limits). See `FORMAT.md` for the entry formats these checks parse.

Generalized from lcms-feature-map's tests/test_spec_hygiene.py. In this repository docs/ is the
generated site, so narrative documents go in notes/. Raise a size limit only with a dated comment
that gives the reason.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

# pytestmark = pytest.mark.l1  # uncomment if the repository marks tests by validation level

#: "full" (goal, constraints, data model, interfaces, invariants, tasks, open questions, bugs) or
#: "reduced" (goal, constraints, invariants, bugs).
FORM = "full"

#: The number of constraints that existed when the spec was written; the list may grow, not shrink.
MIN_CONSTRAINTS = 7

REPO_ROOT = Path(__file__).resolve().parent.parent
SPEC = REPO_ROOT / "SPEC.md"
AGENTS = REPO_ROOT / "AGENTS.md"
SPEC_DIR = REPO_ROOT / "spec"
INVARIANTS_DIR = SPEC_DIR / "invariants"
BUGS = SPEC_DIR / "bugs.md"
TASKS = SPEC_DIR / "tasks.md"
OPEN_QUESTIONS = SPEC_DIR / "open-questions.md"
DATA_MODEL = SPEC_DIR / "data-model.md"
INTERFACES = SPEC_DIR / "interfaces.md"
TESTS_DIR = REPO_ROOT / "tests"

#: A done task keeps its claim, its key numbers, and a pointer; its story is in notes/ and the commit.
DONE_TASK_MAX_CHARS = 900
#: A bug keeps the cause and the transferable rule; the reproduction is in the fixing commit.
BUG_MAX_CHARS = 1_300
#: An invariant states one testable claim.
INVARIANT_MAX_CHARS = 1_200
#: The index is a table of contents.
INDEX_MAX_BYTES = 6_000
#: AGENTS.md loads into every session.
AGENTS_MAX_LINES = 240
#: The whole of spec/, as a ratchet. Set it a little above the current size when the spec is written.
SPEC_BYTE_BUDGET = 20_000  # 2026-11-18: spec written at 15.7 KB

#: Full form: the contract (data model, interfaces, invariants) must stay above this share of spec/.
#: The tasks, open questions, and bug log grow every session, and a spec where they bury the contract
#: has stopped doing its job; one such spec fell to a 16% contract share before this check existed.
MIN_CONTRACT_SHARE = 0.30

#: A resolved question leaves spec/open-questions.md.
RESOLUTION_MARKERS = ("RESOLVED", "CLOSED", "ANSWERED")

#: Invariants with no test, each with the reason it has none (more than 40 characters).
UNTESTED_INVARIANTS: dict[str, str] = {}

FULL = FORM == "full"
full_only = pytest.mark.skipif(not FULL, reason="reduced spec form")

_ENTRY = re.compile(
    r"^### ((?:[VTBO]\d+)|(?:[DI]\.\d+)) — .*?(?=^### |^## |\Z)", re.M | re.S
)


def entries(path: Path) -> list[tuple[str, str]]:
    """(id, whole entry) for every `### <id> — title` entry in one file."""
    if not path.is_file():
        return []
    return [
        (m.group(1), m.group(0).strip())
        for m in _ENTRY.finditer(path.read_text(encoding="utf-8"))
    ]


def invariant_entries() -> list[tuple[str, Path, str]]:
    return [
        (v, path, text)
        for path in sorted(INVARIANTS_DIR.glob("*.md"))
        for v, text in entries(path)
    ]


def invariant_ids() -> list[str]:
    return [v for v, _, _ in invariant_entries()]


def constraint_ids() -> list[str]:
    match = re.search(
        r"^## Constraints$(.*?)(?=^## |\Z)",
        AGENTS.read_text(encoding="utf-8"),
        re.M | re.S,
    )
    assert match, 'AGENTS.md has no "## Constraints" section'
    return [f"C{n}" for n in re.findall(r"^- C(\d+):", match.group(1), re.M)]


def _field(text: str, name: str) -> str:
    match = re.search(rf"\*\*{name}:\*\*\s*(.*?)(?=\s*·\s*\*\*|\n|$)", text)
    return match.group(1).strip() if match else ""


def task_entries() -> list[tuple[str, str, str, str]]:
    """(id, status, refs, whole entry) for every task."""
    return [
        (t, _field(text, "Status"), _field(text, "Refs"), text)
        for t, text in entries(TASKS)
    ]


def bug_entries() -> list[tuple[str, str, str, str]]:
    """(id, status, caught-by, whole entry) for every bug."""
    return [
        (b, _field(text, "Status"), _field(text, "Caught by"), text)
        for b, text in entries(BUGS)
    ]


def open_question_ids() -> list[str]:
    return [o for o, _ in entries(OPEN_QUESTIONS)]


def retired_open_questions() -> set[str]:
    """Ids of answered questions. They stay resolvable because tasks still cite them."""
    match = re.search(
        r"Retired so far — ([^.]*)\.", OPEN_QUESTIONS.read_text(encoding="utf-8"), re.S
    )
    assert match, 'spec/open-questions.md has no "Retired so far — ." sentence'
    return set(re.findall(r"O\d+", match.group(1)))


def cited_in_tests() -> set[str]:
    """Every §-id cited from a Python file under tests/."""
    cited: set[str] = set()
    for path in TESTS_DIR.rglob("*.py"):
        for section, number in re.findall(
            r"§\s?([GCDIVTOB])\.?(\d+)", path.read_text(encoding="utf-8")
        ):
            cited.add(f"{section}{number}")
    return cited


# --- every invariant is defended by a test -----------------------------------------------------


def test_every_invariant_is_cited_by_a_test():
    cited = cited_in_tests()
    uncited = [
        v for v in invariant_ids() if v not in cited and v not in UNTESTED_INVARIANTS
    ]
    assert not uncited, (
        f"invariants with no citation in tests/: {uncited}. Either cite the invariant (as §V.<n>) in "
        f"the test that defends it, or add it to UNTESTED_INVARIANTS with the reason it has none."
    )


def test_every_exemption_carries_a_reason():
    for invariant, reason in UNTESTED_INVARIANTS.items():
        assert reason and len(reason) > 40, (
            f"{invariant} is exempt without a written reason (> 40 characters)"
        )


def test_no_exemption_outlives_its_test():
    stale = sorted(v for v in UNTESTED_INVARIANTS if v in cited_in_tests())
    assert not stale, (
        f"{stale} are listed as untested but are now cited in tests/. Remove them from UNTESTED_INVARIANTS."
    )


def test_every_exempt_invariant_still_exists():
    unknown = sorted(v for v in UNTESTED_INVARIANTS if v not in set(invariant_ids()))
    assert not unknown, (
        f"UNTESTED_INVARIANTS names invariants that do not exist: {unknown}"
    )


# --- ids are defined once and reachable from the index -----------------------------------------


@pytest.mark.parametrize(
    "ids",
    [
        pytest.param(invariant_ids, id="invariants"),
        pytest.param(lambda: [b for b, *_ in bug_entries()], id="bugs"),
        pytest.param(constraint_ids, id="constraints"),
        pytest.param(
            lambda: [t for t, *_ in task_entries()], id="tasks", marks=full_only
        ),
        pytest.param(open_question_ids, id="open-questions", marks=full_only),
        pytest.param(
            lambda: [d for d, _ in entries(DATA_MODEL)],
            id="data-model",
            marks=full_only,
        ),
        pytest.param(
            lambda: [i for i, _ in entries(INTERFACES)],
            id="interfaces",
            marks=full_only,
        ),
    ],
)
def test_every_id_is_defined_once(ids):
    found = ids()
    twice = sorted({i for i in found if found.count(i) > 1})
    assert not twice, (
        f"defined more than once: {twice}. Ids are never reused; give the new entry the next free number."
    )


def test_the_index_lists_every_invariant_file():
    index = SPEC.read_text(encoding="utf-8")
    missing = sorted(
        p.name
        for p in INVARIANTS_DIR.glob("*.md")
        if f"spec/invariants/{p.name}" not in index
    )
    assert not missing, (
        f"SPEC.md does not link these invariant files: {missing}. Add them to the index."
    )


def test_the_constraints_are_numbered_in_order():
    numbers = [int(c[1:]) for c in constraint_ids()]
    assert numbers == list(range(1, len(numbers) + 1)), (
        f"constraint ids are not C1..Cn in order: {numbers}"
    )
    assert len(numbers) >= MIN_CONSTRAINTS, (
        f"AGENTS.md lists {len(numbers)} constraints; at least {MIN_CONSTRAINTS} existed"
    )


# --- bugs name the invariant that catches recurrence -------------------------------------------


def test_every_bug_names_an_existing_invariant():
    known = set(invariant_ids())
    for bug, _, caught_by, _ in bug_entries():
        named = {f"V{n}" for n in re.findall(r"\bV\.?(\d+)\b", caught_by)}
        assert named, (
            f"{bug}'s **Caught by** names no invariant. Name the invariant that would catch it again."
        )
        unknown = sorted(v for v in named if v not in known)
        assert not unknown, f"{bug} names invariants that do not exist: {unknown}"


def test_every_bug_declares_a_status():
    for bug, status, _, _ in bug_entries():
        assert status in {"open", "fixed"}, (
            f"{bug} has status {status!r}; use open or fixed"
        )


def test_bug_entries_stay_short():
    over = [
        (b, len(text)) for b, _, _, text in bug_entries() if len(text) > BUG_MAX_CHARS
    ]
    assert not over, (
        f"bug entries over {BUG_MAX_CHARS} characters: {over}. Move the reproduction to the commit."
    )


def test_invariants_stay_short():
    over = [
        (v, len(text))
        for v, _, text in invariant_entries()
        if len(text) > INVARIANT_MAX_CHARS
    ]
    assert not over, (
        f"invariants over {INVARIANT_MAX_CHARS} characters: {over}. Move the reasoning to notes/."
    )


# --- tasks and open questions (full form) ------------------------------------------------------


@full_only
def test_every_task_declares_a_status():
    for task, status, _, _ in task_entries():
        assert status in {"done", "in progress", "to do"}, (
            f"{task} has status {status!r}"
        )


@full_only
def test_done_tasks_stay_short():
    over = [
        (t, len(x))
        for t, s, _, x in task_entries()
        if s == "done" and len(x) > DONE_TASK_MAX_CHARS
    ]
    assert not over, (
        f"done tasks over {DONE_TASK_MAX_CHARS} characters: {over}. Keep the claim, numbers, and a pointer."
    )


@full_only
def test_tasks_sit_under_the_heading_their_status_names():
    _, _, done_part = TASKS.read_text(encoding="utf-8").partition("\n## Done")
    assert done_part, 'spec/tasks.md has no "## Done" section'
    for task, status, _, _ in task_entries():
        where = "done" if f"### {task} —" in done_part else "open"
        assert (status == "done") == (where == "done"), (
            f"{task} is {status!r} but sits under {where!r}"
        )


@full_only
def test_task_ids_are_in_order_within_each_part():
    for part in TASKS.read_text(encoding="utf-8").split("\n## ")[1:]:
        ids = [int(n) for n in re.findall(r"^### T(\d+) —", part, re.M)]
        assert ids == sorted(ids), (
            f"task ids out of order under {part.splitlines()[0]!r}: {ids}"
        )


@full_only
def test_no_open_question_is_actually_resolved():
    offenders = [
        o
        for o, text in entries(OPEN_QUESTIONS)
        if any(m in text for m in RESOLUTION_MARKERS)
    ]
    assert not offenders, (
        f"open questions marked resolved: {offenders}. Land the answer, then retire the id."
    )


@full_only
def test_a_retired_question_does_not_also_still_have_an_entry():
    both = sorted(set(open_question_ids()) & retired_open_questions())
    assert not both, f"{both} are listed as retired while still carrying an entry"


@full_only
def test_no_task_cites_a_missing_id():
    known = (
        set(invariant_ids())
        | set(constraint_ids())
        | set(open_question_ids())
        | retired_open_questions()
    )
    known |= {t for t, *_ in task_entries()} | {b for b, *_ in bug_entries()}
    known |= {i.replace(".", "") for i, _ in entries(DATA_MODEL)} | {
        i.replace(".", "") for i, _ in entries(INTERFACES)
    }
    dangling = {}
    for task, _, refs, _ in task_entries():
        missing = sorted(
            i
            for i in {
                f"{s}{n}" for s, n in re.findall(r"\b([CVOTBDI])\.?(\d+)\b", refs)
            }
            if i not in known
        )
        if missing:
            dangling[task] = missing
    assert not dangling, f"tasks whose **Refs** cite ids that do not exist: {dangling}"


@pytest.mark.parametrize(
    "path",
    [
        BUGS,
        pytest.param(DATA_MODEL, marks=full_only),
        pytest.param(INTERFACES, marks=full_only),
        pytest.param(TASKS, marks=full_only),
        pytest.param(OPEN_QUESTIONS, marks=full_only),
    ],
    ids=lambda p: p.name,
)
def test_every_part_of_the_spec_is_present(path):
    assert path.is_file(), f"{path.relative_to(REPO_ROOT)} is missing"


# --- size limits -------------------------------------------------------------------------------


def test_the_spec_stays_within_its_budget():
    size = sum(p.stat().st_size for p in SPEC_DIR.rglob("*.md"))
    assert size <= SPEC_BYTE_BUDGET, (
        f"spec/ is {size:,} bytes, over the {SPEC_BYTE_BUDGET:,} budget. Trim history, or raise the budget "
        f"with a dated comment that gives the reason."
    )


@full_only
def test_the_contract_is_the_majority_of_the_spec():
    contract_files = [DATA_MODEL, INTERFACES, *INVARIANTS_DIR.glob("*.md")]
    contract = sum(p.stat().st_size for p in contract_files if p.is_file())
    history_files = [TASKS, OPEN_QUESTIONS, BUGS]
    history = sum(p.stat().st_size for p in history_files if p.is_file())
    share = contract / max(contract + history, 1)
    assert share > MIN_CONTRACT_SHARE, (
        f"the contract is {100 * share:.0f}% of spec/, at or below "
        f"{100 * MIN_CONTRACT_SHARE:.0f}%. Shorten done tasks, retire answered questions, "
        f"and trim bug entries rather than lowering this bar."
    )


def test_the_index_stays_an_index():
    size = SPEC.stat().st_size
    assert size <= INDEX_MAX_BYTES, (
        f"SPEC.md is {size:,} bytes; move contract into a spec/ topic file"
    )


def test_the_always_loaded_file_does_not_grow():
    lines = len(AGENTS.read_text(encoding="utf-8").splitlines())
    assert lines <= AGENTS_MAX_LINES, (
        f"AGENTS.md is {lines} lines and loads into every session; move detail to spec/ or notes/"
    )

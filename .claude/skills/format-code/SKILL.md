---
name: format-code
description: Enforce the repository's Python code style (PEP 8 layout, sorted imports, Google-style docstrings, type hints) with a pinned ruff config. Use when asked to format, lint, tidy or style-check Python files, or before committing Python changes.
---

# Format Code

Applies one consistent style to Python files using ruff with the settings in
`ruff.toml` next to this file. The repository has no linter config of its own, so
always go through the script below rather than running `ruff`, `black` or
`autopep8` with their defaults.

## The style

- **Layout:** ruff's formatter (Black-compatible): 4-space indents, 88-character lines, double quotes.
- **Imports:** sorted and grouped (standard library, third party, local modules); unused imports removed.
- **Docstrings:** on every public module, class, function and method, Google style (`Args:`, `Returns:`, `Raises:`).
- **Type hints:** on every function parameter and return value.
- **Naming and syntax:** PEP 8 names; modern Python 3.12 syntax (`list[str]`, `X | None`).
- **Tests** (`test_*.py`, `conftest.py`) are exempt from the docstring and type-hint rules.

## Scope rules

1. **Only touch what was asked for.** Format the files the user named, or the Python
   files changed in the current work (`git diff --name-only`, plus untracked files).
   Never run it on the whole repository unless the user explicitly asks.
2. **One exercise folder at a time.** Each `music-analytics-*` folder is a separate
   course stage. Read that folder's `CLAUDE.md` first: if it forbids code changes
   (e.g. `music-analytics-reporter-plan`), stop and say so.
3. **Style only, never behaviour.** Don't fix logic, rename public functions or routes,
   or "correct" anything that looks like a bug, even a planted one. Mention bugs you
   notice instead of fixing them.

## Steps

1. **Baseline.** If the folder has tests, run them and note the result
   (`uv run --project .. python -m pytest -q` from inside the folder).
2. **Preview** (optional, for a large change):
   ```bash
   .claude/skills/format-code/scripts/format.sh --check <paths>
   ```
3. **Apply the automatic fixes and formatting:**
   ```bash
   .claude/skills/format-code/scripts/format.sh <paths>
   ```
   Paths are relative to the repository root. The script fixes imports, reformats, then
   lists the problems it cannot fix itself.
4. **Fix the remaining problems by hand:**
   - `ANN*` (missing type hints): add accurate hints. Read the call sites to find the real
     types; use `X | None` where a value can be missing. Don't guess with `Any`.
   - `D*` (missing or malformed docstrings): write a one-line summary, plus `Args:` /
     `Returns:` sections when the function takes parameters or returns something
     non-obvious. Describe what the code actually does, not what it should do.
   - `F841` (unused variable), `B*` (likely bug): these can signal real bugs. Leave the
     code as it is and report them to the user rather than deleting or rewriting.
   - `N*` (naming): rename only private, local names. Renaming public functions, classes
     or anything imported elsewhere changes behaviour, so report those instead.
5. **Repeat** `format.sh --check <paths>` until it reports no problems, or only ones you
   have chosen to report.
6. **Verify.** Rerun the tests; the result must match the baseline exactly. If anything
   changed, undo your last edits and find out why.

## Do not

- Move the `from routes import *` or `from db_routes import db_bp` lines in `app.py` to
  the top of the file. They sit at the bottom on purpose (a circular import); the config
  already allows this.
- Silence problems with `# noqa`, `# type: ignore` or by editing `ruff.toml`, unless the
  user agrees.
- Use `--unsafe-fixes`.

## Report back

Summarise in a few lines: which files changed, what the formatter did, which hints and
docstrings you added, the test result before and after, and anything you left for the
user (possible bugs, public names that break the naming rules).

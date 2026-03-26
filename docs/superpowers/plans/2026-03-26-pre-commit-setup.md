# Pre-commit Setup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add pre-commit hooks to enforce ruff linting/formatting and gitleaks secret detection on every commit.

**Architecture:** Three config changes (`.pre-commit-config.yaml` new file, `pyproject.toml` additions, docs updates) with no runtime code changes. All tasks are independent and can be done sequentially in one session.

**Tech Stack:** `pre-commit>=4.0.0`, `ruff` (via `ruff-pre-commit` hook), `gitleaks`

---

## File Map

| File | Action | What changes |
|------|--------|--------------|
| `.pre-commit-config.yaml` | Create | New hook configuration file |
| `pyproject.toml` | Modify | Add `pre-commit` to dev deps; add `[tool.ruff]` and `[tool.ruff.lint]` sections |
| `CLAUDE.md` | Modify | Remove "No linter is configured" sentence; add pre-commit commands to Commands section |
| `README.md` | Modify | Update Development section with pre-commit setup steps and commit workflow note |

---

## Task 1: Create `.pre-commit-config.yaml`

**Files:**
- Create: `.pre-commit-config.yaml`

- [ ] **Step 1: Run autoupdate dry-run to get current rev tags**

```bash
# Check the latest tags without modifying anything yet
curl -s https://api.github.com/repos/astral-sh/ruff-pre-commit/releases/latest | python3 -c "import sys,json; print(json.load(sys.stdin)['tag_name'])"
curl -s https://api.github.com/repos/gitleaks/gitleaks/releases/latest | python3 -c "import sys,json; print(json.load(sys.stdin)['tag_name'])"
```

Expected: two version strings like `v0.11.x` and `v8.x.x`. Note these for the next step.

- [ ] **Step 2: Create `.pre-commit-config.yaml` with current revs**

Use the versions obtained above (substitute `RUFF_VER` and `GITLEAKS_VER`):

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: RUFF_VER
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/gitleaks/gitleaks
    rev: GITLEAKS_VER
    hooks:
      - id: gitleaks
        args: [protect, --staged]
```

- [ ] **Step 3: Commit**

```bash
git add .pre-commit-config.yaml
git commit -m "chore: add pre-commit config with ruff and gitleaks

Signed-off-by: staryxchen <staryxchen@tencent.com>"
```

---

## Task 2: Update `pyproject.toml`

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Add `pre-commit` to dev dependencies**

In `pyproject.toml`, find `[project.optional-dependencies]` → `dev = [`. Add `pre-commit>=4.0.0` as the first entry:

```toml
[project.optional-dependencies]
dev = [
    "pre-commit>=4.0.0",
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "pytest-mock>=3.14.0",
]
```

- [ ] **Step 2: Append ruff configuration sections at the end of `pyproject.toml`**

Add after the existing `[tool.pytest.ini_options]` block:

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I"]   # pycodestyle errors, pyflakes, isort
```

- [ ] **Step 3: Install updated deps and verify ruff config is picked up**

```bash
uv pip install -e ".[dev]"
.venv/bin/python3 -m ruff check src/ --select E,F,I
```

Expected: Either no output (all clean) or a list of fixable issues. Either is fine — the config is working.

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml
git commit -m "chore: add pre-commit dev dep and ruff config to pyproject.toml

Signed-off-by: staryxchen <staryxchen@tencent.com>"
```

---

## Task 3: Update `CLAUDE.md`

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Remove the "No linter" sentence and replace with ruff note**

Find line 27 in `CLAUDE.md`:
```
No linter is configured; the project uses standard Python conventions.
```

Replace with:
```
Ruff is configured for linting and formatting (see `.pre-commit-config.yaml` and `[tool.ruff]` in `pyproject.toml`).
```

- [ ] **Step 2: Add pre-commit commands to the Commands section**

After the existing `# Inspect tools interactively` block in the Commands section, add:

```bash
# Install pre-commit hooks (run once after cloning)
.venv/bin/pre-commit install

# Run all hooks manually against all files
.venv/bin/pre-commit run --all-files
```

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs(CLAUDE): update linter note and add pre-commit commands

Signed-off-by: staryxchen <staryxchen@tencent.com>"
```

---

## Task 4: Update `README.md`

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update the Development section**

Find the `## Development` section near the bottom of `README.md`:

```markdown
## Development

```bash
# Install with dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest tests/ -v
```
```

Replace with:

```markdown
## Development

```bash
# Install with dev dependencies (includes pre-commit, ruff)
uv pip install -e ".[dev]"

# Install pre-commit hooks (run once after cloning)
.venv/bin/pre-commit install

# Run tests
.venv/bin/python3 -m pytest tests/ -v

# Run all pre-commit hooks manually
.venv/bin/pre-commit run --all-files
```

Pre-commit hooks run automatically on `git commit`. If ruff makes autofix changes, the commit will be blocked — re-stage the modified files (`git add -u`) and commit again. If gitleaks detects a secret, remove it before retrying.
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs(README): update Development section with pre-commit setup

Signed-off-by: staryxchen <staryxchen@tencent.com>"
```

---

## Task 5: Install hooks and verify end-to-end

- [ ] **Step 1: Install hooks**

```bash
.venv/bin/pre-commit install
```

Expected output:
```
pre-commit installed at .git/hooks/pre-commit
```

- [ ] **Step 2: Run all hooks against all files**

```bash
.venv/bin/pre-commit run --all-files
```

Expected: All hooks pass (ruff may apply minor fixes on first run — if so, re-run to confirm clean). No gitleaks findings.

- [ ] **Step 3: If ruff made changes, re-stage and re-run**

```bash
git add -u
.venv/bin/pre-commit run --all-files
```

Expected: All hooks pass with no changes.

- [ ] **Step 4: Commit any ruff autofixes (if needed)**

If ruff modified any files in step 2:

```bash
git add -u
git commit -m "style: apply ruff autofix on initial pre-commit run

Signed-off-by: staryxchen <staryxchen@tencent.com>"
```

- [ ] **Step 5: Run the test suite to confirm nothing is broken**

```bash
.venv/bin/python3 -m pytest tests/ -v
```

Expected: All tests pass.

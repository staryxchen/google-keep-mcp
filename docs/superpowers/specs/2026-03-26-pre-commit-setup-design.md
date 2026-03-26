# Pre-commit Setup Design

**Date:** 2026-03-26
**Status:** Approved

## Goal

Add a pre-commit hook configuration to the `google-keep-mcp` project that enforces code style and detects secret leakage before every commit.

## Scope

- Code formatting and linting via `ruff`
- Secret detection via `gitleaks`
- No type checking (out of scope for this change)

## Files Changed

| File | Change |
|------|--------|
| `.pre-commit-config.yaml` | New file — hook configuration |
| `pyproject.toml` | Add `pre-commit` to dev deps; add `[tool.ruff]` config section |
| `README.md` | Update Development section to document pre-commit setup |
| `CLAUDE.md` | Remove "No linter is configured" sentence; update Commands section |

## `.pre-commit-config.yaml`

Complete YAML (verify revs with `pre-commit autoupdate` before shipping, as ruff releases frequently):

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.10  # run: pre-commit autoupdate to get the latest
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.24.2  # run: pre-commit autoupdate to get the latest
    hooks:
      - id: gitleaks
        args: [protect, --staged]
```

Two hook sources:

1. **`ruff-pre-commit`** — `ruff` runs lint with autofix (`--fix`); `ruff-format` runs the formatter. Both are from `https://github.com/astral-sh/ruff-pre-commit`.
2. **`gitleaks`** — scans staged files for secrets/credentials using the default ruleset. From `https://github.com/gitleaks/gitleaks`. No baseline file needed.

## `pyproject.toml` changes

### Dev dependency

Add `pre-commit>=4.0.0` to `[project.optional-dependencies].dev`.

### Ruff configuration

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I"]   # pycodestyle errors, pyflakes, isort
```

`select = ["E", "F", "I"]` is the minimal set: import order, undefined names, style errors. Keeps noise low.

## Installation (developer workflow)

```bash
uv pip install -e ".[dev]"
.venv/bin/pre-commit install
```

## Commit workflow

When `ruff check --fix` modifies files (e.g., reorders imports), it exits non-zero and the commit is blocked. The developer must re-stage the modified files and commit again:

```bash
git add -u
git commit ...   # second attempt succeeds
```

If `gitleaks` detects a secret, the commit is blocked with a diagnostic message identifying the file and match. No file modification occurs; the developer must remove the secret before retrying.

## Documentation updates

### `CLAUDE.md`

- **Remove** the sentence: `No linter is configured; the project uses standard Python conventions.`
- **Replace** with: `Ruff is configured for linting and formatting (see `.pre-commit-config.yaml` and `[tool.ruff]` in `pyproject.toml`).`
- **Add** to the Commands section:

```bash
# Install pre-commit hooks (run once after cloning)
.venv/bin/pre-commit install

# Run all hooks manually against all files
.venv/bin/pre-commit run --all-files
```

### `README.md`

Update the `Development` section to include `pre-commit install` as a setup step and explain the two-attempt commit flow described above.

## Non-goals

- No CI integration (out of scope)
- No `mypy` or `bandit` (explicitly excluded)
- No custom gitleaks rules (default ruleset sufficient)

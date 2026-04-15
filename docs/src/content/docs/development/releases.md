---
title: Release Process
description: How Medix versions are published to PyPI via Release Please.
---

Medix uses [Release Please](https://github.com/googleapis/release-please)
for fully automated, Conventional-Commits-driven releases.

## The flow

```
conventional commit on main
        │
        ▼
release-please.yml opens or updates a release PR
        │
        ▼
maintainer merges the release PR
        │
        ▼
GitHub release is cut + tag is pushed
        │
        ▼
publish job builds and uploads to PyPI (OIDC, no tokens)
        │
        ▼
docs redeploy if /docs was touched (Cloudflare Pages)
```

## Version bumping rules

Release Please infers the bump from commit prefixes since the last release:

| Commit | Bump |
|--------|------|
| `fix: …` | patch (1.3.0 → 1.3.1) |
| `feat: …` | minor (1.3.0 → 1.4.0) |
| `feat!: …` or `BREAKING CHANGE:` in body | major (1.3.0 → 2.0.0) |
| `chore:`, `docs:`, `refactor:`, `test:`, `ci:`, `style:` | no bump |

## Release PR

When release-worthy commits land on `main`, Release Please opens (or
updates) a PR titled `chore(main): release medix <new-version>`. That PR:

- Bumps `pyproject.toml` `version`
- Bumps `medix/__init__.py` `__version__`
- Updates `CHANGELOG.md`
- Updates `.release-please-manifest.json`

Merging the PR fires the publish job.

## Publishing

The publish job uses PyPI's OIDC trusted publisher flow — no long-lived API
tokens, no secrets. It:

1. Checks out the tagged commit
2. Sets up Python 3.12
3. Runs `python -m build`
4. Uses `pypa/gh-action-pypi-publish` to upload to PyPI

The built wheel and sdist appear on both
[pypi.org](https://pypi.org/project/medix/) and
[libraries.io](https://libraries.io/pypi/medix).

## Docs deployment

Docs live in `docs/` and deploy to Cloudflare Pages on push to `main` — but
only when files under `docs/` change. This keeps the package release and
docs release independent.

## Hotfixes

For urgent fixes that can't wait for a normal release:

1. Land the fix on `main` as `fix: …`
2. Release Please opens a release PR automatically
3. Merge it immediately

There's no separate hotfix branch — the workflow is fast enough.

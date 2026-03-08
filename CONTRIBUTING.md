# Contributing to Medix

Thanks for your interest in contributing! Here's how to get started.

## Development Setup

1. **Fork and clone** the repository:

   ```bash
   git clone git@github.com:<your-username>/medix.git
   cd medix
   ```

2. **Create a virtual environment** and install with dev dependencies:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e ".[dev]"
   ```

3. **Verify** the CLI runs and tests pass:

   ```bash
   medix --version
   pytest
   ```

## Making Changes

1. Create a feature branch from `main`:

   ```bash
   git checkout -b feat/your-feature
   ```

2. Make your changes and ensure tests pass:

   ```bash
   pytest                          # run the full test suite
   ruff check medix/ tests/        # lint
   ruff format --check medix/ tests/  # format check
   ```

   Use `--dry-run` to verify CLI behavior without needing real media files:

   ```bash
   medix /path/to/any/media --dry-run
   ```

3. Commit using [Conventional Commits](https://www.conventionalcommits.org/) — this drives automated releases:

   | Prefix       | Purpose                        |
   |-------------|--------------------------------|
   | `feat:`     | New feature                    |
   | `fix:`      | Bug fix                        |
   | `docs:`     | Documentation only             |
   | `chore:`    | Maintenance / tooling          |
   | `refactor:` | Code restructuring             |
   | `perf:`     | Performance improvement        |

   Example:

   ```bash
   git commit -m "feat: add FLAC output format support"
   ```

4. Push and open a Pull Request against `main`.

## Pull Request Guidelines

- Keep PRs focused — one feature or fix per PR.
- Describe **what** changed and **why** in the PR body.
- All tests must pass (`pytest`) and code must be formatted (`ruff format`).
- Ensure the CLI still works end-to-end (single file and directory conversion).
- Update `README.md` if you add new features or change CLI usage.
- Add tests for new functionality.

## Reporting Issues

- Use [GitHub Issues](https://github.com/vineethkrishnan/medix/issues).
- Include your OS, Python version, FFmpeg version, and the full error output.
- If possible, share the command you ran and a sample media file that triggers the issue.

## Code Style

- Follow existing patterns in the codebase.
- Keep functions focused and well-named.
- Avoid unnecessary comments — code should be self-explanatory.
- Use [ruff](https://docs.astral.sh/ruff/) for linting and formatting (`ruff check` and `ruff format`).

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).

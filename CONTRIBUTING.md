# Contributing to Medix

Thanks for your interest in contributing! Here's how to get started.

## Development Setup

1. **Fork and clone** the repository:

   ```bash
   git clone git@github.com:<your-username>/medix.git
   cd medix
   ```

2. **Create a virtual environment** and install in editable mode:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

3. **Verify** the CLI runs:

   ```bash
   medix --version
   ```

## Making Changes

1. Create a feature branch from `main`:

   ```bash
   git checkout -b feat/your-feature
   ```

2. Make your changes and test them manually with real media files.

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
- Ensure the CLI still works end-to-end (single file and directory conversion).
- Update `README.md` if you add new features or change CLI usage.

## Reporting Issues

- Use [GitHub Issues](https://github.com/vineethkrishnan/medix/issues).
- Include your OS, Python version, FFmpeg version, and the full error output.
- If possible, share the command you ran and a sample media file that triggers the issue.

## Code Style

- Follow existing patterns in the codebase.
- Keep functions focused and well-named.
- Avoid unnecessary comments — code should be self-explanatory.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).

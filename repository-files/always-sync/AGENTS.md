# Extended Data Library - AI Agent Instructions

This is the central source of truth for AI agent instructions.

## Fundamentals
1. **Read before modifying** - Always read the file/code before editing.
2. **Run builds after changes** - Verify your changes compile/lint.
3. **One concern per commit** - Keep commits focused.
4. **Conventional Commits** - Use `feat`, `fix`, `docs`, `chore`, `refactor`, `test`.

## PR Workflow
1. Clear title: `type(scope): description`.
2. Body explains WHAT, WHY, and HOW.
3. Request AI reviews: `/gemini review`, `/q review`, etc.

## Memory Bank Protocol
Use `memory-bank/activeContext.md` and `memory-bank/progress.md` to track state between sessions.

## Technical Standards
- **Python**: Use `uv`, `ruff`, `mypy`, `pytest`.
- **Node.js**: Use `npm`, `eslint`, `prettier`.
- **Versioning**: Semantic Versioning (SemVer) driven by conventional commits.

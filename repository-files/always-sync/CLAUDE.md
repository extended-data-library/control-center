# CLAUDE.md - Extended Data Library

## Project Overview
This repository is part of the **extended-data-library** organization. It follows the organization's standards for development, testing, and CI/CD.

## Development Commands
### Python (if applicable)
- **Install**: `uv sync`
- **Test**: `uv run pytest`
- **Lint**: `uvx ruff check .`
- **Format**: `uvx ruff format .`
- **Type Check**: `uvx mypy .`

### Node.js (if applicable)
- **Install**: `npm install`
- **Build**: `npm run build`
- **Test**: `npm run test`
- **Lint**: `npm run lint`

## Quality Standards
1. **Conventional Commits**: All commits must follow `type(scope): description`.
2. **Type Safety**: All Python code must have type hints. All TypeScript code must be strictly typed.
3. **Tests**: Every PR should include tests for new functionality.
4. **No Placeholders**: Never commit TODOs or incomplete features.
5. **Memory Bank**: Use the `memory-bank/` protocol for session continuity.

## CI/CD
All PRs must pass the automated CI checks before merging.
- Linting
- Type checking
- Unit tests
- Security scanning

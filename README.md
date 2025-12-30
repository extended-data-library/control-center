# extended-data-library Control Center

Organization-level control center for **extended-data-library**.

## Purpose

- Manages CI/CD workflows for all repositories in the organization.
- Syncs shared configuration files (linters, AI instructions, etc.).
- Standardizes repository structure across Python and Node.js projects.
- Connects to enterprise orchestration for AI-powered automation.

## Structure

```text
control-center/
├── .github/workflows/     # Org sync workflows
├── repository-files/      # Files synced to organization repos
│   ├── always-sync/       # Files that are always kept in sync (overwritten)
│   │   ├── .github/       # Shared workflows and actions
│   │   ├── CLAUDE.md      # AI development instructions
│   │   └── ...            # Config files (ruff, mypy, etc.)
│   └── initial-only/      # Files synced only if they don't exist
│       ├── .gitignore     # Default git ignore patterns
│       ├── README.md      # Default README template
│       └── pyproject.toml # Default Python project config
└── ...
```

## Synced Files

### Always Sync (`always-sync/`)
These files are critical for org standards and are updated automatically whenever they change in this repository.
- **CI Workflow**: Unified GitHub Action for Python and Node.js testing, linting, and security.
- **AI Instructions**: `CLAUDE.md` and `AGENTS.md` to ensure consistent AI agent behavior.
- **Linter Config**: `.pre-commit-config.yaml` for standardized quality checks.
- **Ecosystem Connector**: Links repositories to organization-wide AI tools.

### Initial Only (`initial-only/`)
These files are provided as a boilerplate for new repositories. They are only synced if they do not already exist in the target repository.
- `.gitignore`
- `README.md`
- `pyproject.toml` (for Python projects)

## Enterprise Integration

This control-center connects back to enterprise orchestration for:
- AI-powered PR reviews
- Issue triage and delegation
- CI failure auto-resolution via Agentic CI

## Manual Sync

To trigger a manual sync of all files to all organization repositories, run the **Sync Files** workflow from the Actions tab.

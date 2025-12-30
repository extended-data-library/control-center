# extended-data-library Control Center

Organization-level control center for **extended-data-library**.

## Purpose

- Manages CI/CD workflows for all repos in this org
- Syncs shared configuration files
- Connects to enterprise orchestration at `jbcom/control-center`

## Structure

```
control-center/
├── .github/workflows/     # Org sync workflows
├── repository-files/      # Files synced to org repos
│   └── always-sync/       # Always overwrite
└── scripts/               # Sync scripts
```

## Usage

Repos in this org automatically receive:
- CI workflows tailored for extended-data-library project types
- Connection to enterprise AI automation via ecosystem-connector

## Enterprise Integration

This control-center connects back to `jbcom/control-center` for:
- AI-powered PR reviews
- Issue triage and delegation (/jules, /cursor, @claude)
- CI failure auto-resolution


# Objex CLI

Scan your APIs, discover your tools, and register them with the Objex platform.

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/objex/cli/main/scripts/install.sh | bash
```

Or manually:

```bash
git clone https://github.com/objex/cli.git
cd cli
pip install -e .
```

## Stack

- **Runtime**: Python 3.10+ (stdlib only, no external dependencies)
- **Scanner**: Gemini CLI for local codebase scanning, HTTP for agent scanning
- **Repository**: `github.com/objex/cli`

## Commands

| Command | Description |
|---------|-------------|
| `objex install` | Register your organization with the Objex API |
| `objex scan <path>` | Scan a local codebase and generate an OpenAPI spec |
| `objex scan --agents` | Scan live agents via their `/tools` endpoint |
| `objex scan --agents --agent-id smm` | Scan a specific agent |
| `objex update` | Refresh your local profile from the API |
| `objex list` | List locally installed profiles |
| `objex whoami` | Show your current profile |

## Codebase Scanning

Scan a local codebase to discover REST API routes:

```bash
objex scan ./my-api --username mycompany
```

1. Iterates `.py`, `.js`, `.jsx`, `.ts`, `.tsx` files
2. Pre-filters candidates using regex (detects route decorators like `@app.get`, `router.post`)
3. Calls Gemini CLI to extract REST operations from each file
4. Generates OpenAPI 3.0.3 spec
5. Saves locally to `~/.objex/{username}/{codebase}-openapi.json`
6. Uploads to the Objex Gateway

Requires Gemini CLI installed.

## Agent Scanning

Scan live agents by calling their `/tools` endpoint:

```bash
objex scan --agents --username mycompany
```

1. Fetches agent list from `api.objex.app/agents/{username}`
2. For each agent, calls `GET {agent_url}/tools`
3. Tools are auto-discovered via runtime introspection (zero hardcoding)
4. Agent metadata POSTed to `POST /agents/{username}/{agent_id}`
5. Tools POSTed to `POST /agents/{username}/{agent_id}/tools`
6. OpenAPI spec saved locally and uploaded

No Gemini CLI needed for agent scanning.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OBJEX_API_BASE_URL` | `https://api.objex.app/mcp` | Override the gateway API URL |
| `ENVIRONMENT` | `dev` | Environment for tool registration |

## Local Storage

```
~/.objex/
└── {username}/
    ├── profile.json
    └── {codebase}-openapi.json
```

## For Your Agents

Each agent should expose `GET /tools` returning:

```json
{
  "tools": [
    { "id": "post_root", "method": "POST", "path": "/" },
    { "id": "get_status", "method": "GET", "path": "/status" }
  ]
}
```

This can be auto-generated from your framework's route table at runtime:

**Express (Node.js):** Introspect `app._router.stack`
**Flask (Python):** Iterate `app.url_map.iter_rules()`

## Supported Languages for Local Scanning

- Python (`.py`)
- JavaScript (`.js`, `.jsx`)
- TypeScript (`.ts`, `.tsx`)

## Requirements

- Python 3.10+
- Gemini CLI (for local codebase scanning only)

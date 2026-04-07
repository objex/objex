# Objex

Objex is an open-source MCP server platform that turns enterprise APIs and AI agents into a discoverable, callable toolbox. It makes any REST API accessible from Claude Code, Claude Desktop, Cursor, Gemini CLI, and any MCP-compatible client.

## Architecture

```
MCP Clients (Claude Code, Cursor, etc.)
        |
   tools/list, tools/call
        |
   MCP Server (objex/mcp)
        |
   reads agents + tools
        |
   Gateway (objex/gateway, api.objex.app)
        |
   +----+----+
   |         |
  CLI      Agents
  scans    self-register
  /tools   on deploy
```

## Components

| Component | Location | Purpose | Docs |
|-----------|----------|---------|------|
| Gateway | `objex/gateway` | REST API — stores users, agents, tools in Firestore | [gateway.md](gateway.md) |
| MCP Server | `objex/mcp` | MCP protocol server — exposes tools to AI clients | [mcp.md](mcp.md) |
| CLI | `objex/cli` | Scans codebases and agents, populates the gateway | [cli.md](cli.md) |

## Data Model

Everything is user-scoped in Firestore (project: `objexapp`, database: `objex`):

```
mcp/{username}                                             <- profile
mcp/{username}/codebases/{codebase}                        <- OpenAPI specs
mcp/{username}/agents/{agentId}                            <- agent
mcp/{username}/agents/{agentId}/envs/{env}/tools/{toolId}  <- tools per env
```

## How It Works

1. **Register**: `objex install --username mycompany`
2. **Scan**: `objex scan --agents --username mycompany` — calls `GET /tools` on each agent, stores results in the gateway
3. **Serve**: MCP server reads from the gateway, registers tools dynamically
4. **Use**: AI clients call `tools/list` and `tools/call` to discover and invoke agent tools

## Agent Requirements

Every agent exposes two dynamic endpoints (runtime introspection, zero hardcoding):

- `GET /tools` — returns discovered routes as a tool list
- `GET /docs` — returns auto-generated OpenAPI 3.0.3 spec

## Standards

- No hardcoded agent names, URLs, or tool definitions anywhere
- All configuration from environment variables or Firestore
- Tools discovered dynamically via framework route introspection
- Adding a new agent requires zero code changes to gateway or MCP server
- Environment separation (dev/prod) at every level

## Repositories

| Component | Repository |
|-----------|-----------|
| CLI | `github.com/objex/cli` |
| MCP Server | `github.com/objex/mcp` |
| Gateway | `github.com/objex/gateway` |

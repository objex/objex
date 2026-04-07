# Objex MCP Server

Proper MCP (Model Context Protocol) server that exposes registered agent tools to Claude Code, Claude Desktop, Cursor, and any MCP-compatible client.

## Stack

- **Runtime**: Python 3.11, FastMCP (`mcp[cli]` >= 1.2.0)
- **Transport**: stdio (local) or SSE (Cloud Run)
- **Deploy**: Google Cloud Run
- **Repository**: `github.com/objex/mcp`

## How It Works

1. On startup, reads `GET {gateway}/agents/{username}?env={env}`
2. For each agent, reads `GET {gateway}/agents/{username}/{agent_id}/tools?env={env}`
3. Registers one MCP tool per agent tool (e.g., `smm__post_root`)
4. When an AI client calls a tool, proxies the HTTP request to the actual agent endpoint

## Built-in MCP Tools

Always available regardless of registered agents:

| Tool | Description |
|------|-------------|
| `list_agents` | List all registered agents |
| `get_agent_tools` | List tools for a specific agent |
| `get_agent_docs` | Get OpenAPI docs from an agent's `/docs` endpoint |
| `call_agent` | Call any agent tool by `agent_id` + `tool_id` + JSON arguments |

## Dynamic Tools

Registered on startup from the gateway. Named `{agent_id}__{tool_id}`.

Example: SMM agent with tools `post_root`, `post_search`, `post_hashtags` becomes:
- `smm__post_root`
- `smm__post_search`
- `smm__post_hashtags`

Each tool proxies directly to the agent's endpoint when called.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OBJEX_API_URL` | `https://api.objex.app` | Gateway URL |
| `OBJEX_USERNAME` | — | Which user's agents to expose |
| `ENVIRONMENT` | `dev` | Which environment's tools to load (`dev` or `prod`) |

## Claude Code Configuration

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "objex": {
      "command": "python",
      "args": ["/path/to/objex/mcp/mcp_server.py"],
      "env": {
        "OBJEX_API_URL": "https://api.objex.app",
        "OBJEX_USERNAME": "mycompany",
        "ENVIRONMENT": "dev"
      }
    }
  }
}
```

## Deploy to Cloud Run

```bash
cd objex/mcp

# Configure for your environment
export PROJECT_ID=your-gcp-project
export OBJEX_USERNAME=your-username
export ENVIRONMENT=prod

./deploy.sh
```

## Local Development

```bash
cd objex/mcp
./start.sh
# MCP server running on stdio transport
```

## Setup From Scratch

```bash
# 1. Register with Objex
objex install --username mycompany

# 2. Scan your agents to populate the gateway
objex scan --agents --username mycompany

# 3. Run the MCP server
export OBJEX_USERNAME=mycompany
python mcp_server.py
```

## Dependencies

```
mcp[cli]>=1.2.0
httpx==0.28.1
```

# Objex Gateway

REST API that serves as the central registry for users, agents, and tools. Deployed at `api.objex.app`.

## Stack

- **Runtime**: Python 3.11, FastAPI
- **Database**: Google Cloud Firestore (project: `objexapp`, database: `objex`)
- **Deploy**: Google Cloud Run
- **Repository**: `github.com/objex/gateway`

## API Endpoints

### Profiles

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/mcp` | Create user profile |
| `GET` | `/mcp/{username}` | Get user profile |
| `POST` | `/mcp/{username}/{codebase}` | Save OpenAPI spec for a codebase |

### Agents (user-scoped)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/agents/{username}` | List agents. `?env=dev` to filter by environment |
| `GET` | `/agents/{username}/{agent_id}` | Get agent detail |
| `POST` | `/agents/{username}/{agent_id}` | Register or update an agent |

### Tools (user-scoped, per environment)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/agents/{username}/{agent_id}/tools` | List tools. `?env=dev` to filter |
| `POST` | `/agents/{username}/{agent_id}/tools` | Bulk save tools. Body: `{ "tools": [...], "environment": "dev" }` |

### System

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Service info |
| `GET` | `/health` | Health check |
| `POST` | `/registry/inbox` | Pub/Sub push endpoint for agent self-registration |

## Firestore Schema

```
mcp/{username}
  ├── username, companyName, contactPerson, email, createdAt, updatedAt
  ├── codebases/{codebase}
  │     └── specs.current.openapi, updatedAt
  └── agents/{agentId}
        ├── id, name, domainUrl, description, environment, status
        ├── registeredAt, updatedAt
        └── envs/{env}
              ├── updatedAt, toolCount
              └── tools/{toolId}
                    └── id, method, path, description, params, updatedAt
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_CLOUD_PROJECT` | `objexapp` | GCP project |
| `FIRESTORE_DATABASE` | `objex` | Firestore database name |
| `ENVIRONMENT` | `dev` | Default environment |
| `DEFAULT_USERNAME` | `rabbito` | Default username for Pub/Sub registrations |
| `PORT` | `8080` | Server port |

## Self-Registration via Pub/Sub

Agents can self-register by POSTing to `/registry/inbox` (directly or via Pub/Sub push). The payload:

```json
{
  "agent": {
    "id": "smm",
    "name": "Social Media Manager",
    "domainUrl": "https://dev.smmagent.rabbito.ai",
    "endpoints": [
      { "id": "post_root", "method": "POST", "path": "/" }
    ]
  },
  "infrastructure": {
    "domainUrl": "https://dev.smmagent.rabbito.ai",
    "environment": "dev"
  },
  "username": "rabbito"
}
```

If the username doesn't exist, a profile is auto-created.

## Deploy

```bash
cd objex/gateway

# Configure for your environment
export PROJECT_ID=your-gcp-project
export ENVIRONMENT=dev
export DEFAULT_USERNAME=your-username

./deploy.sh
```

## Local Development

```bash
cd objex/gateway
./start.sh
# Gateway running at http://localhost:8080
```

## Dependencies

```
fastapi, uvicorn, gunicorn, google-cloud-firestore, pydantic, email-validator, httpx
```

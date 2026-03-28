# Objex

Objex is an open source MCP server that uses Gemini CLI to discover APIs across an enterprise and make them accessible through a unified Objex server interface.

The project is intended for teams that need a practical way to turn scattered internal and third-party APIs into discoverable, agent-friendly tools without hand-wiring every integration one by one.

## Status

This repository is in the early setup phase. The documentation currently defines the product direction and contribution goals before the server implementation lands.

The first implementation now includes a Python CLI with `install`, `scan`, `update`, and `list` commands.

## Why Objex

Enterprises usually have:

- many APIs spread across teams, gateways, vendors, and legacy systems
- incomplete or outdated documentation
- duplicated integration work across internal tools and AI agents
- no single place where agents can discover what systems exist and how to use them

Objex aims to solve that by combining API discovery with MCP-native access.

## Core Idea

Objex uses Gemini CLI to inspect enterprise environments, identify available APIs, extract useful metadata, and publish those APIs through an MCP server so they can be consumed consistently by compatible clients and agents.

## Planned Capabilities

- Discover APIs from enterprise sources such as OpenAPI specs, gateways, code repositories, service catalogs, and internal docs
- Normalize discovered endpoints into a common internal model
- Expose discovered APIs as MCP tools and resources
- Support incremental rescans so the catalog stays current
- Attach metadata such as authentication needs, ownership, schemas, environments, and tags
- Provide guardrails for enterprise usage, including access controls, allowlists, and auditability
- Reduce manual connector development for internal systems

## High-Level Flow

1. Gemini CLI scans designated enterprise sources.
2. Objex extracts API definitions, endpoints, schemas, and descriptive metadata.
3. Objex normalizes and stores the discovered catalog.
4. The Objex MCP server exposes that catalog to agents and clients as accessible tools.
5. Teams review, approve, and refine the discovered integrations over time.

## Design Principles

- Open source first
- Enterprise-ready by default
- API discovery before manual integration
- Human review where it matters
- Clear provenance for discovered capabilities
- Compatibility with standard MCP workflows

## Use Cases

- Give internal AI agents access to enterprise APIs through one server
- Accelerate onboarding by making available systems easier to discover
- Surface undocumented or under-documented APIs
- Create a searchable inventory of enterprise integrations
- Reduce repeated integration work across teams

## Repository Goals

Project goals and non-goals are tracked in [goals.md](/Users/mazhar/rabbito/objex/goals.md).

## CLI

The repository includes a generic Python CLI service for registering an Objex user and scanning codebases into generated OpenAPI 3 specs.

### Commands

- `objex install`
- `objex scan`
- `objex update`
- `objex list`

### Local Storage

Profiles and generated specs are stored under `~/.objex/<username>/`.

### Development

Install the package locally:

```bash
pip install -e .
```

Show command help:

```bash
objex --help
```

## Install

### Linux

Use a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
objex --help
```

You can also use `pipx` if you prefer a user-level CLI install:

```bash
pipx install .
```

### macOS

You can use the same Python-based installation as Linux, or install through Homebrew once the repository is published at the configured GitHub location.

For a future one-line install command after publishing the repository:

```bash
curl -fsSL https://raw.githubusercontent.com/objex/objex/main/scripts/install.sh | bash
```

For a Homebrew install from source:

```bash
brew install --HEAD ./Formula/objex.rb
```

For a future tap-based install after publishing:

```bash
brew tap objex/tap
brew install objex
```

The Homebrew formula lives at [Formula/objex.rb](/Users/mazhar/rabbito/objex/Formula/objex.rb).

## License

This project is intended to be released under the Apache License 2.0.

If that is the desired license for the repository, the next step should be adding a standard `LICENSE` file with the Apache 2.0 text.

## Contributing

Contributions are welcome. Early contributions are especially useful in these areas:

- MCP server architecture
- API discovery pipeline design
- Gemini CLI integration patterns
- Security and policy enforcement
- Catalog normalization and schema modeling
- Example enterprise connectors and fixtures

As the implementation takes shape, this README should be expanded with setup, local development, configuration, and deployment instructions.

# Objex Goals

This document defines the initial goals for Objex, an open source MCP server that discovers enterprise APIs with Gemini CLI and exposes them through a unified server interface.

## Primary Goals

### 1. Enterprise API Discovery

Detect APIs across enterprise systems from a variety of inputs, including machine-readable specs, gateway definitions, repositories, and internal documentation.

### 2. MCP-Native Access

Expose discovered APIs in a form that works naturally with MCP clients, tools, and agent workflows.

### 3. Unified API Catalog

Create a normalized catalog of discovered APIs so teams can search, understand, and reuse available enterprise capabilities.

### 4. Lower Integration Cost

Reduce the time and effort required to make enterprise systems accessible to internal tools and AI agents.

### 5. Enterprise Guardrails

Support approval workflows, authentication awareness, auditing, and policy controls suitable for enterprise environments.

## Product Objectives

- Make API discovery significantly faster than manual inventory work
- Improve visibility into undocumented or hard-to-find APIs
- Standardize how discovered APIs are represented and exposed
- Help teams move from discovery to usable integrations with minimal manual work
- Build a foundation that is useful both for developers and AI agents

## Technical Goals

- Integrate Gemini CLI into a repeatable discovery workflow
- Build a pluggable ingestion pipeline for multiple API sources
- Normalize discovered API metadata into a stable internal schema
- Expose APIs through a reliable MCP server surface
- Support rescans, updates, and deduplication
- Track provenance for discovered endpoints and metadata
- Design for secure handling of enterprise credentials and permissions

## Non-Goals

- Replacing enterprise API gateways
- Automatically invoking every discovered API without review or policy checks
- Acting as a full API management platform on day one
- Solving every enterprise identity and secrets problem inside the first release
- Providing perfect discovery coverage across all environments from the start

## Early Milestones

### Milestone 1: Foundation

- Define the core data model for discovered APIs
- Implement the basic MCP server skeleton
- Add initial Gemini CLI discovery workflow
- Document repository structure and development conventions

### Milestone 2: Discovery Pipeline

- Support ingestion from at least one structured API source
- Extract endpoints, methods, schemas, and metadata
- Store normalized discovery output
- Add test fixtures for sample enterprise APIs

### Milestone 3: MCP Exposure

- Publish discovered APIs as MCP-friendly tools or resources
- Validate the end-to-end flow with at least one client
- Add filtering, tagging, and search support

### Milestone 4: Enterprise Readiness

- Add access control hooks
- Add audit-oriented logging
- Introduce approval or curation workflows
- Improve operational documentation

## Success Criteria

- A team can point Objex at enterprise sources and get a usable API inventory
- At least one discovered API can be exposed and consumed through MCP end to end
- The discovery output is understandable enough for humans to review and refine
- The system is extensible enough to support new enterprise sources without redesign

## Open Questions

- Which enterprise sources should be prioritized first
- How much of the discovery workflow should be fully automated versus human-reviewed
- What the first stable internal schema for discovered APIs should look like
- How authentication, authorization, and secret handling should be modeled
- Whether discovered APIs should map to tools, resources, prompts, or a combination within MCP

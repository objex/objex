#!/usr/bin/env bash
set -euo pipefail

AGENTS_FILE="${AGENTS_FILE:?Set AGENTS_FILE (path to agents.txt)}"
GATEWAY_URL="${GATEWAY_URL:?Set GATEWAY_URL}"
OBJEX_USERNAME="${OBJEX_USERNAME:-${USERNAME:?Set OBJEX_USERNAME or USERNAME}}"
ENVIRONMENT="${ENVIRONMENT:?Set ENVIRONMENT}"

if [ ! -f "${AGENTS_FILE}" ]; then
  echo "Error: ${AGENTS_FILE} not found" >&2
  exit 1
fi

echo "Scanning agents from ${AGENTS_FILE}"
echo "Gateway: ${GATEWAY_URL}"
echo "Username: ${OBJEX_USERNAME}"
echo "Environment: ${ENVIRONMENT}"
echo ""

total_agents=0
total_tools=0

while IFS=: read -r agent_id agent_url || [ -n "${agent_id}" ]; do
  agent_id="$(echo "${agent_id}" | xargs)"
  agent_url="$(echo "${agent_url}" | xargs)"
  [ -z "${agent_id}" ] && continue
  [[ "${agent_id}" == \#* ]] && continue

  echo "--- ${agent_id} (${agent_url}) ---"

  # Fetch /tools, /docs, and /schemas from the agent
  tools_json="$(curl -sf "${agent_url}/tools" 2>/dev/null || echo '{"tools":[]}')"
  docs_json="$(curl -sf "${agent_url}/docs" 2>/dev/null || echo '{}')"
  schemas_json="$(curl -sf "${agent_url}/schemas" 2>/dev/null || echo '{}')"

  # Merge /tools + /docs + /schemas to produce MCP-compliant tool definitions
  # Priority: /schemas (auto-introspected) > /docs requestBody > empty default
  mcp_tools="$(python3 -c "
import sys, json

tools_raw = json.loads('''${tools_json}''')
docs_raw = json.loads('''${docs_json}''')
schemas_raw = json.loads('''${schemas_json}''')

tools = tools_raw.get('tools', [])
paths = docs_raw.get('paths', {})
endpoint_schemas = schemas_raw.get('endpoints', {})

mcp_tools = []
for tool in tools:
    tid = tool.get('id', '')
    method = tool.get('method', 'POST').upper()
    path = tool.get('path', '/')
    method_lower = method.lower()

    # Look up description from OpenAPI spec
    description = ''
    input_schema = {'type': 'object', 'properties': {}}

    path_item = paths.get(path, {})
    operation = path_item.get(method_lower, {})
    if operation:
        description = operation.get('summary', '') or operation.get('description', '')

        # Extract inputSchema from requestBody
        req_body = operation.get('requestBody', {})
        if req_body:
            content = req_body.get('content', {})
            json_schema = content.get('application/json', {}).get('schema', {})
            if json_schema and json_schema.get('properties'):
                input_schema = json_schema

        # Extract from parameters (for GET requests)
        params = operation.get('parameters', [])
        if params:
            props = {}
            for p in params:
                pname = p.get('name', '')
                if pname:
                    props[pname] = {
                        'type': p.get('schema', {}).get('type', 'string'),
                        'description': p.get('description', ''),
                    }
            if props:
                input_schema = {'type': 'object', 'properties': props}

    # Override with /schemas if available (auto-introspected, more accurate)
    schema_entry = endpoint_schemas.get(path, {})
    if schema_entry.get('schema', {}).get('properties'):
        input_schema = schema_entry['schema']

    if not description:
        description = f'{method} {path}'

    mcp_tools.append({
        'id': tid,
        'name': '${agent_id}__' + tid,
        'description': description,
        'inputSchema': input_schema,
        'method': method,
        'path': path,
    })

print(json.dumps(mcp_tools))
" 2>/dev/null || echo '[]')"

  tool_count="$(echo "${mcp_tools}" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo 0)"
  echo "  Found ${tool_count} tools"

  # Register agent in gateway
  curl -sf -X POST "${GATEWAY_URL}/agents/${OBJEX_USERNAME}/${agent_id}" \
    -H "Content-Type: application/json" \
    -d "{\"id\":\"${agent_id}\",\"domainUrl\":\"${agent_url}\",\"environment\":\"${ENVIRONMENT}\"}" \
    >/dev/null 2>&1 \
    && echo "  Agent registered" \
    || echo "  Warning: agent registration failed"

  # Save MCP-compliant tools to gateway
  tools_payload="$(python3 -c "
import sys, json
tools = json.loads('''${mcp_tools}''')
print(json.dumps({'tools': tools, 'environment': '${ENVIRONMENT}'}))
" 2>/dev/null || echo '{"tools":[],"environment":"'"${ENVIRONMENT}"'"}')"

  curl -sf -X POST "${GATEWAY_URL}/agents/${OBJEX_USERNAME}/${agent_id}/tools" \
    -H "Content-Type: application/json" \
    -d "${tools_payload}" \
    >/dev/null 2>&1 \
    && echo "  Tools saved (MCP format)" \
    || echo "  Warning: tools save failed"

  # Save OpenAPI spec
  if [ "${docs_json}" != "{}" ]; then
    docs_payload="$(python3 -c "
import sys, json
spec = json.loads('''${docs_json}''')
print(json.dumps({'codebase': '${agent_id}', 'openapi': spec}))
" 2>/dev/null || echo '')"

    if [ -n "${docs_payload}" ]; then
      curl -sf -X POST "${GATEWAY_URL}/mcp/${OBJEX_USERNAME}/${agent_id}" \
        -H "Content-Type: application/json" \
        -d "${docs_payload}" \
        >/dev/null 2>&1 \
        && echo "  OpenAPI spec saved" \
        || echo "  Warning: spec save failed"
    fi
  fi

  total_agents=$((total_agents + 1))
  total_tools=$((total_tools + tool_count))
  echo ""

done < "${AGENTS_FILE}"

echo "Done. Scanned ${total_agents} agents, ${total_tools} total tools."

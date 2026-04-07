#!/usr/bin/env bash
set -euo pipefail

AGENTS_FILE="${AGENTS_FILE:?Set AGENTS_FILE (path to agents.txt)}"
GATEWAY_URL="${GATEWAY_URL:?Set GATEWAY_URL}"
USERNAME="${USERNAME:?Set USERNAME}"
ENVIRONMENT="${ENVIRONMENT:?Set ENVIRONMENT}"

if [ ! -f "${AGENTS_FILE}" ]; then
  echo "Error: ${AGENTS_FILE} not found" >&2
  exit 1
fi

echo "Scanning agents from ${AGENTS_FILE}"
echo "Gateway: ${GATEWAY_URL}"
echo "Username: ${USERNAME}"
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

  # Fetch /tools and /docs from the agent
  tools_json="$(curl -sf "${agent_url}/tools" 2>/dev/null || echo '{"tools":[]}')"
  docs_json="$(curl -sf "${agent_url}/docs" 2>/dev/null || echo '{}')"

  # Merge /tools with /docs to produce MCP-compliant tool definitions
  # Each tool gets: name, description, inputSchema, method, path
  mcp_tools="$(python3 -c "
import sys, json

tools_raw = json.loads('''${tools_json}''')
docs_raw = json.loads('''${docs_json}''')

tools = tools_raw.get('tools', [])
paths = docs_raw.get('paths', {})

mcp_tools = []
for tool in tools:
    tid = tool.get('id', '')
    method = tool.get('method', 'POST').upper()
    path = tool.get('path', '/')
    method_lower = method.lower()

    # Look up description and requestBody from OpenAPI spec
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
            if json_schema:
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
  curl -sf -X POST "${GATEWAY_URL}/agents/${USERNAME}/${agent_id}" \
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

  curl -sf -X POST "${GATEWAY_URL}/agents/${USERNAME}/${agent_id}/tools" \
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
      curl -sf -X POST "${GATEWAY_URL}/mcp/${USERNAME}/${agent_id}" \
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

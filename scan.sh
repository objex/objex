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
  # Skip empty lines and comments
  agent_id="$(echo "${agent_id}" | xargs)"
  agent_url="$(echo "${agent_url}" | xargs)"
  [ -z "${agent_id}" ] && continue
  [[ "${agent_id}" == \#* ]] && continue

  echo "--- ${agent_id} (${agent_url}) ---"

  # Call GET /tools on the agent
  tools_json="$(curl -sf "${agent_url}/tools" 2>/dev/null || echo '{"tools":[]}')"
  tool_count="$(echo "${tools_json}" | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('tools',[])))" 2>/dev/null || echo 0)"

  echo "  Found ${tool_count} tools"

  # Register agent in gateway
  curl -sf -X POST "${GATEWAY_URL}/agents/${USERNAME}/${agent_id}" \
    -H "Content-Type: application/json" \
    -d "{\"id\":\"${agent_id}\",\"domainUrl\":\"${agent_url}\",\"environment\":\"${ENVIRONMENT}\"}" \
    >/dev/null 2>&1 \
    && echo "  Agent registered" \
    || echo "  Warning: agent registration failed"

  # Save tools to gateway
  tools_payload="$(echo "${tools_json}" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(json.dumps({'tools': data.get('tools', []), 'environment': '${ENVIRONMENT}'}))
" 2>/dev/null || echo '{"tools":[],"environment":"'"${ENVIRONMENT}"'"}')"

  curl -sf -X POST "${GATEWAY_URL}/agents/${USERNAME}/${agent_id}/tools" \
    -H "Content-Type: application/json" \
    -d "${tools_payload}" \
    >/dev/null 2>&1 \
    && echo "  Tools saved" \
    || echo "  Warning: tools save failed"

  # Fetch and save OpenAPI docs
  docs_json="$(curl -sf "${agent_url}/docs" 2>/dev/null || echo '{}')"
  if [ "${docs_json}" != "{}" ]; then
    docs_payload="$(echo "${docs_json}" | python3 -c "
import sys, json
spec = json.load(sys.stdin)
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

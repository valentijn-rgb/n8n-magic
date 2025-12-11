# n8n-magic Project Instructions

## Purpose
Create production-ready n8n workflows from scoping documents.

---

## Current Investigation: Scoping Template Optimization

### Goal

Investigate whether we can generate n8n workflows programmatically from documentation and scoping documents. Use findings to improve our scoping template.

### Research Questions

1. What information is essential in a scoping document to generate a valid workflow?
2. What gaps exist between current scoping template and workflow generation needs?
3. Which workflow patterns can be reliably generated from structured input?
4. What level of detail is needed for node configuration?
5. How should error handling and edge cases be specified?

### Success Criteria

- [ ] Identify minimum required fields for workflow generation
- [ ] Document what works well in current template
- [ ] List missing information that blocks generation
- [ ] Propose concrete template improvements

### Key Learnings

*Findings from investigation will be documented here as they emerge.*

| Date | Learning | Impact on Template |
|------|----------|-------------------|
| | | |

---

## Context7 Resources for n8n

When building n8n workflows, use Context7 to access up-to-date documentation:

```
# Primary n8n documentation
mcp__context7__get-library-docs with context7CompatibleLibraryID="/n8n-io/n8n-docs"

# n8n-skills for workflow patterns and best practices (HIGHLY RECOMMENDED)
mcp__context7__get-library-docs with context7CompatibleLibraryID="/czlonkowski/n8n-skills"

# Large comprehensive docs collection
mcp__context7__get-library-docs with context7CompatibleLibraryID="/llmstxt/n8n_io_llms-full_txt"
```

### Recommended Topics to Query
- `topic="workflow patterns"` - 5 core patterns covering 90% of use cases
- `topic="node configuration"` - How to configure specific nodes
- `topic="validation"` - Validation loop and error handling
- `topic="webhook"` - Webhook trigger setup
- `topic="HTTP request"` - API integration
- `topic="authentication"` - OAuth, API keys, credentials

---

## The 5 Core Workflow Patterns

90% of n8n workflows fit into these patterns:

| Pattern | Use Case | Trigger |
|---------|----------|---------|
| **Webhook Processing** | React to external events | Webhook node |
| **HTTP API Integration** | Connect to REST APIs | Manual/Schedule/Webhook |
| **Database Operations** | CRUD operations | Any trigger |
| **AI Agent Workflow** | Intelligent automation | Chat/Webhook |
| **Scheduled Tasks** | Recurring jobs | Schedule Trigger |

**Pattern Selection:**
- External events � Webhook Processing
- Integrate with APIs � HTTP API Integration
- Data manipulation � Database Operations
- AI reasoning/tools � AI Agent Workflow
- Periodic tasks � Scheduled Tasks

---

## Workflow Creation Checklist

### 1. Planning Phase
- [ ] Identify the appropriate pattern from the 5 core patterns
- [ ] List all required nodes
- [ ] Map data flow (input � transformations � output)
- [ ] Plan error handling strategy

### 2. Implementation Phase
- [ ] Create workflow with appropriate trigger
- [ ] Add data source nodes
- [ ] Configure authentication/credentials
- [ ] Add transformation nodes (Code, Set, etc.)
- [ ] Add output/action nodes
- [ ] Implement error handling

### 3. Validation Phase
- [ ] Validate each node configuration individually
- [ ] Validate complete workflow structure
- [ ] Test with sample data
- [ ] Test edge cases

### 4. Deployment Phase
- [ ] Review workflow settings
- [ ] Activate workflow (manual in n8n UI)
- [ ] Monitor initial executions
- [ ] Document the workflow

---

## Node Configuration Best Practices

### Start with get_node_essentials
Always use `get_node_essentials` before configuring a node to understand required fields.

### Resource/Operation Pattern
Most n8n nodes follow this structure:
```json
{
  "resource": "<entity>",
  "operation": "<action>",
  // ... operation-specific fields
}
```

### Configuration Order
1. Set parent properties first (method, resource, operation)
2. Then configure dependent fields
3. Validate after each significant change

### HTTP Request Node Example
```json
{
  "method": "POST",
  "url": "https://api.example.com/endpoint",
  "authentication": "none",
  "sendBody": true,
  "body": {
    "contentType": "json",
    "content": {
      "field": "={{$json.field}}"
    }
  }
}
```

---

## Validation Best Practices

### Validation Philosophy
**Validate early, validate often.** Validation is iterative:
- Expect 2-3 validate � fix cycles
- Average: 23s thinking, 58s fixing per cycle

### Validation Loop
1. Configure node/workflow
2. Run validation
3. Read error messages completely
4. Fix one error at a time
5. Validate again
6. Repeat until valid

### Validation Profiles
- `runtime` - Recommended for pre-deployment (balanced)
- `minimal` - Quick checks during development

### Reading Validation Results
1. Check `valid` field first
2. If false, iterate through `errors` array
3. Each error has: `property`, `message`, `fix`
4. Review warnings (not blocking but important)
5. Consider suggestions for improvements

---

## Expression Syntax

### Basic Expressions
```javascript
// Access current item data
{{ $json.fieldName }}

// Access data from another node
{{ $node["Node Name"].json.fieldName }}

// Webhook data (from body)
{{ $json.body.data }}

// Use bracket notation for spaces
{{ $json["field name"] }}
```

### Best Practices
- Always wrap dynamic content in `{{ }}`
- Quote node names with spaces: `$node["Node Name"]`
- Access webhook data from `.body`
- Test expressions in the expression editor

---

## Code Node Best Practices

### JavaScript Data Access
```javascript
// Explicit access (recommended)
$input.first().json.field

// Check for null/undefined
const value = $input.first().json.field ?? 'default';

// Process all items
for (const item of $input.all()) {
  // process item.json
}
```

### Python Data Access
```python
# Use .get() for safe dictionary access
value = _json.get("field", "default")

# Check empty lists before access
if _input.all():
    first_item = _input.first()
```

---

## Security Considerations

### For AI Agent Workflows
- Use read-only database credentials (SELECT only)
- Validate redirect URLs against allow-lists
- Never expose sensitive credentials in logs

### General
- Store credentials in n8n credential manager
- Use environment variables for configuration
- Validate all external input

---

## From Scoping Document to Workflow

When converting a scoping document to n8n workflow:

### Step 1: Analyze Requirements
- Read the "Scope & Requirements" section
- Identify triggers (button click, webhook, schedule)
- List all integrations needed (APIs, databases, services)
- Note security requirements

### Step 2: Map to Patterns
- Match each requirement to a core pattern
- Complex integrations may combine multiple patterns
- Example: OIDC flow = Webhook + HTTP API Integration

### Step 3: Design Node Flow
```
Trigger � Authentication � Data Fetch � Transform � Action � Response
```

### Step 4: Handle Edge Cases
- What if authentication fails?
- What if external API is down?
- What if data is malformed?

### Step 5: Document in Proposed Solution
- Number of workflows needed
- Available webhooks and identifiers
- Required API calls
- Custom fields needed

---

## Python API Client (n8n_client)

A Python wrapper for managing n8n workflows programmatically from your code editor.

### Prerequisites

1. **Python 3.11+** installed
2. **uv** package manager ([install guide](https://docs.astral.sh/uv/getting-started/installation/))
3. **n8n API key** from your n8n instance (Settings → n8n API → Create API key)

### Setup

```bash
# Clone and enter the project
cd n8n-magic

# Install dependencies
uv sync

# Configure credentials (copy and edit)
cp .env.example .env
```

Edit `.env` with your credentials:
```bash
N8N_host="https://your-n8n-instance.com/"
N8N_API_KEY="your-api-key-here"
```

### Quick Start

```python
from n8n_client import N8nClient

# Initialize (auto-loads from .env)
client = N8nClient()

# List all workflows
workflows = client.list_workflows()
for wf in workflows.data:
    print(f"{wf.id}: {wf.name} (active: {wf.active})")
```

### API Reference

#### List Workflows
```python
# List all workflows
workflows = client.list_workflows()

# With filters
workflows = client.list_workflows(
    active=True,           # Only active workflows
    name="search term",    # Filter by name
    limit=50               # Max results (default 100, max 250)
)
```

#### Get Workflow
```python
workflow = client.get_workflow("workflow-id")
print(workflow["name"])
print(workflow["nodes"])
```

#### Create Workflow
```python
# From dict
new_workflow = client.create_workflow({
    "name": "My New Workflow",
    "nodes": [
        {
            "id": "trigger-1",
            "name": "Manual Trigger",
            "type": "n8n-nodes-base.manualTrigger",
            "typeVersion": 1,
            "position": [100, 100],
            "parameters": {}
        }
    ],
    "connections": {},
    "settings": {}
})
print(f"Created: {new_workflow['id']}")

# From JSON file
created = client.import_from_file("path/to/workflow.json")
```

#### Update Workflow
```python
client.update_workflow("workflow-id", {
    "name": "Updated Name",
    "nodes": [...],
    "connections": {...},
    "settings": {}
})
```

#### Delete Workflow
```python
client.delete_workflow("workflow-id")
```

#### Activate/Deactivate
```python
client.activate_workflow("workflow-id")
client.deactivate_workflow("workflow-id")
```

#### Export Workflow
```python
# Export to JSON file
client.export_to_file("workflow-id", "output/my-workflow.json")
```

### Running from Command Line

```bash
# List workflows
uv run python -c "
from n8n_client import N8nClient
client = N8nClient()
for wf in client.list_workflows().data:
    print(f'{wf.id}: {wf.name}')
"

# Export a workflow
uv run python -c "
from n8n_client import N8nClient
N8nClient().export_to_file('workflow-id', 'exported.json')
"

# Import a workflow
uv run python -c "
from n8n_client import N8nClient
result = N8nClient().import_from_file('workflow.json')
print(f'Created: {result[\"id\"]}')
"
```

### Error Handling

```python
from n8n_client import N8nClient, N8nClientError

client = N8nClient()

try:
    workflow = client.get_workflow("nonexistent-id")
except N8nClientError as e:
    print(f"Error: {e}")
    print(f"Status code: {e.status_code}")
    print(f"Response: {e.response}")
```

### Running Tests

```bash
uv run pytest tests/ -v
```

---

## MCP Tools Available

This project has access to n8n MCP tools:

| Tool | Purpose |
|------|---------|
| `n8n_create_workflow` | Create new workflows |
| `n8n_validate_workflow` | Validate entire workflow |
| `validate_node_operation` | Validate single node config |
| `n8n_update_partial_workflow` | Update existing workflow |
| `search_nodes` | Find available nodes |
| `get_node_essentials` | Get node configuration info |
| `search_workflows` | List existing workflows |
| `execute_workflow` | Run a workflow |
| `get_workflow_details` | Get workflow configuration |

### Workflow for Creating via MCP
1. `search_nodes` - Find the right nodes
2. `get_node_essentials` - Understand configuration
3. `n8n_create_workflow` - Create the workflow
4. `n8n_validate_workflow` - Validate it
5. Fix any errors, validate again
6. Activate manually in n8n UI

---

## Common Workflow Templates

### Webhook � Transform � API
```
Webhook Trigger � Set/Code Node � HTTP Request � Respond to Webhook
```

### OAuth/OIDC Flow
```
Webhook (receive code) � HTTP Request (token exchange) � HTTP Request (userinfo) � Set (build response) � Respond/Redirect
```

### Scheduled Sync
```
Schedule Trigger � HTTP Request (fetch) � Code (transform) � Database/API (store)
```

---

## Node Templates (n8n-skills Best Practices)

Production-ready node templates are available in `n8n-workflows-templates/`:

### Directory Structure

```text
n8n-workflows-templates/
├── patterns/              # Complete workflow patterns
│   ├── webhook-http-api.json
│   └── scheduled-sync.json
├── nodes/                 # Individual node templates
│   ├── triggers/          # Webhook, Schedule
│   ├── authentication/    # OAuth2, API Key, Basic Auth
│   ├── http/              # GET, POST requests
│   ├── transform/         # Code, Set, IF nodes
│   └── output/            # Respond to Webhook
└── code-patterns/         # JavaScript patterns
    ├── error-handling.js
    ├── null-safe-access.js
    ├── array-transform.js
    └── data-aggregation.js
```

### Usage

1. **Start from a pattern**: Copy `patterns/webhook-http-api.json` as base
2. **Customize nodes**: Replace placeholders (`{{WEBHOOK_PATH}}`, `{{TOKEN_ENDPOINT}}`, etc.)
3. **Add/remove nodes**: Use individual templates from `nodes/`
4. **Deploy**: Use `n8n_client` to create and activate

### Critical Best Practices

| Rule | Details |
|------|---------|
| Webhook data location | Access via `$json.body.field`, NOT `$json.field` |
| Code node return format | Always return `[{json: {...}}]` |
| Error handling | Use try/catch + null coalescing (`??`) |
| Credentials | Never hardcode - use n8n credential manager |
| Validation | Use `runtime` profile before deployment |

### Expression Syntax Quick Reference

| Use Case | Pattern |
|----------|---------|
| Current node | `{{$json.fieldName}}` |
| Other node | `{{$node["Node Name"].json.data}}` |
| Webhook body | `{{$json.body.fieldName}}` |
| Webhook headers | `{{$json.headers['x-api-key']}}` |
| Default value | `{{$json.value ?? 'default'}}` |
| Conditional | `{{$json.active ? 'Yes' : 'No'}}` |

### Code Node Patterns

```javascript
// Standard error handling - MUST return [{json: {...}}]
try {
  const input = $input.first().json;
  const value = input?.field ?? 'default';  // Null-safe

  if (!input.required) {
    return [{ json: { error: 'Missing field', status: 'error' } }];
  }

  return [{ json: { result: value } }];
} catch (error) {
  return [{ json: { error: error.message, status: 'failed' } }];
}
```

### Test Workflow Script

```bash
# Test workflow creation (validates and creates in n8n)
uv run python scripts/test_workflow.py n8n-workflows-templates/patterns/webhook-http-api.json

# With placeholder replacements
uv run python scripts/test_workflow.py workflow.json -r WEBHOOK_PATH=my-test -r API_URL=https://api.example.com

# Test, activate, and cleanup
uv run python scripts/test_workflow.py workflow.json --activate --cleanup
```

### Deployment Workflow

```bash
# 1. Create workflow from template
uv run python -c "
from n8n_client import N8nClient
import json

client = N8nClient()
with open('n8n-workflows-templates/patterns/webhook-http-api.json') as f:
    workflow = json.load(f)

# Customize placeholders
workflow['name'] = 'My Integration'
# ... replace other placeholders

result = client.create_workflow(workflow)
print(f'Created: {result[\"id\"]}')
"

# 2. Activate in n8n UI or via API
```

---

## Testing Requirements

Every workflow must be tested:
1. Test with valid input data
2. Test with edge cases (empty, malformed)
3. Test error handling paths
4. Document test scenarios in workflow notes

---

## Project-Specific Notes

### Scoping Document Location
`confluence-templates/scoping-document-template.md`

### Key Sections to Extract
- Problem to solve � Workflow purpose
- Scope & Requirements � Node requirements
- Technical Challenges � Error handling needs
- Dependencies � External integrations
- Proposed solution → Workflow documentation

---

## Key Learnings from Integrations

### SOL-381: Utopi-Vertus Integration (2025-12-11)

#### 1. n8n Expression Context Matters

**Problem**: Expressions like `$json.spaceUuid` work differently depending on where they're used.

| Context | Access Pattern | Notes |
|---------|---------------|-------|
| Inside loop | `$json.field` | Current item in iteration |
| After HTTP Request | `$json.responseField` | Response data |
| Reference other node | `$node["Node Name"].json.field` | Explicit node reference |

**Best Practice**: Always be explicit about which node's data you're accessing. Use `$node["Node Name"]` when referencing data from a specific node.

#### 2. Data Merging Strategy

**Problem**: When making parallel API calls per item (e.g., electricity + heating per household), merging results by array position is unreliable.

**Solution**: Use key-based merging with a Map:
```javascript
// Build a map keyed by unique identifier
const electricityMap = new Map();
for (const item of $('Get Electricity1').all()) {
  const spaceUuid = item.json.spaceUuid;  // Preserve the key
  electricityMap.set(spaceUuid, item.json);
}

// Merge by key, not position
const electricity = electricityMap.get(household.space_uuid) ?? null;
```

**Key Insight**: HTTP Request nodes don't preserve input data by default. Either:
- Store the key in a separate field before the request
- Use `$node["Previous Node"]` to get original data
- Enable "Include Response Headers and Status" which preserves some context

#### 3. UOM Transform Table Pattern

**Problem**: External APIs return data in various units. Need flexible conversion to target units.

**Solution**: Centralized transform table:
```javascript
const UOM_TRANSFORM = {
  'J':   { targetUnit: 'GJ', factor: 1e-9 },
  'kJ':  { targetUnit: 'GJ', factor: 1e-6 },
  'MJ':  { targetUnit: 'GJ', factor: 1e-3 },
  'GJ':  { targetUnit: 'GJ', factor: 1 },
  'kWh': { targetUnit: 'GJ', factor: 0.0036 },
  'MWh': { targetUnit: 'GJ', factor: 3.6 },
};

function transformValue(value, apiUnit, metricType) {
  // Skip conversion for some metric types
  if (metricType === 'electricity') {
    return { value, unit: apiUnit || 'kWh' };
  }
  const transform = UOM_TRANSFORM[apiUnit];
  if (transform) {
    return { value: value * transform.factor, unit: transform.targetUnit };
  }
  return { value, unit: apiUnit || 'unknown' };
}
```

**Benefits**:
- Single source of truth for conversions
- Easy to add new units
- Self-documenting
- Handles unknown units gracefully

#### 4. Utopi API Specifics

| Aspect | Details |
|--------|---------|
| Auth | Azure AD OAuth2 (client_credentials) |
| Token endpoint | `https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token` |
| Base URL | `https://partner-api.utopi.io/v2` |
| Energy units | Returns `kWh` (not Joules as initially assumed) |
| Rate limits | Unknown - implement batch processing |

**Critical**: Always verify actual API response units. Documentation may differ from implementation.

#### 5. Error Handling in Workflows

**Pattern**: Use `onError: continueRegularOutput` with `neverError: true` in HTTP Request nodes:
```javascript
// In HTTP Request node settings
"onError": "continueRegularOutput"
// In options
"options": { "neverError": true }
```

Then check for errors in Code node:
```javascript
if (item.json.error || item.json.statusCode >= 400) {
  errors.push({ type: 'api_call', message: item.json.message });
}
```

#### 6. Chainels API Custom Fields Access

Custom fields in Chainels API are in `householdCustomFieldValues` array:
```javascript
const customFields = household.householdCustomFieldValues || [];
const spaceUuid = customFields.find(f => f.customField?.name === 'space_uuid')?.value;
```

**Important**: Always use optional chaining (`?.`) and provide fallbacks.

#### 7. JavaScript Number Precision

When dealing with unit conversions, be aware of floating-point precision:
```javascript
// 6.1935 * 0.0036 = 0.0222966 (not exactly)
// Use toFixed() for display, keep full precision for calculations
const display = value.toFixed(4);
```

---

### Template Impact Assessment

| Learning | Template Change Needed |
|----------|----------------------|
| Expression context | Add section on data flow and node references |
| Key-based merging | Require unique identifiers in data specs |
| UOM transforms | Include unit specifications in API sections |
| Error handling | Standardize error response format |
| Custom fields | Document field access patterns per platform |

# Weather API Harmonization Layer Demo

A reference implementation demonstrating how to scale integrations using the **Harmonization Layer architecture**. This demo uses two weather providers to show the pattern in action.

## TL;DR

Instead of building N separate integrations with inconsistent data formats, we:

1. Build **one Experience API** (business logic, provider-agnostic)
2. Build **small System API adapters** (one per external provider)
3. All adapters output the **same canonical data model**

Result: Adding provider #10 takes the same effort as provider #2.

---

## Quick Test

```bash
# Test the unified Experience API (recommended entry point)
curl -X POST 'https://internal.integrations.chainels.com/webhook/weather' \
  -H 'Content-Type: application/json' \
  -d '{"city": "Amsterdam", "provider": "open-meteo"}'

# Same API, different provider - returns IDENTICAL structure
curl -X POST 'https://internal.integrations.chainels.com/webhook/weather' \
  -H 'Content-Type: application/json' \
  -d '{"city": "Amsterdam", "provider": "wttr"}'
```

Both return the same canonical format - only `meta.provider` differs.

---

## The Problem This Solves

### Without Harmonization Layer

```
┌─────────────┐     ┌──────────────────┐
│  Consumer   │────►│ Open-Meteo Flow  │──► { temp_2m: 12.5, ... }
└─────────────┘     └──────────────────┘

┌─────────────┐     ┌──────────────────┐
│  Consumer   │────►│ wttr.in Flow     │──► { temp_C: "12", ... }
└─────────────┘     └──────────────────┘

┌─────────────┐     ┌──────────────────┐
│  Consumer   │────►│ Provider #3 Flow │──► { temperature: 12.5, ... }
└─────────────┘     └──────────────────┘
```

**Problems:**
- Each consumer must understand each provider's unique format
- Bug fixes applied N times
- Testing N separate workflows
- N providers = N × complexity

### With Harmonization Layer

```
                    ┌─────────────────────────────────┐
                    │     EXPERIENCE API              │
┌─────────────┐     │     /webhook/weather            │
│  Consumer   │────►│                                 │
└─────────────┘     │  Dynamic URL: /system-api/{provider}
                    │  Provider-AGNOSTIC (no hardcoded providers)
                    └───────────┬─────────────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              ▼                 ▼                 ▼
    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │ SYSTEM API      │ │ SYSTEM API      │ │ SYSTEM API      │
    │ /system-api/    │ │ /system-api/    │ │ /system-api/    │
    │ open-meteo      │ │ wttr            │ │ {new-provider}  │
    │                 │ │                 │ │                 │
    │ Transform to    │ │ Transform to    │ │ Transform to    │
    │ canonical       │ │ canonical       │ │ canonical       │
    └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
             │                   │                   │
             └───────────────────┴───────────────────┘
                                 │
                                 ▼
                    { location: {...}, current: {...}, status: "success" }

                    ALL return IDENTICAL structure
```

**Benefits:**
- Consumers only learn ONE format
- Experience API is **provider-agnostic** - no code changes when adding providers
- Bug fixes in Experience API apply to all
- Test Experience API + adapters separately
- Adding provider #10 = add one small adapter workflow (no Experience API changes!)

---

## The Three Workflows

| Workflow | Type | Purpose | Webhook |
|----------|------|---------|---------|
| **Experience API - Weather** | Orchestrator | Routes requests, contains business logic | `POST /webhook/weather` |
| **System API - Open-Meteo** | Adapter | Transforms Open-Meteo response to canonical | `POST /webhook/system-api/open-meteo` |
| **System API - wttr.in** | Adapter | Transforms wttr.in response to canonical | `POST /webhook/system-api/wttr` |

### When to call what?

- **External consumers** → Always call the **Experience API** (`/webhook/weather`)
- **Testing/debugging** → Can call System APIs directly to isolate issues

---

## Canonical Data Model

Both System APIs return this **identical** structure. This is the contract that all adapters must fulfill.

```json
{
  "location": {
    "city": "Amsterdam",
    "country": "The Netherlands",
    "latitude": 52.37403,
    "longitude": 4.88969
  },
  "current": {
    "temperature": 7.2,
    "feelsLike": 3.6,
    "humidity": 79,
    "windSpeed": 15.1,
    "windDirection": 185,
    "weatherCode": 0,
    "pressure": 1008.3
  },
  "meta": {
    "provider": "open-meteo",
    "timestamp": "2025-12-15T13:55:18.277Z",
    "requestedCity": "Amsterdam"
  },
  "status": "success"
}
```

### Field Reference

| Field | Unit | Description |
|-------|------|-------------|
| `temperature` | °C | Current temperature |
| `feelsLike` | °C | Apparent temperature (wind chill factor) |
| `humidity` | % | Relative humidity (0-100) |
| `windSpeed` | km/h | Wind speed |
| `windDirection` | ° | Wind direction (0-360, 0=North) |
| `weatherCode` | - | WMO weather condition code |
| `pressure` | hPa | Atmospheric pressure |

### Error Response

```json
{
  "status": "error",
  "error": "City not found: asdfghjkl",
  "meta": {
    "provider": "open-meteo",
    "timestamp": "2025-12-15T13:56:01.489Z",
    "requestedCity": "asdfghjkl"
  }
}
```

---

## Test Commands

### 1. Test Experience API (Main Entry Point)

```bash
# Get weather for Amsterdam using Open-Meteo
curl -X POST 'https://internal.integrations.chainels.com/webhook/weather' \
  -H 'Content-Type: application/json' \
  -d '{"city": "Amsterdam", "provider": "open-meteo"}'

# Get weather for London using wttr.in
curl -X POST 'https://internal.integrations.chainels.com/webhook/weather' \
  -H 'Content-Type: application/json' \
  -d '{"city": "London", "provider": "wttr"}'

# Test error handling - invalid provider
curl -X POST 'https://internal.integrations.chainels.com/webhook/weather' \
  -H 'Content-Type: application/json' \
  -d '{"city": "Paris", "provider": "invalid"}'
# Returns: {"status":"error","error":"Invalid provider: invalid. Valid options are: open-meteo, wttr",...}

# Test error handling - invalid city
curl -X POST 'https://internal.integrations.chainels.com/webhook/weather' \
  -H 'Content-Type: application/json' \
  -d '{"city": "asdfghjkl12345", "provider": "open-meteo"}'
# Returns: {"status":"error","error":"City not found: asdfghjkl12345",...}
```

### 2. Test System APIs Directly (For Debugging)

```bash
# Open-Meteo System API
curl -X POST 'https://internal.integrations.chainels.com/webhook/system-api/open-meteo' \
  -H 'Content-Type: application/json' \
  -d '{"city": "Amsterdam"}'

# wttr.in System API
curl -X POST 'https://internal.integrations.chainels.com/webhook/system-api/wttr' \
  -H 'Content-Type: application/json' \
  -d '{"city": "Amsterdam"}'
```

### 3. Compare Outputs (Verify Canonical Format)

```bash
# Both should return the same structure - pipe to jq to compare
curl -s -X POST 'https://internal.integrations.chainels.com/webhook/weather' \
  -H 'Content-Type: application/json' \
  -d '{"city": "Amsterdam", "provider": "open-meteo"}' | jq 'keys'

curl -s -X POST 'https://internal.integrations.chainels.com/webhook/weather' \
  -H 'Content-Type: application/json' \
  -d '{"city": "Amsterdam", "provider": "wttr"}' | jq 'keys'

# Both return: ["current", "location", "meta", "status"]
```

---

## How to Add a New Provider

Adding a third weather provider (e.g., OpenWeatherMap) requires **only creating a new System API workflow**. The Experience API is provider-agnostic and requires **zero changes**.

### Step 1: Create a New System API Workflow

Copy `system-api-wttr.json` and modify:

1. **Webhook path**: Change to `/system-api/openweathermap`
2. **HTTP Request node**: Update URL to new provider's API
3. **Code node**: Map new provider's fields to canonical format

```javascript
// Example mapping for a hypothetical provider
const canonical = {
  location: {
    city: response.name,           // Provider-specific field
    country: response.sys.country, // Provider-specific field
    latitude: response.coord.lat,
    longitude: response.coord.lon
  },
  current: {
    temperature: response.main.temp,
    feelsLike: response.main.feels_like,
    humidity: response.main.humidity,
    windSpeed: response.wind.speed * 3.6, // Convert m/s to km/h
    windDirection: response.wind.deg,
    weatherCode: response.weather[0].id,
    pressure: response.main.pressure
  },
  meta: {
    provider: 'openweathermap',
    timestamp: new Date().toISOString(),
    requestedCity: inputCity
  },
  status: 'success'
};
```

### Step 2: Deploy and Test

```bash
# Upload the new System API workflow
uv run python -c "
from n8n_client import N8nClient
client = N8nClient()
result = client.import_from_file('system-api-openweathermap.json')
client.activate_workflow(result['id'])
print(f'Created and activated: {result[\"id\"]}')
"

# Test new provider - Experience API automatically routes to it!
curl -X POST 'https://internal.integrations.chainels.com/webhook/weather' \
  -H 'Content-Type: application/json' \
  -d '{"city": "Amsterdam", "provider": "openweathermap"}'
```

**That's it!** No changes to the Experience API required. The dynamic URL `/webhook/system-api/{provider}` automatically routes to the new System API based on the `provider` parameter.

---

## Architecture Decisions

### Why Dynamic URL Instead of Switch/IF Node?

The Experience API uses a **dynamic URL pattern** instead of conditional routing:

```
URL: /webhook/system-api/{provider}
```

| Approach | Adding New Provider | Experience API Changes |
|----------|---------------------|----------------------|
| Switch/IF node | Create adapter + modify Experience API | Yes - add new branch |
| **Dynamic URL** | Create adapter only | **None** |

**We chose Dynamic URL** because:

1. **Zero coupling** - Experience API doesn't know about specific providers
2. **True scalability** - Adding provider #100 is identical to provider #2
3. **Simpler workflow** - Only 3 nodes instead of N+2 nodes
4. **Built-in validation** - n8n returns 404 if System API doesn't exist

### Why Only Overlapping Fields?

Both APIs have unique fields:
- **Open-Meteo only**: timezone, elevation
- **wttr.in only**: UV index, visibility, cloud cover

We **excluded** these from the canonical model because:
1. Canonical model must be **provider-agnostic**
2. All fields must be available from **all** providers
3. Consumers shouldn't need conditional logic per provider

If a field is critical, either:
- Add it to all adapters (even if estimated/derived)
- Create a separate "extended" response type

### Versioning System APIs

The dynamic URL pattern naturally supports **versioning** of System APIs. This allows you to evolve adapters without breaking existing consumers.

#### URL Patterns for Versioning

Option 1 - Version in path (recommended):

```
/webhook/system-api/{provider}/v1
/webhook/system-api/{provider}/v2
```

Option 2 - Version as parameter:

```json
{"city": "Amsterdam", "provider": "open-meteo", "version": "v2"}
```

#### How It Works

The Experience API constructs the URL dynamically:

```javascript
// Current (unversioned)
const url = `/webhook/system-api/${provider}`;

// With versioning
const version = input.version || 'v1';  // Default to v1
const url = `/webhook/system-api/${provider}/${version}`;
```

#### Example Versioned Workflows

| Workflow | Webhook Path | Purpose |
|----------|--------------|---------|
| System API - Open-Meteo v1 | `/system-api/open-meteo/v1` | Original implementation |
| System API - Open-Meteo v2 | `/system-api/open-meteo/v2` | New fields, different source |
| System API - wttr v1 | `/system-api/wttr/v1` | Original implementation |

#### Versioning Strategies

| Strategy | When to Use | Trade-offs |
|----------|-------------|------------|
| **Same canonical model** | Internal changes only (new data source, performance) | Consumers unchanged, but limits new fields |
| **Extended canonical model** | Adding optional fields | Backwards compatible, v2 returns superset |
| **Breaking changes** | Major restructure needed | Requires consumer updates, run both versions |

#### Best Practices

1. **Default to latest stable** - If no version specified, route to v1 (or current stable)
2. **Run versions side-by-side** - Keep v1 active while v2 is adopted
3. **Per-provider versioning** - Each provider can be on different versions
4. **Deprecation notices** - Add `meta.deprecation` field when sunsetting versions

```json
{
  "meta": {
    "provider": "open-meteo",
    "version": "v1",
    "deprecation": "v1 will be removed on 2025-06-01. Please migrate to v2."
  }
}
```

#### Adding a New Version

1. Copy existing System API workflow (e.g., `system-api-open-meteo.json`)
2. Update webhook path to include version (`/system-api/open-meteo/v2`)
3. Implement changes (new fields, different transformation, etc.)
4. Deploy alongside existing version
5. Update Experience API to support version parameter (one-time change)

```bash
# Test v1 (existing)
curl -X POST 'https://internal.integrations.chainels.com/webhook/weather' \
  -H 'Content-Type: application/json' \
  -d '{"city": "Amsterdam", "provider": "open-meteo", "version": "v1"}'

# Test v2 (new)
curl -X POST 'https://internal.integrations.chainels.com/webhook/weather' \
  -H 'Content-Type: application/json' \
  -d '{"city": "Amsterdam", "provider": "open-meteo", "version": "v2"}'
```

---

## Files in This Folder

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `experience-api-weather.json` | Experience API workflow (orchestrator) |
| `system-api-open-meteo.json` | Open-Meteo adapter workflow |
| `system-api-wttr.json` | wttr.in adapter workflow |

---

## Workflow IDs (Current Deployment)

| Workflow | ID |
|----------|-----|
| Experience API - Weather | `TZBSLLsF1j4eSTSw` |
| System API - Open-Meteo | `Y0Xhj54XzK0RkslJ` |
| System API - wttr.in | `HEAjmdnwFznzQszR` |

---

## Related Documentation

- [Harmonization Layer Architecture](../confluence-templates/harmonization-layer.md) - Full architecture principles
- [Self-Service Integration Admin Panel](../confluence-templates/self-service-integration.md) - Integration management UI concept

---

## Weather Providers Used

| Provider | URL | Auth | Notes |
|----------|-----|------|-------|
| Open-Meteo | [open-meteo.com](https://open-meteo.com) | None | Requires geocoding step (city → lat/lon) |
| wttr.in | [wttr.in](https://wttr.in) | None | Direct city lookup, use `?format=j1` for JSON |

Both providers are free with no API key required - ideal for demos and testing.

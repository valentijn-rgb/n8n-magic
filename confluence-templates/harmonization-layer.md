# Harmonization of Different Providers

Internal architecture documentation for standardizing integrations across different external systems.

> **Audience**: Engineering team, Solution Engineers building n8n workflows
>
> **Related**: [Integration Admin Panel](admin-panel.md) describes the user-facing Integration Admin Panel

---

## The Problem

Today, each integration is built as a standalone workflow:

* Entrata tenant sync has its own logic, API calls, and data transformations
* Lavanda tenant sync duplicates the same logic with different API calls
* YARDI tenant sync duplicates again with SFTP/CSV handling

This leads to:

| Issue | Impact |
| --- | --- |
| **Duplicated logic** | Same business rules implemented N times |
| **Inconsistent behavior** | Each integration handles edge cases differently |
| **High maintenance** | Bug fix in one doesn't propagate to others |
| **Slow onboarding** | New providers require building from scratch |

---

## The Solution: API Layering

Separate **what we do** (business logic) from **how we connect** (provider specifics) using two API layers:

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   EXPERIENCE APIs                                                   │
│   (Canonical Business Processes)                                    │
│                                                                     │
│   ┌───────────────┐  ┌───────────────┐  ┌───────────────┐          │
│   │  Tenant Sync  │  │  Ticket Sync  │  │ Booking Sync  │   ...    │
│   └───────┬───────┘  └───────┬───────┘  └───────┬───────┘          │
│           │                  │                  │                   │
│           │    Standardized Data Models (Canonicals)                │
│           │                  │                  │                   │
└───────────┼──────────────────┼──────────────────┼───────────────────┘
            │                  │                  │
            ▼                  ▼                  ▼
┌───────────────────────────────────────────────────────────────────────┐
│                                                                       │
│   SYSTEM APIs                                                         │
│   (Provider-Specific Adapters)                                        │
│                                                                       │
│   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐        │
│   │ Entrata │ │ Lavanda │ │  YARDI  │ │Freshdesk│ │  iLOQ   │  ...   │
│   │  (REST) │ │(GraphQL)│ │ (SFTP)  │ │  (REST) │ │  (REST) │        │
│   └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘        │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

---

## Layer Definitions

### Experience APIs (Top Layer)

**Purpose**: Define standardized business processes using canonical data models.

| Characteristic | Description |
| --- | --- |
| **Focus** | Business logic, workflows, orchestration |
| **Data format** | Canonical models (e.g., `StandardTenant`) |
| **Provider-agnostic** | No knowledge of Entrata, Lavanda, etc. |
| **Reusable** | One implementation serves all providers |

**Examples**:

* `tenant-sync` — Onboard/offboard/update tenants
* `ticket-sync` — Create/update/resolve tickets bidirectionally
* `booking-sync` — Sync room reservations to external panels
* `parcel-notify` — Send parcel arrival notifications

### System APIs (Bottom Layer)

**Purpose**: Expose specific external systems through a standardized interface.

| Characteristic | Description |
| --- | --- |
| **Focus** | Authentication, protocol handling, data transformation |
| **Data format** | Transforms provider format ↔ canonical format |
| **Provider-specific** | Each adapter knows one external system |
| **Encapsulated** | Hides API quirks, pagination, rate limits |

**Examples**:

* `entrata-api` — REST API, API key auth, multiple endpoints
* `lavanda-api` — GraphQL API, OAuth2, single query endpoint
* `yardi-api` — SFTP file transfer, CSV parsing
* `freshdesk-api` — REST API, API key + webhooks

---

## Real Example: Tenant Sync (Inbound)

This example shows a **unidirectional inbound** flow where tenant data is read from an external system and synced to Chainels. The System API only reads; all writes happen to the Chainels API.

> **Note**: Bidirectional flows (e.g., ticketing) would have System APIs with both read and write operations.

### Call Hierarchy

```
┌─────────────────┐      ┌─────────────────────────────────┐      ┌─────────────────────────────┐
│                 │      │                                 │      │                             │
│    Chainels     │─────►│  Experience API: tenant-sync    │─────►│  System API: entrata-adapter│
│    Platform     │      │  /tenant-sync                   │      │  /fetch-tenants             │
│                 │      │                                 │      │                             │
└─────────────────┘      └─────────────────────────────────┘      └─────────────────────────────┘
                                      │                                        │
                                      │  1. Calls System API to fetch tenants  │
                                      │     (read-only from external system)   │
                                      │                                        │
                                      │  2. Compares with Chainels members     │
                                      │                                        │
                                      │  3. Executes actions in CHAINELS:      │
                                      │     • POST /members (onboard)          │
                                      │     • DELETE /members (offboard)       │
                                      │     • PUT /members (update)            │
                                      │                                        │
                                      ▼                                        │
                              ┌───────────────┐                                │
                              │  Chainels API │◄───────────────────────────────┘
                              └───────────────┘
```

### The Experience API Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  EXPERIENCE API: tenant-sync                                    │
│  Webhook: POST /tenant-sync                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Call System API /{adapter}/fetch-tenants                    │
│           │                                                     │
│           ▼  Returns StandardTenant[]                           │
│                                                                 │
│  2. Fetch current Chainels members                              │
│           │                                                     │
│           ▼  GET /api/v2/companies/{id}/members                 │
│                                                                 │
│  3. Compare datasets                                            │
│           │                                                     │
│           ├──► toOnboard[]   (in external, not in Chainels)     │
│           ├──► toOffboard[]  (in Chainels, not in external)     │
│           └──► toUpdate[]    (in both, but different unit)      │
│                                                                 │
│  4. Execute actions against Chainels API                        │
│           │                                                     │
│           ├──► POST /members    for each toOnboard              │
│           ├──► DELETE /members  for each toOffboard             │
│           └──► PUT /members     for each toUpdate               │
│                                                                 │
│  5. Return ExecutionSummary                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

This flow is **identical** regardless of whether the source is Entrata, Lavanda, or YARDI. Only the System API adapter changes.

### System API: Entrata Adapter

```
┌─────────────────────────────────────────────────────────────────┐
│  SYSTEM API: entrata-api                                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Authentication: API Key (stored in Secrets Manager)            │
│  Protocol: REST                                                 │
│                                                                 │
│  fetchTenants(config):                                          │
│    1. GET /ext/orgs/{org}/v1/customers                          │
│    2. GET /ext/orgs/{org}/v1/leases                             │
│    3. GET /ext/orgs/{org}/v1/propertyunits                      │
│    4. Join data by customerId                                   │
│    5. Transform to StandardTenant[]                             │
│                                                                 │
│  Field Mapping:                                                 │
│  ┌────────────────────┬────────────────────────┐                │
│  │ Entrata Field      │ StandardTenant Field   │                │
│  ├────────────────────┼────────────────────────┤                │
│  │ customerId         │ externalId             │                │
│  │ firstName          │ firstName              │                │
│  │ lastName           │ lastName               │                │
│  │ email              │ email                  │                │
│  │ phone              │ phone                  │                │
│  │ unit.unitNumber    │ unitCode               │                │
│  │ lease.leaseFromDate│ leaseStartDate         │                │
│  │ lease.leaseToDate  │ leaseEndDate           │                │
│  │ customerStatus     │ status (mapped)        │                │
│  └────────────────────┴────────────────────────┘                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### System API: Lavanda Adapter

```
┌─────────────────────────────────────────────────────────────────┐
│  SYSTEM API: lavanda-api                                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Authentication: OAuth2 Client Credentials                      │
│  Protocol: GraphQL                                              │
│                                                                 │
│  fetchTenants(config):                                          │
│    1. POST /v1/oauth2/token (get access token)                  │
│    2. POST /graphql with bookings query                         │
│    3. Flatten contacts from bookings                            │
│    4. Transform to StandardTenant[]                             │
│                                                                 │
│  GraphQL Query:                                                 │
│    query {                                                      │
│      bookings(filter: { status: CHECKED_IN }) {                 │
│        bookingId                                                │
│        contacts { contactId, firstName, lastName, ... }         │
│        checkInDate                                              │
│        checkOutDate                                             │
│        accommodations { unitInfo { unitNumber } }               │
│      }                                                          │
│    }                                                            │
│                                                                 │
│  Field Mapping:                                                 │
│  ┌────────────────────────┬────────────────────────┐            │
│  │ Lavanda Field          │ StandardTenant Field   │            │
│  ├────────────────────────┼────────────────────────┤            │
│  │ contact.contactId      │ externalId             │            │
│  │ contact.firstName      │ firstName              │            │
│  │ contact.lastName       │ lastName               │            │
│  │ contact.primaryEmail   │ email                  │            │
│  │ contact.phoneNumber    │ phone                  │            │
│  │ accommodation.unitNumber│ unitCode              │            │
│  │ booking.checkInDate    │ leaseStartDate         │            │
│  │ booking.checkOutDate   │ leaseEndDate           │            │
│  │ booking.status         │ status (mapped)        │            │
│  └────────────────────────┴────────────────────────┘            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Side-by-Side Comparison

| Aspect | Entrata | Lavanda | Canonical |
| --- | --- | --- | --- |
| **Auth** | API Key | OAuth2 | — |
| **Protocol** | REST (3 endpoints) | GraphQL (1 query) | — |
| **Tenant ID** | `customerId` | `contactId` | `externalId` |
| **Lease Start** | `leaseFromDate` | `checkInDate` | `leaseStartDate` |
| **Lease End** | `leaseToDate` | `checkOutDate` | `leaseEndDate` |
| **Unit** | Separate API call | Nested in booking | `unitCode` |
| **Status values** | Custom statuses | `CHECKED_IN/OUT` | `active/departed` |

Despite these differences, the Experience API receives the same `StandardTenant[]` format from both.

---

## Building New Integrations

### Adding a New Provider (System API)

When adding support for a new property management system (e.g., RealPage):

#### 1. Define the Field Mapping

First, document how the provider's data model maps to the canonical Chainels data model. This is the most critical step.

| Provider Field | Canonical Field | Transformation |
| --- | --- | --- |
| `resident_id` | `externalId` | Direct mapping |
| `first_name` | `firstName` | Direct mapping |
| `unit_code` | `unitCode` | Direct mapping |
| `lease_start` | `leaseStartDate` | Parse to ISO 8601 |
| `status` | `status` | Map: "Active" → "active", "Notice" → "departed" |

The canonical model must align with the Chainels member data structure so the Experience API can write directly to the Chainels API without additional transformation.

#### 2. Create the Adapter Workflow

Build the n8n workflow with a webhook endpoint: `/{provider}-adapter/:action`

The adapter receives configuration (including credentials) from the Experience API call:

```json
{
  "communityId": "12345",
  "credentials": {
    "apiKey": "***",
    "propertyId": "67890"
  }
}
```

> **Credentials**: All passwords, tokens, and API keys are stored in an encrypted Secrets Manager. They are passed to the System API as part of the configuration payload (see Integration Admin Panel for the configuration API).

#### 3. Implement Adapter Operations

For tenant sync (inbound), typically only one operation is needed:

* `fetchTenants(config)` → Returns `StandardTenant[]`

The adapter handles:

* Authentication with the external system
* Pagination and rate limiting
* Error handling and retries
* Data transformation to canonical format

#### 4. Document the Integration

Add to Confluence:

* API endpoints used
* Field mapping table
* Authentication requirements
* Known limitations

The Experience API (tenant-sync) requires **zero changes**.

### Adding a New Experience API

When adding a new business process (e.g., visitor management):

1. **Define the canonical model** (e.g., `StandardVisitor`)
2. **Build the Experience API workflow**:

    * Define the process steps
    * Use canonical models throughout
    * Call System APIs through standardized interface

3. **Create adapters** for each supported provider:

    * Map provider data → canonical
    * Map canonical → provider data (if bidirectional)

4. **Document** the canonical model and supported providers

---

## n8n Implementation Pattern

### Workflow Structure

```
┌─────────────────────────────────────────────────────────────────┐
│  Main Workflow: [Customer] - Tenant Sync                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐                                                │
│  │  Schedule   │  (Daily at 6:00 AM)                            │
│  └──────┬──────┘                                                │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Sub-workflow: System API - {Provider}                  │    │
│  │  (e.g., "System API - Entrata" or "System API - Lavanda")│   │
│  │  Returns: StandardTenant[]                              │    │
│  └──────┬──────────────────────────────────────────────────┘    │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Sub-workflow: Experience API - Tenant Sync             │    │
│  │  (Shared across all providers)                          │    │
│  │  Input: StandardTenant[]                                │    │
│  │  Output: ExecutionSummary                               │    │
│  └──────┬──────────────────────────────────────────────────┘    │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────┐                                                │
│  │  Log/Alert  │                                                │
│  └─────────────┘                                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Naming Conventions

| Type | Naming Pattern | Example |
| --- | --- | --- |
| **Main workflow** | `[Customer] - {Process}` | `[Greystar] - Tenant Sync` |
| **System API** | `System API - {Provider}` | `System API - Entrata` |
| **Experience API** | `Experience API - {Process}` | `Experience API - Tenant Sync` |
| **Sub-workflow** | `{Process} - {Action}` | `Tenant Sync - Onboard Members` |

---

## Benefits Summary

| Aspect | Before (Direct) | After (Harmonized) |
| --- | --- | --- |
| **New provider** | Build from scratch (~40h) | Build adapter only (~8h) |
| **Bug in logic** | Fix in N workflows | Fix once in Experience API |
| **Testing** | Test each integration | Test Experience API + adapters separately |
| **Consistency** | Varies by implementation | Guaranteed identical behavior |
| **Documentation** | Scattered | Canonical models are self-documenting |

---

## Related Documents

* Integration Admin Panel — User-facing Integration Admin Panel proposal
* Integration Strategy — Full integration strategy
* Existing integration documentation in Confluence

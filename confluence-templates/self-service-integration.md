# Integration Admin Panel

A proposal for a self-service integration management system within the Chainels Admin Panel.

---

## The Problem

Today, setting up integrations for Chainels clients is a **manual, time-consuming process**:

* Engineering team must configure each integration individually
* Clients cannot self-service or troubleshoot their own integrations
* No visibility into integration health or execution history
* Credentials and settings are scattered across systems
* Scaling to more clients means linear growth in engineering overhead

---

## The Vision

**What if clients could configure and manage their integrations themselves?**

An Integration Admin Panel would allow clients to:

1. **Browse** a marketplace of pre-built integration templates
2. **Configure** integrations with a guided setup wizard
3. **Monitor** integration health and execution history
4. **Self-service** common issues (update credentials, adjust schedules, retry failed runs)

---

## Key Concepts

### Integration Templates

A **template** is a reusable integration blueprint that can be instantiated for any client.

| Template Component | Description |
| --- | --- |
| **Workflow Logic** | The actual data transformation and sync logic |
| **Configuration Schema** | What inputs the client needs to provide (credentials, mapping, options) |
| **Category & Metadata** | How the template appears in the marketplace |

**Example templates by category:**

* **Access Control**: iLOQ, Salto, 2N, Paxton
* **Ticketing**: Freshdesk, Zendesk, ServiceNow
* **Property Management**: Entrata, YARDI, MRI, RealPage
* **Payments**: Stripe, Mollie
* **Parcels**: Parcel Pending, Luxer One

### Integration Instances

When a client configures a template, it creates an **workflow** with:

* Client-specific credentials
* Selected communities/scope
* Schedule preferences
* Custom field mappings (if applicable)

One template can have many instances across different clients.

---

## Benefits

### For Clients

| Benefit | Impact |
| --- | --- |
| **Self-service** | Configure integrations without waiting for Chainels support |
| **Visibility** | See exactly what's syncing and when |
| **Control** | Update settings, retry failures, pause/resume |
| **Faster onboarding** | New integrations in minutes, not days |

### For Chainels

| Benefit | Impact |
| --- | --- |
| **Scalability** | Onboard 100 clients without 100x engineering effort |
| **Reduced support** | Clients handle common issues themselves |
| **Consistency** | All instances use the same tested template |
| **Focus on building** | Engineering builds templates once, clients deploy many times |

---

## Integration Types to Support

### By Trigger Method

| Type | Description | Example |
| --- | --- | --- |
| **Scheduled** | Runs on a fixed interval (hourly, daily) | Tenant sync from Entrata |
| **Real-time** | Triggered by webhooks from external system | Ticket created in Freshdesk |
| **On-demand** | Triggered by action in Chainels | Booking synced to external calendar |

### By Data Flow

| Direction | Description | Example |
| --- | --- | --- |
| **Inbound** | External system → Chainels | Tenant data from property management |
| **Outbound** | Chainels → External system | Booking to room panel |
| **Bidirectional** | Both directions | Ticketing with status sync |

---

## API Endpoints (Admin Panel)

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/integrations/categories` | List all integration categories |
| `GET` | `/integrations/{category}/templates` | List available templates for a category |
| `GET` | `/integrations/templates/{templateId}` | Get template details (required fields, options) |
| `POST` | `/integrations` | Create new integration instance (configure + activate) |
| `GET` | `/integrations` | List all integration instances for client |
| `GET` | `/integrations/{integrationId}` | Get integration instance details |
| `PUT` | `/integrations/{integrationId}` | Update integration settings |
| `DELETE` | `/integrations/{integrationId}` | Deactivate/remove integration |
| `GET` | `/integrations/{integrationId}/executions` | List execution history |
| `GET` | `/integrations/{integrationId}/executions/{executionId}` | Get execution details |
| `POST` | `/integrations/{integrationId}/executions` | Trigger manual execution |
| `GET` | `/integrations/{integrationId}/settings` | Get all settings for integration |
| `PUT` | `/integrations/{integrationId}/settings` | Update settings |
| `PUT` | `/integrations/{integrationId}/credentials` | Update credentials (encrypted) |
| `GET` | `/integrations/{integrationId}/schedule` | Get schedule configuration |
| `PUT` | `/integrations/{integrationId}/schedule` | Update schedule |
| `GET` | `/integrations/{integrationId}/health` | Get integration health status |
| `GET` | `/integrations/health` | Get health overview for all integrations |

---

## Real-Life Example: Entrata (Tenant Onboarding)

This section demonstrates how the Admin Panel workflow would work with **Entrata**, a Property Management System integration for tenant onboarding/offboarding.

### Integration Overview

| Attribute | Value |
| --- | --- |
| **Provider** | Entrata |
| **Category** | Property Management |
| **Data Flow** | Inbound (Entrata → Chainels) |
| **Trigger Type** | Scheduled (Daily) |
| **Use Case** | Sync tenant move-ins and move-outs to automatically create/archive Chainels members |

### What Data Gets Synced

| Data Field | Source (Entrata) | Target (Chainels) |
| --- | --- | --- |
| Customer ID | Entrata tenant ID | Member external reference |
| First/Last Name | Tenant profile | Member name |
| Email | Tenant contact | Member email |
| Lease Start Date | Lease record | Member activation date |
| Lease End Date | Lease record | Member archival trigger |
| Unit Number | Property unit | Community assignment |
| Move-in Date | Lease record | Member onboarding date |

---

### Step 1: Browse & Select Template

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  CHAINELS ADMIN PANEL - INTEGRATIONS                                         │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─ SIDEBAR ─────────┐   ┌─ MAIN CONTENT ──────────────────────────────────┐ │
│  │                   │   │                                                 │ │
│  │  📂 Categories    │   │  PROPERTY MANAGEMENT TEMPLATES                  │ │
│  │  ├─ Access Ctrl   │   │  ═══════════════════════════════════════════    │ │
│  │  ├─ Ticketing     │   │                                                 │ │
│  │  ├─ Payments      │   │  ┌─────────┐  ┌─────────┐  ┌─────────┐         │ │
│  │  ├─ Property Mgmt◄│   │  │ Entrata │  │  YARDI  │  │ MRI     │         │ │
│  │  ├─ Parcels       │   │  │  ┌───┐  │  │  ┌───┐  │  │  ┌───┐  │         │ │
│  │  └─ Utilities     │   │  │  │ 🏢 │  │  │  │ 🏢 │  │  │  │ 🏢 │  │         │ │
│  │                   │   │  │  └───┘  │  │  └───┘  │  │  └───┘  │         │ │
│  │                   │   │  │ Tenant  │  │ Tenant  │  │ Tenant  │         │ │
│  │                   │   │  │  Sync   │  │  Sync   │  │  Sync   │         │ │
│  │                   │   │  └────┬────┘  └─────────┘  └─────────┘         │ │
│  │                   │   │       │                                        │ │
│  │                   │   │       ▼  [Configure]                           │ │
│  │                   │   │                                                 │ │
│  └───────────────────┘   └─────────────────────────────────────────────────┘ │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

**User action**: Admin selects "Property Mgmt" category, then clicks "Configure" on Entrata template.

---

### Step 2: Configure Authentication

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  CONFIGURE INTEGRATION: Entrata Tenant Sync                                  │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Step 1 of 3: Authentication                                                 │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                       │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  Entrata API Key *                                                      │ │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │ │
│  │  │ ent_api_k3y_xxxxxxxxxxxxxxxxx                                   │   │ │
│  │  └─────────────────────────────────────────────────────────────────┘   │ │
│  │  ⓘ Obtain from Entrata Admin > API Settings                            │ │
│  │                                                                         │ │
│  │  Entrata Property ID *                                                  │ │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │ │
│  │  │ 12345                                                           │   │ │
│  │  └─────────────────────────────────────────────────────────────────┘   │ │
│  │  ⓘ Your Entrata property identifier                                    │ │
│  │                                                                         │ │
│  │  Environment                                                            │ │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │ │
│  │  │ Production                                                    ▼ │   │ │
│  │  └─────────────────────────────────────────────────────────────────┘   │ │
│  │                                                                         │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│                                              [Cancel]  [Next: Schedule →]    │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Template-specific fields for Entrata**:

* API Key (provided by client from their Entrata account)
* Property ID (maps to their Entrata property)
* Environment selector (Production/Sandbox)

---

### Step 3: Configure Schedule

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  CONFIGURE INTEGRATION: Entrata Tenant Sync                                  │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Step 2 of 3: Trigger & Schedule                                             │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                       │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  Trigger Type                                                           │ │
│  │                                                                         │ │
│  │  ○ Real-time (Webhook)                                                  │ │
│  │    └─ Not available for Entrata (API polling only)                      │ │
│  │                                                                         │ │
│  │  ● Scheduled                                                            │ │
│  │    └─ Recommended: Daily sync for tenant changes                        │ │
│  │                                                                         │ │
│  │       Schedule: ┌─────────────────┐                                     │ │
│  │                 │ Daily at 6:00 ▼ │                                     │ │
│  │                 └─────────────────┘                                     │ │
│  │                                                                         │ │
│  │       ⓘ Syncs new move-ins and processes move-outs daily                │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│                                          [← Back]  [Next: Select Scope →]    │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Schedule considerations for Entrata**:

* Daily sync is recommended (tenant data doesn't change frequently)
* Early morning runs ensure data is ready for business hours
* Entrata API is polling-based, not webhook-based

---

### Step 4: Configure Scope & Communities

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  CONFIGURE INTEGRATION: Entrata Tenant Sync                                  │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Step 3 of 3: Scope & Communities                                            │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                       │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  Select Communities                                                     │ │
│  │                                                                         │ │
│  │  ☐ All communities                                                     │ │
│  │                                                                         │ │
│  │  Select specific (1 selected):                                          │ │
│  │  ☑ Riverside Apartments - Chicago         (Entrata Prop: 12345)        │ │
│  │  ☐ Downtown Lofts - Miami                 (Not linked)                 │ │
│  │  ☐ Harbor View - Seattle                  (Not linked)                 │ │
│  │                                                                         │ │
│  │  ─────────────────────────────────────────────────────────────────     │ │
│  │                                                                         │ │
│  │  Sync Options                                                           │ │
│  │  ☑ Create new members on move-in                                       │ │
│  │  ☑ Archive members on move-out                                         │ │
│  │  ☑ Update member details on lease changes                              │ │
│  │  ☐ Sync household members (roommates)                                  │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│                                              [← Back]  [✓ Activate]          │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Scope options for Entrata**:

* Map Entrata Property ID to Chainels Community
* Choose which tenant lifecycle events to sync
* Option to include household members (roommates on same lease)

---

### Activation & Data Flow

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │
│    ENTRATA      │      │      N8N        │      │    CHAINELS     │
│   (External)    │      │   (Workflow)    │      │   (Platform)    │
│                 │      │                 │      │                 │
└────────┬────────┘      └────────┬────────┘      └────────┬────────┘
         │                        │                        │
         │                        │◄───── Trigger ─────────│ Daily 6:00 AM
         │                        │       (Schedule)       │
         │                        │                        │
         │◄──── GET /residents ───│                        │
         │      (with filters)    │                        │
         │                        │                        │
         │───── Tenant List ─────►│                        │
         │      (JSON response)   │                        │
         │                        │                        │
         │                        │──── POST /members ────►│ New move-ins
         │                        │                        │
         │                        │──── PUT /members ─────►│ Updates
         │                        │                        │
         │                        │─── DELETE /members ───►│ Move-outs
         │                        │                        │
         │                        │───── Execution ───────►│ Log result
         │                        │       Complete         │
         │                        │                        │
```

**What happens during execution**:

1. **Chainels triggers N8N** at scheduled time (6:00 AM daily)
2. **N8N calls Entrata API** with configured credentials
3. **Entrata returns** tenant data (new leases, ended leases, changes)
4. **N8N processes data** using priority-based matching logic:

    * Match by Customer ID (primary)
    * Match by Email (secondary)
    * Match by Name + Unit (fallback)

5. **N8N calls Chainels API** to create/update/archive members
6. **Execution logged** with success/failure status and record counts

---

### Active Integration Dashboard (Entrata)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  INTEGRATION: Entrata Tenant Sync                               [Settings]   │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Status: ● Active                          Schedule: Daily at 6:00 AM       │
│  Community: Riverside Apartments           Next run: Tomorrow 6:00 AM       │
│                                                                              │
│  ┌─ EXECUTION HISTORY ──────────────────────────────────────────────────────┐│
│  │                                                                          ││
│  │  [▶ Run Now]                                                             ││
│  │                                                                          ││
│  │  ┌────────┬─────────────────────┬──────────┬───────────────────────────┐││
│  │  │ Status │ Timestamp           │ Duration │ Details                   │││
│  │  ├────────┼─────────────────────┼──────────┼───────────────────────────┤││
│  │  │ ✓ OK   │ 2024-01-15 06:00:12 │ 8.3s     │ +3 new, 1 updated, 2 out  │││
│  │  │ ✓ OK   │ 2024-01-14 06:00:09 │ 7.1s     │ +1 new, 0 updated, 0 out  │││
│  │  │ ✓ OK   │ 2024-01-13 06:00:15 │ 6.8s     │ +0 new, 2 updated, 1 out  │││
│  │  │ ✗ FAIL │ 2024-01-12 06:00:03 │ 30.0s    │ Entrata API timeout       │││
│  │  │ ✓ OK   │ 2024-01-11 06:00:11 │ 7.4s     │ +5 new, 0 updated, 0 out  │││
│  │  └────────┴─────────────────────┴──────────┴───────────────────────────┘││
│  │                                                                          ││
│  │  Legend: +N new = move-ins, N updated = lease changes, N out = move-outs ││
│  └──────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  ┌─ SYNC SUMMARY (Last 30 Days) ───────────────────────────────────────────┐│
│  │  New Members Created: 47  │  Members Updated: 12  │  Members Archived: 8 ││
│  │  Success Rate: 96.7%      │  Avg Duration: 7.4s   │  Total Runs: 30      ││
│  └──────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

### Error Handling Example

When the Entrata API times out (as shown on 2024-01-12), the system:

1. **Automatic retry** (3 attempts with exponential backoff)
2. If all retries fail → **Mark execution as failed**
3. **Alert triggered** based on error type:

    * Entrata API timeout → Retry next scheduled run (transient)
    * Invalid credentials → Alert client admin (configuration error)
    * Chainels API error → Alert Chainels engineering (technical)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  ⚠ EXECUTION FAILED                                              [Dismiss]   │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Integration: Entrata Tenant Sync                                            │
│  Timestamp: 2024-01-12 06:00:03                                              │
│  Error: Entrata API timeout after 30 seconds                                 │
│                                                                              │
│  Retry attempts: 3/3 failed                                                  │
│  Next scheduled run: 2024-01-13 06:00:00                                     │
│                                                                              │
│  ℹ This appears to be a transient Entrata API issue.                         │
│    The sync will retry automatically at the next scheduled time.             │
│                                                                              │
│  [View Logs]  [Run Now]  [Contact Support]                                   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

### API Calls for This Integration

| Step | API Call | Purpose |
| --- | --- | --- |
| Activation | `POST /integrations` | Create Entrata integration instance |
| Daily Trigger | Platform scheduler | Triggers N8N workflow |
| Fetch Tenants | N8N → Entrata API | `GET /residents?propertyId=12345` |
| Create Member | N8N → Chainels | `POST /api/v2/companies/{communityId}/members` |
| Update Member | N8N → Chainels | `PUT /api/v2/companies/{communityId}/members/{id}` |
| Archive Member | N8N → Chainels | `DELETE /api/v2/companies/{communityId}/members/{id}` |
| Log Execution | N8N → Chainels | Execution result stored for dashboard |
| View History | `GET /integrations/{id}/executions` | Admin views past runs |

---

## Questions to Explore

1. **Which integrations are candidates for self-service?**

    * Some integrations may be too complex for client configuration
    * Others are perfect candidates (standard API, clear configuration)

2. **What's the migration path for existing integrations?**

    * Can current client integrations be converted to template instances?
    * Or start fresh with new clients?

3. **What level of customization is needed?**

    * Simple credential + scope may cover 80% of cases
    * Complex field mapping may be needed for some integrations

4. **How do we handle template updates?**

    * When we improve a template, how do existing instances get the update?

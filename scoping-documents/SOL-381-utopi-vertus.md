# Scoping Document: Utopi/Vertus Energy Data Integration

[Click here to see pricing](#-pricing)

## :flag_on: Problem to solve

Enable automatic synchronization of utility consumption data (electricity, heating, water, gas, cooling) from Utopi to Chainels households for the Vertus site, ensuring that each household's daily consumption is displayed within the Chainels platform.

## :dart: Scope & Requirements

1. **Custom Field Setup**
   * Create a `space_uuid` custom field on Chainels households to store the corresponding Utopi Space UUID for mapping.

2. **Webhook Integration**
   * Receive consumption data requests from Chainels via webhook, including household identifier and date range (start_date, end_date).

3. **OAuth2 Authentication**
   * Exchange client credentials for an access token via Microsoft OAuth2 (client_credentials flow).
   * Token endpoint: `POST https://login.microsoftonline.com/c1365f8a-9b37-4a25-8af0-5c7b84f88917/oauth2/v2.0/token`

4. **Space UUID Lookup**
   * Read the Space UUID from the household's custom field to identify the correct Utopi space.

5. **Data Retrieval**
   * Call Utopi Get Space Aggregated Metrics API for all metric types:
     - Electricity
     - Heating
     - Water
     - Gas
     - Cooling
   * Endpoint: `GET /spaces/:spaceuuid/aggregate/:metrictype/:granularity`

6. **Data Transformation**
   * Format Utopi API response to match Chainels consumption display requirements.

7. **Response Delivery**
   * Return consumption data to Chainels via webhook response.

## :x: Out of Scope

* **Local data storage / SFTP** - Not needed; direct API integration is sufficient (per feedback from Alonso).
* **Real-time streaming** - On-demand via webhook only; no continuous data push.
* **Manual data entry** - All data is fetched automatically from Utopi API.
* **Historical backfill beyond API limits** - Subject to Utopi API data retention policies.

## :boxing_glove: Technical Challenges

* **API rate limits** - Utopi API rate limits are unknown; needs monitoring during initial deployment.
* **Missing data periods** - Some metrics may have gaps; need graceful handling of null/missing data.
* **Token expiration** - OAuth2 tokens expire; need to handle refresh or re-authentication.
* **Multiple metric types** - Need to call API multiple times (once per metric type) or handle batch requests if supported.

## :construction: Dependencies

* **Chainels webhook configuration** - Webhook must provide start_date and end_date in the request payload.
* **Custom field creation** - The `space_uuid` custom field must be created and populated for each household in Chainels before the integration can work.
* **1Password credentials** - API credentials (client_id, client_secret, scope) must be configured in n8n from 1Password.
* **Utopi API access** - Active API credentials with access to the Vertus site.

## :bulb: Workarounds

* None required - direct API integration meets all requirements.

## :star: Proposed solution

### Architecture

**Single n8n Workflow**: Webhook Processing + HTTP API Integration pattern

```
Webhook Trigger → OAuth2 Token → Get Metrics → Transform → Respond to Webhook
```

### Workflow Nodes

1. **Webhook Trigger** - Receive request with household_id, start_date, end_date
2. **HTTP Request (OAuth2)** - Get access token from Microsoft OAuth2 endpoint
3. **HTTP Request (Utopi API)** - Call Get Space Aggregated Metrics for each metric type
4. **Code Node** - Transform Utopi response to Chainels format
5. **Respond to Webhook** - Return consumption data to Chainels

### Available webhooks and identifiers

| Webhook | Purpose | Trigger |
| ------- | ------- | ------- |
| Consumption Data Request | Receive requests from Chainels for household consumption data | Chainels platform |

**Expected webhook payload:**
```json
{
  "household_id": "string",
  "space_uuid": "9584D210-52FB-4E58-BE55-FED31AB6A260",
  "start_date": "2025-01-01",
  "end_date": "2025-01-31"
}
```

### Available API calls to perform

| Endpoint | Method | Purpose |
| -------- | ------ | ------- |
| `/oauth2/v2.0/token` | POST | Get OAuth2 access token |
| `/spaces/:spaceuuid/aggregate/electricity/daily` | GET | Get electricity consumption |
| `/spaces/:spaceuuid/aggregate/heating/daily` | GET | Get heating consumption |
| `/spaces/:spaceuuid/aggregate/water/daily` | GET | Get water consumption |
| `/spaces/:spaceuuid/aggregate/gas/daily` | GET | Get gas consumption |
| `/spaces/:spaceuuid/aggregate/cooling/daily` | GET | Get cooling consumption |

### Custom fields needed

| Field Name | Type | Location | Purpose |
| ---------- | ---- | -------- | ------- |
| `space_uuid` | Text | Chainels Household | Store Utopi Space UUID for mapping |

### Configuration Details

| Item | Value |
| ---- | ----- |
| Vertus Site ID | `9584D210-52FB-4E58-BE55-FED31AB6A260` |
| API Documentation | https://partner.utopi.io/ |
| Credentials | [1Password Link](https://start.1password.com/open/i?a=PHYWTMXZY5D4LBNBWDA4IV4H2E&v=dl6ppgtobxbpargd7zat5kffiu&i=qqo4pmdunrvvfi3uzn6j6qaaiu&h=chainels.1password.com) |

### Authentication Flow

1. **Token Request:**
   ```
   POST https://login.microsoftonline.com/c1365f8a-9b37-4a25-8af0-5c7b84f88917/oauth2/v2.0/token
   Content-Type: application/x-www-form-urlencoded
   ```

2. **Token Request Body:**
   | Key | Value |
   | --- | ----- |
   | client_id | (from 1Password) |
   | client_secret | (from 1Password) |
   | scope | (from 1Password) |
   | grant_type | client_credentials |

3. **API Request Header:**
   ```
   Authorization: Bearer {access_token}
   ```

## :busts_in_silhouette: Checkpoints

- [x] Initial call / request raised by the customer.
- [x] First time integration? Gather the requirements and fill them in the **Scope & Requirements** section of this document.
- [x] Existing integration? Explain to the customer how this integration works.
- [ ] Check with commercial when is the expected timeline to deliver the quote.
- [ ] Create the integration in the Discovery Chainels project.

- [x] Engage with 3rd party provider. Send an email and/or propose a meeting to discuss the integration.
- [x] Access to the 3rd party tool or documentation has been provided.
- [x] API/Documentation reference: https://partner.utopi.io/

- [x] Access to the 3rd party API (if applicable) or data has been provided.
- [x] API/Credentials in 1Password.

- [ ] Is there a possibility of having webhooks?
- [ ] Are webhooks set?

- [ ] Check if the steps to become a certified partner:
- [ ] Integration should be certified before launching. Check this box once is certified.
- [ ] Are there any costs?
- [ ] NDA needed? Check this box once it is signed and sent to the provider.

- [x] Review API documentation or data.
- [x] Check if all the relevant endpoints for the integration exist. Find possible missing endpoints.
- [x] Do we have unique identifiers? Yes - Space UUID.
- [x] Do we have all the necessary data? Yes - via Get Space Aggregated Metrics endpoint.

- [x] Check the data structure format. Find possible roadblocks and list them below.
- [x] Document findings.
- [ ] Are the findings a blocker? No blockers identified.
- [ ] Communicate the blocker with the team and Aron. Proceed with any of the actions below depending on the situation:
  - [ ] 3rd party software: Engage with the 3rd party software provider
  - [ ] Infrastructure: Engage with DevSecOps → Caslay
  - [ ] Chainels Platform: Engage with Product → Aron/Berk

- [x] Document the results as needed (challenges, out of scope, workarounds, dependencies).

- [x] Write down the proposed solution.
- [ ] Update the integration in Discovery Chainels.
- [ ] Quotation
  - [ ] Quotation not needed or is part of the deal.
  - [ ] Share and review quote with account manager.

- [ ] Have a final meeting with the customer.
  - [ ] Present the proposed solution and exchange feedback.
  - [ ] If there is feedback that is needed to be implemented in the solution, document it as part of the solution.
  - [ ] Are these major changes? → Re-engage with Aron to re-quote.

- [ ] If the customer agrees with the proposed solution:
  - [ ] Move the integration to the backlog in Discovery Chainels → This will create a task in the Solutions project automatically.

## :moneybag: Pricing

|  | **One Time Fee** | **License fee (per month)** |
| --- | --- | --- |
| 1st Community |  |  |
| Next communities |  |  |

---

## Links

- [Jira Ticket SOL-381](https://chainels.atlassian.net/browse/SOL-381)
- [Confluence Scoping Document](https://chainels.atlassian.net/wiki/x/CAALOQ)
- [Utopi API Documentation](https://partner.utopi.io/)

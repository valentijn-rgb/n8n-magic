# Scoping Document Template

[Click here to see pricing](#-pricing)

## :flag_on: Problem to solve

Enable Chainels users to click a "Send to External Service" button in the content service and have their profile data (first name, last name, email) automatically retrieved via OIDC and appended as query parameters to a redirect URL—seamlessly, both on web and mobile, with a one-time consent flow.

## :dart: Scope & Requirements

1. **Button Trigger**

* Add a button in the Chainels content service UI (web & mobile) that opens a configurable URL (n8n webhook).

2. **OIDC Consent Flow**

* On first click, redirect user through Chainels OIDC authorize endpoint to obtain consent.

* Support standard OIDC scopes (openid profile email).

3. **Token Exchange & Profile Fetch**

* In n8n: receive authorization code, exchange for tokens, call /userinfo to get { given_name, family_name, email }.

4. **Persist Consent**

* Store refresh token server-side to avoid re-prompting user on subsequent clicks.

5. **Redirect with Query Parameters**

* After fetching profile, redirect browser (or mobile WebView) to target URL, appending ?firstName=…&lastName=…&email=….

6. **Cross-Platform Support**

* Ensure deep-link or universal-link behavior on Android and iOS apps.

7. **Security & Validation**

* Validate redirect URL against an allow-list to prevent open-redirect vulnerabilities.

8. **Configuration UI**

* Admin interface to configure the external target URL per environment.


## :x: Out of Scope

* The list of things we don't do because of:

    * Technical limitation
    * Too much complexity
    * Not requested by the customer


## :boxing_glove: Technical Challenges

* List all the possible roadblocks that prevent a smooth integration.

## :construction: Dependencies

* Any **infrastructure or product limitation/requirement** that must be fulfilled to achieve the scope and requirements. Add the Jira ticket when possible.

## :bulb: Workarounds

* List any workarounds that we need to build this solution (if any)

## :star: Proposed solution

Describe the implementation of the solution and  highlight number of workflows, custom work or any other highlight needed to implement the goals/requirements.

**Available webhooks and the identifiers:**

**Available API calls to perform:**

**Custom fields needed:**

## :busts_in_silhouette: Checkpoints

- [ ] Initial call / request raised by the customer.
- [ ] First time integration? Gather the requirements and fill them in the **Scope & Requirements** section of this document.
- [ ] Existing integration ? Explain to the customer how this integration works.
- [ ] Check with commercial when is the expected timeline to deliver the quote
- [ ] Create the integration in the Discovery Chainels project.


- [ ] Engage with 3rd party provider. Send an email and/or propose a meeting to discuss the integration.
- [ ] Access to the 3rd party tool or documentation has been provided.
- [ ] API/Documentation reference


- [ ] Access to the 3rd party API (if applicable) or data has been provided.
- [ ] API/Credentials in 1Password


- [ ] Is there a possibility of having webhooks ?
- [ ] Are webhooks set ?


- [ ] Check if the steps to become a certified partner:
- [ ] Integration should be certified before launching. Check this box once is certified.
- [ ] Are there any costs ?
- [ ] NDA needed ? Check this box once is it signed and sent to the provider.




- [ ] Review API documentation or data
- [ ] Check if all the relevant endpoints for the integration exist. Find possible missing endpoints.
- [ ] Do we have unique identifiers ?
- [ ] Do we have all the necessary data ?




- [ ] Check the data structure format. Find possible roadblocks and list them below.
- [ ] Document findings
- [ ] Are the findings a blocker ?
- [ ] Communicate the blocker with the team and Aron. Proceed with any of the actions below depending of the situation:
- [ ] 3rd party software: Engage with the 3rd party software provider
- [ ] Infrastructure: Engage with DevSecOps → Caslay
- [ ] Chainels Platform: Engage with Product → Aron/Berk




- [ ] Document the results as needed (challenges, out of scope, workarounds, dependencies)


- [ ] Write down the proposed solution.
- [ ] Update the integration in Discovery Chainels.
- [ ] Quotation
- [ ] Quotation not needed or is part of the deal
- [ ] Share and review quote with account manager.


- [ ] Have a final meeting with the customer
- [ ] Present the proposed solution and exchange feedback.
- [ ] If there is feedback that is needed to be implemented in the solution, document it as part of the solution.
- [ ] Are these major changes? → Re-engage with Aron to re-quote.




- [ ] If the customer agrees with the proposed solution
- [ ] Move the integration to the backlog in Discovery Chainels → This will create a task in the Solutions project automatically.



## :moneybag: Pricing

|  | **One Time Fee** | **License fee (per month)** |
| --- | --- | --- |
| 1st Community |  |  |
| Next communities |  |  |

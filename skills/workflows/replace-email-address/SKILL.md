---
name: replace-email-address
description: Replace an email channel with a new email address. Looks up the current email channel, then replaces it with a new address while preserving user association. Use when updating a user's email address.
---

# Replace Email Address Workflow

This workflow updates a user's email address by replacing the existing email channel with a new one. The workflow looks up the current email channel, then calls the replace endpoint to create a new channel with the new address while preserving user association.

## Prerequisites

- Airship account with API access
- Current email address (must be registered as a channel)
- New email address to replace it with

## Skills Required

- [Email Lookup](../../../skills/api/email-lookup/SKILL.md) - Get channel_id from current email address
- [Email Replace](../../../skills/api/email-replace/SKILL.md) - Replace email channel with new address

## Step 1: Lookup Current Email Channel

Lookup the channel_id of the current email address:

```json
GET /api/channels/email/old-email%40example.com
Authorization: Bearer <token>
Accept: application/vnd.urbanairship+json; version=3
```

**Response**:
```json
{
  "ok": true,
  "channel": {
    "channel_id": "251d3318-b3cb-4e9f-876a-ea3bfa6e47bd",
    "device_type": "email",
    "installed": true,
    "email_address": "old-email@example.com",
    "named_user_id": "user_12345",
    "commercial_opted_in": "2024-01-15T10:30:00Z",
    "timezone": "America/Los_Angeles",
    "locale_country": "US",
    "locale_language": "en"
  }
}
```

**Note**: Extract the `channel_id` from the response. Also note the `named_user_id`, `commercial_opted_in`, `timezone`, `locale_country`, and `locale_language` values if you want to preserve them in the new channel.

**Error Handling**: If the email address is not found (404), you cannot replace it. The user must register the email address first.

## Step 2: Replace Email Channel

Use the `channel_id` from Step 1 to replace the email channel with the new address:

```json
POST /api/channels/email/replace/251d3318-b3cb-4e9f-876a-ea3bfa6e47bd
Authorization: Bearer <token>
Content-Type: application/json

{
  "channel": {
    "type": "email",
    "address": "new-email@example.com",
    "commercial_opted_in": "2024-01-15T10:30:00Z",
    "timezone": "America/Los_Angeles",
    "locale_country": "US",
    "locale_language": "en"
  }
}
```

**Response**:
```json
{
  "ok": true,
  "channel_id": "a7808f6b-5cd8-458b-88d0-96eceEXAMPLE"
}
```

**Important Notes**:
- A **new channel** is created with a new `channel_id`
- The new channel is automatically associated with the same user (`named_user_id`) as the source channel
- The **source channel is uninstalled** (the old email address is no longer active)
- Use the new `channel_id` from the response for future operations

## Outcomes

- New email channel created with new email address
- New channel automatically associated with same user as original channel
- Original channel uninstalled (old email address no longer receives messages)
- New `channel_id` returned for future operations

## Use Cases

- User updates email address in account settings
- Email address correction (fixing typos or incorrect addresses)
- Account migration to new email addresses
- Maintaining user association when email addresses change

## Related Workflows

- [Register and Associate Email](../register-associate-email/SKILL.md) - Register a new email address
- [Complete User Onboarding](../complete-user-onboarding/SKILL.md) - Full onboarding workflow including email registration

## Best Practices

1. **Preserve opt-in dates**: Include `commercial_opted_in` and `transactional_opted_in` dates from Step 1 to maintain subscription status
2. **Preserve timezone and locale**: Include `timezone`, `locale_country`, and `locale_language` from Step 1 for consistency
3. **Handle 404 errors**: If the current email is not found, guide the user to register it first
4. **Update your records**: Store the new `channel_id` returned in Step 2 for future operations
5. **Verify user association**: The new channel inherits user association automatically, but verify that the source channel was associated with a named user

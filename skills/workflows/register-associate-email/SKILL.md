---
name: register-associate-email
description: Register an email address as a channel and associate it with a named user. The registration endpoint handles both new and existing channels automatically. Use when onboarding users, integrating with CRM systems, or bulk importing users.
---

# Register and Associate Email Workflow

This workflow registers an email address and associates it with a named user.

## Prerequisites

- Airship account with API access
- Email address to register
- Named user ID

## Skills Required

- [Email Registration](../../../skills/api/email-registration/SKILL.md)
- [Named Users](../../../skills/api/named-users/SKILL.md)

## Authentication Note

Before making API calls, obtain an OAuth token via the client credentials grant. The client ID and secret **must be URL-encoded** before base64-encoding them into the Basic auth header (per RFC 6749 `client_secret_basic`). Skipping URL-encoding will cause authentication failures if either value contains special characters.

```
POST https://oauth2.asnapius.com/token  (EU: oauth2.asnapieu.com)
Authorization: Basic base64(url_encode(client_id) + ":" + url_encode(client_secret))
Content-Type: application/x-www-form-urlencoded
Accept: application/json

grant_type=client_credentials&sub=app:<app_key>&scope=chn%20nu
```

## Step 1: Register Email

Register the email address. The registration endpoint will create a new channel if it doesn't exist, or update and return the existing channel if it does:

```json
POST /api/channels/email
Authorization: Bearer <oauth_token>
Content-Type: application/json

{
  "channel": {
    "type": "email",
    "address": "name@example.com",
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
  "channel_id": "251d3318-b3cb-4e9f-876a-ea3bfa6e47bd"
}
```

## Step 2: Associate with Named User

For email channels, associate using the `email_address` field — **not** `channel_id`. The `channel_type` field does not exist on this endpoint and will cause a 400 error.

```json
POST /api/named_users/associate
Authorization: Bearer <oauth_token>
Content-Type: application/json

{
  "named_user_id": "user_12345",
  "email_address": "name@example.com"
}
```

**Response**:
```json
{
  "ok": true
}
```

## Outcomes

- Email channel registered or updated
- Email channel associated with named user
- channel_id available for future operations

## Use Cases

- User onboarding from website forms
- CRM integration
- Bulk user import
- Email channel registration

## Related Workflows

- [Register and Associate SMS](../register-associate-sms/SKILL.md)
- [Complete User Onboarding](../complete-user-onboarding/SKILL.md)

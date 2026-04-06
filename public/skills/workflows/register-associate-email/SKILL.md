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

## Step 1: Register Email

Register the email address. The registration endpoint will create a new channel if it doesn't exist, or update and return the existing channel if it does:

```json
POST /api/channels/email
Authorization: Bearer <token>
Content-Type: application/json

{
  "channel": {
    "type": "email",
    "address": "name@example.com",
    "commercial_opted_in": "2024-01-15T10:30:00",
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

Use the `channel_id` from Step 1 or Step 2 to associate with a named user:

```json
POST /api/named_users/associate
Authorization: Bearer <token>
Content-Type: application/json

{
  "named_user_id": "user_12345",
  "channel_id": "251d3318-b3cb-4e9f-876a-ea3bfa6e47bd",
  "channel_type": "email"
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

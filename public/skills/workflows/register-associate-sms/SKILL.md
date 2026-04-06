---
name: register-associate-sms
description: Register an SMS phone number as a channel and associate it with a named user. The registration endpoint handles both new and existing channels automatically. Use when onboarding users, integrating with CRM systems, or bulk importing users.
---

# Register and Associate SMS Workflow

This workflow registers an SMS phone number and associates it with a named user.

## Prerequisites

- Airship account with API access
- SMS phone number (MSISDN)
- Sender code
- Named user ID

## Skills Required

- [SMS Registration](../../../skills/api/sms-registration/SKILL.md)
- [Named Users](../../../skills/api/named-users/SKILL.md)

## Step 1: Lookup SMS Channel

Check if the SMS number is already registered:

```json
GET /api/channels/sms/15035556789/12345
Authorization: Bearer <token>
```

**Response (if exists)**:
```json
{
  "ok": true,
  "channel": {
    "channel_id": "existing-channel-id",
    "msisdn": "15035556789",
    "sender": "12345",
    "opt_in": true
  }
}
```

**Response (if not exists)**:
```json
{
  "ok": false,
  "error": "A channel_id does not exist for the msisdn and sender."
}
```

## Step 2: Register SMS (if needed)

If lookup returns 404, register the SMS number:

```json
POST /api/channels/sms
Authorization: Bearer <token>
Content-Type: application/json

{
  "msisdn": "15035556789",
  "sender": "12345",
  "opted_in": "2024-01-15T10:30:00",
  "timezone": "America/Los_Angeles",
  "locale_country": "US",
  "locale_language": "en"
}
```

**Response**:
```json
{
  "ok": true,
  "channel_id": "df6a6b50-9843-0304-d5a5-743f246a4946",
  "opt_in": true
}
```

## Step 3: Associate with Named User

Use the `channel_id` from Step 1 or Step 2 to associate with a named user:

```json
POST /api/named_users/associate
Authorization: Bearer <token>
Content-Type: application/json

{
  "named_user_id": "user_12345",
  "channel_id": "df6a6b50-9843-0304-d5a5-743f246a4946",
  "channel_type": "sms",
  "msisdn": "15035556789",
  "sender": "12345"
}
```

**Response**:
```json
{
  "ok": true
}
```

## Outcomes

- SMS channel registered or updated
- SMS channel associated with named user
- channel_id available for future operations

## Use Cases

- User onboarding from website forms
- SMS channel registration
- Bulk user import
- CRM integration

## Related Workflows

- [Register and Associate Email](../register-associate-email/SKILL.md)
- [Complete User Onboarding](../complete-user-onboarding/SKILL.md)

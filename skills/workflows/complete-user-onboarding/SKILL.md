---
name: complete-user-onboarding
description: Complete user onboarding workflow that registers multiple channels (email and SMS), associates them with a named user, tracks completion with a custom event, and sends a welcome notification. Use when onboarding new users, setting up multi-channel user accounts, or automating welcome sequences.
---

# Complete User Onboarding Workflow

This workflow demonstrates registering multiple channels and associating them with a named user.

## Prerequisites

- Airship account with API access
- User email address (required)
- User SMS phone number (optional)
- Sender code (if using SMS)
- Named user ID

## Skills Required

- [Email Registration](../../../skills/api/email-registration/SKILL.md)
- [SMS Registration](../../../skills/api/sms-registration/SKILL.md) (optional)
- [Named Users](../../../skills/api/named-users/SKILL.md)
- [Custom Events](../../../skills/api/custom-events/SKILL.md)
- [Push Notification](../../../skills/api/push-notification/SKILL.md)

## Step 1: Register Email

```json
POST /api/channels/email
Authorization: Bearer <token>
Content-Type: application/json

{
  "channel": {
    "type": "email",
    "address": "user@example.com",
    "commercial_opted_in": "2024-01-15T10:30:00"
  }
}
```

**Get**: `email_channel_id`

## Step 2: Register SMS (if provided)

```json
POST /api/channels/sms
Authorization: Bearer <token>
Content-Type: application/json

{
  "msisdn": "15035556789",
  "sender": "12345",
  "opted_in": "2024-01-15T10:30:00"
}
```

**Get**: `sms_channel_id`

## Step 3: Associate Email with Named User

```json
POST /api/named_users/associate
Authorization: Bearer <token>
Content-Type: application/json

{
  "named_user_id": "user_12345",
  "channel_id": "<email_channel_id>",
  "channel_type": "email"
}
```

## Step 4: Associate SMS with Named User

```json
POST /api/named_users/associate
Authorization: Bearer <token>
Content-Type: application/json

{
  "named_user_id": "user_12345",
  "channel_id": "<sms_channel_id>",
  "channel_type": "sms",
  "msisdn": "15035556789",
  "sender": "12345"
}
```

## Step 5: Submit Custom Event

Track the onboarding completion:

```json
POST /api/custom-events
Authorization: Bearer <token>
Content-Type: application/json

{
  "user": {
    "named_user_id": "user_12345"
  },
  "body": {
    "name": "onboarding_complete",
    "occurred": "2024-01-15T10:35:00",
    "properties": {
      "channels_registered": ["email", "sms"]
    }
  }
}
```

## Step 6: Send Welcome Push

Send a welcome notification to the user:

```json
POST /api/push
Authorization: Bearer <token>
Content-Type: application/json

{
  "audience": {
    "named_user": "user_12345"
  },
  "device_types": ["ios", "android", "web", "email", "sms"],
  "notification": {
    "alert": "Welcome! Your account is set up."
  }
}
```

## Outcomes

- Email channel registered and associated
- SMS channel registered and associated (if provided)
- Onboarding completion tracked
- Welcome notification sent

## Use Cases

- New user registration
- Account setup completion
- Multi-channel user onboarding
- Welcome message automation

## Related Workflows

- [Register and Associate Email](../register-associate-email/SKILL.md)
- [Register and Associate SMS](../register-associate-sms/SKILL.md)

## Best Practices

1. **Registration handles existing channels automatically**: The registration endpoint handles both new and existing channels, so no lookup step is needed
2. **Handle errors gracefully**: Implement retry logic and error handling for network issues
3. **Handle partial failures**: Consider rollback or resume strategies if steps fail mid-workflow
4. **Validate inputs**: Ensure email addresses and phone numbers are valid before registration

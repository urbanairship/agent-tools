---
name: named-users
metadata:
  category: api
description: Associate channels (devices) with named users to create unified user profiles across multiple devices and channels. Use when linking devices to user accounts or coordinating messages across channels.
---

# Skill: Associate Named User

## Overview

This skill enables agents to associate channels (devices) with named users, creating unified user profiles across multiple devices and channels. Named users allow you to coordinate messages across channels and gather data at the user level rather than the channel level.

## API Endpoint

**Primary Endpoint**: `POST /api/named_users/associate`  
**Base URL**:
- US: `https://go.urbanairship.com`
- EU: `https://go.airship.eu`
- US (OAuth): `https://api.asnapius.com`
- EU (OAuth): `https://api.asnapieu.com`

**Path**: `/api/named_users/associate`

### Additional Endpoint

**Disassociate Endpoint**: `POST /api/named_users/disassociate`  
**Path**: `/api/named_users/disassociate`

## Authentication

| Method | Endpoint | Scope |
|---|---|---|
| OAuth (recommended) | `api.asnapius.com` | `nu` |
| Bearer token | `go.urbanairship.com` | — |
| Basic | `go.urbanairship.com` | — |

See [Authentication Guide](../../AUTHENTICATION.md) for token request details and MCP setup.

## Request Headers

**OAuth** (`api.asnapius.com`):
```
Authorization: Bearer <oauth_token>
Content-Type: application/json
Accept: application/vnd.urbanairship+json; version=3
```

**Bearer token** (`go.urbanairship.com`):
```
Authorization: Bearer <dashboard_token>
Content-Type: application/json
Accept: application/vnd.urbanairship+json; version=3
```

**Basic** (`go.urbanairship.com`):
```
Authorization: Basic <base64(app_key:master_secret)>
Content-Type: application/json
Accept: application/vnd.urbanairship+json; version=3
```

## Association Request Schema

The request body can use one of two formats:

### Format 1: Channel ID Association

```json
{
  "channel_id": "uuid",
  "device_type": "ios",  // Required for iOS, Android, Amazon, SMS
  "named_user_id": "user-123"
}
```

**Device Types**:
- `ios` - iOS device
- `android` - Android device
- `amazon` - Fire OS device
- `web` - Web channel (device_type optional)
- `sms` - SMS channel
- `email` - Use email_address format instead
- `open` - Open channel

### Format 2: Email Address Association

```json
{
  "email_address": "user@example.com",
  "named_user_id": "user-123"
}
```

## Disassociation Request Schema

### Channel ID Disassociation

```json
{
  "channel_id": "uuid",
  "device_type": "ios",  // Optional but recommended
  "named_user_id": "user-123"  // Optional
}
```

### Email Address Disassociation

```json
{
  "email_address": "user@example.com",
  "named_user_id": "user-123"  // Optional
}
```

## Response Schema

**Success (200 OK):**
```json
{
  "ok": true
}
```

**Note**: The request is accepted but not guaranteed to be successfully processed. If a named user has more than 1,000 channels associated, the request will be ignored.

**Error (400 Bad Request):**
```json
{
  "ok": false,
  "error": "Error message",
  "error_code": 40001
}
```

## Important Constraints

1. **Channel Limit**: Maximum 100 channels per named user
2. **Automatic Creation**: Named users are automatically created when first associated
3. **Reassociation**: Associating a channel with a new named user removes it from the previous named user
4. **Tag Inheritance**: Tags set on named users apply to all associated channels
5. **Channel Uniqueness**: A channel can only be associated with one named user at a time

## Examples

### Example 1: Associate iOS Channel

```json
{
  "channel_id": "df6a6b50-9843-0304-d5a5-743f246a4946",
  "device_type": "ios",
  "named_user_id": "user-id-1234"
}
```

### Example 2: Associate Web Channel

```json
{
  "channel_id": "wf6a6b50-9843-0304-d5a5-743f246a4946",
  "named_user_id": "user-id-1234"
}
```

**Note**: `device_type` is optional for web channels.

### Example 3: Associate Email Address

```json
{
  "email_address": "monopoly.man@example.com",
  "named_user_id": "user-id-1234"
}
```

### Example 4: Associate Android Channel

```json
{
  "channel_id": "8bb5df16-bcca-4a55-ba71-8417525732f5",
  "device_type": "android",
  "named_user_id": "user-id-1234"
}
```

### Example 5: Associate SMS Channel

```json
{
  "channel_id": "sms-channel-uuid",
  "device_type": "sms",
  "named_user_id": "user-id-1234"
}
```

### Example 6: Disassociate Channel

```json
{
  "channel_id": "df6a6b50-9843-0304-d5a5-743f246a4946",
  "device_type": "ios",
  "named_user_id": "user-id-1234"
}
```

### Example 7: Disassociate Email

```json
{
  "email_address": "user@example.com",
  "named_user_id": "user-id-1234"
}
```

## Best Practices

1. **Associate on Login**: Associate channels when users log in or register
2. **Disassociate on Logout**: Disassociate channels when users log out or uninstall
3. **Use Consistent IDs**: Use the same named_user_id across your systems (e.g., CRM)
4. **Monitor Limits**: Track channel counts to avoid hitting the 100-channel limit
5. **Handle Reassociation**: Be aware that reassociating removes previous associations
6. **Set Tags on Named Users**: Apply tags at the named user level, not channel level
7. **Automatic Disassociation**: Set up automatic disassociation to prevent limit issues

## Common Error Codes

- **400**: Bad Request - Invalid channel ID, missing required fields, or validation failure
- **401**: Unauthorized - Invalid or missing authentication
- **403**: Forbidden - Client-side association disabled (requires server-side only)
- **406**: Not Acceptable - Missing or invalid API version header

## Channel Type Requirements

| Channel Type | device_type Required | Notes |
|-------------|---------------------|-------|
| iOS | Yes | Must specify `ios` |
| Android | Yes | Must specify `android` |
| Amazon/Fire OS | Yes | Must specify `amazon` |
| Web | No | Optional, Airship determines type |
| SMS | Yes | Must specify `sms` |
| Email | N/A | Use `email_address` field instead |
| Open | Yes | Must specify `open` |

## Use Cases

- **Multi-Device Users**: Associate multiple devices (phone, tablet, web) with one user
- **Cross-Channel Messaging**: Coordinate messages across email, SMS, and push
- **User Profile Unification**: Create unified user profiles across channels
- **CRM Integration**: Match Airship users with CRM customer IDs
- **Lifecycle Management**: Track user lifecycle across devices

## Workflows Using This Skill

- **Register and Associate Email**: Register email → Associate with named user
  - See [Workflow Guide](../../docs/workflows.md#register-associate-email)
- **Register and Associate SMS**: Register SMS → Associate with named user
  - See [Workflow Guide](../../docs/workflows.md#register-associate-sms)
- **Complete User Onboarding**: Register email → Register SMS → Associate both → Send welcome
  - See [Workflow Guide](../../docs/workflows.md#complete-user-onboarding)

## Related Operations

- **Lookup Named User**: `GET /api/named_users?id={named_user_id}`
- **Update Named User**: `POST /api/named_users/{named_user_id}` (batch operations)
- **Uninstall Named User**: `POST /api/named_users/uninstall` (delete all channels)

## Related Documentation

- [Named Users Guide](https://docs.airship.com/guides/audience/named-users/)
- [Named Users API Reference](https://docs.airship.com/developer/rest-api/ua/operations/named-users/)
- [OpenAPI Specification](https://docs.airship.com/developer/rest-api/)

## Function Calling Schema (OpenAI Format)

```json
{
  "name": "associate_named_user",
  "description": "Associate a channel or email address with a named user to create unified user profiles",
  "parameters": {
    "type": "object",
    "properties": {
      "operation": {
        "type": "string",
        "enum": ["associate", "disassociate"],
        "description": "Whether to associate or disassociate"
      },
      "named_user_id": {
        "type": "string",
        "description": "Named user identifier (1-128 characters, no leading/trailing whitespace)"
      },
      "channel_id": {
        "type": "string",
        "format": "uuid",
        "description": "Channel ID (required for channel association)"
      },
      "device_type": {
        "type": "string",
        "enum": ["ios", "android", "amazon", "web", "sms", "open"],
        "description": "Device type (required for iOS, Android, Amazon, SMS, Open; optional for Web)"
      },
      "email_address": {
        "type": "string",
        "format": "email",
        "description": "Email address (required for email association)"
      }
    },
    "required": ["operation", "named_user_id"]
  }
}
```

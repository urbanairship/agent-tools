---
name: email-replace
metadata:
  category: api
description: Replace an email channel with a new email address. Creates a new channel, associates it with the same user, and uninstalls the source channel. Use when updating a user's email address.
---

# Skill: Replace Email Channel

## Overview

This skill enables agents to replace an email channel with a new email address. When called, it creates a new email channel with the new address, associates the new channel with the same user as the source channel, and uninstalls the original channel. Use this when a user needs to update their email address.

## API Endpoint

**Method**: `POST`  
**Path**: `/api/channels/email/replace/{channel_id}`  
**Base URL**:
- US: `https://go.urbanairship.com`
- EU: `https://go.airship.eu`
- US (OAuth): `https://api.asnapius.com`
- EU (OAuth): `https://api.asnapieu.com`

**Path**: `/api/channels/email/replace/{channel_id}`

## Authentication

- **OAuth Token**: `Authorization: Bearer <oauth_token>` with scope `chn` — obtain via OAuth client credentials (POST `grant_type=client_credentials&sub=app:<app_key>`) or dashboard-generated token
- **Basic Auth** (avoid in production): `Authorization: Basic <base64(app_key:master_secret)>` — master secret grants full account access

> **MCP server**: set `AIRSHIP_BEARER_TOKEN` (Bearer) or `AIRSHIP_APP_KEY` + `AIRSHIP_MASTER_SECRET` (Basic Auth). `AIRSHIP_REGION` defaults to `us`. See [setup guide](../../../README.md).

## Request Headers

```
Accept: application/vnd.urbanairship+json; version=3
Content-Type: application/json
Authorization: Basic <credentials> (or Bearer token)
```

## Path Parameters

- `channel_id`: The UUID of the email channel to replace (string, required)

## Request Schema

### Email Channel Object

```json
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

### Required Fields

- `channel.type`: Must be `"email"`
- `channel.address`: The new email address (string)

### Optional Fields

**Opt-in Status** (date-time format):
- `channel.commercial_opted_in`: Date-time when user opted in to commercial emails
- `channel.commercial_opted_out`: Date-time when user opted out of commercial emails
- `channel.transactional_opted_in`: Date-time when user opted in to transactional emails
- `channel.transactional_opted_out`: Date-time when user opted out of transactional emails
- `channel.click_tracking_opted_in`: Date-time when user opted in to click tracking
- `channel.click_tracking_opted_out`: Date-time when user opted out of click tracking
- `channel.open_tracking_opted_in`: Date-time when user opted in to open tracking
- `channel.open_tracking_opted_out`: Date-time when user opted out of open tracking

**Date Format Requirements**:
- **Format**: ISO 8601 UTC datetime string
- **Required**: Must include UTC timezone indicator (`Z` suffix or `+00:00`)
- **No microseconds**: Microseconds are not accepted

**Channel Properties**:
- `channel.timezone`: IANA timezone identifier (e.g., `"America/Los_Angeles"`)
- `channel.locale_country`: ISO 3166 two-character country code (e.g., `"US"`)
- `channel.locale_language`: ISO 639-1 two-character language code (e.g., `"en"`)

**Note**: You cannot provide both opt-in and opt-out values for the same email type in a single request.

## Examples

See example files in the `examples/` directory:
- `replace-email-address.json` - Replace email channel with new address

### Example: Replace Email Channel

```json
POST /api/channels/email/replace/251d3318-b3cb-4e9f-876a-ea3bfa6e47bd
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

## Response Schema

### Success Response (201 Created)

```json
{
  "ok": true,
  "channel_id": "a7808f6b-5cd8-458b-88d0-96eceEXAMPLE"
}
```

**Response Headers**:
- `Location`: URI of the newly created email channel

**Important Notes**:
- A **new channel** is created with a new `channel_id`
- The new channel is automatically associated with the same user (named_user_id) as the source channel
- The **source channel is uninstalled** (not deleted)
- Properties from the source channel (tags, attributes, opt-in dates) are **NOT inherited** - only user association is preserved

## Error Handling

### 400 Bad Request

Occurs when:
- Invalid email address format
- Both opt-in and opt-out dates provided for the same email type
- Invalid date-time format
- Invalid timezone or locale values
- Missing required fields

### 401 Unauthorized

Invalid or missing authentication credentials.

### 404 Not Found

The specified `channel_id` does not exist or is not an email channel.

## Best Practices

1. **Lookup channel_id first**: Use the email-lookup skill to get the channel_id before replacing
2. **Preserve opt-in dates**: When replacing, include opt-in dates from the original channel if you want to preserve subscription status
3. **Preserve timezone/locale**: Include timezone and locale from the original channel for consistency
4. **Associate with named users**: The new channel inherits user association automatically, but ensure the source channel was associated with a named user
5. **Note the new channel_id**: The response returns a new channel_id - use this for future operations

## Use Cases

1. **Update user email address**: When a user changes their email address in your system
2. **Email address correction**: Fix incorrect email addresses that were registered
3. **Account migration**: Move email channels to new addresses while preserving user association

## Workflows Using This Skill

- **Replace Email Address**: Lookup current email → Replace with new email address
  - See [Workflow Guide](../../docs/workflows.md#replace-email-address)

## Related Skills

- [Lookup Email Channel](../email-lookup/) - Get channel_id from email address before replacing
- [Register Email Channel](../email-registration/) - Register a new email channel (use replace when updating existing address)

## Additional Resources

- [Email API Reference](https://docs.airship.com/developer/rest-api/ua/operations/email/#replaceemailchannel)
- [Email Integration Guide](https://docs.airship.com/developer/api-integrations/email/getting-started/)
- [OpenAPI Specification](https://docs.airship.com/developer/rest-api/)

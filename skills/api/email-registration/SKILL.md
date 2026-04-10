---
name: email-registration
description: Register email addresses as channels in Airship. Use when onboarding users, importing email lists, or creating email channels for messaging. Returns a channel_id for use in workflows.
metadata:
  category: api
---

# Skill: Register Email Channel

## Overview

This skill enables agents to register email addresses as channels in Airship. Registration creates a new email channel or updates an existing one, and returns a `channel_id` that can be used in workflows like associating the channel with a named user.

## API Endpoint

**Method**: `POST`  
**Path**: `/api/channels/email`  
**Base URL**:
- US: `https://go.urbanairship.com`
- EU: `https://go.airship.eu`
- US (OAuth): `https://api.asnapius.com`
- EU (OAuth): `https://api.asnapieu.com`

**Path**: `/api/channels/email`

## Authentication

| Method | Endpoint | Scope |
|---|---|---|
| OAuth (recommended) | `api.asnapius.com` | `chn` |
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

## Request Schema

### Email Channel Object

```json
{
  "channel": {
    "type": "email",
    "address": "user@example.com",
    "commercial_opted_in": "2020-10-28T10:34:22",
    "transactional_opted_in": "2020-10-28T10:34:22",
    "timezone": "America/Los_Angeles",
    "locale_country": "US",
    "locale_language": "en"
  },
  "opt_in_mode": "classic",
  "properties": {
    "interests": "newsletter"
  },
  "attributes": {
    "first_name": "John",
    "last_name": "Doe"
  },
  "tag_operations": {
    "add": {
      "tag_group_1": ["tag1", "tag2"]
    }
  }
}
```

### Required Fields

- `channel.type`: Must be `"email"`
- `channel.address`: The email address being registered (string)

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
- **No microseconds**: Microseconds are not accepted (format must be `YYYY-MM-DDTHH:mm:ssZ` or `YYYY-MM-DDTHH:mm:ss+00:00`)
- **Examples**:
  - `"2024-01-15T10:30:00Z"` ✅
  - `"2024-01-15T10:30:00+00:00"` ✅
  - `"2024-01-15T10:30:00"` ❌ (missing UTC indicator)
  - `"2024-01-15T10:30:00.123456Z"` ❌ (microseconds not accepted)

**Note**: You cannot provide both opt-in and opt-out values for the same email type in a single request.

**Channel Properties**:
- `channel.timezone`: IANA timezone identifier (e.g., `"America/Los_Angeles"`)
- `channel.locale_country`: ISO 3166 two-character country code (e.g., `"US"`)
- `channel.locale_language`: ISO 639-1 two-character language code (e.g., `"en"`)

**Registration Options**:
- `opt_in_mode`: `"classic"` (default) or `"double"` (creates a `double_opt_in` event)
- `properties`: Object containing event properties (max 255 characters per value)
- `attributes`: Object containing customer-provided attributes
- `tag_operations`: Tag group operations (add, remove, set)

## Examples

See example files in the `examples/` directory:
- `register-email.json` - Basic email registration
- `register-with-opt-in.json` - Registration with opt-in dates

### Example 1: Basic Email Registration

```json
POST /api/channels/email
{
  "channel": {
    "type": "email",
    "address": "user@example.com"
  }
}
```

### Example 2: Registration with Opt-in Dates

```json
POST /api/channels/email
{
  "channel": {
    "type": "email",
    "address": "user@example.com",
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
  "channel_id": "251d3318-b3cb-4e9f-876a-ea3bfa6e47bd",
  "attributes": {"ok": true},
  "tags": {"ok": true}
}
```

**Response Headers**:
- `Location`: URI of the newly created email channel

### Update Response (200 OK)

If an email channel already exists with the provided address, the existing channel is updated:

```json
{
  "ok": true,
  "channel_id": "251d3318-b3cb-4e9f-876a-ea3bfa6e47bd",
  "attributes": {"ok": true},
  "tags": {"ok": true}
}
```

## Opt-in Handling

### Single Opt-in

When you provide `commercial_opted_in` or `transactional_opted_in` dates, the user is immediately opted in to receive emails of that type. This is appropriate when you have explicit written consent from the user.

### Double Opt-in Flow

When you register an email address **without** providing `commercial_opted_in` or `transactional_opted_in` dates:

1. The channel is created but cannot receive commercial emails until opt-in is completed
2. If `opt_in_mode: "double"` is specified, a `double_opt_in` event is created
3. You can trigger automations or sequences based on this event
4. The user must complete the opt-in process (typically via email confirmation link) before receiving commercial emails

**Note**: Transactional emails do not require opt-in, but users can opt out of transactional emails.

## Best Practices

1. **Always provide opt-in dates when you have explicit consent** - This ensures users can receive messages immediately
2. **Use double opt-in for compliance** - When users provide email addresses through forms but haven't explicitly consented, use `opt_in_mode: "double"`
3. **Set timezone and locale** - Helps with delivery scheduling and localization
4. **Associate with named users** - After registration, use the returned `channel_id` to associate the email channel with a named user
5. **Handle existing channels** - The endpoint updates existing channels by email address, so you can safely call it multiple times

## Error Handling

### 400 Bad Request

Occurs when:
- Invalid email address format
- Both opt-in and opt-out dates provided for the same email type
- Invalid date-time format
- Invalid timezone or locale values

### 401 Unauthorized

Invalid or missing authentication credentials.

## Use Cases

1. **Register email from form submission**: Register email addresses collected from website forms
2. **Bulk registration**: Register multiple email addresses from your CRM or database
3. **Update opt-in status**: Update existing email channels with new opt-in dates
4. **Register and associate**: Register email → Get `channel_id` → Associate with named user

## Workflows Using This Skill

- **Register and Associate Email**: Register email → Associate with named user
  - See [Workflow Guide](../../docs/workflows.md#register-associate-email)
- **Complete User Onboarding**: Register email → Register SMS → Associate both → Send welcome
  - See [Workflow Guide](../../docs/workflows.md#complete-user-onboarding)

## Related Skills

- [Lookup Email Channel](../email-lookup/) - Check if an email is already registered
- [Replace Email Channel](../email-replace/) - Replace an email channel with a new address (use when updating email address)
- [Associate Named User](../named-users/) - Associate the registered email channel with a named user

## Additional Resources

- [Email API Reference](https://docs.airship.com/developer/rest-api/ua/operations/email/#registeremailchannel)
- [Email Integration Guide](https://docs.airship.com/developer/api-integrations/email/getting-started/)
- [OpenAPI Specification](https://docs.airship.com/developer/rest-api/)

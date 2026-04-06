---
name: sms-registration
metadata:
  category: api
description: Register SMS phone numbers as channels in Airship. Use when onboarding users, importing phone lists, or creating SMS channels for messaging. Returns a channel_id for use in workflows.
---

# Skill: Register SMS Channel

## Overview

This skill enables agents to register SMS phone numbers as channels in Airship. Registration creates a new SMS channel or updates an existing one, and returns a `channel_id` that can be used in workflows like associating the channel with a named user.

## API Endpoint

**Method**: `POST`  
**Path**: `/api/channels/sms`  
**Base URL**: `https://go.urbanairship.com`  
**Full URL**: `https://go.urbanairship.com/api/channels/sms`

## Authentication

Supports multiple authentication methods:
- **Basic Auth**: `Authorization: Basic <base64(app_key:master_secret)>`
- **Bearer Token**: `Authorization: Bearer <token>`
- **OAuth2**: `Authorization: Bearer <oauth_token>` with scope `chn`

## Request Headers

```
Accept: application/vnd.urbanairship+json; version=3
Content-Type: application/json
Authorization: Basic <credentials> (or Bearer token)
```

## Request Schema

### SMS Channel Object

```json
{
  "msisdn": "15035556789",
  "sender": "12345",
  "opted_in": "2020-02-13T11:58:59",
  "timezone": "America/Los_Angeles",
  "locale_country": "US",
  "locale_language": "en",
  "attributes": {
    "first_name": "Jane",
    "last_name": "Smith"
  },
  "tag_operations": {
    "add": {
      "tag_group_1": ["tag1", "tag2"]
    }
  }
}
```

### Required Fields

- `msisdn`: The mobile phone number (string, numeric characters only, max 15 digits, no leading zeros)
- `sender`: A long or short code the app is configured to send from (integer or string)

### Optional Fields

**Opt-in Status**:
- `opted_in`: Date-time when explicit permission was received from the user to receive messages

**Date Format Requirements**:
- **Format**: ISO 8601 UTC datetime string
- **Required**: Must include UTC timezone indicator (`Z` suffix or `+00:00`)
- **No microseconds**: Microseconds are not accepted (format must be `YYYY-MM-DDTHH:mm:ssZ` or `YYYY-MM-DDTHH:mm:ss+00:00`)
- **Examples**:
  - `"2024-01-15T10:30:00Z"` ✅
  - `"2024-01-15T10:30:00+00:00"` ✅
  - `"2024-01-15T10:30:00"` ❌ (missing UTC indicator)
  - `"2024-01-15T10:30:00.123456Z"` ❌ (microseconds not accepted)

**Channel Properties**:
- `timezone`: IANA timezone identifier (e.g., `"America/Los_Angeles"`)
- `locale_country`: ISO 3166 two-character country code (e.g., `"US"`)
- `locale_language`: ISO 639-1 two-character language code (e.g., `"en"`)

**Additional Data**:
- `attributes`: Object containing customer-provided attributes
- `tag_operations`: Tag group operations (add, remove, set)

## Response Schema

### Success Response (201 Created)

When a new channel is created:

```json
{
  "ok": true,
  "channel_id": "df6a6b50-9843-0304-d5a5-743f246a4946",
  "opt_in": true
}
```

**Response Headers**:
- `Location`: URI of the newly created SMS channel

### Update Response (200 OK)

If an SMS channel already exists with the provided `msisdn`/`sender` combination:

```json
{
  "ok": true,
  "channel_id": "df6a6b50-9843-0304-d5a5-743f246a4946",
  "opt_in": true
}
```

### Pending Opt-in Response

When `opted_in` is not provided, the channel is created with `pending` status:

```json
{
  "ok": true,
  "channel_id": "df6a6b50-9843-0304-d5a5-743f246a4946",
  "opt_in": false
}
```

## Opt-in Handling

### Single Opt-in

When you provide an `opted_in` date-time, the user is immediately opted in to receive SMS messages. This is appropriate when you have explicit written consent from the user (e.g., they texted a keyword or completed an opt-in form).

### Double Opt-in Flow

When you register an SMS number **without** providing an `opted_in` value:

1. The channel is created with `opt_in: false` and `pending` status
2. Airship sends an opt-in instruction message to the MSISDN
3. The user must respond with a keyword (typically "Y" or "YES") to complete opt-in
4. You can assign tags and organize `pending` channels before opt-in is completed
5. **You cannot send messages to channels until they complete the opt-in flow**

**Important**: Avoid repeated registration attempts. Repeated registrations of the same MSISDN and sender without an `opted_in` value will result in multiple opt-in instruction messages being sent.

## MSISDN Format Requirements

- Must be numeric characters only (0-9)
- Maximum 15 digits
- Must not contain leading zeros
- Must conform to E.164 international standard
- Examples:
  - Valid: `"15035556789"`, `"15551234567"`
  - Invalid: `"015035556789"` (leading zero), `"1-503-555-6789"` (contains dashes)

## Examples

### Example 1: Basic SMS Registration

```json
POST /api/channels/sms
{
  "msisdn": "15035556789",
  "sender": "12345"
}
```

### Example 2: Registration with Opt-in Date

```json
POST /api/channels/sms
{
  "msisdn": "15035556789",
  "sender": "12345",
  "opted_in": "2024-01-15T10:30:00Z",
  "timezone": "America/Los_Angeles",
  "locale_country": "US",
  "locale_language": "en"
}
```

## Best Practices

1. **Always provide opt-in dates when you have explicit consent** - This ensures users can receive messages immediately
2. **Use double opt-in for compliance** - When users provide phone numbers through forms but haven't explicitly consented via SMS keyword
3. **Set timezone and locale** - Helps with delivery scheduling and localization
4. **Associate with named users** - After registration, use the returned `channel_id` to associate the SMS channel with a named user
5. **Handle existing channels** - The endpoint updates existing channels by `msisdn`/`sender` combination
6. **Avoid repeated registrations** - Don't repeatedly register the same MSISDN/sender without `opted_in` to prevent multiple opt-in messages

## Error Handling

### 400 Bad Request

Occurs when:
- Missing required fields (`msisdn` or `sender`)
- MSISDN does not meet E.164 standard
- MSISDN contains non-numeric characters or leading zeros
- Project is not configured with a valid sender
- Invalid date-time format for `opted_in`
- Invalid timezone or locale values

### 401 Unauthorized

Invalid or missing authentication credentials.

## Use Cases

1. **Register SMS from form submission**: Register phone numbers collected from website forms
2. **Bulk registration**: Register multiple phone numbers from your CRM or database
3. **Update opt-in status**: Update existing SMS channels with new opt-in dates
4. **Register and associate**: Register SMS → Get `channel_id` → Associate with named user
5. **Keyword opt-in**: Register users who texted a keyword (with `opted_in` date)

## Workflows Using This Skill

- **Register and Associate SMS**: Register SMS → Associate with named user
  - See [Workflow Guide](../../docs/workflows.md#register-associate-sms)
- **Complete User Onboarding**: Register email → Register SMS → Associate both → Send welcome
  - See [Workflow Guide](../../docs/workflows.md#complete-user-onboarding)

## Related Skills

- [Lookup SMS Channel](../sms-lookup/) - Check if an SMS number is already registered
- [Associate Named User](../named-users/) - Associate the registered SMS channel with a named user

## Additional Resources

- [SMS API Reference](https://docs.airship.com/developer/rest-api/ua/operations/sms/#registersmschannel)
- [SMS Integration Guide](https://docs.airship.com/developer/api-integrations/sms/getting-started/)
- [OpenAPI Specification](https://docs.airship.com/developer/rest-api/)

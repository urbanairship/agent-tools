---
name: sms-lookup
metadata:
  category: api
description: Lookup an SMS channel by phone number (msisdn) and sender to check if it's registered, retrieve its channel_id, and get channel details. Use before registration or association operations.
---

# Skill: Lookup SMS Channel

## Overview

This skill enables agents to lookup an SMS channel by phone number (`msisdn`) and sender. Use this to check if an SMS number is already registered, retrieve its `channel_id`, and get channel details before performing operations like registration or association.

## API Endpoint

**Method**: `GET`  
**Path**: `/api/channels/sms/{msisdn}/{sender}`  
**Base URL**:
- US: `https://go.urbanairship.com`
- EU: `https://go.airship.eu`
- US (OAuth): `https://api.asnapius.com`
- EU (OAuth): `https://api.asnapieu.com`

**Path**: `/api/channels/sms/{msisdn}/{sender}`

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
Accept: application/vnd.urbanairship+json; version=3
```

**Bearer token** (`go.urbanairship.com`):
```
Authorization: Bearer <dashboard_token>
Accept: application/vnd.urbanairship+json; version=3
```

**Basic** (`go.urbanairship.com`):
```
Authorization: Basic <base64(app_key:master_secret)>
Accept: application/vnd.urbanairship+json; version=3
```

## Path Parameters

- `msisdn`: The mobile phone number (integer or string, numeric characters only, max 15 digits, no leading zeros)
- `sender`: A long or short code the app is configured to send from (integer)

**Note**: Each unique `msisdn`/`sender` combination represents a separate channel.

## Response Schema

### Success Response (200 OK)

```json
{
  "ok": true,
  "channel": {
    "channel_id": "df6a6b50-9843-0304-d5a5-743f246a4946",
    "device_type": "sms",
    "installed": true,
    "created": "2020-02-13T11:58:59",
    "named_user_id": "user_12345",
    "msisdn": "15035556789",
    "sender": "12345",
    "tag_groups": {
      "ua_channel_type": ["sms"],
      "ua_sender_id": ["12345"],
      "ua_opt_in": ["true"],
      "source": ["website_form"]
    },
    "opt_in": true,
    "last_registration": "2020-02-13T11:58:59"
  }
}
```

### Channel Object Properties

- `channel_id`: Unique identifier for the SMS channel (UUID)
- `device_type`: Always `"sms"` for SMS channels
- `installed`: Boolean indicating if the channel is active
- `created`: Date-time when the channel was created
- `named_user_id`: Associated named user ID, if any
- `msisdn`: The mobile phone number
- `sender`: The sender code used for this channel
- `tag_groups`: Object containing tag groups and their tags
  - `ua_channel_type`: Always contains `["sms"]`
  - `ua_sender_id`: Contains the sender ID
  - `ua_opt_in`: Contains `["true"]` if opted in, `["false"]` if pending
- `opt_in`: Boolean indicating if the user has opted in (`true`) or is pending (`false`)
- `last_registration`: Date-time of the last registration update

## Error Handling

### 404 Not Found

Returned when no channel exists for the specified `msisdn`/`sender` combination:

```json
{
  "ok": false,
  "error": "A channel_id does not exist for the msisdn and sender.",
  "error_code": 40401
}
```

### 400 Bad Request

Occurs when:
- Invalid MSISDN format (contains non-numeric characters, leading zeros, or exceeds 15 digits)
- Invalid sender format

### 401 Unauthorized

Invalid or missing authentication credentials.

## MSISDN Format Requirements

- Must be numeric characters only (0-9)
- Maximum 15 digits
- Must not contain leading zeros
- Must conform to E.164 international standard
- Examples:
  - Valid: `15035556789`, `15551234567`
  - Invalid: `015035556789` (leading zero), `"1-503-555-6789"` (contains dashes)

## Use Cases

1. **Check before registration**: Lookup an SMS number to see if it's already registered before attempting registration
2. **Get channel_id for association**: Retrieve the `channel_id` to associate the SMS channel with a named user
3. **Check opt-in status**: Verify if a user has opted in (`opt_in: true`) or is pending (`opt_in: false`)
4. **Retrieve channel details**: Get tags, sender information, and other channel details

## Best Practices

1. **Handle 404 gracefully**: A 404 response means the MSISDN/sender combination is not registered - you can proceed with registration
2. **Use channel_id from response**: After lookup, use the `channel_id` for subsequent operations like association
3. **Check opt-in status**: Verify `opt_in: true` before sending messages to ensure the user has completed opt-in
4. **Include sender in lookup**: Always provide both `msisdn` and `sender` since each combination is a separate channel

## Example Workflow

1. Lookup SMS number with sender → Get `channel_id` if exists
2. If 404, register SMS → Get new `channel_id`
3. Associate `channel_id` with named user

## Workflows Using This Skill

- **Register and Associate SMS**: Lookup is optional - the registration endpoint handles both new and existing channels automatically. Use lookup only if you need to check channel existence without modifying it.
  - See [Workflow Guide](../../docs/workflows.md#register-associate-sms)

## Related Skills

- [Register SMS Channel](../sms-registration/) - Register a new SMS channel
- [Associate Named User](../named-users/) - Associate the SMS channel with a named user

## Additional Resources

- [SMS API Reference](https://docs.airship.com/developer/rest-api/ua/operations/sms/#getsmschannel)
- [OpenAPI Specification](https://docs.airship.com/developer/rest-api/)

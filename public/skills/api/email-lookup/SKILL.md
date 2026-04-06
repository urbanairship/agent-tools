---
name: email-lookup
metadata:
  category: api
description: Lookup an email channel by email address to check if it's registered, retrieve its channel_id, and get channel details. Use before registration or association operations.
---

# Skill: Lookup Email Channel

## Overview

This skill enables agents to lookup an email channel by email address. Use this to check if an email address is already registered, retrieve its `channel_id`, and get channel details before performing operations like registration or association.

## API Endpoint

**Method**: `GET`  
**Path**: `/api/channels/email/{email}`  
**Base URL**: `https://go.urbanairship.com`  
**Full URL**: `https://go.urbanairship.com/api/channels/email/{email}`

**Note**: The `@` character in the email address must be URL-encoded as `%40` in the path.

## Authentication

Supports multiple authentication methods:
- **Basic Auth**: `Authorization: Basic <base64(app_key:master_secret)>`
- **Bearer Token**: `Authorization: Bearer <token>`
- **OAuth2**: `Authorization: Bearer <oauth_token>` with scope `chn`

## Request Headers

```
Accept: application/vnd.urbanairship+json; version=3
Authorization: Basic <credentials> (or Bearer token)
```

## Path Parameters

- `email`: The email address of the channel you want to look up (string)
  - Must be URL-encoded (e.g., `name@example.com` becomes `name%40example.com`)

## Response Schema

### Success Response (200 OK)

```json
{
  "ok": true,
  "channel": {
    "channel_id": "01234567-890a-bcde-f012-3456789abc0",
    "device_type": "email",
    "installed": true,
    "created": "2020-08-08T20:41:06",
    "named_user_id": "some_id_that_maps_to_your_systems",
    "email_address": "name@example.com",
    "tag_groups": {
      "tag_group_1": ["tag1", "tag2"],
      "tag_group_2": ["tag1", "tag2"]
    },
    "address": null,
    "opt_in": true,
    "commercial_opted_in": "2020-10-28T10:34:22",
    "commercial_opted_out": null,
    "transactional_opted_in": "2020-10-28T10:34:22",
    "transactional_opted_out": null,
    "open_tracking_opted_in": "2022-12-11T00:00:00",
    "click_tracking_opted_in": "2022-12-11T00:00:00",
    "last_registration": "2020-05-01T18:00:27"
  }
}
```

### Channel Object Properties

- `channel_id`: Unique identifier for the email channel (UUID)
- `device_type`: Always `"email"` for email channels
- `installed`: Boolean indicating if the channel is active
- `created`: Date-time when the channel was created
- `named_user_id`: Associated named user ID, if any
- `email_address`: The email address (note: `address` field is null for security)
- `tag_groups`: Object containing tag groups and their tags
- `opt_in`: Always `true` for email channels (can be ignored)
- `commercial_opted_in`: Date-time when user opted in to commercial emails
- `commercial_opted_out`: Date-time when user opted out of commercial emails
- `transactional_opted_in`: Date-time when user opted in to transactional emails
- `transactional_opted_out`: Date-time when user opted out of transactional emails
- `open_tracking_opted_in`: Date-time when user opted in to open tracking
- `click_tracking_opted_in`: Date-time when user opted in to click tracking
- `last_registration`: Date-time of the last registration update

## Error Handling

### 404 Not Found

Returned when no channel exists for the specified email address:

```json
{
  "ok": false,
  "error": "No channel found for email address"
}
```

### 401 Unauthorized

Invalid or missing authentication credentials.

## Use Cases

1. **Check before registration**: Lookup an email to see if it's already registered before attempting registration
2. **Get channel_id for association**: Retrieve the `channel_id` to associate the email channel with a named user
3. **Check opt-in status**: Verify if a user has opted in to commercial or transactional emails
4. **Retrieve channel details**: Get tags, attributes, and other channel information

## Best Practices

1. **URL encode the email address**: Always encode `@` as `%40` in the URL path
2. **Handle 404 gracefully**: A 404 response means the email is not registered - you can proceed with registration
3. **Use channel_id from response**: After lookup, use the `channel_id` for subsequent operations like association
4. **Check opt-in status**: Verify `commercial_opted_in` and `transactional_opted_in` dates before sending messages

## Example Workflow

1. Lookup email address → Get `channel_id` if exists
2. If 404, register email → Get new `channel_id`
3. Associate `channel_id` with named user

## Workflows Using This Skill

- **Register and Associate Email**: Lookup is optional - the registration endpoint handles both new and existing channels automatically. Use lookup only if you need to check channel existence without modifying it.
  - See [Workflow Guide](../../docs/workflows.md#register-associate-email)
- **Replace Email Address**: Lookup current email channel to get channel_id before replacing with new address.
  - See [Workflow Guide](../../docs/workflows.md#replace-email-address)

## Related Skills

- [Register Email Channel](../email-registration/) - Register a new email channel
- [Replace Email Channel](../email-replace/) - Replace an email channel with a new address
- [Associate Named User](../named-users/) - Associate the email channel with a named user

## Additional Resources

- [Email API Reference](https://docs.airship.com/developer/rest-api/ua/operations/email/#getemailchannel)
- [OpenAPI Specification](https://docs.airship.com/developer/rest-api/)

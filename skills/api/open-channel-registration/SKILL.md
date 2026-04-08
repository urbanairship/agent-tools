---
name: open-channel-registration
metadata:
  category: api
description: Register or update an Open Channel in Airship. Use when onboarding users to a custom delivery platform (e.g., WhatsApp, Slack, smart device) that is not backed by an Airship SDK. Returns a channel_id for use in push and named user workflows.
---

# Skill: Register Open Channel

## Overview

This skill enables agents to register a delivery address as an Open Channel in Airship. Unlike iOS, Android, or web channels, Open Channels are not backed by an SDK — your server is responsible for registering users and delivering payloads. Registration creates a new channel or updates an existing one, and returns a `channel_id`.

## API Endpoint

**Method**: `POST`
**Path**: `/api/channels/open`
**Base URL**:
- US: `https://go.urbanairship.com`
- EU: `https://go.airship.eu`
- US (OAuth): `https://api.asnapius.com`
- EU (OAuth): `https://api.asnapieu.com`

**Path**: `/api/channels/open`

## Authentication

- **OAuth Token**: `Authorization: Bearer <oauth_token>` with scope `chn` — obtain via OAuth client credentials (POST `grant_type=client_credentials&sub=app:<app_key>`) or dashboard-generated token
- **Basic Auth** (avoid in production): `Authorization: Basic <base64(app_key:master_secret)>` — master secret grants full account access

> **MCP server**: set `AIRSHIP_BEARER_TOKEN` (Bearer) or `AIRSHIP_APP_KEY` + `AIRSHIP_MASTER_SECRET` (Basic Auth). `AIRSHIP_REGION` defaults to `us`. See [setup guide](../../../README.md).

## Request Headers

```
Accept: application/vnd.urbanairship+json; version=3
Content-Type: application/json
Authorization: Basic <credentials>
```

## Request Schema

The request body wraps the channel object under a `"channel"` key.

```json
{
  "channel": {
    "type": "open",
    "opt_in": true,
    "address": "<delivery address>",
    "open": {
      "open_platform_name": "<platform name>",
      "identifiers": {
        "key": "value"
      }
    },
    "tags": ["tag1", "tag2"],
    "timezone": "America/Los_Angeles",
    "locale_country": "US",
    "locale_language": "en"
  }
}
```

### Required Fields

`channel.type`
: Must be `"open"`.

`channel.opt_in`
: Boolean. Whether the user has consented to receive notifications. If `false`, Airship will not deliver payloads to the webhook for this channel.

`channel.address`
: String. The primary delivery address for this channel — e.g., a phone number for WhatsApp, a user ID for Slack, or any unique identifier meaningful to your platform. 128-character maximum.

`channel.open.open_platform_name`
: String. The canonical name of your configured open platform — must match exactly what was entered in the Airship dashboard (e.g., `"whatsapp"`, `"slack"`).

### Optional Fields

`channel.open.identifiers`
: Object. Up to 100 string:string pairs delivered in push payloads but not usable for segmentation. This map is **exhaustive** — it replaces existing identifiers on update rather than merging.

`channel.tags`
: Array of strings. Used for audience segmentation.

`channel.timezone`
: IANA timezone identifier (e.g., `"America/Los_Angeles"`). Sets the `timezone` tag group.

`channel.locale_country`
: ISO 3166 two-letter country code (e.g., `"US"`).

`channel.locale_language`
: ISO 639-1 two-letter language code (e.g., `"en"`).

## Response Schema

### Created (201)

```json
{
  "ok": true,
  "channel_id": "a61448e1-be63-43ee-84eb-19446ba743f0"
}
```

**Response Headers**:
- `Location`: URI of the newly created channel.

### Updated (200)

When a channel already exists for the given `address` + `open_platform_name` combination:

```json
{
  "ok": true,
  "channel_id": "a61448e1-be63-43ee-84eb-19446ba743f0"
}
```

Both create and update return the same shape — callers do not need to check for existence before registering.

## Examples

### Example 1: Basic Registration

```json
POST /api/channels/open
{
  "channel": {
    "type": "open",
    "opt_in": true,
    "address": "+15035556789",
    "open": {
      "open_platform_name": "whatsapp"
    }
  }
}
```

### Example 2: Registration with Identifiers and Tags

```json
POST /api/channels/open
{
  "channel": {
    "type": "open",
    "opt_in": true,
    "address": "+15035556789",
    "tags": ["premium", "en-us"],
    "timezone": "America/Los_Angeles",
    "locale_country": "US",
    "locale_language": "en",
    "open": {
      "open_platform_name": "whatsapp",
      "identifiers": {
        "crm_id": "usr_9876",
        "account_tier": "gold"
      }
    }
  }
}
```

### Example 3: Opt-Out Update

To stop delivery to a channel without deleting it, set `opt_in` to `false`:

```json
POST /api/channels/open
{
  "channel": {
    "type": "open",
    "opt_in": false,
    "address": "+15035556789",
    "open": {
      "open_platform_name": "whatsapp"
    }
  }
}
```

## Error Handling

### 400 Bad Request
- Missing required fields (`type`, `opt_in`, `address`, or `open_platform_name`)
- `open_platform_name` does not match any configured platform in the project
- `address` exceeds 128 characters
- More than 100 identifier pairs

### 401 Unauthorized
- Invalid or missing credentials

## Best Practices

1. **Register on first contact** — Call this endpoint the first time you see a new address. The upsert behavior means you can safely call it again to update opt-in status or identifiers.
2. **Propagate opt-out immediately** — When a user opts out in your system, update Airship with `opt_in: false` before they could receive another push.
3. **Keep identifiers exhaustive** — The `identifiers` map replaces on update, so always send the complete set.
4. **Associate with a named user after registration** — Use the returned `channel_id` with the [Named Users](../named-users/SKILL.md) skill to link the channel to a known user identity.

## Workflows Using This Skill

- **Open Channel Middleware**: Full middleware build guide for webhook server + registration + delivery.
  - See [Workflow Guide](../../workflows/open-channel-middleware/SKILL.md)

## Related Skills

- [Named Users](../named-users/SKILL.md) — Associate the registered channel with a named user
- [Tags](../tags/SKILL.md) — Manage tags on the channel after registration
- [Push Notification](../push-notification/SKILL.md) — Send to an open channel using `open_channel` audience selector and `open::<platform>` device type

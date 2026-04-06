---
name: channel-listing
description: List all channels registered to an app key with pagination support. Channels are returned in sorted order by channel_id (UUID). Use when you need to retrieve multiple channels, export audience data, or perform bulk operations on channels.
metadata:
  category: api
---

# Skill: Channel Listing

## Overview

List all channels registered to an app key with pagination support. Channels are returned in sorted order by `channel_id` (UUID), enabling efficient parallel pagination strategies. Tags added via Named Users tag endpoint won't appear - use Named User lookup if needed.

## API Endpoint

**Method**: `GET`  
**Path**: `/api/channels`  
**Base URL**: `https://go.urbanairship.com`  
**Full URL**: `https://go.urbanairship.com/api/channels`

## Authentication

Supports Basic Auth, Bearer Token, or OAuth2 with scope `chn`.

## Request Headers

```
Accept: application/vnd.urbanairship+json; version=3
Authorization: Basic <credentials> (or Bearer token)
```

## Request Parameters

- **`limit`** (integer, optional): Maximum results per request. Default 1,000, maximum 1,000.
- **`start`** (string, optional): `channel_id` (UUID) to start pagination from. Channels returned in sorted order.

## Pagination

Uses cursor-based pagination with `start` parameter:
1. First request: Omit `start` to get first page
2. Subsequent requests: Use `channel_id` from last item of previous page as `start`
3. Response includes `next_page` URL with `start` already set

**Key Insight**: UUIDs are evenly distributed across hex digits (0-9, a-f), enabling parallel pagination across 16 threads.

## Response Schema

### Success Response (200 OK)

```json
{
  "ok": true,
  "channels": [
    {
      "channel_id": "9c36e8c7-5a73-47c0-9716-99fd3d4197d5",
      "device_type": "ios",
      "installed": true,
      "opt_in": true,
      "push_address": "FE66489F304DC75B8D6E8200DFF8A456E8DAEACEC428B427E9518741C92C6660",
      "created": "2020-08-08T20:41:06",
      "last_registration": "2020-10-07T21:28:35",
      "named_user_id": "some_id_that_maps_to_your_systems",
      "tags": ["tag1", "tag2"],
      "tag_groups": {
        "tag_group_1": ["tag1", "tag2"]
      }
    }
  ],
  "next_page": "https:\/\/go.urbanairship.com\/api\/channels?limit=1000&start=535ec31e-4b07-4b26-bead-a1c0e94e133c"
}
```

### Key Channel Fields

- `channel_id` (UUID): Unique identifier
- `device_type`: `ios`, `android`, `amazon`, `web`, `open`, `email`, `sms`
- `installed`, `opt_in` (boolean): Channel status
- `push_address` / `address`: Push notification address
- `named_user_id`: Associated named user
- `tags`, `tag_groups`: Tags and tag groups
- `created`, `last_registration`: Timestamps

## Examples

See example files: `list-channels-first-page.json`, `list-channels-paginated.json`

```json
GET /api/channels?limit=1000
Authorization: Bearer <token>
Accept: application/vnd.urbanairship+json; version=3
```

## Error Handling

- **401**: Unauthorized - Invalid credentials
- **404**: Not Found - No channels found
- **406**: Not Acceptable - Invalid API version header

## Best Practices

1. Use `limit=1000` for optimal performance
2. Leverage sorted ordering for parallel pagination (16 threads by hex digit)
3. Use `next_page` URL for subsequent requests
4. Continue until `next_page` is null
5. Respect rate limits for multiple requests

## Use Cases

- Audience export and backup
- Bulk operations (tags, attributes, messaging)
- Data synchronization
- Audit and reporting
- Parallel pagination (see Download Entire Audience workflow)

## Workflows Using This Skill

- **[Download Entire Audience](../../../workflows/download-entire-audience/SKILL.md)** - Parallel pagination across UUID prefixes

## Related Skills

- [Email Lookup](../email-lookup/) - Lookup specific email channel
- [SMS Lookup](../sms-lookup/) - Lookup specific SMS channel
- [Named Users](../named-users/) - Associate channels with named users

## Additional Resources

- [Channel Listing API Reference](https://docs.airship.com/developer/rest-api/ua/operations/channels/#channellisting)
- [Pagination Documentation](https://docs.airship.com/developer/rest-api/ua/operations/#pagination)

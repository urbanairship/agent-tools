---
name: tags
metadata:
  category: api
description: Add, remove, or set tags on named users or channels for audience segmentation and targeting. Use when organizing users into groups, creating segments, or managing user metadata.
---

# Skill: Manage Tags

## Overview

This skill enables agents to add, remove, or set tags on named users or channels. Tags are metadata used for audience segmentation and targeting. Tags belong to tag groups, which help organize and categorize your tags.

## Tag Operations

There are two main endpoints for tag management:

1. **Named User Tags** - `POST /api/named_users/tags` (Recommended)
2. **Channel Tags** - `POST /api/channels/{channel_id}/tags`

## Best Practices

- **Prefer Named User Tags**: When using named users, apply tags at the named user level rather than channel level
- **Use Tag Groups**: Always use custom tag groups instead of device tags to avoid SDK overwrites
- **Tag Limits**: Maximum 1,000 tags per named user (strongly recommended to stay below this)
- **Tag Length**: Tags must be less than 128 characters

## Endpoint 1: Named User Tags

**Method**: `POST`  
**Path**: `/api/named_users/tags`  
**Base URL**:
- US: `https://go.urbanairship.com`
- EU: `https://go.airship.eu`
- US (OAuth): `https://api.asnapius.com`
- EU (OAuth): `https://api.asnapieu.com`

### Authentication

| Method | Endpoint | Scope |
|---|---|---|
| OAuth (recommended) | `api.asnapius.com` | `nu` |
| Bearer token | `go.urbanairship.com` | — |
| Basic | `go.urbanairship.com` | — |

See [Authentication Guide](../../AUTHENTICATION.md) for token request details and MCP setup.

### Request Headers

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

### Request Schema

```json
{
  "audience": {
    "named_user_id": ["user-1", "user-2", "user-3"]  // 1-1000 named users
  },
  "add": {
    "tag_group_1": ["tag1", "tag2", "tag3"],
    "tag_group_2": ["tag1", "tag4", "tag5"]
  },
  "remove": {
    "tag_group_2": ["tag6", "tag7"]
  },
  "set": {
    "tag_group_3": ["tag8", "tag9"]  // Replaces all tags in group
  }
}
```

**Note**: At least one of `add`, `remove`, or `set` must be present.

### Request Fields

- **audience.named_user_id**: Array of named user IDs (1-1000 items)
- **add**: Object mapping tag group names to arrays of tags to add
- **remove**: Object mapping tag group names to arrays of tags to remove
- **set**: Object mapping tag group names to arrays of tags to set (replaces existing tags in group)

### Response Schema

**Success (200 OK):**
```json
{
  "ok": true,
  "tag_warnings": "tag_group_1,tag_group_2"  // CSV list if some groups failed
}
```

**Error (400 Bad Request):**
```json
{
  "ok": false,
  "error": "Same tag present in both add and remove",
  "error_code": 40001
}
```

## Endpoint 2: Channel Tags

**Method**: `POST`  
**Path**: `/api/channels/{channel_id}/tags`  
**Base URL**: (same as above)

### Authentication

| Method | Endpoint | Scope |
|---|---|---|
| OAuth (recommended) | `api.asnapius.com` | `chn` |
| Bearer token | `go.urbanairship.com` | — |
| Basic | `go.urbanairship.com` | — |

See [Authentication Guide](../../AUTHENTICATION.md) for token request details and MCP setup.

### Request Headers

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

### Request Schema

```json
{
  "add": {
    "tag_group_1": ["tag1", "tag2"],
    "tag_group_2": ["tag3"]
  },
  "remove": {
    "tag_group_1": ["tag1"]
  },
  "set": {
    "tag_group_3": ["tag4", "tag5"]
  }
}
```

### Path Parameters

- **channel_id**: UUID of the channel (required in URL path)

## Tag Groups

### Types of Tag Groups

1. **Custom Tag Groups**: Created by you in the dashboard
   - Maximum 100 custom tag groups
   - You manage tags and group names
   - Recommended for most use cases

2. **Device Tags** (`device` group): Primary device tags
   - Can be overwritten by SDK
   - Not recommended for API-set tags
   - Associated with channel IDs only, not named users

3. **Device Property Tags** (`ua_*` groups): Airship-managed
   - Cannot be modified
   - Used for device properties (locale, timezone, etc.)

### Tag Group Structure

```json
{
  "tag_group_name": ["tag1", "tag2", "tag3"]
}
```

- Tag group name: 1-128 characters
- Tags array: 0-100 tags per group
- Each tag: 1-128 characters

## Examples

### Example 1: Add Tags to Named Users

```json
{
  "audience": {
    "named_user_id": ["user-123", "user-456"]
  },
  "add": {
    "loyalty": ["gold-member", "ten-plus-years"],
    "interests": ["sports", "technology"]
  }
}
```

### Example 2: Remove Tags from Named Users

```json
{
  "audience": {
    "named_user_id": ["user-123"]
  },
  "remove": {
    "loyalty": ["bronze-member"],
    "interests": ["old-interest"]
  }
}
```

### Example 3: Set Tags (Replace All Tags in Group)

```json
{
  "audience": {
    "named_user_id": ["user-123"]
  },
  "set": {
    "loyalty": ["gold-member"],
    "interests": ["sports", "technology", "music"]
  }
}
```

### Example 4: Combined Add and Remove

```json
{
  "audience": {
    "named_user_id": ["user-123"]
  },
  "add": {
    "loyalty": ["gold-member"]
  },
  "remove": {
    "loyalty": ["silver-member"]
  }
}
```

### Example 5: Channel Tags

```json
POST /api/channels/9c36e8c7-5a73-47c0-9716-99fd3d4197d5/tags

{
  "add": {
    "device_properties": ["push_enabled"],
    "user_preferences": ["newsletter_subscribed"]
  }
}
```

## Common Error Codes

- **400**: Bad Request - Same tag in both add and remove, tag > 128 chars, or validation failure
- **401**: Unauthorized - Invalid or missing authentication
- **403**: Forbidden - Secure tag groups require master secret
- **406**: Not Acceptable - Missing or invalid API version header

## Important Notes

1. **Tag Group Creation**: Tag groups must be created in the dashboard before use
2. **Tag Creation**: Tags are automatically created when first used
3. **Named User Tags**: Tags set on named users apply to all associated channels
4. **Channel Limits**: Named users can have up to 100 associated channels
5. **Tag Limits**: Maximum 1,000 tags per named user (recommended to stay well below)
6. **Secure Tag Groups**: Require master secret authentication
7. **Partial Success**: API may return 200 with warnings if some tag groups fail

## Use Cases

- **Segmentation**: Tag users based on behavior, preferences, or attributes
- **Targeting**: Use tags to target specific audience segments
- **Lifecycle Tracking**: Tag users at different stages (new, active, churned)
- **Preference Management**: Track user preferences and interests
- **Campaign Tracking**: Tag users who engaged with specific campaigns

## Workflows Using This Skill

Tags are commonly used across many workflows for segmentation and targeting:
- **Complete User Onboarding**: Tag users during onboarding for segmentation
- **Channel Registration**: Add tags when registering channels to organize users
- **Event Tracking**: Use tags with custom events for advanced segmentation

See [Workflow Examples](../../docs/workflows.md) for complete workflows.

## Related Documentation

- [Tags Guide](https://docs.airship.com/guides/audience/tags/)
- [Named User Tags API](https://docs.airship.com/developer/rest-api/ua/operations/tags/#modifynamedusertags)
- [Channel Tags API](https://docs.airship.com/developer/rest-api/ua/operations/tags/#modifychanneltags)
- [Tag Groups Reference](https://docs.airship.com/reference/integration/device-properties/)

## Function Calling Schema (OpenAI Format)

```json
{
  "name": "manage_tags",
  "description": "Add, remove, or set tags on named users or channels for audience segmentation",
  "parameters": {
    "type": "object",
    "properties": {
      "target_type": {
        "type": "string",
        "enum": ["named_user", "channel"],
        "description": "Whether to tag named users or a specific channel"
      },
      "named_user_ids": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Array of named user IDs (1-1000) - required if target_type is named_user"
      },
      "channel_id": {
        "type": "string",
        "format": "uuid",
        "description": "Channel ID - required if target_type is channel"
      },
      "add": {
        "type": "object",
        "description": "Tags to add, organized by tag group",
        "additionalProperties": {
          "type": "array",
          "items": {"type": "string"}
        }
      },
      "remove": {
        "type": "object",
        "description": "Tags to remove, organized by tag group",
        "additionalProperties": {
          "type": "array",
          "items": {"type": "string"}
        }
      },
      "set": {
        "type": "object",
        "description": "Tags to set (replaces all tags in group), organized by tag group",
        "additionalProperties": {
          "type": "array",
          "items": {"type": "string"}
        }
      }
    },
    "required": ["target_type"]
  }
}
```

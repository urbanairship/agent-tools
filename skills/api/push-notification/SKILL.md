---
name: push-notification
metadata:
  category: api
description: Send push notifications to Airship audiences across multiple platforms including iOS, Android, Web, Email, and SMS. Use when the user wants to send notifications, alerts, or messages to users.
---

# Skill: Send Push Notification

## Overview

This skill enables agents to send push notifications to Airship audiences across multiple platforms including iOS, Android, Web, Email, and SMS.

## API Endpoint

**Method**: `POST`  
**Path**: `/api/push`  
**Base URL**:
- US: `https://go.urbanairship.com`
- EU: `https://go.airship.eu`
- US (OAuth): `https://api.asnapius.com`
- EU (OAuth): `https://api.asnapieu.com`

**Path**: `/api/push`

## Authentication

| Method | Endpoint | Scope |
|---|---|---|
| OAuth (recommended) | `api.asnapius.com` | `psh` |
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

The request body can be either:
1. A single Push Object
2. An array of Push Objects (1-100 items)

### Push Object Schema

```json
{
  "audience": {
    // Required: One of the audience selectors below
  },
  "device_types": ["ios", "android", "web", "email", "sms", "amazon"],
  "notification": {
    // Required: Notification content
  },
  "message": {
    // Optional: Message Center content
  },
  "in_app": {
    // Optional: In-app message content
  },
  "options": {
    // Optional: Push options
  },
  "campaigns": {
    // Optional: Campaign tracking
  }
}
```

### Audience Selectors

Choose ONE of the following audience types:

**By Channel ID:**
```json
{
  "audience": {
    "ios_channel": "uuid",
    "android_channel": "uuid",
    "web_channel": "uuid",
    "email_address": "user@example.com",
    "sms_id": {
      "msisdn": "15551234567",
      "sender": "12345"
    }
  }
}
```

**By Named User:**
```json
{
  "audience": {
    "named_user": "user-id-1234"
  }
}
```

**By Tag:**
```json
{
  "audience": {
    "tag": "tag_name",
    "group": "tag_group_name"  // Optional, defaults to "device"
  }
}
```

**By Segment:**
```json
{
  "audience": {
    "segment": "segment-id"
  }
}
```

**By Static List:**
```json
{
  "audience": {
    "static_list": "list_name"
  }
}
```

**Compound Selectors:**
```json
{
  "audience": {
    "AND": [
      {"tag": "sports", "group": "interests"},
      {"tag": "language_en"}
    ]
  }
}
```

### Notification Object

**Simple Alert (all platforms):**
```json
{
  "notification": {
    "alert": "Hello, world!"
  }
}
```

**Platform-Specific Overrides:**
```json
{
  "notification": {
    "alert": "Default message",
    "ios": {
      "alert": "iOS-specific message",
      "badge": "+1",
      "sound": "default"
    },
    "android": {
      "alert": "Android-specific message",
      "title": "Notification Title"
    },
    "web": {
      "alert": "Web notification",
      "title": "Web Title",
      "icon": "icon-url"
    },
    "email": {
      "subject": "Email Subject",
      "html_body": "<h1>HTML Content</h1>",
      "plaintext_body": "Plain text content",
      "message_type": "commercial"
    },
    "sms": {
      "alert": "SMS message text"
    }
  }
}
```

### Device Types

Required array specifying target platforms:
```json
{
  "device_types": ["ios", "android", "web", "email", "sms", "amazon"]
}
```

### Options Object

```json
{
  "options": {
    "expiry": "2024-12-31T23:59:59",  // ISO 8601 datetime
    "personalization": true,  // Enable handlebars templating
    "no_throttle": false  // Disable rate limiting
  }
}
```

## Response Schema

**Success (202 Accepted):**
```json
{
  "ok": true,
  "operation_id": "uuid",
  "push_ids": ["uuid1", "uuid2"],
  "message_ids": ["id1", "id2"],  // If Message Center included
  "content_urls": ["url1", "url2"],  // If rich content included
  "localized_ids": ["uuid"]  // If localizations included
}
```

**Error (400 Bad Request):**
```json
{
  "ok": false,
  "error": "Error message",
  "error_code": 40001,
  "details": {
    "field": "additional error details"
  }
}
```

## Common Error Codes

- **400**: Bad Request - Invalid payload, missing required fields, or validation failure
- **401**: Unauthorized - Invalid or missing authentication
- **406**: Not Acceptable - Missing or invalid API version header
- **413**: Payload Too Large - Request exceeds 5 MiB limit
- **429**: Too Many Requests - Rate limit exceeded

## Examples

### Example 1: Simple Push to iOS Channel

```json
{
  "audience": {
    "ios_channel": "9c36e8c7-5a73-47c0-9716-99fd3d4197d5"
  },
  "notification": {
    "alert": "Hello!"
  },
  "device_types": ["ios"]
}
```

### Example 2: Push to Tagged Audience

```json
{
  "audience": {
    "tag": "needs_a_greeting",
    "group": "new_customer"
  },
  "notification": {
    "alert": "Hi! Welcome to our app."
  },
  "device_types": ["ios", "android"]
}
```

### Example 3: Multi-Platform Push with Overrides

```json
{
  "audience": {
    "named_user": "user-123"
  },
  "device_types": ["ios", "android", "email"],
  "notification": {
    "alert": "Default message",
    "ios": {
      "alert": "iOS message",
      "badge": "+1"
    },
    "android": {
      "alert": "Android message",
      "title": "Important"
    },
    "email": {
      "subject": "Email Subject",
      "html_body": "<h1>Email Content</h1>",
      "plaintext_body": "Email Content",
      "message_type": "transactional"
    }
  }
}
```

### Example 4: Push with Message Center

```json
{
  "audience": {
    "tag": "premium_members"
  },
  "notification": {
    "alert": "You have a new message"
  },
  "message": {
    "title": "Message Title",
    "body": "<html><body><h1>Rich Content</h1></body></html>",
    "content_type": "text/html"
  },
  "device_types": ["ios", "android"]
}
```

## Validation Endpoint

Before sending, you can validate your push payload:

**Endpoint**: `POST /api/push/validate`  
**Same payload format** as `/api/push`  
**Response**: `200 OK` with `{"ok": true}` if valid, `400` with error details if invalid

## Best Practices

1. **Always specify device_types** - Match device_types to your audience selector
2. **Use named users** - Prefer named_user audience when possible for better user coordination
3. **Validate first** - Use `/api/push/validate` before sending to production
4. **Handle errors** - Check response codes and handle errors appropriately
5. **Respect rate limits** - Implement backoff for 429 responses
6. **Use tag groups** - Prefer custom tag groups over device tags
7. **Set expiry** - Use options.expiry for time-sensitive messages

## Limits

- Maximum payload size: 5 MiB
- Maximum array size: 100 push objects per request
- Rate limits: Varies by plan (check with Airship Support)

## Workflows Using This Skill

- **Complete User Onboarding**: Register email → Register SMS → Associate both → Send welcome
  - See [Workflow Guide](../../docs/workflows.md#complete-user-onboarding)

## Related Documentation

- [Push API Reference](https://docs.airship.com/developer/rest-api/ua/operations/push/)
- [OpenAPI Specification](https://docs.airship.com/developer/rest-api/)
- [Audience Selection Guide](https://docs.airship.com/developer/rest-api/ua/schemas/audience-selection/)
- [Push Notification Guide](https://docs.airship.com/guides/features/messaging/push-notifications/)

## Function Calling Schema (OpenAI Format)

```json
{
  "name": "send_push_notification",
  "description": "Send a push notification to Airship audience across iOS, Android, Web, Email, or SMS platforms",
  "parameters": {
    "type": "object",
    "properties": {
      "audience": {
        "type": "object",
        "description": "Audience selector - one of: channel, named_user, tag, segment, or static_list",
        "properties": {
          "ios_channel": {"type": "string", "format": "uuid"},
          "android_channel": {"type": "string", "format": "uuid"},
          "web_channel": {"type": "string", "format": "uuid"},
          "named_user": {"type": "string"},
          "tag": {"type": "string"},
          "group": {"type": "string"},
          "segment": {"type": "string"},
          "static_list": {"type": "string"}
        }
      },
      "device_types": {
        "type": "array",
        "items": {"type": "string", "enum": ["ios", "android", "web", "email", "sms", "amazon"]},
        "description": "Target device platforms"
      },
      "notification": {
        "type": "object",
        "description": "Notification content",
        "properties": {
          "alert": {"type": "string", "description": "Default alert message"},
          "ios": {"type": "object"},
          "android": {"type": "object"},
          "web": {"type": "object"},
          "email": {"type": "object"},
          "sms": {"type": "object"}
        }
      },
      "options": {
        "type": "object",
        "properties": {
          "expiry": {"type": "string", "format": "date-time"},
          "personalization": {"type": "boolean"},
          "no_throttle": {"type": "boolean"}
        }
      }
    },
    "required": ["audience", "device_types", "notification"]
  }
}
```

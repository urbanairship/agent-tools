---
name: custom-events
metadata:
  category: api
description: Submit custom events to Airship for user tracking, automation triggers, and audience segmentation. Use when tracking user actions, behaviors, or when events need to trigger automated messages and sequences.
---

# Skill: Submit Custom Event

## Overview

This skill enables agents to submit custom events to Airship for user tracking, automation triggers, and audience segmentation. Custom events can trigger automated messages and sequences, and can be used for detailed user behavior analysis.

## API Endpoint

**Method**: `POST`  
**Path**: `/api/custom-events`  
**Base URL**: `https://go.urbanairship.com`  
**Full URL**: `https://go.urbanairship.com/api/custom-events`

## Authentication

**Required**: Bearer Token or OAuth2 Token with `evt` scope

**Headers**:
```
Authorization: Bearer <bearer_token>
X-UA-Appkey: <application_key>
Accept: application/vnd.urbanairship+json; version=3
Content-Type: application/json
```

## Request Schema

The request body must be an **array** of Custom Event objects (1-100 events per request).

### Custom Event Object Schema

```json
{
  "occurred": "2024-01-15T14:30:00Z",  // Optional, defaults to current time
  "user": {
    // Required: One of the user identifiers below
  },
  "body": {
    "name": "event_name",  // Required: lowercase only
    "value": 123.45,  // Optional: numeric value
    "transaction": "transaction-uuid",  // Optional: transaction ID
    "interaction_type": "url",  // Optional: url, email, social, etc.
    "interaction_id": "path/to/resource",  // Optional: where event occurred
    "session_id": "session-uuid",  // Optional: user session ID
    "unique_id": "unique-event-id",  // Optional: for deduplication
    "properties": {  // Optional: custom properties object
      "key1": "value1",
      "key2": 123,
      "nested": {
        "property": "value"
      }
    }
  }
}
```

### User Identification

Choose ONE of the following user identifier types:

**By Named User ID:**
```json
{
  "user": {
    "named_user_id": "user-123"
  }
}
```

**By Channel ID:**
```json
{
  "user": {
    "ios_channel": "uuid",
    "android_channel": "uuid",
    "web_channel": "uuid",
    "amazon_channel": "uuid",
    "channel": "uuid"  // Generic channel (Airship determines device)
  }
}
```

### Event Name Rules

- **Required**: Must be present in `body.name`
- **Case**: Must be lowercase only (no uppercase characters)
- **Pattern**: `[^A-Z]` - any characters except uppercase letters
- **Rejection**: Events with uppercase characters will return `400 Bad Request`

### Event Properties

The `body.properties` object:
- Can contain any JSON-serializable data
- String values limited to 255 characters maximum
- Can be nested objects
- Used for handlebars templating in triggered messages
- Accessible in automation and sequence triggers

### Occurred Timestamp

- **Format**: ISO 8601 datetime in UTC
- **Range**: Must be within past 90 days
- **Future dates**: Not allowed
- **Default**: Current time if omitted
- **Examples**:
  - `2024-01-15T14:30:00Z`
  - `2024-01-15T14:30:00`
  - `2024-01-15 14:30:00Z`

## Response Schema

**Success (200 OK):**
```json
{
  "ok": true,
  "operation_id": "ef625038-70a3-41f1-826f-57bc11dd625a"
}
```

**Error (400 Bad Request):**
```json
{
  "ok": false,
  "error": "Event name contains uppercase characters",
  "error_code": 40001
}
```

## Common Error Codes

- **400**: Bad Request - Invalid event name (uppercase), missing required fields, or validation failure
- **401**: Unauthorized - Invalid or missing authentication
- **406**: Not Acceptable - Missing or invalid API version header

## Examples

### Example 1: Simple Purchase Event

```json
[
  {
    "occurred": "2024-01-15T14:30:00Z",
    "user": {
      "named_user_id": "hugh.manbeing"
    },
    "body": {
      "name": "purchased",
      "value": 239.85,
      "transaction": "886f53d4-3e0f-46d7-930e-c2792dac6e0a",
      "properties": {
        "product_id": "prod-456",
        "category": "electronics"
      }
    }
  }
]
```

### Example 2: Event with Full Details

```json
[
  {
    "occurred": "2024-01-15T14:30:00Z",
    "user": {
      "named_user_id": "user-123"
    },
    "body": {
      "name": "product_viewed",
      "interaction_type": "url",
      "interaction_id": "your.store/us/en_us/pd/shoe/pid-11046546",
      "session_id": "22404b07-3f8f-4e42-a4ff-a996c18fa9f1",
      "properties": {
        "product_id": "pid-11046546",
        "category": "footwear",
        "price": 79.95,
        "brand": "Victory Sneakers"
      }
    }
  }
]
```

### Example 3: Multiple Events in One Request

```json
[
  {
    "user": {
      "named_user_id": "user-123"
    },
    "body": {
      "name": "page_viewed",
      "properties": {
        "page": "home"
      }
    }
  },
  {
    "user": {
      "named_user_id": "user-123"
    },
    "body": {
      "name": "button_clicked",
      "properties": {
        "button": "signup"
      }
    }
  }
]
```

### Example 4: Event with Channel ID

```json
[
  {
    "occurred": "2024-01-15T14:30:00Z",
    "user": {
      "ios_channel": "f59970d3-3d42-4584-907e-f5c57f5d46a1"
    },
    "body": {
      "name": "app_opened",
      "properties": {
        "source": "push_notification"
      }
    }
  }
]
```

## Best Practices

1. **Use lowercase event names** - Always use lowercase for event names
2. **Include occurred timestamp** - Specify when event occurred for accurate tracking
3. **Use named_user_id** - Prefer named users over channel IDs when possible
4. **Add meaningful properties** - Include relevant context in properties for segmentation
5. **Use transaction IDs** - Group related events with transaction field
6. **Include session_id** - Track user sessions for better analytics
7. **Batch events** - Send multiple events in one request (up to 100) for efficiency
8. **Set unique_id** - Use unique_id for sequence triggers to prevent duplicate sends

## Limits

- Maximum events per request: 100
- Event name: lowercase only, no uppercase characters
- Property string length: 255 characters maximum
- Occurred timestamp: Must be within past 90 days
- Request validation: Complete validation before response

## Use Cases

- **E-commerce**: Track purchases, cart additions, product views
- **Content**: Track article reads, video plays, content engagement
- **Gaming**: Track level completions, achievements, in-game purchases
- **Automation Triggers**: Trigger automated messages based on events
- **Segmentation**: Build segments based on event history
- **Analytics**: Analyze user behavior patterns

## Workflows Using This Skill

- **Complete User Onboarding**: Register email → Register SMS → Associate both → Track completion → Send welcome
  - See [Workflow Guide](../../docs/workflows.md#complete-user-onboarding)
- **Purchase-to-Pass Update**: POS system emits purchase events → RTDS listener processes events → Updates wallet pass points
  - See [Workflow Guide](../../docs/workflows.md#purchase-to-pass-update)

## Related Documentation

- [Custom Events API Reference](https://docs.airship.com/developer/rest-api/ua/operations/custom-events/)
- [Custom Events Guide](https://docs.airship.com/guides/audience/events/custom-events/)
- [OpenAPI Specification](https://docs.airship.com/developer/rest-api/)

## Function Calling Schema (OpenAI Format)

```json
{
  "name": "submit_custom_event",
  "description": "Submit custom events to Airship for user tracking, automation triggers, and segmentation",
  "parameters": {
    "type": "object",
    "properties": {
      "events": {
        "type": "array",
        "description": "Array of custom events (1-100 events)",
        "items": {
          "type": "object",
          "properties": {
            "occurred": {
              "type": "string",
              "format": "date-time",
              "description": "ISO 8601 datetime when event occurred (within past 90 days)"
            },
            "user": {
              "type": "object",
              "description": "User identifier - named_user_id or channel ID",
              "properties": {
                "named_user_id": {"type": "string"},
                "ios_channel": {"type": "string", "format": "uuid"},
                "android_channel": {"type": "string", "format": "uuid"},
                "web_channel": {"type": "string", "format": "uuid"},
                "channel": {"type": "string", "format": "uuid"}
              }
            },
            "body": {
              "type": "object",
              "properties": {
                "name": {
                  "type": "string",
                  "description": "Event name (lowercase only, no uppercase)"
                },
                "value": {"type": "number"},
                "transaction": {"type": "string"},
                "interaction_type": {"type": "string"},
                "interaction_id": {"type": "string"},
                "session_id": {"type": "string"},
                "unique_id": {"type": "string"},
                "properties": {
                  "type": "object",
                  "description": "Custom properties (string values max 255 chars)"
                }
              },
              "required": ["name"]
            }
          },
          "required": ["user", "body"]
        }
      }
    },
    "required": ["events"]
  }
}
```

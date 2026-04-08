# Airship Push API Specification

Complete API specification for the `/api/push` endpoint - use this to understand how to construct push payloads.

## Push Endpoint

**POST** `/api/push`

Send a push notification, Message Center message, SMS, email, or a combination.

### Base Request Structure

```json
{
  "audience": <audience_selector>,
  "device_types": <device_types_array>,
  "notification": <notification_object>,
  "message": <message_object>,
  "in_app": <in_app_object>,
  "campaigns": <campaigns_object>,
  "options": <options_object>,
  "message_type": <string>
}
```

## Audience Selectors

### Simple Selectors

#### Tag
Target users with a specific tag.
```json
{"tag": "tag_name"}
```

#### Tag with Group
Target users with a tag in a specific group.
```json
{
  "tag": "tag_name",
  "group": "group_name"
}
```

#### iOS Channel
Target a specific iOS device by channel ID.
```json
{"ios_channel": "channel-uuid"}
```

#### Android Channel
Target a specific Android device by channel ID.
```json
{"android_channel": "channel-uuid"}
```

#### Amazon Channel
Target a specific Amazon device by channel ID.
```json
{"amazon_channel": "channel-uuid"}
```

#### Web Channel
Target a specific web push device by channel ID.
```json
{"web_channel": "channel-uuid"}
```

#### Open Channel
Target a specific open channel by channel ID.
```json
{"open_channel": "channel-uuid"}
```

#### Named User
Target a specific named user.
```json
{"named_user": "user_identifier"}
```

#### Segment
Target all users in a segment.
```json
{"segment": "segment_id"}
```

#### All
Target all active channels.
```json
"all"
```

### Compound Selectors

#### OR
Target users matching ANY of the conditions.
```json
{
  "or": [
    {"tag": "tag1"},
    {"tag": "tag2"},
    {"named_user": "user123"}
  ]
}
```

#### AND
Target users matching ALL of the conditions.
```json
{
  "and": [
    {"tag": "premium"},
    {"tag": "ios"}
  ]
}
```

#### NOT
Exclude users matching the condition.
```json
{
  "not": {"tag": "unsubscribed"}
}
```

#### Complex Logic
Combine operators for complex targeting.
```json
{
  "and": [
    {
      "or": [
        {"tag": "premium"},
        {"tag": "trial"}
      ]
    },
    {
      "not": {"tag": "inactive"}
    }
  ]
}
```

## Device Types

Array specifying which device types to target. Must include at least one.

```json
["ios", "android", "amazon", "web"]
```

Available types:
- `"ios"` - iOS devices
- `"android"` - Android devices
- `"amazon"` - Amazon devices
- `"web"` - Web push
- `"sms"` - SMS (requires SMS configuration)
- `"email"` - Email (requires email configuration)

## Notification Object

Platform-specific notification configurations.

### Cross-Platform Alert
Simple alert for all platforms.
```json
{
  "notification": {
    "alert": "Hello World!"
  }
}
```

### iOS Notification

```json
{
  "notification": {
    "ios": {
      "alert": "Simple alert",
      "badge": "+1",
      "sound": "default",
      "category": "custom_category",
      "thread_id": "thread_identifier",
      "content_available": true,
      "mutable_content": true,
      "extra": {
        "custom_key": "custom_value"
      }
    }
  }
}
```

#### iOS Alert Object
```json
{
  "ios": {
    "alert": {
      "title": "Notification Title",
      "subtitle": "Notification Subtitle",
      "body": "Notification body text"
    }
  }
}
```

#### iOS Actions
```json
{
  "ios": {
    "alert": "Check this out!",
    "actions": {
      "open": {
        "type": "url",
        "content": "https://example.com"
      }
    }
  }
}
```

Action types:
- `"url"` - Open a URL
- `"deep_link"` - Open a deep link
- `"landing_page"` - Open a landing page
- `"app"` - Open the app

#### iOS Media Attachment
```json
{
  "ios": {
    "alert": "Check out this image",
    "media_attachment": {
      "url": "https://example.com/image.jpg",
      "content": {
        "title": "Image Title",
        "body": "Image description"
      }
    }
  }
}
```

### Android Notification

```json
{
  "notification": {
    "android": {
      "alert": "Notification body",
      "title": "Notification Title",
      "summary": "Notification summary",
      "icon": "ic_notification",
      "icon_color": "#FF5733",
      "sound": "custom_sound",
      "priority": "high",
      "category": "alarm",
      "visibility": "public",
      "notification_channel": "channel_id",
      "extra": {
        "custom_key": "custom_value"
      }
    }
  }
}
```

Priority values: `"min"`, `"low"`, `"default"`, `"high"`, `"max"`

#### Android Style
```json
{
  "android": {
    "alert": "Main text",
    "style": {
      "type": "big_text",
      "big_text": "This is a longer text that will be expanded",
      "title": "Big Text Title",
      "summary": "Summary text"
    }
  }
}
```

Style types:
- `"big_text"` - Expandable text
- `"big_picture"` - Expandable image
- `"inbox"` - Multiple lines

#### Android Actions
```json
{
  "android": {
    "alert": "Click to view",
    "actions": {
      "open": {
        "type": "landing_page",
        "content": {
          "url": "https://example.com/page.html"
        }
      }
    }
  }
}
```

### Web Push

```json
{
  "notification": {
    "web": {
      "alert": "Web notification",
      "title": "Notification Title",
      "icon": "https://example.com/icon.png",
      "extra": {
        "custom_key": "value"
      }
    }
  }
}
```

## Message Object (Message Center)

Create a Message Center message that persists in the app.

```json
{
  "message": {
    "title": "Message Title",
    "body": "Message body content",
    "content_type": "text/html",
    "content_encoding": "utf8",
    "expiry": "2024-12-31T23:59:59",
    "extra": {
      "custom_data": "value"
    },
    "icons": {
      "list_icon": "https://example.com/list.png"
    }
  }
}
```

Content types:
- `"text/html"` - HTML content with inline styles
- `"text/plain"` - Plain text

## In-App Message

```json
{
  "in_app": {
    "alert": "In-app message",
    "display_type": "banner",
    "display": {
      "position": "top"
    },
    "actions": {
      "button_actions": {
        "yes": {
          "type": "url",
          "label": "Learn More",
          "content": "https://example.com"
        },
        "no": {
          "type": "dismiss",
          "label": "Cancel"
        }
      }
    }
  }
}
```

## Options

Additional sending options.

```json
{
  "options": {
    "test": false,
    "expiry": "2024-12-31T23:59:59"
  }
}
```

### Test Mode
Validate the request without sending.
```json
{"options": {"test": true}}
```

## Message Type

Classify the message type for reporting.

```json
"message_type": "transactional"
```

Types:
- `"transactional"` - Transactional messages (order confirmations, etc.)
- `"commercial"` - Marketing messages

## Campaigns

Associate the push with a campaign.

```json
{
  "campaigns": {
    "categories": ["sale", "promotion"]
  }
}
```

## Localization

Send localized content based on device language.

```json
{
  "notification": {
    "alert": "Hello",
    "localizations": [
      {
        "language": "es",
        "alert": "Hola"
      },
      {
        "language": "fr",
        "alert": "Bonjour"
      }
    ]
  }
}
```

## Interactive Notifications (iOS)

```json
{
  "notification": {
    "ios": {
      "alert": "Rate our app",
      "interactive": {
        "type": "custom_category",
        "button_actions": {
          "yes": {
            "type": "open_url",
            "content": "https://apps.apple.com/app/id123"
          },
          "no": {
            "type": "dismiss"
          }
        }
      }
    }
  }
}
```

## Scheduling

Schedule a push for future delivery.

### Scheduled Time
```json
{
  "schedule": {
    "scheduled_time": "2024-12-25T09:00:00Z"
  }
}
```

### Local Scheduled Time
Send at a specific local time in each timezone.
```json
{
  "schedule": {
    "local_scheduled_time": "2024-12-25T09:00:00"
  }
}
```

## Response Format

### Success Response
```json
{
  "ok": true,
  "operation_id": "uuid",
  "push_ids": ["push-id-1", "push-id-2"],
  "message_ids": ["message-id-1"],
  "content_urls": []
}
```

### Error Response
```json
{
  "ok": false,
  "error": "Error description",
  "error_code": 40000,
  "details": {
    "path": "audience.tag",
    "error": "Invalid tag format"
  }
}
```

## Common Error Codes

- `400` - Bad Request (invalid payload)
- `401` - Unauthorized (invalid credentials)
- `403` - Forbidden (insufficient permissions)
- `406` - Not Acceptable (invalid API version)
- `429` - Too Many Requests (rate limit exceeded)

## Rate Limits

- Default: 500 requests per second
- Batch size: 100 pushes per request
- Burst limit: 1000 requests per 10 seconds

## Best Practices

1. **Always specify device_types** matching your audience
2. **Use test mode** to validate payloads before sending
3. **Channel IDs require platform prefix**: `ios_channel`, `android_channel`, etc.
4. **For single devices**, use channel IDs, not tags
5. **Include error handling** for 400 errors with validation details
6. **Check push_ids** in response for tracking
7. **Use transactional type** for critical notifications
8. **Keep payloads under 4KB** for best delivery
9. **Test on real devices** before large sends
10. **Monitor delivery** via admin dashboard URLs

## Payload Size Limits

- iOS: 4KB (4096 bytes)
- Android: 4KB (4096 bytes)
- Web: 4KB (4096 bytes)
- Message Center: 10KB for HTML content

## Required Fields

At minimum, a push must include:
```json
{
  "audience": <selector>,
  "device_types": [<types>],
  "notification": {"alert": "message"}
}
```

## Common Mistakes

1. **Using `channel_id` instead of `ios_channel` or `android_channel`**
   - ❌ Wrong: `{"audience": {"channel_id": "uuid"}}`
   - ✅ Correct: `{"audience": {"ios_channel": "uuid"}}`

2. **Mismatched device_types and audience**
   - ❌ Wrong: iOS channel with `["android"]` device types
   - ✅ Correct: iOS channel with `["ios"]` device types

3. **Missing device_types**
   - ❌ Wrong: Only specifying audience
   - ✅ Correct: Include both audience and device_types

4. **Incorrect action format**
   - ❌ Wrong: `{"actions": {"open": "url"}}`
   - ✅ Correct: `{"actions": {"open": {"type": "url", "content": "https://..."}}}`

5. **Testing without test mode**
   - ❌ Wrong: Sending to production without validation
   - ✅ Correct: Use `{"options": {"test": true}}` first
---
name: rtds-connection
description: Connect to Airship's Real-Time Data Streaming (RTDS) API to consume event streams with filtering capabilities. Use when monitoring user interactions, push delivery, custom events, or building real-time integrations.
metadata:
  category: rtds
---

# Skill: RTDS Direct Connection

## Overview

This skill enables agents to connect to Airship's Real-Time Data Streaming (RTDS) API to consume event streams with filtering capabilities. RTDS delivers user-level events in real time as newline-delimited JSON (NDJSON), allowing you to monitor user interactions, push delivery, custom events, and more.

## API Endpoint

**Method**: `POST`  
**Path**: `/api/events` (or `/api/events/general` for compliance events only)  
**Base URLs**:
- North America: `https://connect.urbanairship.com`
- Europe: `https://connect.asnapieu.com`

**Full URL**: `https://connect.urbanairship.com/api/events`

## Authentication

**Bearer Token Authentication** (required):
- Obtain access token from RTDS Direct Integration setup in Airship dashboard
- Header: `Authorization: Bearer <access-token>`
- Header: `X-UA-Appkey: <app-key>`

**Note**: RTDS requires a separate access token created in the dashboard. Basic Auth and standard Bearer tokens are not supported.

## Request Headers

```
Accept: application/vnd.urbanairship+x-ndjson; version=3;
Content-Type: application/json
Authorization: Bearer <access-token>
X-UA-Appkey: <app-key>
```

## Request Schema

### Basic Connection

```json
{
  "start": "LATEST"
}
```

### With Filters

```json
{
  "start": "LATEST",
  "filters": [
    {
      "device_types": ["ios", "android"],
      "types": ["OPEN", "SEND", "CLICK"]
    }
  ]
}
```

### With Resume Offset

```json
{
  "resume_offset": "abc123def456..."
}
```

### Request Body Properties

**Start Position** (choose one):
- `start`: `"EARLIEST"` or `"LATEST"` - Start at beginning or end of data window
- `resume_offset`: String - Resume from a specific offset (use when reconnecting)

**Filtering**:
- `filters`: Array of filter objects (see Filter Types below)
- `subset`: Subset specification for sampling (optional)

## Filter Types

### Device Type Filter

Filter events by platform:

```json
{
  "filters": [
    {
      "device_types": ["android", "ios", "web", "email", "sms", "open"]
    }
  ]
}
```

### Event Type Filter

Filter by specific event types:

```json
{
  "filters": [
    {
      "types": ["OPEN", "SEND", "CLICK", "CUSTOM", "COMPLIANCE"]
    }
  ]
}
```

Available event types include: `OPEN`, `SEND`, `CLICK`, `CUSTOM`, `COMPLIANCE`, `ATTRIBUTE_OPERATION`, `TAG_CHANGE`, `UNINSTALL`, `FIRST_OPEN`, `IN_APP_MESSAGE_DISPLAY`, and many more.

### User Filter

Filter events for specific users:

```json
{
  "filters": [
    {
      "users": [
        {"named_user_id": "user_12345"},
        {"contact_id": "contact_abc"}
      ]
    }
  ]
}
```

### Channel/Device Filter

Filter events for specific channels:

```json
{
  "filters": [
    {
      "devices": [
        {"channel": "channel-uuid-here"},
        {"named_user_id": "user_12345"}
      ]
    }
  ]
}
```

### Notification Filter

Filter events related to specific pushes:

```json
{
  "filters": [
    {
      "notifications": {
        "push_id": "push-uuid-here"
      }
    }
  ]
}
```

Or filter by group:

```json
{
  "filters": [
    {
      "notifications": {
        "group_id": "group-uuid-here"
      }
    }
  ]
}
```

### Latency Filter

Filter events by time window (milliseconds):

```json
{
  "filters": [
    {
      "latency": 3600000
    }
  ]
}
```

Returns only events that occurred within the last hour (3600000 ms).

### JSON Predicate Filters

For complex filtering logic, use JSON Predicates:

**Simple predicate**:
```json
{
  "filters": [
    {
      "predicates": [
        {
          "key": "type",
          "value": {"equals": "OPEN"}
        }
      ]
    }
  ]
}
```

**Predicate with scope**:
```json
{
  "filters": [
    {
      "predicates": [
        {
          "scope": ["device"],
          "key": "device_type",
          "value": {"equals": "ANDROID"}
        }
      ]
    }
  ]
}
```

**Combined predicates** (AND):
```json
{
  "filters": [
    {
      "predicates": [
        {
          "and": [
            {"scope": ["device"], "key": "device_type", "value": {"equals": "ANDROID"}},
            {"key": "type", "value": {"equals": "OPEN"}}
          ]
        }
      ]
    }
  ]
}
```

**Value matchers**:
- `equals`: Exact match
- `at_least`: Numeric minimum
- `at_most`: Numeric maximum
- `version_matches`: Version matching (Ivy syntax)
- `is_present`: Check if value exists
- `array_contains`: Check if array contains matching object

## Response Format

### NDJSON (Newline-Delimited JSON)

The response is a stream of newline-delimited JSON objects. Each line is a complete JSON event:

```
{"id":"event-id-1","type":"OPEN","occurred":"2024-01-15T10:30:00Z","offset":"offset-1",...}
{"id":"event-id-2","type":"SEND","occurred":"2024-01-15T10:30:01Z","offset":"offset-2",...}
{"id":"event-id-3","type":"CLICK","occurred":"2024-01-15T10:30:02Z","offset":"offset-3",...}
```

### Event Structure

Each event contains:
- `id`: Unique event identifier
- `type`: Event type (e.g., `OPEN`, `SEND`, `CLICK`)
- `occurred`: Date-time when event occurred
- `processed`: Date-time when event was processed
- `offset`: Offset identifier for reconnection
- `device`: Device information
- `user`: User information (if applicable)
- `body`: Event-specific data

### Example Event

```json
{
  "id": "abc123",
  "type": "OPEN",
  "occurred": "2024-01-15T10:30:00Z",
  "processed": "2024-01-15T10:30:00.100Z",
  "offset": "offset-abc123",
  "device": {
    "channel": "channel-uuid",
    "device_type": "IOS",
    "push_address": "device-token"
  },
  "user": {
    "named_user_id": "user_12345"
  },
  "body": {
    "last_delivered": "2024-01-15T09:00:00Z",
    "session_id": "session-abc"
  }
}
```

## Offset Tracking and Reconnection

### Storing Offsets

Each event includes an `offset` field. Store the last successfully processed offset to enable reconnection:

```json
{
  "offset": "offset-abc123"
}
```

### Reconnecting After Disconnect

If the connection is lost, reconnect using the last processed offset:

```json
{
  "resume_offset": "offset-abc123"
}
```

This ensures you don't miss events that occurred while disconnected.

### Data Retention

Airship stores 7 days or 100 GB of data per app key, whichever comes first. If you need to resume from an offset older than 7 days, use `start: "EARLIEST"` to get available data.

## Best Practices

1. **Always track offsets**: Store the last processed offset to enable seamless reconnection
2. **Use appropriate filters**: Filter events at the API level to reduce processing overhead
3. **Handle disconnections gracefully**: Implement reconnection logic with offset resumption
4. **Process events asynchronously**: Don't block the stream while processing individual events
5. **Monitor connection health**: Implement heartbeat/keepalive mechanisms
6. **Use compliance endpoint for compliance-only**: Use `/api/events/general` if you only need compliance events

## Error Handling

### 401 Unauthorized

Invalid or expired access token. Obtain a new token from the dashboard.

### Connection Drops

If the connection drops:
1. Store the last processed offset
2. Reconnect with `resume_offset` set to the last offset
3. Continue processing from that point

### Rate Limiting

Monitor for rate limiting responses and implement backoff strategies if needed.

## Use Cases

1. **Real-time push monitoring**: Track push delivery, opens, and clicks in real time
2. **Custom event tracking**: Monitor custom events as they occur
3. **Compliance monitoring**: Track opt-in/opt-out events for compliance
4. **User behavior analysis**: Analyze user interactions and app usage patterns
5. **Integration with external systems**: Stream events to data warehouses, analytics platforms, or other systems

## Workflows Using This Skill

- **RTDS Monitoring**: Connect to RTDS → Filter events → Process stream → Reconnect on disconnect
  - See [Workflow Guide](../../docs/workflows.md#rtds-monitoring)
- **Purchase-to-Pass Update**: RTDS listener filters for purchase events → Processes events → Updates wallet pass points
  - See [Workflow Guide](../../docs/workflows.md#purchase-to-pass-update)

## Related Skills

- [Submit Custom Event](../custom-events/) - Submit custom events that appear in RTDS
- [Register Email Channel](../email-registration/) - Register channels that generate RTDS events
- [Register SMS Channel](../sms-registration/) - Register channels that generate RTDS events

## Additional Resources

- [RTDS API Reference](https://docs.airship.com/developer/rest-api/connect/)
- [RTDS Guide](https://docs.airship.com/guides/reports/real-time-data-streaming/)
- [Event Schemas](https://docs.airship.com/developer/rest-api/connect/schemas/events/)
- [OpenAPI Specification](https://docs.airship.com/developer/rest-api/)

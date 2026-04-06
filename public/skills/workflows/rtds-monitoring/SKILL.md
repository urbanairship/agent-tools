---
name: rtds-monitoring
description: Connect to Real-Time Data Streaming API to monitor events, process them, and handle reconnection using offset tracking. Enables real-time monitoring of push delivery, custom events, and user interactions. Use when building real-time integrations, monitoring systems, or event-driven applications.
---

# RTDS Monitoring Workflow

This workflow connects to RTDS, processes events, and handles reconnection.

## Prerequisites

- RTDS must be enabled for your Airship account
- RTDS access token configured in dashboard
- Application ready to process events
- App key

## Skills Required

- [RTDS Connection](../../../skills/rtds/rtds-connection/SKILL.md)

## Step 1: Connect to RTDS Stream

Connect with filters for specific event types:

```json
POST https://connect.urbanairship.com/api/events
Authorization: Bearer <rtds-access-token>
X-UA-Appkey: <app-key>
Accept: application/vnd.urbanairship+x-ndjson; version=3;
Content-Type: application/json

{
  "start": "LATEST",
  "filters": [
    {
      "types": ["OPEN", "SEND", "CLICK", "CUSTOM"]
    }
  ]
}
```

**Response**: Stream of NDJSON events:
```
{"id":"event-1","type":"OPEN","offset":"offset-1",...}
{"id":"event-2","type":"SEND","offset":"offset-2",...}
{"id":"event-3","type":"CLICK","offset":"offset-3",...}
```

## Step 2: Process Events

For each event in the stream:
1. Parse the JSON event
2. Extract the `offset` field
3. Process the event (store in database, trigger actions, etc.)
4. Store the `offset` as the last processed offset

## Step 3: Handle Disconnection

If the connection drops:
1. Use the last stored `offset`
2. Reconnect with `resume_offset`:

```json
POST https://connect.urbanairship.com/api/events
Authorization: Bearer <rtds-access-token>
X-UA-Appkey: <app-key>
Accept: application/vnd.urbanairship+x-ndjson; version=3;
Content-Type: application/json

{
  "resume_offset": "offset-3",
  "filters": [
    {
      "types": ["OPEN", "SEND", "CLICK", "CUSTOM"]
    }
  ]
}
```

This ensures no events are missed between disconnection and reconnection.

## Outcomes

- Real-time event stream connection
- Processed events stored/analyzed
- Seamless reconnection capability

## Use Cases

- Real-time push delivery monitoring
- Custom event tracking
- Compliance monitoring
- User behavior analysis
- Integration with external systems

## Best Practices

1. **Store offsets**: Always track the last processed offset for seamless reconnection
2. **Use appropriate filters**: Filter RTDS events at the API level to reduce processing overhead
3. **Handle errors gracefully**: Implement retry logic and error handling for network issues
4. **Process events efficiently**: Parse and process events as they arrive to avoid backlog

---
name: rtds-event-scan
description: Scan RTDS for specific custom events by named user, channel, or event name within a lookback window. Closes the stream automatically once caught up to live. Use when you need to look up historical custom event activity for a specific user.
metadata:
  category: rtds
---

# Skill: RTDS Event Scan

## Overview

Use the `scan_rtds_events` tool to search Airship's Real-Time Data Streaming (RTDS) history for custom events matching a named user, channel, and/or event name. The tool opens a streaming connection, collects matching events within the requested lookback window, closes the stream once it has caught up to live data, and returns results sorted newest-first.

## When to Use

- "Show me the most recent X event for user Y"
- "Did mia@23grande.demo trigger grande_session_end?"
- "What custom events has channel <id> fired in the last hour?"
- Any query asking about historical custom event activity per user

## Ask Before Calling

**Always ask the user how far back to look before calling this tool**, unless they already specified a time range. Suggested prompt:

> "How far back should I scan? (default: last 10 minutes, max: 7 days)"

If they don't respond or say "default", use `lookback_minutes: 10`.

## Tool

```
scan_rtds_events(
  event_name: str,              # e.g. "grande_session_end" — required
  named_user_id: str = None,    # filter to this named user
  channel_id: str = None,       # filter to this channel instead
  rtds_token: str = None,       # Bearer token from RTDS Direct Integration
                                # Falls back to AIRSHIP_RTDS_TOKEN env var
  lookback_minutes: int = 10,   # how far back to scan (default 10, max 10080 = 7 days)
  max_events: int = 50,         # stop after collecting this many matches
  timeout_seconds: int = 60,    # hard wall-clock safety cap
)
```

## How the Stream Closes

RTDS has no native "stop at now" signal — the stream stays open indefinitely by design. This tool bounds it in two ways:

1. **Latency filter** (`lookback_minutes × 60000 ms`): the RTDS server only delivers events that occurred within the lookback window. Events older than the window are silently discarded server-side before reaching the client.

2. **Catch-up detection**: each RTDS event carries a `processed` timestamp (when Airship ingested it). Once `processed ≥ stream_open_time`, the tool has consumed all historical events in the window and breaks the connection.

`timeout_seconds` is a hard safety cap in case the catch-up signal takes too long.

## PUSH_BODY Events

When scanning for journey/pipeline attribution, `scan_rtds_events` with `event_types: ["PUSH_BODY"]` (or `scan_rtds_sends` with `include_push_body: true`) gives you the best signal.

Key PUSH_BODY facts:

- `body.payload` arrives base64-encoded in the raw stream; this tool decodes it automatically to structured JSON.
- Decoded `body.payload.name` contains the pipeline/journey name (e.g. "Coastal Edit Campaign 1").
- Decoded `body.payload.immediate_trigger` describes what triggered this pipeline step (`segmentation_result`, `pipeline_event`, `custom_event`, `tag_added`, etc.).
- `body.campaigns` is always `null` for pipeline-triggered pushes. Do not use it for journey attribution.
- `body.group_id` is the pipeline UUID; it groups all PUSH_BODY events that fired for the same pipeline definition.
- For pipeline-triggered pushes, SEND events may not appear in the stream at all. PUSH_BODY is the primary record.

### `occurred` is unreliable for PUSH_BODY

PUSH_BODY `occurred` reflects when the pipeline definition was configured in the dashboard, not when the push was sent. The RTDS server-side latency filter is based on `occurred`, so it may not correctly filter PUSH_BODY events. This tool applies a client-side filter using `processed` time instead.

## RTDS Retention

Airship retains up to **7 days** or **100 GB** per app key, whichever comes first. Lookback values beyond 7 days are clamped to 7 days.

## Response

```json
{
  "status": "success",
  "event_name": "grande_session_end",
  "named_user_id": "mia@23grande.demo",
  "lookback_minutes": 10,
  "events_found": 1,
  "events": [
    {
      "id": "abc123",
      "type": "CUSTOM",
      "occurred": "2026-06-11T19:26:34.000Z",
      "processed": "2026-06-11T19:26:34.150Z",
      "offset": "...",
      "device": { "channel": "f8f03514-...", "device_type": "IOS" },
      "user": { "named_user_id": "mia@23grande.demo" },
      "body": {
        "name": "grande_session_end",
        "value": 0,
        "properties": { ... }
      }
    }
  ]
}
```

## Setup

The RTDS token is separate from the standard OAuth token. Obtain it from:

**Airship Dashboard** → **Real-Time Data Streaming** → your Direct Integration → copy the access token.

Set it once as an environment variable so you don't need to pass it each call:

```bash
export AIRSHIP_RTDS_TOKEN=<your-rtds-token>
```

## Related Skills

- [RTDS Connection](../rtds-connection/) — low-level RTDS connection reference
- [Custom Events](../../api/custom-events/) — submit custom events that appear in RTDS

---
name: purchase-to-pass-update
description: Event-driven workflow where in-store purchases trigger wallet pass updates. POS system emits custom events with named users, RTDS listener filters for purchase events, and updates pass points. Use when integrating POS systems with wallet passes, building loyalty programs, or implementing real-time pass updates.
---

# Purchase-to-Pass Update Workflow

This workflow demonstrates an event-driven integration where in-store purchases trigger real-time wallet pass updates. The system consists of two decoupled components: a POS system that emits custom events and an RTDS listener that processes events and updates wallet passes.

## Overview

When a customer makes an in-store purchase and provides their email address, the POS system correlates the email with a named user and emits a custom event. An RTDS listener running separately filters for these purchase events and updates the customer's wallet pass with earned points in real-time.

## Architecture

This workflow uses a decoupled, event-driven architecture:

1. **POS System Component**: Emits custom events when purchases occur
2. **RTDS Listener Component**: Continuously listens for purchase events and updates passes

The components operate independently, allowing the POS system to emit events without waiting for pass updates, and enabling the listener to process events asynchronously.

## Prerequisites

- POS system with Airship API access
- RTDS enabled for your Airship account
- RTDS access token configured in dashboard
- Wallet passes distributed to customers with external IDs
- Mapping system between named users and pass external IDs (CRM, database, or lookup service)
  - **Note**: The `named_user_id` may differ from the pass external ID - ensure your system can map between them
- Template ID for the wallet pass template

## Skills Required

- **[Custom Events](../../skills/api/custom-events/SKILL.md)** - Emit purchase events from POS system
- **[RTDS Connection](../../skills/rtds/rtds-connection/SKILL.md)** - Listen for custom events in real-time
- **[Update Wallet Pass](../../skills/wallet/update-wallet-pass/SKILL.md)** - Update pass points field

## Part A: POS System - Emit Purchase Event

### Step 1: Customer Makes Purchase

Customer completes an in-store purchase and provides their email address at checkout.

### Step 2: Correlate Email with Named User

The POS system correlates the email address with a named user ID. Common approaches:

- **CRM Lookup**: Query your CRM system using the email address to retrieve the named user ID
- **Hashed Email**: Use a consistent hashing algorithm to convert email to named user ID
- **Database Lookup**: Query your user database for the email-to-named-user mapping

**Example**: If your CRM stores `named_user_id` as `user_12345` for `customer@example.com`, retrieve that ID.

### Step 3: Emit Custom Event

The POS system emits a custom event with the purchase details:

```json
POST /api/custom-events
Authorization: Bearer <oauth_token>
X-UA-Appkey: <application_key>
Content-Type: application/json

[
  {
    "occurred": "2024-01-15T14:30:00Z",
    "user": {
      "named_user_id": "user_12345"
    },
    "body": {
      "name": "purchase_completed",
      "value": 89.99,
      "transaction": "pos-txn-abc123",
      "properties": {
        "points_earned": 90,
        "purchase_amount": 89.99,
        "transaction_id": "pos-txn-abc123",
        "store_location": "store-001",
        "pass_external_id": "pass-user-12345"
      }
    }
  }
]
```

**Key Fields**:
- `named_user_id`: The customer's named user ID (from Step 2)
- `name`: Event name must be lowercase (`purchase_completed`)
- `value`: Purchase amount (optional, numeric)
- `transaction`: Transaction ID for deduplication
- `properties.points_earned`: Points to add to the pass
- `properties.pass_external_id`: External ID of the wallet pass (optional, may differ from `named_user_id` - if not included, the RTDS listener will need to look it up)

**Response**:
```json
{
  "ok": true,
  "operationId": "ef625038-70a3-41f1-826f-57bc11dd625a"
}
```

## Part B: RTDS Listener - Process Events and Update Pass

### Step 4: Connect to RTDS with Custom Event Filter

The RTDS listener connects to the RTDS stream and filters specifically for `purchase_completed` custom events:

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
      "types": ["CUSTOM"],
      "predicates": [
        {
          "scope": ["body"],
          "key": "name",
          "value": {"equals": "purchase_completed"}
        }
      ]
    }
  ]
}
```

**Response**: Stream of NDJSON events:
```
{"id":"event-1","type":"CUSTOM","offset":"offset-1","user":{"named_user_id":"user_12345"},"body":{"name":"purchase_completed","properties":{"points_earned":90}},...}
```

### Step 5: Process Purchase Event

When a purchase event is received, extract the necessary data:

**Example RTDS Event Structure**:
```json
{
  "id": "event-abc123",
  "type": "CUSTOM",
  "occurred": "2024-01-15T14:30:00Z",
  "offset": "offset-abc123",
  "user": {
    "named_user_id": "user_12345"
  },
  "body": {
    "name": "purchase_completed",
    "value": 89.99,
    "transaction": "pos-txn-abc123",
    "properties": {
      "points_earned": 90,
      "purchase_amount": 89.99,
      "transaction_id": "pos-txn-abc123",
      "store_location": "store-001",
      "pass_external_id": "pass-user-12345"
    }
  }
}
```

**Extract**:
- `user.named_user_id`: `"user_12345"` (may differ from pass external ID)
- `body.properties.points_earned`: `90`
- `body.properties.pass_external_id`: `"loyalty-card-abc123"` (if included, may differ from named_user_id - in this example, `user_12345` maps to `loyalty-card-abc123`)
- `body.transaction`: `"pos-txn-abc123"` (for idempotency)

### Step 6: Map Named User to Pass External ID

**Important**: The `named_user_id` may not be the same as the pass external ID. The pass external ID can be obtained in one of these ways:

- **Option A**: Extract from event properties (if included in Step 3)
  - Use `body.properties.pass_external_id` directly from the event
  
- **Option B**: Query your CRM/database using `named_user_id` to get the pass external ID
  - Lookup the mapping between named user and pass external ID
  
- **Option C**: Use a consistent mapping rule (e.g., `pass-{named_user_id}`)
  - Only if your system uses a predictable naming convention
  
**Example Lookup**:
```python
# Pseudocode
# First check if pass_external_id is in event properties
if 'pass_external_id' in event['body']['properties']:
    pass_external_id = event['body']['properties']['pass_external_id']
    # Example: named_user_id="user_12345" -> pass_external_id="loyalty-card-abc123"
else:
    # Lookup from CRM/database using named_user_id
    pass_external_id = lookup_pass_external_id(named_user_id)
    # Returns: "loyalty-card-abc123" (may differ from named_user_id)
    # The lookup maps named_user_id to the actual pass external ID used when creating the pass
```

### Step 7: Update Wallet Pass Points

Update the wallet pass with the new points. If you need to calculate the total (current + earned), you may need to retrieve the current points first, or track points separately in your system.

**Update Pass**:
```json
PUT /pass/template/{templateId}/id/{pass_external_id}
Authorization: Basic <base64(app_key:master_secret)>
Content-Type: application/json

{
  "fields": {
    "points": {
      "value": "1,090",
      "changeMessage": "You earned %@ points! Your new balance is %@."
    }
  }
}
```

**Note**: Replace `{templateId}` with your actual template ID and `{pass_external_id}` with the external ID from Step 6.

**Response**:
```json
{
  "ticketId": 12345
}
```

The `ticketId` can be used to track the update operation status.

## Outcomes

- Purchase events emitted from POS system
- Real-time processing of purchase events via RTDS
- Wallet passes updated with earned points automatically
- Decoupled architecture allowing independent scaling
- Idempotent updates using transaction IDs

## Use Cases

- **Loyalty Programs**: Automatically update loyalty points on wallet passes when customers make purchases
- **POS Integration**: Integrate point-of-sale systems with wallet pass updates
- **Real-time Pass Updates**: Keep wallet passes synchronized with purchase activity
- **Multi-location Retail**: Update passes for purchases across multiple store locations
- **Event-driven Architecture**: Build decoupled systems that communicate via events

## Best Practices

1. **Store Offsets**: Always track the last processed RTDS offset for seamless reconnection
2. **Idempotency**: Use transaction IDs to prevent duplicate pass updates if events are reprocessed
3. **Error Handling**: Handle cases where:
   - Pass doesn't exist (404) - log and skip or create pass
   - RTDS disconnects - reconnect using stored offset
   - Invalid event data - log and skip
4. **Pass External ID Strategy**: Choose a consistent strategy for mapping named users to pass external IDs. Note that `named_user_id` may differ from the pass external ID - the external ID can be passed in event properties or looked up separately
5. **Points Calculation**: Decide whether to:
   - Track points separately in your system (recommended)
   - Retrieve current points before updating (requires additional API call)
   - Always send total points (simpler but requires external tracking)
6. **Filtering**: Use RTDS predicates to filter at the API level, reducing processing overhead
7. **Monitoring**: Monitor RTDS connection health and implement reconnection logic
8. **Transaction Deduplication**: Store processed transaction IDs to prevent duplicate processing

## Related Workflows

- **[RTDS Monitoring](../rtds-monitoring/SKILL.md)** - General RTDS monitoring workflow with reconnection handling
- **[Complete User Onboarding](../complete-user-onboarding/SKILL.md)** - Onboard users and distribute passes

## Additional Notes

### Points Calculation Example

If you need to calculate total points (current + earned):

```python
# Pseudocode
current_points = get_current_pass_points(pass_external_id)  # May require GET pass API
new_total = current_points + points_earned
update_pass_points(pass_external_id, new_total)
```

Alternatively, track points in your own system:

```python
# Pseudocode
current_points = database.get_user_points(named_user_id)
new_total = current_points + points_earned
database.update_user_points(named_user_id, new_total)
update_pass_points(pass_external_id, new_total)
```

### Reconnection Handling

If the RTDS connection drops, reconnect using the last processed offset:

```json
POST https://connect.urbanairship.com/api/events
Authorization: Bearer <rtds-access-token>
X-UA-Appkey: <app-key>
Accept: application/vnd.urbanairship+x-ndjson; version=3;
Content-Type: application/json

{
  "resume_offset": "offset-abc123",
  "filters": [
    {
      "types": ["CUSTOM"],
      "predicates": [
        {
          "scope": ["body"],
          "key": "name",
          "value": {"equals": "purchase_completed"}
        }
      ]
    }
  ]
}
```

This ensures no purchase events are missed during disconnection.

---
name: update-wallet-pass
description: Update fields on a wallet pass using an external ID. Use when updating pass information like values, labels, locations, or beacons for Apple Wallet or Google Pay passes.
metadata:
  category: wallet
---

# Skill: Update Wallet Pass

## Overview

This skill enables agents to update fields on a wallet pass using an external ID. You can update field values, labels, headers, locations, beacons, and other pass properties. Only include the fields you want to update in the request.

## API Endpoint

**Method**: `PUT`  
**Path**: `/pass/template/{templateId}/id/{passExternalId}`  
**Base URL**:
- US: `https://wallet-api.urbanairship.com/v1`
- EU: `https://wallet-api.asnapieu.com/v1`

**Path**: `/pass/template/{templateId}/id/{passExternalId}`

## Authentication

**Preferred**: OAuth 2.0 Bearer token  
**Fallback**: Basic Auth (`app_key:master_secret`) for environments not using OAuth

### OAuth (recommended)

1. Request a token from the OAuth endpoint for your region.
2. Use the token as `Authorization: Bearer <access_token>`.
3. Ensure token includes the `wpas` scope for pass operations.

OAuth token endpoints:
- US: `https://oauth2.asnapius.com/token`
- EU: `https://oauth2.asnapieu.com/token`

### Basic Auth (fallback)

If OAuth is not configured, use:
`Authorization: Basic <base64(app_key:master_secret)>`

## Request Headers

```
Api-Revision: 1.2
Accept: application/json
Content-Type: application/json
Authorization: Bearer <access_token>
```

If using fallback auth:
`Authorization: Basic <base64(app_key:master_secret)>`

## Request Schema

Provide only the fields you want to update. The request body supports partial updates.

### Update Pass Request

```json
{
  "fields": {
    "fieldName": {
      "value": "New Value",
      "label": "Field Label",
      "changeMessage": "Your pass has been updated"
    }
  },
  "headers": {
    "headerName": {
      "value": "Header Value",
      "label": "Header Label",
      "changeMessage": "Header updated"
    }
  },
  "locations": [
    {
      "latitude": 37.7749,
      "longitude": -122.4194,
      "relevantText": "Near San Francisco"
    }
  ],
  "beacons": [
    {
      "uuid": "550e8400-e29b-41d4-a716-446655440000",
      "relevantText": "Near beacon"
    }
  ]
}
```

### Required Path Parameters

- `templateId`: The ID of the template the pass was created from (string)
- `passExternalId`: The external ID assigned to the pass (string)

### Optional Request Fields

**Fields Object** (`fields`):
- Object mapping field names to field update objects
- Each field update object contains:
  - `value` (required): string - The new field value
  - `label` (optional): string - The field label/title
  - `changeMessage` (optional): string - Message shown when field updates (use `%@` for variables)

**Headers Object** (`headers`):
- Object mapping header names to header update objects
- Same structure as fields (value, label, changeMessage)

**Locations Array** (`locations`):
- Array of location objects (replaces all existing locations)
- Each location requires:
  - `latitude`: number
  - `longitude`: number
  - `relevantText`: string (optional) - Text shown when near location

**Beacons Array** (`beacons`):
- Array of beacon objects (Apple Wallet only, up to 10 beacons)
- Each beacon requires:
  - `uuid`: string - UUID of the iBeacon
  - `major`: integer - Major identifier of the beacon
  - `minor`: integer - Minor identifier of the beacon
  - `relevantText`: string - Text shown when near beacon

**Semantics Object** (`semantics`):
- Apple Wallet boarding pass semantics (object)

**Universal Links Object** (`universalLinks`):
- Object containing universal link key-value pairs

## Examples

See example files in the `examples/` directory:
- `update-pass-fields.json` - Update field values and labels
- `update-pass-locations.json` - Update pass locations

### Example 1: Update Field Values

```json
PUT /pass/template/123/id/pass-abc-123
{
  "fields": {
    "balance": {
      "value": "$150.00",
      "changeMessage": "Your balance has been updated to %@"
    },
    "memberName": {
      "value": "John Doe",
      "label": "Member"
    }
  }
}
```

### Example 2: Update Locations

```json
PUT /pass/template/123/id/pass-abc-123
{
  "locations": [
    {
      "latitude": 37.7749,
      "longitude": -122.4194,
      "relevantText": "Near Store Location"
    }
  ]
}
```

## Response Schema

### Success Response (200 OK)

```json
{
  "ticketId": 12345
}
```

The `ticketId` can be used to track the update operation status via the tickets API.

## Error Handling

### 400 Bad Request

Occurs when:
- Request body is malformed
- Invalid field values
- Missing required fields in nested objects

### 404 Not Found

Occurs when:
- Template ID does not exist
- Pass with the specified external ID does not exist

## Best Practices

1. **Partial Updates**: Only include fields you want to update - you don't need to send the entire pass object
2. **Locations Replacement**: Updating locations replaces all existing locations - include all locations you want to keep
3. **Change Messages**: Use `changeMessage` to notify pass holders when important fields update
4. **Field Labels**: Only provide `label` if you want to override the template's default label
5. **Beacon Limits**: Apple Wallet supports up to 10 beacons per pass

## Use Cases

1. **Update Pass Values**: Update field values like balance, points, or status
2. **Update Locations**: Add or replace pass locations for location-based notifications
3. **Update Beacons**: Add or update iBeacons for proximity-based pass relevance
4. **Update Headers**: Modify header information displayed on the pass
5. **Notify Users**: Use change messages to notify users when pass information changes

## Workflows Using This Skill

- **Purchase-to-Pass Update**: POS system emits purchase events → RTDS listener processes events → Updates wallet pass points
  - See [Workflow Guide](../../../docs/workflows.md#purchase-to-pass-update)

## Related Skills

None currently. This is the first wallet skill.

## Additional Resources

- [Wallet API Reference](https://docs.airship.com/developer/rest-api/wallet/)
- [Wallet OpenAPI Specification](https://www.airship.com/docs/openapi/wallet/spec.json)
- [Update Passes Guide](https://docs.airship.com/guides/wallet/user-guide/updating-passes/)

---
name: list-pipelines
metadata:
  category: api
description: List pipelines (automations) in Airship with filtering by trigger type, enabled status, and other criteria. Use when discovering automations, checking pipeline configurations, or finding pipelines triggered by specific events like Custom Events.
---

# Skill: List Pipelines

## Overview

This skill enables agents to list pipelines (automations) in Airship with support for filtering by trigger type, enabled status, and other criteria. Pipelines are automated message sequences that trigger based on events like Custom Events, tag changes, app opens, and more.

## API Endpoints

**Method**: `GET`  
**Path**: `/api/pipelines` or `/api/pipelines/filtered`  
**Base URL**: `https://go.urbanairship.com`  
**Full URLs**: 
- `https://go.urbanairship.com/api/pipelines`
- `https://go.urbanairship.com/api/pipelines/filtered`

## Authentication

**Required**: Bearer Token or OAuth2 Token with `pln` scope

**Headers**:
```
Authorization: Bearer <bearer_token>
X-UA-Appkey: <application_key>
Accept: application/vnd.urbanairship+json; version=3
```

## Request Parameters

### `/api/pipelines` Endpoint

- **`limit`** (integer, optional): Maximum number of results to return (page size). Recommended between 25-100 for performance. No default limit.
- **`enabled`** (boolean, optional): If `true`, returns only enabled pipelines. If `false` or omitted, returns all pipelines regardless of enabled state.
- **`offset`** (integer, optional): First result to return (for pagination). Default: 0.

### `/api/pipelines/filtered` Endpoint

All parameters from `/api/pipelines`, plus:

- **`triggers`** (string, optional): Filter by trigger type. Can specify multiple values. Valid enum values:
  - `TAG_ADDED`
  - `TAG_REMOVED`
  - `FIRST_REG`
  - `FIRST_OPT_IN`
  - `ACTIVITY`
  - `REGION_ENTERED`
  - `REGION_EXITED`
  - `CUSTOM_EVENT` - Filters for pipelines triggered by Custom Events
  - `SUBSCRIPTION_ADDED`
  - `SUBSCRIPTION_REMOVED`
- **`start`** (integer, optional): Non-negative zero-based index for pagination. Default: 0.
- **`started_date_mills`** (integer, optional): Filter pipelines started after this timestamp (milliseconds).
- **`prefix`** (string, optional): Search term used as prefix search on pipeline names.
- **`sort`** (string, optional): Field to sort by. Values: `name`, `started_date`. Default: `name`.
- **`order`** (string, optional): Sort order. Values: `asc`, `desc`. Default: `asc`.

## Response Schema

**Success (200 OK):**
```json
{
  "ok": true,
  "operation_id": "ef625038-70a3-41f1-826f-57bc11dd625a",
  "pipelines": [
    {
      "uid": "3987f98s-89s3-cx98-8z89-89adjkl29zds",
      "name": "Purchase Event Automation",
      "enabled": true,
      "status": "live",
      "creation_time": "2024-01-15T10:30:00Z",
      "last_modified_time": "2024-01-15T10:30:00Z",
      "immediate_trigger": {
        "custom_event": {
          "key": "name",
          "value": {
            "equals": "purchased"
          }
        }
      },
      "outcome": {
        "push": {
          "audience": "triggered",
          "device_types": [
            "ios",
            "android"
          ],
          "notification": {
            "alert": "Thank you for your purchase!"
          }
        }
      },
      "url": "https:\/\/go.urbanairship.com/api/pipelines/abc123-def456"
    }
  ],
  "total_count": 42,
  "next_page": "https:\/\/go.urbanairship.com/api/pipelines/filtered?start=20&limit=20",
  "prev_page": null
}
```

**Note**: The `immediate_trigger` field can be either a single object (when there's one trigger) or an array of objects (when there are multiple triggers). See the Trigger Types section for examples of both formats.

### Pipeline Object Fields

- **`uid`** (string): Unique pipeline identifier
- **`name`** (string): Pipeline name
- **`enabled`** (boolean): Whether pipeline is enabled
- **`status`** (string, read-only): Current pipeline status:
  - `pending`: Enabled but `activation_time` is in the future
  - `live`: Enabled and currently active
  - `completed`: `deactivation_time` has passed
  - `disabled`: Pipeline is disabled (`enabled: false`)
- **`creation_time`** (string, ISO 8601): When pipeline was created
- **`last_modified_time`** (string, ISO 8601): When pipeline was last modified
- **`immediate_trigger`** (object | array): Trigger configuration. Single object for one trigger, array of objects for multiple triggers (see Trigger Types below)
- **`outcome`** (object): What happens when pipeline triggers (push, email, etc.). May contain handlebars template syntax (e.g., `{{custom_event.properties.product_name}}`) for personalization.
- **`url`** (string): Pipeline resource URL

### Important Notes on Filtering

- **`enabled` filter**: The API supports filtering by `enabled=true` to get enabled pipelines. However, this does NOT guarantee "live" status. Enabled pipelines may be `pending` if `activation_time` is in the future.
- **`status` field**: The `status` field is read-only and calculated from `enabled`, `activation_time`, and `deactivation_time`. It cannot be used as a query parameter.
- **To get only "live" pipelines**: Filter by `enabled=true` via API, then filter client-side by `status === "live"` (or check that current time is between `activation_time` and `deactivation_time`).

## Trigger Types

Pipelines can be triggered by various event types. The `immediate_trigger` field contains the trigger configuration.

**Important**: The `immediate_trigger` field can be either a single object or an array of objects. When a pipeline has multiple triggers, the API returns an array. Always check the type before accessing trigger properties to avoid errors (e.g., use `Array.isArray()` or similar type checking).

### Custom Event Trigger

```json
{
  "immediate_trigger": {
    "custom_event": {
      "key": "name",
      "value": {
        "equals": "purchased"
      }
    }
  }
}
```

Or with complex selectors:

```json
{
  "immediate_trigger": {
    "custom_event": {
      "and": [
        {
          "key": "name",
          "value": {
            "equals": "purchased"
          }
        },
        {
          "key": "value",
          "scope": "properties",
          "value": {
            "greater_than": 50
          }
        }
      ]
    }
  }
}
```

### Multiple Triggers Example

When a pipeline has multiple triggers, `immediate_trigger` is returned as an array:

```json
{
  "immediate_trigger": [
    {
      "custom_event": {
        "key": "name",
        "value": {
          "equals": "purchased"
        }
      }
    },
    {
      "tag_added": {
        "tag": "vip"
      }
    }
  ]
}
```

See `examples/multiple-triggers.json` for a complete response example.

### Other Trigger Types

- **Tag triggers**: `{"tag_added": {"tag": "vip"}}` or `{"tag_removed": "customer"}`
- **Simple events**: `"open"`, `"first_open"`, `"first_opt_in"`, `"double_opt_in"`
- **Region triggers**: `{"region_entered": {...}}` or `{"region_exited": {...}}`
- **Subscription triggers**: `{"subscription_added": "list_name"}` or `{"subscription_removed": "list_name"}`

## Examples

### Example 1: List All Pipelines

```
GET /api/pipelines?limit=20
Authorization: Bearer <token>
Accept: application/vnd.urbanairship+json; version=3
```

### Example 2: List Pipelines with Custom Event Triggers

```
GET /api/pipelines/filtered?triggers=CUSTOM_EVENT&enabled=true&limit=50
Authorization: Bearer <token>
Accept: application/vnd.urbanairship+json; version=3
```

### Example 3: List Enabled Pipelines with Pagination

```
GET /api/pipelines/filtered?enabled=true&limit=25&start=0&sort=name&order=asc
Authorization: Bearer <token>
Accept: application/vnd.urbanairship+json; version=3
```

### Example 4: Search Pipelines by Name Prefix

```
GET /api/pipelines/filtered?prefix=purchase&limit=20
Authorization: Bearer <token>
Accept: application/vnd.urbanairship+json; version=3
```

## Common Error Codes

- **401**: Unauthorized - Invalid or missing authentication
- **403**: Forbidden - Insufficient permissions (missing `pln` scope)
- **406**: Not Acceptable - Missing or invalid API version header

## Best Practices

1. **Use filtered endpoint for trigger-specific queries**: Use `/api/pipelines/filtered` with `triggers` parameter when looking for specific trigger types
2. **Set appropriate limits**: Use limits between 25-100 for optimal performance
3. **Handle pagination**: Check `next_page` and `prev_page` links or use `start`/`limit` parameters
4. **Filter by enabled status**: Use `enabled=true` to focus on active pipelines, but remember this includes `pending` pipelines
5. **Client-side status filtering**: If you need only "live" pipelines, filter client-side by `status === "live"` after fetching
6. **Use prefix search**: Use `prefix` parameter for name-based searches instead of fetching all pipelines
7. **Handle both trigger formats**: The `immediate_trigger` field can be a single object or an array. Always check the type (using `Array.isArray()` or similar) before accessing trigger properties to avoid AttributeError when encountering pipelines with multiple triggers

## Use Cases

- **Discover automations**: Find all pipelines configured in your account
- **Find Custom Event triggers**: List pipelines triggered by Custom Events
- **Audit pipeline configurations**: Review pipeline settings and triggers
- **Workflow discovery**: Identify pipelines for testing or documentation
- **Integration planning**: Understand automation setup before integration

## Workflows Using This Skill

- **Custom Event Automation Discovery**: List pipelines triggered by Custom Events and generate sample events
  - See [Workflow Guide](../../../workflows/custom-event-automation-discovery/SKILL.md)

## Related Documentation

- [Pipelines API Reference](https://docs.airship.com/developer/rest-api/ua/operations/automation/)
- [Pipeline Objects Schema](https://docs.airship.com/developer/rest-api/ua/schemas/pipeline-objects/)
- [OpenAPI Specification](https://docs.airship.com/developer/rest-api/)

## Function Calling Schema (OpenAI Format)

```json
{
  "name": "list_pipelines",
  "description": "List pipelines (automations) in Airship with filtering by trigger type, enabled status, and other criteria",
  "parameters": {
    "type": "object",
    "properties": {
      "endpoint": {
        "type": "string",
        "enum": ["/api/pipelines", "/api/pipelines/filtered"],
        "description": "Endpoint to use. Use filtered for trigger-specific queries."
      },
      "triggers": {
        "type": "array",
        "items": {
          "type": "string",
          "enum": ["TAG_ADDED", "TAG_REMOVED", "FIRST_REG", "FIRST_OPT_IN", "ACTIVITY", "REGION_ENTERED", "REGION_EXITED", "CUSTOM_EVENT", "SUBSCRIPTION_ADDED", "SUBSCRIPTION_REMOVED"]
        },
        "description": "Filter by trigger types. Only available with filtered endpoint."
      },
      "enabled": {
        "type": "boolean",
        "description": "Filter by enabled status. If true, returns only enabled pipelines."
      },
      "limit": {
        "type": "integer",
        "minimum": 1,
        "description": "Maximum number of results (page size). Recommended 25-100."
      },
      "start": {
        "type": "integer",
        "minimum": 0,
        "description": "Starting index for pagination. Only available with filtered endpoint."
      },
      "offset": {
        "type": "integer",
        "minimum": 0,
        "description": "First result to return. Only available with /api/pipelines endpoint."
      },
      "prefix": {
        "type": "string",
        "description": "Search term for prefix search on pipeline names. Only available with filtered endpoint."
      },
      "sort": {
        "type": "string",
        "enum": ["name", "started_date"],
        "description": "Field to sort by. Only available with filtered endpoint."
      },
      "order": {
        "type": "string",
        "enum": ["asc", "desc"],
        "description": "Sort order. Only available with filtered endpoint."
      }
    },
    "required": []
  }
}
```

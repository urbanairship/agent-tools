---
name: custom-event-automation-discovery
description: Discover all automations (pipelines) triggered by Custom Events and create sample Custom Events that would trigger them. This workflow extracts trigger criteria and handlebars template requirements to generate complete test events. Use when testing automations, documenting event requirements, or understanding pipeline configurations.
---

# Custom Event Automation Discovery Workflow

This workflow discovers all pipelines (automations) triggered by Custom Events and generates sample Custom Events that match both the trigger criteria and any handlebars template requirements in the pipeline outcomes.

## Prerequisites

- Airship account with API access
- Bearer token with `pln` scope (for pipelines API)
- Bearer token with `evt` scope (for custom events API)
- Test user identifier (named_user_id or channel_id) for submitting sample events

## Skills Required

- [Pipelines](../../../skills/api/list-pipelines/SKILL.md) - List and filter pipelines
- [Custom Events](../../../skills/api/custom-events/SKILL.md) - Submit custom events

## Step 1: List Pipelines with Custom Event Triggers

Use the filtered pipelines endpoint to get all pipelines triggered by Custom Events:

```json
GET /api/pipelines/filtered?triggers=CUSTOM_EVENT&enabled=true&limit=50
Authorization: Bearer <token>
Accept: application/vnd.urbanairship+json; version=3
```

**Optional filtering:**
- Add `enabled=true` to get only enabled pipelines (note: this includes `pending` pipelines if `activation_time` is in the future)
- To get only currently active ("live") pipelines: filter by `enabled=true` via API, then filter client-side by checking `status === "live"` or verifying current time is between `activation_time` and `deactivation_time`

**Handle pagination:**
- Check `next_page` link in response to get additional pages
- Or use `start` and `limit` parameters for manual pagination

**Response example:**
```json
{
  "ok": true,
  "pipelines": [
    {
      "uid": "abc123-def456-ghi789",
      "name": "Purchase Event Automation",
      "enabled": true,
      "status": "live",
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
          "device_types": ["ios", "android"],
          "notification": {
            "alert": "Thank you for purchasing {{custom_event.properties.product_name}}! Your order total was ${{custom_event.value}}."
          }
        }
      }
    }
  ],
  "total_count": 1,
  "next_page": null
}
```

## Step 2: Extract Custom Event Criteria from Triggers

For each pipeline, examine the `immediate_trigger.custom_event` selector to extract matching criteria.

### Simple Selector

If the trigger is a simple selector:

```json
{
  "custom_event": {
    "key": "name",
    "value": {
      "equals": "purchased"
    }
  }
}
```

**Extract:**
- Event name: `"purchased"` (from `key: "name"` with `value.equals`)

### Complex Selector with AND

If the trigger uses AND logic:

```json
{
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
        "value": {
          "greater_than": 50
        }
      }
    ]
  }
}
```

**Extract:**
- Event name: `"purchased"`
- Value constraint: must be greater than 50

### Selector with Property Constraints

If the trigger checks properties:

```json
{
  "custom_event": {
    "and": [
      {
        "key": "name",
        "value": {
          "equals": "purchased"
        }
      },
      {
        "key": "category",
        "scope": "properties",
        "value": {
          "equals": "electronics"
        }
      }
    ]
  }
}
```

**Extract:**
- Event name: `"purchased"`
- Property constraint: `properties.category` must equal `"electronics"`

### Handling OR and NOT Operators

For OR selectors, extract all possible values. For NOT selectors, note the exclusion criteria.

## Step 2a: Extract Handlebars References from Pipeline Outcome

Examine the pipeline's `outcome` object for handlebars template syntax. Look for handlebars patterns in:

- **Push notifications**: `notification.alert`
- **Email**: `notification.email.subject`, `notification.email.html_body`, `notification.email.plaintext_body`
- **SMS**: `notification.sms`
- **Any other templated fields** in the outcome

### Handlebars Pattern Examples

Extract references matching these patterns:

- `{{custom_event.properties.<property_name>}}` - Property reference
- `{{custom_event.value}}` - Event value reference
- `{{custom_event.name}}` - Event name reference
- `{{custom_event.<field>}}` - Other field references
- `{{custom_event.properties.product.name}}` - Nested property access

### Example: Extract from Notification Alert

Given this outcome:
```json
{
  "outcome": {
    "push": {
      "notification": {
        "alert": "Thank you for purchasing {{custom_event.properties.product_name}}! Your order total was ${{custom_event.value}}."
      }
    }
  }
}
```

**Extract handlebars references:**
- `{{custom_event.properties.product_name}}` → requires `properties.product_name`
- `{{custom_event.value}}` → requires `value` field

### Example: Extract from Email Body

Given this outcome:
```json
{
  "outcome": {
    "push": {
      "notification": {
        "email": {
          "subject": "Order Confirmation",
          "html_body": "<h1>Thank you, {{custom_event.properties.customer_name}}!</h1><p>Your order {{custom_event.properties.order_id}} is confirmed.</p>"
        }
      }
    }
  }
}
```

**Extract handlebars references:**
- `{{custom_event.properties.customer_name}}` → requires `properties.customer_name`
- `{{custom_event.properties.order_id}}` → requires `properties.order_id`

## Step 3: Generate Sample Custom Events

For each pipeline, create a sample Custom Event that:
1. Matches the trigger criteria (from Step 2)
2. Includes properties needed for handlebars substitution (from Step 2a)

### Example 1: Simple Trigger with Handlebars

**Pipeline trigger:**
```json
{
  "custom_event": {
    "key": "name",
    "value": {
      "equals": "purchased"
    }
  }
}
```

**Pipeline outcome:**
```json
{
  "notification": {
    "alert": "Thank you for purchasing {{custom_event.properties.product_name}}! Total: ${{custom_event.value}}."
  }
}
```

**Generated sample event:**
```json
[{
  "user": {
    "named_user_id": "test-user-123"
  },
  "body": {
    "name": "purchased",
    "value": 99.99,
    "properties": {
      "product_name": "Sample Product"
    }
  }
}]
```

**Why each field:**
- `name: "purchased"` - Matches trigger requirement
- `value: 99.99` - Referenced in handlebars (`{{custom_event.value}}`)
- `properties.product_name` - Referenced in handlebars (`{{custom_event.properties.product_name}}`)

### Example 2: Complex Trigger with Multiple Properties

**Pipeline trigger:**
```json
{
  "custom_event": {
    "and": [
      {
        "key": "name",
        "value": {
          "equals": "purchased"
        }
      },
      {
        "key": "category",
        "scope": "properties",
        "value": {
          "equals": "electronics"
        }
      },
      {
        "key": "value",
        "value": {
          "greater_than": 50
        }
      }
    ]
  }
}
```

**Pipeline outcome:**
```json
{
  "notification": {
    "alert": "Your {{custom_event.properties.category}} purchase of ${{custom_event.value}} is confirmed!"
  }
}
```

**Generated sample event:**
```json
[{
  "user": {
    "named_user_id": "test-user-123"
  },
  "body": {
    "name": "purchased",
    "value": 75.00,
    "properties": {
      "category": "electronics"
    }
  }
}]
```

**Why each field:**
- `name: "purchased"` - Matches trigger requirement
- `value: 75.00` - Matches trigger constraint (`greater_than: 50`) AND referenced in handlebars
- `properties.category: "electronics"` - Matches trigger constraint AND referenced in handlebars

### Example 3: Nested Properties

**Pipeline outcome:**
```json
{
  "notification": {
    "alert": "Product {{custom_event.properties.product.name}} from {{custom_event.properties.product.brand}} is ready!"
  }
}
```

**Generated sample event:**
```json
[{
  "user": {
    "named_user_id": "test-user-123"
  },
  "body": {
    "name": "product_ready",
    "properties": {
      "product": {
        "name": "Sample Product",
        "brand": "Sample Brand"
      }
    }
  }
}]
```

## Step 4: Submit Sample Custom Events

Use the custom-events skill to submit the generated events:

```json
POST /api/custom-events
Authorization: Bearer <token>
X-UA-Appkey: <application_key>
Accept: application/vnd.urbanairship+json; version=3
Content-Type: application/json

[
  {
    "user": {
      "named_user_id": "test-user-123"
    },
    "body": {
      "name": "purchased",
      "value": 99.99,
      "properties": {
        "product_name": "Sample Product"
      }
    }
  }
]
```

**Best practices:**
- Submit events as an array (up to 100 events per request)
- Use a test user identifier that won't affect real users
- Include `occurred` timestamp if testing historical scenarios
- Set `unique_id` if testing sequence triggers to prevent duplicate sends

## Complete Workflow Example

### Input: List of Pipelines

```json
{
  "pipelines": [
    {
      "name": "Purchase Automation",
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
          "notification": {
            "alert": "Thanks for buying {{custom_event.properties.product_name}}!"
          }
        }
      }
    }
  ]
}
```

### Output: Generated Sample Events

```json
[
  {
    "user": {
      "named_user_id": "test-user-123"
    },
    "body": {
      "name": "purchased",
      "properties": {
        "product_name": "Sample Product"
      }
    }
  }
]
```

### Result

When submitted, this event will:
1. ✅ Trigger the "Purchase Automation" pipeline (matches trigger criteria)
2. ✅ Render the notification as: "Thanks for buying Sample Product!" (handlebars resolve correctly)

## Outcomes

- All pipelines with Custom Event triggers identified
- Trigger criteria extracted and documented
- Handlebars template requirements identified
- Sample Custom Events generated that match both trigger criteria and template needs
- Sample events submitted to test automations

## Use Cases

- **Testing automations**: Generate test events to verify pipeline behavior
- **Documentation**: Document what events trigger which automations
- **Integration planning**: Understand event requirements before implementation
- **Debugging**: Create sample events to troubleshoot pipeline issues
- **Onboarding**: Help developers understand automation setup

## Best Practices

1. **Use test users**: Always use test named_user_id or channel_id when submitting sample events
2. **Extract all criteria**: Include both trigger constraints AND handlebars references
3. **Handle complex selectors**: Properly parse AND/OR/NOT operators in triggers
4. **Check nested properties**: Look for nested property access in handlebars (e.g., `properties.product.name`)
5. **Use meaningful sample values**: Choose sample property values that demonstrate the templating
6. **Handle pagination**: Process all pipelines across multiple pages
7. **Filter by status**: Consider filtering to only "live" pipelines if testing active automations
8. **Document findings**: Keep track of which events trigger which pipelines

## Related Workflows

- [Complete User Onboarding](../complete-user-onboarding/SKILL.md) - Uses custom events in a multi-step workflow

## Troubleshooting

**Issue**: Sample event doesn't trigger pipeline
- **Check**: Verify event name matches trigger criteria exactly (case-sensitive, lowercase only)
- **Check**: Ensure value constraints are met (e.g., `greater_than`, `equals`)
- **Check**: Verify property constraints match (if trigger checks properties)

**Issue**: Handlebars don't render correctly
- **Check**: Ensure all referenced properties are included in the event
- **Check**: Verify property paths match handlebars references (e.g., `properties.product_name` vs `properties.product.name`)
- **Check**: Ensure nested properties are structured correctly

**Issue**: Pipeline not found in filtered results
- **Check**: Verify pipeline has `enabled: true` if using `enabled=true` filter
- **Check**: Ensure trigger type is correctly identified as `CUSTOM_EVENT`
- **Check**: Pipeline may be on a different page (handle pagination)

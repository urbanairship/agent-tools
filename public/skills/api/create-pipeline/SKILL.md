---
name: create-pipeline
metadata:
  category: api
description: Create pipelines (automations) in Airship that trigger automated messages based on events like Custom Events, tag changes, app opens, and more. Use when setting up automated messaging workflows, creating event-triggered notifications, or building personalized automation sequences.
---

# Skill: Create Pipeline

## Overview

This skill enables agents to create pipelines (automations) in Airship that automatically send messages when specific events occur. Pipelines can be triggered by Custom Events, tag changes, app opens, region entry/exit, and other user behaviors. Messages can be personalized using handlebars templating to access data from the triggering event.

## API Endpoint

**Method**: `POST`  
**Path**: `/api/pipelines`  
**Base URL**: `https://go.urbanairship.com`  
**Full URL**: `https://go.urbanairship.com/api/pipelines`

## Authentication

**Required**: Bearer Token, Basic Auth, or OAuth2 Token with `pln` scope

**Headers**:
```
Authorization: Bearer <bearer_token> (or Basic <credentials>)
Accept: application/vnd.urbanairship+json; version=3
Content-Type: application/json
```

## Request Schema

The request body can be either:
1. A single Pipeline Object
2. An array of Pipeline Objects (1-100 items)

### Pipeline Object Schema

```json
{
  "name": "Pipeline Name",  // Optional: Descriptive name
  "enabled": true,  // Required: Whether pipeline is active
  "immediate_trigger": {
    // Required (or historical_trigger): Event that triggers the pipeline
  },
  "outcome": {
    // Required: What happens when pipeline triggers
  },
  "timing": {
    // Optional: When to send messages
  },
  "constraint": [
    // Optional: Rate limiting constraints
  ],
  "condition": [
    // Optional: Additional conditions
  ],
  "activation_time": "2024-01-15T10:00:00Z",  // Optional: When pipeline becomes active
  "deactivation_time": "2024-12-31T23:59:59Z"  // Optional: When pipeline becomes inactive
}
```

### Immediate Trigger

At least one of `immediate_trigger` or `historical_trigger` must be provided.

#### Custom Event Trigger

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

**Complex Custom Event Selector with AND:**
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
          "value": {
            "greater_than": 50
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
}
```

**Other Trigger Types:**
- Tag triggers: `{"tag_added": {"tag": "vip"}}` or `{"tag_removed": "customer"}`
- Simple events: `"open"`, `"first_open"`, `"first_opt_in"`, `"double_opt_in"`
- Region triggers: `{"region_entered": {...}}` or `{"region_exited": {...}}`
- Subscription triggers: `{"subscription_added": "list_name"}` or `{"subscription_removed": "list_name"}`

### Outcome Object

The `outcome` must contain a `push` object where `audience` is set to `"triggered"`.

```json
{
  "outcome": {
    "push": {
      "audience": "triggered",  // Required: Must be "triggered"
      "device_types": ["ios", "android", "web", "email", "sms"],
      "notification": {
        "alert": "Message text"
      },
      "message": {
        // Optional: Message Center content
      }
    }
  }
}
```

### Personalization with Handlebars

Pipelines support handlebars templating to personalize messages using data from the triggering Custom Event.

**Available Handlebars Variables:**
- `{{custom_event.name}}` - The Custom Event name
- `{{custom_event.value}}` - The Custom Event numeric value
- `{{custom_event.properties.field_name}}` - Access Custom Event properties
- `{{custom_event.properties.nested.field}}` - Access nested properties

**Example Personalized Notification:**
```json
{
  "notification": {
    "alert": "Thank you for purchasing {{custom_event.properties.product_name}}! Your order total was ${{custom_event.value}}."
  }
}
```

**Example Personalized Message Center:**
```json
{
  "message": {
    "title": "Order Confirmation - {{custom_event.properties.product_name}}",
    "body": "<html><body><h1>Thank you for your purchase!</h1><p>Product: {{custom_event.properties.product_name}}</p><p>Total: ${{custom_event.value}}</p><p>Order ID: {{custom_event.properties.order_id}}</p></body></html>",
    "content_type": "text/html"
  }
}
```

### Notification Object

```json
{
  "notification": {
    "alert": "Default alert message",
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

### Message Center Object

```json
{
  "message": {
    "title": "Message Title",
    "body": "<html><body><h1>Rich Content</h1></body></html>",
    "content_type": "text/html"  // Optional, defaults to "text/html"
  }
}
```

### Timing Object

```json
{
  "timing": {
    "delay": {
      "seconds": 60  // Delay in seconds before sending
    },
    "schedule": {
      "type": "local",  // or "utc"
      "miss_behavior": "wait",  // or "cancel"
      "dayparts": [
        {
          "days_of_week": ["monday", "tuesday", "wednesday", "thursday", "friday"],
          "allowed_times": [
            {
              "start": "09:00:00",
              "end": "17:00:00",
              "preferred": "10:00:00"
            }
          ]
        }
      ]
    }
  }
}
```

### Constraint Object

Rate limiting constraints:

```json
{
  "constraint": [
    {
      "rate": {
        "pushes": 3,
        "days": 7
      }
    },
    {
      "rate": {
        "pushes": 1,
        "lifetimes": 1
      }
    }
  ]
}
```

## Response Schema

**Success (201 Created):**
```json
{
  "ok": true,
  "operation_id": "ef625038-70a3-41f1-826f-57bc11dd625a",
  "pipeline_urls": ["https:\/\/go.urbanairship.com/api/pipelines/4d3ff1fd-9ce6-5ea4-5dc9-5ccbd38597f4"]
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
- **403**: Forbidden - Insufficient permissions (missing `pln` scope)
- **406**: Not Acceptable - Missing or invalid API version header
- **409**: Conflict - Application has exceeded maximum number of active or total pipelines
- **413**: Payload Too Large - Request exceeds 5 MiB limit

## Examples

### Example 1: Simple Custom Event Trigger with Personalized Push

```json
{
  "name": "Purchase Confirmation",
  "enabled": true,
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
```

### Example 2: Custom Event Trigger with Push and Message Center (Both Personalized)

```json
{
  "name": "Order Confirmation Automation",
  "enabled": true,
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
        "alert": "Your order for {{custom_event.properties.product_name}} is confirmed!"
      },
      "message": {
        "title": "Order Confirmation - {{custom_event.properties.product_name}}",
        "body": "<html><body><h1>Thank you for your purchase!</h1><p><strong>Product:</strong> {{custom_event.properties.product_name}}</p><p><strong>Total:</strong> ${{custom_event.value}}</p><p><strong>Order ID:</strong> {{custom_event.properties.order_id}}</p><p><strong>Estimated Delivery:</strong> {{custom_event.properties.delivery_date}}</p></body></html>",
        "content_type": "text/html"
      }
    }
  }
}
```

### Example 3: Custom Event Trigger with Delay and Personalization

```json
{
  "name": "Delayed Purchase Follow-up",
  "enabled": true,
  "immediate_trigger": {
    "custom_event": {
      "key": "name",
      "value": {
        "equals": "purchased"
      }
    }
  },
  "timing": {
    "delay": {
      "seconds": 3600
    }
  },
  "outcome": {
    "push": {
      "audience": "triggered",
      "device_types": ["ios", "android"],
      "notification": {
        "alert": "How are you enjoying {{custom_event.properties.product_name}}? We'd love your feedback!"
      }
    }
  }
}
```

### Example 4: Custom Event Trigger with Constraints

```json
{
  "name": "Weekly Purchase Summary",
  "enabled": true,
  "immediate_trigger": {
    "custom_event": {
      "key": "name",
      "value": {
        "equals": "purchased"
      }
    }
  },
  "constraint": [
    {
      "rate": {
        "pushes": 1,
        "days": 7
      }
    }
  ],
  "outcome": {
    "push": {
      "audience": "triggered",
      "device_types": ["ios", "android"],
      "notification": {
        "alert": "You've made {{custom_event.properties.purchase_count}} purchases this week!"
      }
    }
  }
}
```

### Example 5: Complex Custom Event Trigger with Multiple Conditions

```json
{
  "name": "High-Value Purchase Automation",
  "enabled": true,
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
          "value": {
            "greater_than": 100
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
  },
  "outcome": {
    "push": {
      "audience": "triggered",
      "device_types": ["ios", "android", "email"],
      "notification": {
        "alert": "Thank you for your {{custom_event.properties.category}} purchase!",
        "email": {
          "subject": "Thank you for your ${{custom_event.value}} purchase!",
          "html_body": "<html><body><h1>Thank you!</h1><p>Your {{custom_event.properties.product_name}} order is being processed.</p></body></html>",
          "plaintext_body": "Thank you! Your {{custom_event.properties.product_name}} order is being processed.",
          "message_type": "transactional"
        }
      },
      "message": {
        "title": "Premium Purchase Confirmation",
        "body": "<html><body><h1>Thank you for your premium purchase!</h1><p><strong>Product:</strong> {{custom_event.properties.product_name}}</p><p><strong>Category:</strong> {{custom_event.properties.category}}</p><p><strong>Total:</strong> ${{custom_event.value}}</p><p>As a valued customer, you'll receive priority support for this order.</p></body></html>",
        "content_type": "text/html"
      }
    }
  }
}
```

## Validation Endpoint

Before creating a pipeline, you can validate the payload:

**Endpoint**: `POST /api/pipelines/validate`  
**Same payload format** as `/api/pipelines`  
**Response**: `200 OK` with `{"ok": true}` if valid, `400` with error details if invalid

## Personalization Best Practices

1. **Use Custom Event properties**: Reference properties that exist in the triggering Custom Event
2. **Provide fallbacks**: Consider what happens if a property is missing (handlebars will render empty string)
3. **Test with sample events**: Ensure handlebars resolve correctly with actual Custom Event data
4. **Document required properties**: List which Custom Event properties are needed for the pipeline to work correctly
5. **Use in both notification and message**: Personalize both push notification alerts and Message Center content for consistency
6. **Access nested properties**: Use dot notation for nested properties (e.g., `{{custom_event.properties.product.name}}`)
7. **Use event value**: Reference `{{custom_event.value}}` for numeric values in messages

## Best Practices

1. **Always validate first**: Use `/api/pipelines/validate` before creating to catch errors early
2. **Use descriptive names**: Provide clear pipeline names for easier management
3. **Set appropriate constraints**: Use rate limiting to avoid overwhelming users
4. **Test trigger conditions**: Ensure Custom Event triggers match your event structure
5. **Handle missing data**: Consider handlebars behavior when properties might be missing
6. **Use timing wisely**: Add delays or schedules to improve user experience
7. **Monitor pipeline limits**: Check `/api/pipelines/limits` to avoid hitting account limits
8. **Enable/disable appropriately**: Use `enabled: false` to disable without deleting

## Limits

- Maximum payload size: 5 MiB
- Maximum array size: 100 pipeline objects per request
- Pipeline limits: Varies by plan (check `/api/pipelines/limits` endpoint)
- Rate limits: Varies by plan (check with Airship Support)

## Workflows Using This Skill

- **Create Custom Event Automation**: Create an automation triggered by Custom Events with personalized push and Message Center
  - See [Workflow Guide](../../../workflows/create-custom-event-automation/SKILL.md)

## Related Documentation

- [Pipelines API Reference](https://docs.airship.com/developer/rest-api/ua/operations/automation/)
- [Pipeline Objects Schema](https://docs.airship.com/developer/rest-api/ua/schemas/pipeline-objects/)
- [Custom Event Triggers](https://docs.airship.com/developer/rest-api/ua/schemas/pipeline-objects/#custom-event-selector)
- [Handlebars Templating](https://docs.airship.com/developer/rest-api/ua/schemas/handlebars/)
- [OpenAPI Specification](https://docs.airship.com/developer/rest-api/)

## Function Calling Schema (OpenAI Format)

```json
{
  "name": "create_pipeline",
  "description": "Create a pipeline (automation) in Airship that triggers automated messages based on events. Supports personalization using handlebars templating to access Custom Event data.",
  "parameters": {
    "type": "object",
    "properties": {
      "name": {
        "type": "string",
        "description": "Descriptive name for the pipeline"
      },
      "enabled": {
        "type": "boolean",
        "description": "Whether the pipeline is active (required)"
      },
      "immediate_trigger": {
        "type": "object",
        "description": "Event that triggers the pipeline. Must include custom_event, tag_added, tag_removed, open, or other trigger types."
      },
      "outcome": {
        "type": "object",
        "description": "What happens when pipeline triggers. Must include push object with audience set to 'triggered'.",
        "properties": {
          "push": {
            "type": "object",
            "description": "Push notification configuration",
            "properties": {
              "audience": {
                "type": "string",
                "enum": ["triggered"],
                "description": "Must be 'triggered' for pipelines"
              },
              "device_types": {
                "type": "array",
                "items": {
                  "type": "string",
                  "enum": ["ios", "android", "web", "email", "sms", "amazon"]
                },
                "description": "Target device platforms"
              },
              "notification": {
                "type": "object",
                "description": "Notification content. Supports handlebars templating (e.g., {{custom_event.properties.field_name}})"
              },
              "message": {
                "type": "object",
                "description": "Message Center content. Supports handlebars templating.",
                "properties": {
                  "title": {"type": "string"},
                  "body": {"type": "string"},
                  "content_type": {"type": "string", "default": "text/html"}
                }
              }
            },
            "required": ["audience", "device_types"]
          }
        },
        "required": ["push"]
      },
      "timing": {
        "type": "object",
        "description": "Optional timing configuration",
        "properties": {
          "delay": {
            "type": "object",
            "properties": {
              "seconds": {"type": "integer", "minimum": 1}
            }
          }
        }
      },
      "constraint": {
        "type": "array",
        "description": "Optional rate limiting constraints",
        "maxItems": 3
      },
      "activation_time": {
        "type": "string",
        "format": "date-time",
        "description": "Optional datetime when pipeline becomes active"
      },
      "deactivation_time": {
        "type": "string",
        "format": "date-time",
        "description": "Optional datetime when pipeline becomes inactive"
      }
    },
    "required": ["enabled", "outcome"]
  }
}
```

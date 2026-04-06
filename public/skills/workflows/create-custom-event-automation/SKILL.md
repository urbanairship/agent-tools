---
name: create-custom-event-automation
description: Create an automation (pipeline) triggered by Custom Events that sends personalized push notifications and Message Center messages. The messages use handlebars templating to access Custom Event properties, value, and name for personalization. Use when setting up event-triggered messaging, creating personalized automation sequences, or building Custom Event-driven workflows.
---

# Create Custom Event Automation Workflow

This workflow demonstrates creating a pipeline (automation) that triggers when a Custom Event occurs, sending personalized push notifications and Message Center messages using data from the triggering Custom Event.

## Prerequisites

- Airship account with API access
- OAuth token with `pln` scope (for pipelines API)
- Custom Event name and structure defined
- Understanding of which Custom Event properties will be available for personalization

## Skills Required

- [Create Pipeline](../../../skills/api/create-pipeline/SKILL.md)

## Step 1: Define Custom Event Trigger Criteria

Identify the Custom Event that should trigger the automation. Determine the event name and any conditions (e.g., event value thresholds, property values).

**Example**: Trigger on `purchased` events where the value is greater than $50:

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
        }
      ]
    }
  }
}
```

**Simple trigger** (event name only):

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

## Step 2: Identify Custom Event Properties for Personalization

Review your Custom Event structure to identify which properties will be available for personalization. Common properties might include:
- `product_name` - Product purchased
- `order_id` - Order identifier
- `category` - Product category
- `delivery_date` - Estimated delivery date
- `customer_name` - Customer name
- Any other custom properties in your event

**Example Custom Event structure**:
```json
{
  "body": {
    "name": "purchased",
    "value": 99.99,
    "properties": {
      "product_name": "Wireless Headphones",
      "order_id": "ORD-12345",
      "category": "electronics",
      "delivery_date": "2024-01-20"
    }
  }
}
```

## Step 3: Create Personalized Push Notification Content

Design the push notification alert using handlebars templating to access Custom Event data.

**Handlebars syntax**:
- `{{custom_event.name}}` - Event name
- `{{custom_event.value}}` - Event numeric value
- `{{custom_event.properties.field_name}}` - Property value
- `{{custom_event.properties.nested.field}}` - Nested property

**Example personalized notification**:

```json
{
  "notification": {
    "alert": "Thank you for purchasing {{custom_event.properties.product_name}}! Your order total was ${{custom_event.value}}."
  }
}
```

**Multi-platform personalized notification**:

```json
{
  "notification": {
    "alert": "Thank you for your purchase!",
    "ios": {
      "alert": "Thank you for purchasing {{custom_event.properties.product_name}}!"
    },
    "android": {
      "alert": "Order confirmed: {{custom_event.properties.product_name}} - ${{custom_event.value}}",
      "title": "Purchase Confirmation"
    },
    "email": {
      "subject": "Thank you for your ${{custom_event.value}} purchase!",
      "html_body": "<h1>Thank you!</h1><p>Your {{custom_event.properties.product_name}} order is confirmed.</p>",
      "plaintext_body": "Thank you! Your {{custom_event.properties.product_name}} order is confirmed.",
      "message_type": "transactional"
    }
  }
}
```

## Step 4: Create Personalized Message Center Content

Design the Message Center message with rich HTML content using handlebars templating.

**Example personalized Message Center**:

```json
{
  "message": {
    "title": "Order Confirmation - {{custom_event.properties.product_name}}",
    "body": "<html><body><h1>Thank you for your purchase!</h1><p><strong>Product:</strong> {{custom_event.properties.product_name}}</p><p><strong>Total:</strong> ${{custom_event.value}}</p><p><strong>Order ID:</strong> {{custom_event.properties.order_id}}</p><p><strong>Estimated Delivery:</strong> {{custom_event.properties.delivery_date}}</p><p>We'll send you tracking information once your order ships.</p></body></html>",
    "content_type": "text/html"
  }
}
```

**Rich Message Center with styling**:

```json
{
  "message": {
    "title": "Order #{{custom_event.properties.order_id}} Confirmed",
    "body": "<html><head><style>body { font-family: Arial, sans-serif; } .header { background-color: #4CAF50; color: white; padding: 20px; } .content { padding: 20px; } .detail { margin: 10px 0; }</style></head><body><div class=\"header\"><h1>Thank you for your purchase!</h1></div><div class=\"content\"><div class=\"detail\"><strong>Product:</strong> {{custom_event.properties.product_name}}</div><div class=\"detail\"><strong>Category:</strong> {{custom_event.properties.category}}</div><div class=\"detail\"><strong>Total:</strong> ${{custom_event.value}}</div><div class=\"detail\"><strong>Order ID:</strong> {{custom_event.properties.order_id}}</div><div class=\"detail\"><strong>Delivery Date:</strong> {{custom_event.properties.delivery_date}}</div></div></body></html>",
    "content_type": "text/html"
  }
}
```

## Step 5: Combine into Pipeline Outcome

Combine the notification and message into the pipeline outcome structure. The `audience` must be set to `"triggered"`.

**Complete outcome example**:

```json
{
  "outcome": {
    "push": {
      "audience": "triggered",
      "device_types": ["ios", "android"],
      "notification": {
        "alert": "Thank you for purchasing {{custom_event.properties.product_name}}! Your order total was ${{custom_event.value}}."
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

## Step 6: Create Pipeline via POST /api/pipelines

Combine all components into a complete pipeline object and create it:

```json
POST /api/pipelines
Authorization: Bearer <token>
Accept: application/vnd.urbanairship+json; version=3
Content-Type: application/json

{
  "name": "Purchase Confirmation Automation",
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

**Response**:

```json
{
  "ok": true,
  "operation_id": "ef625038-70a3-41f1-826f-57bc11dd625a",
  "pipeline_urls": [
    "https://go.urbanairship.com/api/pipelines/4d3ff1fd-9ce6-5ea4-5dc9-5ccbd38597f4"
  ]
}
```

## Step 7: (Optional) Validate Pipeline Before Creation

Before creating the pipeline, you can validate the payload to catch errors early:

```json
POST /api/pipelines/validate
Authorization: Bearer <token>
Accept: application/vnd.urbanairship+json; version=3
Content-Type: application/json

{
  "name": "Purchase Confirmation Automation",
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
      },
      "message": {
        "title": "Order Confirmation - {{custom_event.properties.product_name}}",
        "body": "<html><body><h1>Thank you for your purchase!</h1><p><strong>Product:</strong> {{custom_event.properties.product_name}}</p><p><strong>Total:</strong> ${{custom_event.value}}</p></body></html>",
        "content_type": "text/html"
      }
    }
  }
}
```

**Response** (if valid):
```json
{
  "ok": true
}
```

## Outcomes

- Pipeline created and enabled
- Automation will trigger when matching Custom Events occur
- Personalized push notifications sent to users
- Personalized Message Center messages delivered
- Messages use Custom Event data for personalization via handlebars templating

## Use Cases

- Purchase confirmation automations
- Event-triggered personalized notifications
- Order status updates
- Personalized welcome messages based on user actions
- Custom Event-driven marketing campaigns
- Transactional messaging with rich content

## Related Workflows

- [Custom Event Automation Discovery](../custom-event-automation-discovery/SKILL.md) - Discover existing automations and their requirements

## Best Practices

1. **Identify required properties**: Document which Custom Event properties are needed for personalization
2. **Test handlebars syntax**: Ensure handlebars references match your Custom Event structure
3. **Handle missing properties**: Consider what happens if a property is missing (handlebars renders empty string)
4. **Validate before creating**: Use `/api/pipelines/validate` to catch errors early
5. **Use descriptive names**: Provide clear pipeline names for easier management
6. **Personalize consistently**: Use the same property references in both notification and Message Center
7. **Test with sample events**: Submit test Custom Events to verify handlebars resolve correctly
8. **Consider timing**: Add delays if needed to improve user experience
9. **Set constraints**: Use rate limiting to avoid overwhelming users
10. **Monitor pipeline status**: Check pipeline status and limits regularly

## Example: Complete Pipeline with All Features

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
        }
      ]
    }
  },
  "timing": {
    "delay": {
      "seconds": 30
    }
  },
  "constraint": [
    {
      "rate": {
        "pushes": 1,
        "days": 1
      }
    }
  ],
  "outcome": {
    "push": {
      "audience": "triggered",
      "device_types": ["ios", "android", "email"],
      "notification": {
        "alert": "Thank you for your premium purchase!",
        "ios": {
          "alert": "Thank you for purchasing {{custom_event.properties.product_name}}!"
        },
        "android": {
          "alert": "Order confirmed: {{custom_event.properties.product_name}}",
          "title": "Premium Purchase"
        },
        "email": {
          "subject": "Thank you for your ${{custom_event.value}} purchase!",
          "html_body": "<html><body><h1>Thank you!</h1><p>Your {{custom_event.properties.product_name}} order is being processed.</p></body></html>",
          "plaintext_body": "Thank you! Your {{custom_event.properties.product_name}} order is being processed.",
          "message_type": "transactional"
        }
      },
      "message": {
        "title": "Premium Purchase Confirmation - {{custom_event.properties.product_name}}",
        "body": "<html><body><h1>Thank you for your premium purchase!</h1><p><strong>Product:</strong> {{custom_event.properties.product_name}}</p><p><strong>Category:</strong> {{custom_event.properties.category}}</p><p><strong>Total:</strong> ${{custom_event.value}}</p><p><strong>Order ID:</strong> {{custom_event.properties.order_id}}</p><p>As a valued customer, you'll receive priority support for this order.</p></body></html>",
        "content_type": "text/html"
      }
    }
  }
}
```

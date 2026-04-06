# Airship Push Notification Examples

Complete examples of valid push payloads for the Airship API.

## ⚠️ Common Mistakes

### Android Alert Format (Most Common Error)

**WRONG** - This causes a 400 error:
```json
{
  "notification": {
    "android": {
      "alert": {
        "title": "Hello",
        "body": "This is wrong"
      }
    }
  }
}
```

**CORRECT** - Android requires alert as string with separate title:
```json
{
  "notification": {
    "android": {
      "alert": "This is correct",
      "title": "Hello"
    }
  }
}
```

### Platform Alert Format Quick Reference

| Platform | Alert Format | Title Field |
|----------|--------------|-------------|
| **iOS** | String OR Object `{"title": "...", "body": "..."}` | Inside alert object |
| **Android** | String only | Separate `"title"` field |
| **Web** | String only | Separate `"title"` field |

### Cross-Platform Example (Correct)
```json
{
  "audience": {"tag": "users"},
  "device_types": ["ios", "android", "web"],
  "notification": {
    "ios": {
      "alert": {
        "title": "Hello",
        "body": "This works for iOS"
      }
    },
    "android": {
      "alert": "This works for Android",
      "title": "Hello"
    },
    "web": {
      "alert": "This works for Web",
      "title": "Hello"
    }
  }
}
```

## Basic Push Notifications

### Push to Tag
```json
{
  "audience": {
    "tag": "vip_users"
  },
  "device_types": ["ios", "android"],
  "notification": {
    "alert": "Special offer for VIP members!"
  }
}
```

### Push to Channel ID
```json
{
  "audience": {
    "ios_channel": "ba05df9e-9c7b-40f4-a867-870a281dbf8c"
  },
  "device_types": ["ios"],
  "notification": {
    "alert": "Hello specific device!"
  }
}
```

### Push to Named User
```json
{
  "audience": {
    "named_user": "user_12345"
  },
  "device_types": ["ios", "android"],
  "notification": {
    "alert": "Hello John!"
  }
}
```

### Push to Multiple Channels
```json
{
  "audience": {
    "or": [
      {"ios_channel": "channel-id-1"},
      {"android_channel": "channel-id-2"}
    ]
  },
  "device_types": ["ios", "android"],
  "notification": {
    "alert": "Message to multiple devices"
  }
}
```

## Platform-Specific Notifications

### iOS with Title and Badge
```json
{
  "audience": {"tag": "ios_users"},
  "device_types": ["ios"],
  "notification": {
    "ios": {
      "alert": {
        "title": "New Message",
        "body": "You have a new message!"
      },
      "badge": "+1",
      "sound": "default"
    }
  }
}
```

### Android with Icon and Color
```json
{
  "audience": {"tag": "android_users"},
  "device_types": ["android"],
  "notification": {
    "android": {
      "alert": "New notification",
      "title": "App Name",
      "icon": "ic_notification",
      "icon_color": "#FF5733"
    }
  }
}
```

## Background/Silent Notifications

### Content Available (Silent Push)
```json
{
  "audience": {"tag": "david"},
  "device_types": ["ios"],
  "notification": {
    "alert": "New content available",
    "ios": {
      "content_available": 1,
      "badge": 1
    }
  }
}
```

### Background Update Only
```json
{
  "audience": {"tag": "users"},
  "device_types": ["ios"],
  "notification": {
    "ios": {
      "content_available": 1
    }
  }
}
```

### Badge Update with Collapse ID
```json
{
  "audience": {"tag": "users"},
  "device_types": ["ios"],
  "notification": {
    "ios": {
      "collapse_id": "badge-update",
      "badge": 5,
      "sound": "default"
    }
  }
}
```

## In-App Messages

### Banner with Deep Link
```json
{
  "audience": {"tag": "david"},
  "device_types": ["ios"],
  "in_app": {
    "alert": "Airship test",
    "display_type": "banner",
    "display": {
      "position": "top"
    },
    "actions": {
      "open": {
        "type": "deep_link",
        "content": "www.airship.com"
      }
    }
  }
}
```

### Banner at Bottom
```json
{
  "audience": {"ios_channel": "30420308-8353-4508-9962-a89537ee4d67"},
  "device_types": ["ios"],
  "in_app": {
    "alert": "Check out this offer!",
    "display_type": "banner",
    "display": {
      "position": "bottom"
    },
    "actions": {
      "open": {
        "type": "deep_link",
        "content": "myapp://special-offer"
      }
    }
  }
}
```

### In-App with Custom Colors
```json
{
  "audience": {"tag": "users"},
  "device_types": ["ios", "android"],
  "in_app": {
    "alert": "Limited time offer!",
    "display_type": "banner",
    "expiry": "25200",
    "display": {
      "primary_color": "#ff6600",
      "secondary_color": "#000000",
      "position": "bottom"
    }
  }
}
```

## Advanced Actions

### Landing Page Action
```json
{
  "audience": {"tag": "customers"},
  "device_types": ["ios", "android"],
  "notification": {
    "ios": {
      "alert": "Check out our sale!",
      "actions": {
        "open": {
          "type": "landing_page",
          "content": {
            "url": "https://example.com/sale.html"
          }
        }
      }
    },
    "android": {
      "alert": "Check out our sale!",
      "actions": {
        "open": {
          "type": "landing_page",
          "content": {
            "url": "https://example.com/sale.html"
          }
        }
      }
    }
  }
}
```

### Landing Page with Media Attachment (iOS)
```json
{
  "audience": {"tag": "david"},
  "device_types": ["ios"],
  "notification": {
    "ios": {
      "alert": "Special promotion - 50% off!",
      "mutable_content": true,
      "media_attachment": {
        "url": "https://example.com/promo-image.jpg",
        "options": {
          "hidden": false
        }
      },
      "actions": {
        "open": {
          "type": "landing_page",
          "content": {
            "content_type": "text/html",
            "body": "<!doctype html><html><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><style>body{font-family:arial,helvetica,sans-serif;margin:0;padding:20px;background:#fff}.container{max-width:500px;margin:0 auto}h1{color:#dd1d21;font-size:24px;margin:0 0 16px}img{width:100%;max-width:100%;height:auto}.button{display:inline-block;padding:12px 24px;background:#007AFF;color:#fff;text-decoration:none;border-radius:8px;margin:20px 0}</style></head><body><div class=\"container\"><h1>Limited Time Offer!</h1><img src=\"https://example.com/promo-image.jpg\" alt=\"Promotion\"><p>Save 50% on all items today only!</p><a href=\"uairship://run-actions?add_custom_event_action=%7B%22event_name%22%3A%22promo_clicked%22%7D\" class=\"button\">Shop Now</a></div></body></html>"
          }
        }
      }
    }
  },
  "message_type": "transactional"
}
```

### Landing Page with HTML Content (Android)
```json
{
  "audience": {"tag": "david"},
  "device_types": ["android"],
  "notification": {
    "android": {
      "alert": "Check out this special offer!",
      "actions": {
        "open": {
          "type": "landing_page",
          "content": {
            "content_type": "text/html",
            "body": "<!doctype html><html><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><style>body{font-family:sans-serif;padding:20px;background:#f5f5f5}h1{color:#1a73e8}.cta-button{display:block;padding:15px;background:#1a73e8;color:#fff;text-align:center;text-decoration:none;border-radius:4px;margin:20px 0}</style></head><body><h1>Exclusive Android Offer</h1><p>Limited time promotion just for you!</p><a href=\"uairship://run-actions?add_custom_event_action=%7B%22event_name%22%3A%22android_offer_tap%22%7D\" class=\"cta-button\">Claim Offer</a></body></html>"
          }
        }
      }
    }
  },
  "message_type": "transactional"
}
```

### App-Defined Actions
```json
{
  "audience": {"android_channel": "a8eeea0a-6559-4c53-a731-01fbaa1b5ae8"},
  "device_types": ["android"],
  "notification": {
    "alert": "Check out our documentation",
    "actions": {
      "app_defined": {
        "^u": "https://docs.airship.com/"
      }
    }
  }
}
```

### Deep Link Action
```json
{
  "audience": {"tag": "users"},
  "device_types": ["ios", "android"],
  "notification": {
    "alert": "View your order",
    "actions": {
      "open": {
        "type": "deep_link",
        "content": {
          "url": "myapp://orders/12345"
        }
      }
    }
  }
}
```

### URL Action
```json
{
  "audience": {"tag": "users"},
  "device_types": ["ios", "android"],
  "notification": {
    "alert": "Visit our website",
    "actions": {
      "open": {
        "type": "url",
        "content": "https://example.com"
      }
    }
  }
}
```

## Message Center

### Message Center with Push
```json
{
  "audience": {"tag": "subscribers"},
  "device_types": ["ios", "android"],
  "notification": {
    "alert": "You have a new message"
  },
  "message": {
    "title": "Welcome!",
    "body": "<h1>Welcome to our app!</h1><p>Get started here...</p>",
    "content_type": "text/html"
  }
}
```

### Message Center Only (No Push)
```json
{
  "audience": {"tag": "users"},
  "device_types": ["ios", "android"],
  "message": {
    "title": "Important Update",
    "body": "<div><h2>What's New</h2><p>Check out our latest features!</p></div>",
    "content_type": "text/html"
  }
}
```

### Push with Deep Link to Message Center
```json
{
  "audience": {"tag": "david"},
  "device_types": ["ios", "android"],
  "notification": {
    "ios": {
      "alert": "Where do I add my message center message?",
      "actions": {
        "open": {
          "type": "deep_link",
          "content": "uairship://message_center",
          "fallback_url": "uairship://message_center"
        }
      }
    },
    "android": {
      "alert": "Where do I add my message center message?",
      "actions": {
        "open": {
          "type": "deep_link",
          "content": "uairship://message_center",
          "fallback_url": "uairship://message_center"
        }
      }
    }
  },
  "message_type": "commercial"
}
```

### Message Center with Interactive HTML Button
```json
{
  "audience": {"tag": "david"},
  "device_types": ["ios", "android"],
  "notification": {
    "android": {
      "alert": "Got 2 minutes? Receive 100 Stars for filling out a quick survey!",
      "title": "How did we brew?"
    },
    "ios": {
      "alert": {
        "title": "How did we brew?",
        "body": "Got 2 minutes? Receive 100 Stars for filling out a quick survey!"
      }
    }
  },
  "message": {
    "title": "Message center message with button",
    "body": "<div style=\"font-family: arial,helvetica,sans-serif; padding: 10px;\"><h1 style=\"color: #dd1d21;\">Take Our Survey!</h1><p>Help us improve by taking a quick survey.</p><div style=\"text-align: center;\"><a href=\"uairship://run-actions?add_custom_event_action=%7B%22event_name%22%3A%22ua_button_tap-event-survey%22%7D\" style=\"color:#555555;background-color:#e1e4e6;border-radius: 4px;padding:10px 20px;text-decoration:none;display:inline-block;\">Click Here</a></div></div>",
    "content_type": "text/html"
  }
}
```

### Message Center with Custom Icon
```json
{
  "audience": {"tag": "david"},
  "device_types": ["ios", "android"],
  "notification": {
    "alert": "Don't forget to drink water and stay hydrated!",
    "ios": {
      "badge": "+1"
    }
  },
  "message": {
    "title": "Hydration Reminder!",
    "body": "Hi! This is a friendly reminder to drink some H2O and make a splash in your day!",
    "content_type": "text/html",
    "extra": {
      "emoji_count": 5
    },
    "icons": {
      "list_icon": "https://example.com/water-icon.png"
    }
  }
}
```

## Audience Targeting

### Complex AND/OR Logic
```json
{
  "audience": {
    "or": [
      {
        "and": [
          {"tag": "premium"},
          {"tag": "ios"}
        ]
      },
      {
        "and": [
          {"tag": "trial"},
          {"tag": "android"}
        ]
      }
    ]
  },
  "device_types": ["ios", "android"],
  "notification": {
    "alert": "Special offer!"
  }
}
```

### NOT Logic
```json
{
  "audience": {
    "and": [
      {"tag": "users"},
      {"not": {"tag": "unsubscribed"}}
    ]
  },
  "device_types": ["ios", "android"],
  "notification": {
    "alert": "Weekly newsletter"
  }
}
```

### Segment
```json
{
  "audience": {
    "segment": "segment-id-here"
  },
  "device_types": ["ios", "android"],
  "notification": {
    "alert": "Message for segment"
  }
}
```

## Special Features

### Test Mode
```json
{
  "audience": {"tag": "test_users"},
  "device_types": ["ios", "android"],
  "notification": {
    "alert": "Test notification"
  },
  "options": {
    "test": true
  }
}
```

### Transactional Messages
```json
{
  "audience": {"named_user": "user_123"},
  "device_types": ["ios", "android"],
  "notification": {
    "alert": "Your order has shipped!"
  },
  "message_type": "transactional"
}
```

### Custom Metadata
```json
{
  "audience": {"tag": "users"},
  "device_types": ["ios", "android"],
  "notification": {
    "alert": "New content available",
    "extra": {
      "content_id": "12345",
      "category": "news",
      "custom_data": "value"
    }
  }
}
```

### Scheduled Push
```json
{
  "audience": {"tag": "users"},
  "device_types": ["ios", "android"],
  "notification": {
    "alert": "Don't forget!"
  },
  "schedule": {
    "scheduled_time": "2024-12-25T09:00:00Z"
  }
}
```

## Notification Grouping (iOS)

### Grouping with Collapse ID
```json
{
  "audience": {"tag": "users"},
  "device_types": ["ios"],
  "notification": {
    "ios": {
      "collapse_id": "order-updates",
      "alert": "Your order has been updated",
      "badge": "+1"
    }
  }
}
```

### Multiple Notifications with Same Collapse ID
```json
{
  "audience": {"tag": "users"},
  "device_types": ["ios"],
  "notification": {
    "ios": {
      "collapse_id": "chat-thread-123",
      "alert": "New message in conversation",
      "badge": "+1",
      "sound": "default"
    }
  }
}
```

### Badge Update Only with Collapse ID
```json
{
  "audience": {"tag": "users"},
  "device_types": ["ios"],
  "notification": {
    "ios": {
      "collapse_id": "badge-counter",
      "badge": 5
    }
  }
}
```

## Interactive Notifications

### Action Buttons (iOS)
```json
{
  "audience": {"tag": "ios_users"},
  "device_types": ["ios"],
  "notification": {
    "ios": {
      "alert": "Rate our app!",
      "category": "rating_category",
      "interactive": {
        "type": "rating",
        "button_actions": {
          "yes": {
            "type": "open_url",
            "content": "https://apps.apple.com/app/id123456"
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

### Interactive with Tag Actions
```json
{
  "audience": {"tag": "david"},
  "device_types": ["ios"],
  "notification": {
    "ios": {
      "alert": "Special offer just for you!",
      "interactive": {
        "type": "ua_buy_now",
        "button_actions": {
          "buy_now": {
            "add_tag": "buy_now_tapped"
          }
        }
      }
    }
  }
}
```

### Interactive with Localization
```json
{
  "audience": {"tag": "david"},
  "device_types": ["ios"],
  "notification": {
    "ios": {
      "alert": "Hi",
      "interactive": {
        "type": "ua_buy_now",
        "button_actions": {
          "buy_now": {
            "add_tag": "buy_now_tapped"
          }
        }
      }
    }
  },
  "localizations": [
    {
      "language": "fr",
      "notification": {
        "alert": "Bonjour",
        "interactive": {
          "type": "ua_buy_now",
          "button_actions": {
            "buy_now": {
              "add_tag": "buy_now_tapped"
            }
          }
        }
      }
    },
    {
      "language": "de",
      "notification": {
        "alert": "Guten Tag",
        "interactive": {
          "type": "ua_buy_now",
          "button_actions": {
            "buy_now": {
              "add_tag": "buy_now_tapped"
            }
          }
        }
      }
    }
  ]
}
```

## Media Attachments

### Image Notification (iOS)
```json
{
  "audience": {"tag": "users"},
  "device_types": ["ios"],
  "notification": {
    "ios": {
      "alert": "Check out this image!",
      "media_attachment": {
        "url": "https://example.com/image.jpg",
        "content": {
          "title": "Beautiful Photo",
          "body": "Taken today"
        }
      }
    }
  }
}
```

### Big Picture Notification (Android)
```json
{
  "audience": {"tag": "android_users"},
  "device_types": ["android"],
  "notification": {
    "android": {
      "alert": "New photo",
      "style": {
        "type": "big_picture",
        "big_picture": "https://example.com/image.jpg",
        "summary": "Check this out!"
      }
    }
  }
}
```

## Localization

### Localized Notifications
```json
{
  "audience": {"tag": "global_users"},
  "device_types": ["ios", "android"],
  "notification": {
    "alert": "Hello!",
    "localizations": [
      {
        "language": "es",
        "alert": "¡Hola!"
      },
      {
        "language": "fr",
        "alert": "Bonjour!"
      },
      {
        "language": "de",
        "alert": "Guten Tag!"
      }
    ]
  }
}
```

## Common Patterns

### Re-engagement Campaign
```json
{
  "audience": {
    "and": [
      {"tag": "inactive_30d"},
      {"not": {"tag": "uninstalled"}}
    ]
  },
  "device_types": ["ios", "android"],
  "notification": {
    "alert": "We miss you! Come back for 20% off",
    "actions": {
      "open": {
        "type": "deep_link",
        "content": {
          "url": "myapp://promo/comeback20"
        }
      }
    }
  }
}
```

### Flash Sale
```json
{
  "audience": {"tag": "shoppers"},
  "device_types": ["ios", "android"],
  "notification": {
    "ios": {
      "alert": {
        "title": "⚡ Flash Sale!",
        "body": "50% off for the next 2 hours"
      },
      "sound": "sale.wav",
      "badge": "+1"
    },
    "android": {
      "alert": "50% off for the next 2 hours",
      "title": "⚡ Flash Sale!",
      "priority": "high"
    }
  },
  "message_type": "commercial"
}
```

## Multi-Feature Combinations

### Push + Message Center + In-App Message
```json
{
  "audience": {"tag": "david"},
  "device_types": ["ios"],
  "notification": {
    "ios": {
      "alert": "Grab your tickets to the festival!",
      "badge": "+1"
    }
  },
  "message": {
    "title": "Festival Tickets Are Selling Fast!",
    "body": "<!doctype html><html><head><meta charset=\"utf-8\"><style>body{font-family:arial,sans-serif;padding:20px}h1{color:#ff6600;margin-bottom:20px}.cta{display:inline-block;padding:12px 24px;background:#ff6600;color:#fff;text-decoration:none;border-radius:6px;margin-top:15px}</style></head><body><h1>Don't Miss Out!</h1><p>Grab your crew and lock-in your tickets to the festival!</p><a href=\"uairship://run-actions?add_custom_event_action=%7B%22event_name%22%3A%22festival_cta_tap%22%7D\" class=\"cta\">Get Tickets</a></body></html>",
    "content_type": "text/html",
    "content_encoding": "utf-8",
    "extra": {
      "com.urbanairship.listing.template": "image"
    }
  },
  "in_app": {
    "alert": "Grab your crew, and lock-in your tickets!",
    "display_type": "banner",
    "expiry": "25200",
    "display": {
      "primary_color": "#ff6600",
      "secondary_color": "#000000",
      "position": "bottom"
    }
  }
}
```

### Message Center with Deep Link Button
```json
{
  "audience": {"tag": "david"},
  "device_types": ["ios", "android"],
  "notification": {
    "ios": {
      "title": "Milwaukee Buy More, Get More!",
      "alert": "Exclusive deals on tools",
      "badge": "+1"
    }
  },
  "message": {
    "title": "Milwaukee Buy More, Get More GOING ON NOW!",
    "body": "<!doctype html><html><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><style>body{font-family:arial,helvetica,sans-serif;margin:0;padding:20px}.container{max-width:500px;margin:0 auto}h1{font-size:22px;text-align:center;margin-bottom:20px}p{font-size:14px;line-height:1.6}.button{display:inline-block;padding:10px 20px;background:#d6202d;color:#fff;text-decoration:none;border-radius:4px;text-align:center;margin:20px auto;display:block;width:150px}</style></head><body><div class=\"container\"><img src=\"https://example.com/milwaukee-promo.jpg\" style=\"width:100%;max-width:100%\"/><h1>Milwaukee Buy More, Get More GOING ON NOW!</h1><p>Get a FREE tumbler and organizer when you spend $249 on select Milwaukee PACKOUT products.</p><a href=\"uairship://run-actions?deep_link_action=%22myapp%3A%2F%2Fshop%2Fmilwaukee%22&add_custom_event_action=%7B%22event_name%22%3A%22ua_button_tap%22%7D\" class=\"button\">SHOP NOW</a></div></body></html>",
    "content_type": "text/html"
  }
}
```

### Landing Page + Media + Transactional
```json
{
  "audience": {"tag": "customers"},
  "device_types": ["ios"],
  "notification": {
    "ios": {
      "alert": "Special loyalty rewards available!",
      "mutable_content": true,
      "media_attachment": {
        "url": "https://example.com/rewards-banner.jpg",
        "options": {
          "hidden": false
        }
      },
      "actions": {
        "open": {
          "type": "landing_page",
          "content": {
            "content_type": "text/html",
            "body": "<!doctype html><html><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><style>body{font-family:sans-serif;margin:0;padding:0;background:#f5f5f5}.header{background:#1a73e8;color:#fff;padding:30px 20px;text-align:center}h1{margin:0;font-size:28px}.content{padding:20px;max-width:600px;margin:0 auto;background:#fff}.reward-card{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;padding:30px;border-radius:12px;margin:20px 0;text-align:center}.points{font-size:48px;font-weight:bold;margin:10px 0}.cta-button{display:block;background:#1a73e8;color:#fff;padding:16px;text-align:center;text-decoration:none;border-radius:8px;margin:20px 0;font-weight:bold}</style></head><body><div class=\"header\"><h1>Your Loyalty Rewards</h1></div><div class=\"content\"><div class=\"reward-card\"><p style=\"margin:0;font-size:18px\">Available Points</p><div class=\"points\">2,500</div><p style=\"margin:0\">Ready to redeem!</p></div><h2>Exclusive Offers</h2><p>Use your points for amazing rewards and special discounts.</p><a href=\"uairship://run-actions?deep_link_action=%22myapp%3A%2F%2Frewards%2Fredeem%22&add_custom_event_action=%7B%22event_name%22%3A%22redeem_rewards_tap%22%7D\" class=\"cta-button\">Redeem Now</a></div></body></html>"
          }
        }
      }
    }
  },
  "message_type": "transactional"
}
```

### Localized Interactive with Multiple Languages
```json
{
  "audience": {"tag": "global_users"},
  "device_types": ["ios"],
  "notification": {
    "ios": {
      "alert": "Special offer - Act now!",
      "interactive": {
        "type": "ua_yes_no",
        "button_actions": {
          "yes": {
            "add_tag": "offer_accepted"
          },
          "no": {
            "add_tag": "offer_declined"
          }
        }
      }
    }
  },
  "localizations": [
    {
      "language": "es",
      "notification": {
        "alert": "Oferta especial - ¡Actúa ahora!",
        "interactive": {
          "type": "ua_yes_no",
          "button_actions": {
            "yes": {"add_tag": "offer_accepted"},
            "no": {"add_tag": "offer_declined"}
          }
        }
      }
    },
    {
      "language": "fr",
      "notification": {
        "alert": "Offre spéciale - Agissez maintenant!",
        "interactive": {
          "type": "ua_yes_no",
          "button_actions": {
            "yes": {"add_tag": "offer_accepted"},
            "no": {"add_tag": "offer_declined"}
          }
        }
      }
    },
    {
      "language": "de",
      "notification": {
        "alert": "Sonderangebot - Jetzt handeln!",
        "interactive": {
          "type": "ua_yes_no",
          "button_actions": {
            "yes": {"add_tag": "offer_accepted"},
            "no": {"add_tag": "offer_declined"}
          }
        }
      }
    }
  ]
}
```

## Notes

- **Channel IDs**: Use `ios_channel` or `android_channel` instead of just `channel_id`
- **Device Types**: Always specify device_types that match your audience
- **Test Mode**: Use `"options": {"test": true}` to validate without sending
- **URLs**: Use `https://` for web URLs and custom schemes for deep links
- **HTML**: Message Center supports inline CSS only, no external stylesheets
- **uairship:// Schemes**: Use for deep links (`uairship://message_center`) and action URLs (`uairship://run-actions`)
- **Collapse IDs**: iOS only - groups related notifications together
- **Content Available**: Set to 1 (not true) for iOS background updates
- **In-App Messages**: Can be combined with push notifications and message center
---
name: sdk-reference
description: Airship SDK and API documentation. Use when helping with Airship push notifications, Message Center, Preference Center, In-App Messaging, or SDK integration for iOS, Android, React Native, Flutter, Capacitor, or Cordova.
license: Copyright Airship. All rights reserved.
---

# Airship Documentation

This skill provides comprehensive documentation for the Airship SDK and Push API.

## When to Use

- Setting up Airship SDK on any platform
- Sending push notifications via the Airship API
- Implementing Message Center, Preference Center, or In-App Messaging
- Troubleshooting push notification issues
- Understanding API payload formats
- Finding SDK sample code

## Documentation Structure

### API Documentation (`references/api/`)

| File | Description |
|------|-------------|
| `push-api-spec.md` | Complete Push API specification - audiences, notifications, options |
| `push-examples.md` | Working payload examples for all use cases |
| `html-reference.md` | HTML formatting guide for Message Center messages |

### Platform Setup Guides (`references/setup/{platform}/`)

Each platform has setup guides for:
- `push-setup.md` - Push notification configuration
- `message-center-setup.md` - Message Center / Inbox setup
- `preference-center-setup.md` - Subscription preferences UI
- `feature-flags-setup.md` - Feature flag configuration

**Platforms**: ios, android, react-native, flutter, capacitor, cordova

### Troubleshooting (`references/troubleshooting/`)

Platform-specific and shared troubleshooting guides:
- `push-troubleshooting.md` - Push delivery issues
- `configuration-troubleshooting.md` - SDK configuration problems
- `message-center-troubleshooting.md` - Message Center issues
- `preference-center-troubleshooting.md` - Preference Center issues

## How to Find Documentation

### For API Payload Help
Read `references/api/push-api-spec.md` for the specification, then `references/api/push-examples.md` for working examples.

### For Platform Setup
Read `references/setup/{platform}/setup/{feature}-setup.md`

Example: iOS push setup → `references/setup/ios/setup/push-setup.md`

### For Troubleshooting
1. Try platform-specific: `references/setup/{platform}/troubleshooting/{topic}-troubleshooting.md`
2. Fall back to shared: `references/troubleshooting/shared/troubleshooting/{topic}-troubleshooting.md`

### For SDK Sample Code
Run the search script:
```bash
python scripts/search_sdk_code.py --platform ios --query "push notification handler"
```

## Quick Reference

### Platform Alert Formats (Critical!)

| Platform | Alert Format | Title Field |
|----------|--------------|-------------|
| **iOS** | String OR Object `{"title": "...", "body": "..."}` | Inside alert object |
| **Android** | String only | Separate `"title"` field |
| **Web** | String only | Separate `"title"` field |

### Audience Selectors

```json
// Tag
{"audience": {"tag": "users"}}

// Channel (use platform prefix!)
{"audience": {"ios_channel": "channel-id"}}
{"audience": {"android_channel": "channel-id"}}

// Named User
{"audience": {"named_user": "user_123"}}

// Complex logic
{"audience": {"and": [{"tag": "premium"}, {"not": {"tag": "inactive"}}]}}
```

### Test Mode
Always validate before sending:
```json
{"options": {"test": true}}
```

## Related Skills

- `custom-views` - Custom UI component registration
- `migration` - SDK migration guides

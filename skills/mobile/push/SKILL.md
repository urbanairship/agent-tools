---
name: push
description: Implement and test Airship push notifications. Use when setting up push notifications, troubleshooting delivery issues, or testing push integration on iOS, Android, React Native, Flutter, Capacitor, or Cordova.
license: Copyright Airship. All rights reserved.
---

# Airship Push Notifications

This skill guides you through implementing and testing Airship push notifications.

## When to Use

- Setting up push notifications for a new app
- Troubleshooting push delivery issues
- Testing push integration after SDK updates
- Verifying push configuration

## Prerequisites

Ensure the Airship SDK is integrated. If migrating versions, use the `migration` skill first.

## Implementation Workflow

### Step 1: Platform Setup

Ask the user which platform they're targeting, then follow the appropriate guide:

| Platform | Setup Guide |
|----------|-------------|
| iOS | `references/ios-setup.md` |
| Android | `references/android-setup.md` |
| React Native | `references/react-native-setup.md` |
| Flutter | `references/flutter-setup.md` |
| Capacitor | `references/capacitor-setup.md` |
| Cordova | `references/cordova-setup.md` |

### Step 2: Build and Verify

After implementing push setup, verify the build.

**If the Airship MCP server is available:**
```
Use MCP tool: airship.verify_build(project_path="<path>")
```

**Otherwise, run the platform build command:**

| Platform | Build Command |
|----------|---------------|
| iOS | `xcodebuild -scheme <scheme> -sdk iphonesimulator build` |
| Android | `./gradlew assembleDebug` |
| React Native | `npx react-native run-ios` or `npx react-native run-android` |
| Flutter | `flutter build apk` or `flutter build ios` |
| Capacitor | `npx cap build ios` or `npx cap build android` |
| Cordova | `cordova build ios` or `cordova build android` |

### Step 3: Test Push Delivery

Once the build succeeds, test push notification delivery.

**If the Airship MCP server is available:**
```
Use MCP tool: airship.send_push_to_tag(tag="test", alert="Test notification", title="Hello")
```
Or for a specific device:
```
Use MCP tool: airship.send_push_to_channel(channel_id="<channel>", platform="ios", alert="Test")
```

**Otherwise:**
- Use the [Airship dashboard](https://go.urbanairship.com) to send a test push via Messages > Test Devices
- Or send via the Push API directly — see the `sdk-reference` skill for API payload format and examples
- If web search is available, search `site:docs.airship.com push api` for the latest API reference

### Step 4: Verify Receipt

Check that the device received the notification:
1. For simulators: Check Xcode console or Android logcat
2. For physical devices: Verify notification appears in notification center

## Troubleshooting

If push notifications aren't working:

1. **Verify channel registration:**
   - *With MCP:* `airship.lookup_channel(channel_id="<channel>")`
   - *Without MCP:* Check the Airship dashboard under Audience > Channels, or review device logs for the channel ID logged by the SDK on startup

2. **Check opt-in status:** The channel lookup (or dashboard) will show `opted_in` status

3. **Review configuration:** See `references/troubleshooting.md`

## MCP Tools (Optional)

These tools are available if the `airship` MCP server is configured. The skill works without them using the fallbacks above.

| Tool | Purpose |
|------|---------|
| `verify_build` | Build and check for errors |
| `send_push_to_tag` | Send test push to tag |
| `send_push_to_channel` | Send test push to device |
| `lookup_channel` | Verify channel configuration |

## Scripts

- `scripts/test-push.py` - Automated push testing script

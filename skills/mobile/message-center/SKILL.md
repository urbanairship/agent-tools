---
name: message-center
description: Implement Airship Message Center (app inbox). Use when adding an inbox to your app, customizing message list UI, or troubleshooting message delivery.
license: Copyright Airship. All rights reserved.
---

# Airship Message Center

This skill guides you through implementing and customizing Airship Message Center.

## When to Use

- Adding an inbox/message center to your app
- Customizing the message list or detail UI
- Sending rich HTML messages to the inbox
- Troubleshooting message delivery

## Implementation Workflow

### Step 1: Platform Setup

Follow the setup guide for your platform:

| Platform | Setup Guide |
|----------|-------------|
| iOS | `references/ios-setup.md` |
| Android | `references/android-setup.md` |
| React Native | `references/react-native-setup.md` |
| Flutter | `references/flutter-setup.md` |
| Capacitor | `references/capacitor-setup.md` |
| Cordova | `references/cordova-setup.md` |

### Step 2: Build and Verify

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

### Step 3: Send Test Message

Send a message center message with HTML content to verify delivery.

**If the Airship MCP server is available:**
```
Use MCP tool: airship.send_message_center_message(
    title="Welcome!",
    body_html="<h1>Hello</h1><p>This is a test message.</p>",
    tag="test"
)
```

**Otherwise:**
- Use the [Airship dashboard](https://go.urbanairship.com) under Messages > Message Center to compose and send a test message
- Or send via the Airship Push API — see the `sdk-reference` skill for API payload format
- If web search is available, search `site:docs.airship.com message center api` for the latest API reference

### Step 4: Verify in App

Open the message center in your app to verify the message appears.

## Customization

For custom UI, see the `custom-views` skill or `references/customization.md`.

## MCP Tools (Optional)

These tools are available if the Airship MCP server is configured. The skill works without them using the fallbacks above.

| Tool | Server | Purpose |
|------|--------|---------|
| `verify_build` | airship-mobile-dev | Build and verify |
| `send_message_center_message` | airship-api | Send inbox message |

## HTML Reference

See `references/html-reference.md` for supported HTML tags in message content.

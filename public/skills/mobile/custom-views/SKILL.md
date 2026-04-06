---
name: custom-views
description: Register custom native views for Airship Thomas scenes. Use when customizing Message Center, Preference Center, In-App Messages, or creating custom UI components for iOS, Android, React Native, Flutter, Capacitor, or Cordova.
license: Copyright Airship. All rights reserved.
---

# Airship Custom Views

This skill guides you through registering custom native views for use in Airship Thomas scenes (Airship's declarative layout engine for in-app messages and experiences).

## When to Use

- Registering a custom native view for Thomas scenes
- Customizing Message Center / Inbox UI
- Styling Preference Center
- Customizing In-App Message appearance
- Embedding native components (maps, cameras, charts) in Airship layouts

## Supported Platforms

| Platform | Implementation | Notes |
|----------|----------------|-------|
| **iOS** | SwiftUI | Uses `AirshipCustomViewManager.shared.register()` |
| **Android** | Compose or View-based | Uses `AirshipCustomViewManager.register()` |
| **React Native** | Native iOS + Android | Requires native code in both platforms |
| **Flutter** | Native iOS + Android | Requires native code in both platforms |
| **Capacitor** | Native iOS + Android | Requires native code in both platforms |
| **Cordova** | Native iOS + Android | Requires native code in both platforms |

## Interactive Workflow

When helping a user register a custom view, follow this workflow:

### Step 1: Identify Platform

Ask the user which platform they're targeting:
- iOS
- Android
- React Native
- Flutter
- Capacitor
- Cordova

**For cross-platform SDKs (React Native, Flutter, Capacitor, Cordova):** Explain that custom views require native iOS AND Android implementations.

### Step 2: Identify Use Case

Ask what they want to customize:
1. **Message Center / Inbox UI** - Custom message list and detail views
2. **Preference Center styling** - Subscription preferences UI
3. **In-App Message appearance** - Banners, modals, full-screen messages
4. **Custom Thomas view component** - Native view for Thomas scenes

### Step 3: Gather View Details

For custom Thomas views, ask:
1. **Class name** - e.g., "WeatherWidget", "MapView", "CameraView"
2. **Identifier** - Suggest snake_case from class name (WeatherWidget → weather_widget)
3. **Properties** - What data should be configurable from Thomas scenes?

**IMPORTANT:** Before asking about properties, analyze the user's existing code:
- Search for the class definition with Grep
- Read the file to understand the implementation
- Look for hardcoded values that should be configurable
- Look for constructor parameters or @State/@Published properties

### Step 4: Generate Code

Use the templates in `assets/templates/` to generate:
1. Registration code for the target platform
2. Thomas scene YAML snippet
3. Integration instructions

## Code Generation

### iOS Registration

```swift
import AirshipCore

// Add to your App.init() or AppDelegate
AirshipCustomViewManager.shared.register(name: "IDENTIFIER") { args in
    CLASS_NAME(properties: args.properties)
}
```

**Property access:**
```swift
let value = properties?["key"]?.unWrap() as? String ?? "default"
```

### Android Registration (Compose)

```kotlin
import com.urbanairship.android.layout.ui.AirshipCustomViewManager

// Add to your Application.onCreate()
AirshipCustomViewManager.shared().register("IDENTIFIER") { args ->
    CLASS_NAME(properties = args.properties)
}
```

**Property access:**
```kotlin
val value = properties?.get("key")?.string ?: "default"
```

### Thomas Scene YAML

```yaml
view:
  type: custom_view
  name: IDENTIFIER
  properties:
    key1: "value1"
    key2: 42
    key3: true
```

## Property Type Mapping

| JSON Type | Swift Type | Kotlin Accessor |
|-----------|------------|-----------------|
| string | `String` | `.string` |
| number (int) | `Int` or `Double` | `.int` or `.double` |
| boolean | `Bool` | `.boolean` |
| array | `[AirshipJSON]` | `.list` |
| object | `AirshipJSON` | `.map` |

## Use Case Templates

### Message Center (iOS)

See `assets/templates/ios-message-center.swift` for:
- `MessageCenterDisplayDelegate` implementation
- Custom message list and detail views
- Integration instructions

### Message Center (Android)

See `assets/templates/android-message-center.kt` for:
- `OnShowMessageCenterListener` implementation
- Custom message center activity
- Integration instructions

### Preference Center (iOS)

See `assets/templates/ios-preference-center.swift` for:
- `PreferenceCenterTheme` configuration
- `PreferenceCenterViewDelegate` for full custom UI

### Preference Center (Android)

See `assets/templates/android-preference-center.kt` for:
- Theme overrides in styles.xml
- `OnShowPreferenceCenterListener` for full custom UI

### In-App Messages (iOS)

See `assets/templates/ios-in-app.swift` for:
- `BannerTheme` and `ModalTheme` configuration
- `InAppMessageDisplayDelegate` for full custom display

### In-App Messages (Android)

See `assets/templates/android-in-app.kt` for:
- Theme overrides in styles.xml
- Custom `DisplayAdapter` implementation

## Cross-Platform Notes

For React Native, Flutter, Capacitor, and Cordova:

1. Custom views are implemented in **native code**, not JavaScript/Dart
2. You need implementations for **both iOS and Android**
3. Use the platform-specific extender classes:
   - **React Native**: `AirshipPluginExtenderDelegate`
   - **Flutter**: `AirshipPluginExtenderProtocol`
   - **Capacitor/Cordova**: `AirshipPluginExtenderDelegate`

See `references/cross-platform-guide.md` for detailed instructions.

## References

- `references/ios-guide.md` - Complete iOS implementation guide
- `references/android-guide.md` - Complete Android implementation guide
- `references/cross-platform-guide.md` - React Native, Flutter, Capacitor, Cordova

## Scripts

- `scripts/generate_code.py` - Generate registration code from parameters

## Related Skills

- `sdk-reference` - SDK documentation and setup guides
- `migration` - SDK migration guides

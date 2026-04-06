# Message Center Troubleshooting Guide

Common Message Center issues and fixes.

## Message Center Not Displaying

### iOS (SDK 20+)

**Basic Display:**
```swift
import AirshipMessageCenter

// Full Message Center
MessageCenterView()

// Or programmatically
Airship.messageCenter.display()
```

**Common Issues:**

1. **Wrong View Type**
   - SDK 20 changed architecture
   - Use `MessageCenterView` (with navigation) or `MessageCenterContent` (content only)

2. **Missing Import**
   ```swift
   import AirshipMessageCenter  // Required for UI components
   ```

### Android

**Add Dependency:**
```groovy
dependencies {
    // Traditional View-based UI
    implementation 'com.urbanairship.android:urbanairship-message-center:20.+'

    // OR Jetpack Compose
    implementation 'com.urbanairship.android:urbanairship-message-center-compose:20.+'
}
```

**Display:**
```kotlin
// View-based
MessageCenter.shared().showMessageCenter()

// Compose
@Composable
fun MyScreen() {
    MessageCenterScreen()
}
```

## Messages Not Loading

**Check:**

1. **Network Connectivity**
   - Message Center requires network to fetch messages

2. **Privacy Manager**
   ```swift
   // iOS
   Airship.privacyManager.enabledFeatures.insert(.messageCenter)
   ```

   ```kotlin
   // Android
   Airship.privacyManager.setEnabledFeatures(PrivacyManager.FEATURE_MESSAGE_CENTER)
   ```

3. **Channel ID Created**
   - Messages require valid channel
   - Check Channel ID exists

## Customization Issues

### iOS - Styling

```swift
MessageCenterView()
    .messageCenterContentStyle(CustomStyle())

struct CustomStyle: MessageCenterContentStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.content
            .tint(.purple)
    }
}
```

### Android - Theming

See SDK documentation for Message Center theme customization.

## Unread Count Not Updating

**iOS:**
```swift
// Listen for updates
for await count in Airship.messageCenter.unreadCountPublisher.values {
    print("Unread: \(count)")
}
```

**Android:**
```kotlin
// Observe unread count
MessageCenter.shared().inbox.unreadCountFlow.collect { count ->
    Log.d("Airship", "Unread: $count")
}
```

# Message Center Implementation Guide

Guide to implementing Airship Message Center.

## Overview

Message Center provides an in-app inbox for rich messages.

## iOS Implementation

### 1. Add Message Center Import

```swift
import AirshipMessageCenter
```

Message Center is included in core Airship SDK - no additional dependency needed.

### 2. Display Message Center

**Full Message Center with Navigation:**
```swift
import SwiftUI
import AirshipMessageCenter

struct MyView: View {
    var body: some View {
        MessageCenterView()
    }
}
```

**Programmatic Display:**
```swift
Airship.messageCenter.display()

// Or display specific message
Airship.messageCenter.display(messageID: "message-id")
```

### 3. Customize Styling

```swift
MessageCenterView()
    .messageCenterContentStyle(CustomMessageCenterStyle())

struct CustomMessageCenterStyle: MessageCenterContentStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.content
            .tint(.purple)
            .background(Color.gray.opacity(0.1))
    }
}
```

### 4. Monitor Unread Count

```swift
for await count in Airship.messageCenter.unreadCountPublisher.values {
    // Update badge
    print("Unread messages: \(count)")
}
```

## Android Implementation

### 1. Add Dependency

```groovy
dependencies {
    // Traditional View-based UI
    implementation 'com.urbanairship.android:urbanairship-message-center:20.+'

    // OR Jetpack Compose
    implementation 'com.urbanairship.android:urbanairship-message-center-compose:20.+'
}
```

### 2. Display Message Center

**View-based:**
```kotlin
import com.urbanairship.messagecenter.MessageCenter

// Show Message Center
MessageCenter.shared().showMessageCenter()

// Show specific message
MessageCenter.shared().showMessageCenter("message-id")
```

**Jetpack Compose:**
```kotlin
import com.urbanairship.messagecenter.compose.ui.MessageCenterScreen

@Composable
fun MyScreen() {
    MessageCenterScreen()
}
```

### 3. Monitor Unread Count

```kotlin
MessageCenter.shared().inbox.unreadCountFlow.collect { count ->
    // Update UI with unread count
    Log.d("Airship", "Unread: $count")
}
```

## Testing

1. Send Message Center message from Airship Dashboard
2. Open Message Center in app
3. Verify message appears
4. Test unread count updates

# Push Notification Implementation Guide

Complete guide to implementing push notifications with Airship SDK.

## Overview

This guide covers setting up push notifications from scratch for iOS and Android.

## Prerequisites

- Airship SDK installed and integrated
- Valid Airship app credentials
- Apple Developer account (iOS) or Firebase project (Android)

---

## iOS Implementation

### 1. Configure APNs in Apple Developer Portal

1. Create APNs Key (recommended):
   - Go to developer.apple.com → Certificates, Identifiers & Profiles
   - Keys → Create a key
   - Enable "Apple Push Notifications service (APNs)"
   - Download `.p8` key file
   - Note Key ID and Team ID

2. Or create APNs Certificate (.p12) - legacy method

### 2. Upload APNs Credentials to Airship Dashboard

1. Log into Airship Dashboard
2. Settings → iOS Push Credentials
3. Upload `.p8` key or `.p12` certificate
4. For .p8: Enter Key ID, Team ID, and Bundle ID

### 3. Enable Push Capability in Xcode

1. Select your target
2. Signing & Capabilities
3. + Capability → Push Notifications

### 4. Implement Push in Code

```swift
import Airship
import AirshipKit

// 1. Initialize SDK (in App init)
@main
struct MyApp: App {
    init() {
        Airship.takeOff()
    }
}

// 2. Enable push and request authorization
func setupPush() {
    // Enable push
    Airship.push.userPushNotificationsEnabled = true

    // Request authorization
    Task {
        let granted = await Airship.push.enableUserNotifications()
        print("Push authorized: \(granted)")
    }
}

// 3. Handle notification responses
Airship.push.onReceivedNotificationResponse = { response in
    print("Notification tapped: \(response.actionIdentifier)")
    // Handle deep links, navigation, etc.
}
```

### 5. Test Push Notifications

1. Run app on physical device (simulator doesn't support APNs)
2. Get Channel ID: `print(Airship.channel.identifier)`
3. Go to Airship Dashboard → Messages → Create Test Message
4. Enter Channel ID as audience
5. Send test push

---

## Android Implementation

### 1. Set Up Firebase Cloud Messaging

1. Go to Firebase Console (console.firebase.google.com)
2. Create project or select existing
3. Add Android app with your package name
4. Download `google-services.json`

### 2. Add google-services.json to Project

```
Place in: app/google-services.json (NOT app/src/)
```

### 3. Configure Build Files

**Project-level build.gradle:**
```groovy
buildscript {
    dependencies {
        classpath 'com.google.gms:google-services:4.4.0'
    }
}
```

**App-level build.gradle:**
```groovy
plugins {
    id 'com.android.application'
    id 'com.google.gms.google-services'  // Add this
}

dependencies {
    implementation 'com.urbanairship.android:urbanairship-core:20.+'
    implementation 'com.urbanairship.android:urbanairship-fcm:20.+'
}
```

### 4. Upload FCM Credentials to Airship

1. Firebase Console → Project Settings → Service Accounts
2. Generate new private key (downloads JSON)
3. Airship Dashboard → Settings → Android Push Credentials
4. Upload FCM service account JSON

### 5. Implement Push in Code

```kotlin
// 1. Create Autopilot class
class MyAutopilot : Autopilot() {
    override fun onAirshipReady(context: Context) {
        // Enable push
        Airship.push.userNotificationsEnabled = true

        // For Android 13+, request permission
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            Airship.permissionsManager.requestPermission(
                Permission.POST_NOTIFICATIONS
            ) { result ->
                Log.d("Airship", "Permission: $result")
            }
        }
    }
}

// 2. Register in AndroidManifest.xml
<meta-data
    android:name="com.urbanairship.autopilot"
    android:value="com.yourpackage.MyAutopilot" />

// 3. Handle notification actions (optional)
class MyNotificationListener : AirshipListener {
    override fun onNotificationOpened(context: Context, notificationInfo: NotificationInfo): Boolean {
        Log.d("Airship", "Notification opened")
        // Handle navigation
        return false  // Return true to override default behavior
    }
}

// Register listener
Airship.addAirshipListener(MyNotificationListener())
```

### 6. Test Push Notifications

1. Run app on device or emulator with Google Play Services
2. Get Channel ID: `Log.d("Airship", "Channel: ${Airship.channel.id}")`
3. Use Airship Dashboard to send test message

---

## Advanced Features

### Named Users

Associate channel with user identity:

```swift
// iOS
Airship.contact.identify("user_12345")
```

```kotlin
// Android
Airship.contact.identify("user_12345")
```

### Tags

Segment users with tags:

```swift
// iOS
Airship.channel.editTags {
    addTag("vip")
    addTag("ios-user")
}
```

```kotlin
// Android
Airship.channel.editTags {
    addTag("vip")
    addTag("android-user")
}.apply()
```

### Custom Notification Actions

Define custom actions users can take on notifications.

See SDK documentation for notification action configuration.

---

## Troubleshooting

If push notifications aren't working, consult the push troubleshooting guide:
- Check APNs/FCM configuration
- Verify credentials uploaded to dashboard
- Ensure channel ID is created
- Test on physical device (iOS)
- Check notification permissions granted

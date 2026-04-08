# Push Notification Troubleshooting Guide

This guide helps diagnose and fix common push notification issues with Airship SDK.

## Table of Contents

- [Not Receiving Notifications](#not-receiving-notifications)
- [Registration Failures](#registration-failures)
- [Channel ID Not Created](#channel-id-not-created)
- [Device Token Issues](#device-token-issues)
- [Foreground vs Background Issues](#foreground-vs-background-issues)
- [Platform-Specific Issues](#platform-specific-issues)

---

## Not Receiving Notifications

### iOS

**Check List:**

1. **APNs Configuration in Dashboard**
   - Go to Airship Dashboard → Settings → iOS Push Credentials
   - Verify certificate/key is uploaded and valid
   - Ensure environment matches (Production vs Development)

2. **Enable User Notifications**
   ```swift
   // SDK 20+
   Airship.push.userPushNotificationsEnabled = true

   // Request authorization
   let granted = await Airship.push.enableUserNotifications()
   print("Authorized: \(granted)")
   ```

3. **Check Privacy Manager**
   ```swift
   // Ensure push feature is enabled
   if !Airship.privacyManager.enabledFeatures.contains(.push) {
       Airship.privacyManager.enabledFeatures = [.push, .analytics]
   }
   ```

4. **Verify Device is Registered**
   ```swift
   // Check for device token
   Airship.push.onAPNSRegistrationFinished = { result in
       switch result {
       case .success(let token):
           print("✅ APNs Token: \(token)")
       case .failure(let error):
           print("❌ Registration failed: \(error)")
       }
   }
   ```

### Android

**Check List:**

1. **FCM Configuration**
   - Verify `google-services.json` is in `app/` directory
   - Check Firebase Console for valid FCM credentials
   - Upload FCM credentials to Airship Dashboard

2. **Enable User Notifications**
   ```kotlin
   // SDK 20+
   Airship.push.userNotificationsEnabled = true

   // For Android 13+, request permission
   if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
       Airship.permissionsManager.requestPermission(Permission.POST_NOTIFICATIONS) { result ->
           Log.d("Airship", "Permission: $result")
       }
   }
   ```

3. **Check Privacy Manager**
   ```kotlin
   // Ensure required features are enabled
   Airship.privacyManager.setEnabledFeatures(
       PrivacyManager.FEATURE_PUSH,
       PrivacyManager.FEATURE_ANALYTICS
   )
   ```

4. **Verify google-services Plugin**
   ```groovy
   // In app/build.gradle
   plugins {
       id 'com.google.gms.google-services'
   }
   ```

---

## Registration Failures

### iOS - APNs Registration

**Common Causes:**

1. **Missing Capabilities**
   - Enable Push Notifications in Xcode: Target → Signing & Capabilities → + Capability → Push Notifications

2. **Provisioning Profile Issues**
   - Ensure provisioning profile includes Push Notifications entitlement
   - Regenerate profile if needed

3. **Simulator Limitations**
   - APNs does NOT work in iOS Simulator
   - Always test on physical device

**Debug Registration:**
```swift
Airship.push.onAPNSRegistrationFinished = { result in
    switch result {
    case .success(let deviceToken):
        print("✅ APNs registered: \(deviceToken)")
    case .failure(let error):
        print("❌ APNs failed: \(error)")
        // Common errors:
        // - Network connection issues
        // - Invalid provisioning
        // - APNs unavailable
    }
}
```

### Android - FCM Registration

**Common Causes:**

1. **Missing google-services.json**
   - Download from Firebase Console → Project Settings
   - Place in `app/` directory (NOT `app/src/`)

2. **Incorrect Package Name**
   - Verify package name in `google-services.json` matches `applicationId` in `build.gradle`

3. **FCM Dependencies**
   ```groovy
   dependencies {
       implementation 'com.urbanairship.android:urbanairship-core:20.+'
       implementation 'com.urbanairship.android:urbanairship-fcm:20.+'
   }
   ```

---

## Channel ID Not Created

A Channel ID is required for all Airship operations. If it's not being created:

### Diagnostics

```swift
// iOS
let channelID = Airship.channel.identifier
print("Channel ID: \(channelID.isEmpty ? "NOT CREATED" : channelID)")
```

```kotlin
// Android
val channelID = Airship.channel.id
Log.d("Airship", "Channel ID: ${channelID ?: "NOT CREATED"}")
```

### Common Causes

1. **Privacy Manager Blocks Channel Creation**
   ```swift
   // iOS
   Airship.privacyManager.enabledFeatures = [.push, .analytics]
   ```

   ```kotlin
   // Android
   Airship.privacyManager.setEnabledFeatures(
       PrivacyManager.FEATURE_PUSH,
       PrivacyManager.FEATURE_ANALYTICS
   )
   ```

2. **SDK Not Initialized**
   - Ensure `Airship.takeOff()` is called early in app lifecycle
   - Check for errors during takeOff

3. **Network Connectivity**
   - Channel registration requires network access
   - Check device connectivity

---

## Device Token Issues

### iOS - APNs Token Not Generated

**Check:**

1. **Entitlements**
   - Push Notifications capability must be enabled in Xcode

2. **Environment Mismatch**
   - Development builds use sandbox APNs
   - Production builds use production APNs
   - Ensure certificates match environment

3. **Token Refresh**
   ```swift
   // Token can change - always update on each app launch
   Airship.push.onAPNSRegistrationFinished = { result in
       if case .success(let token) = result {
           print("Updated token: \(token)")
       }
   }
   ```

### Android - FCM Token Not Generated

**Check:**

1. **Google Play Services**
   - Ensure device has Google Play Services installed
   - Update to latest version

2. **Firebase Initialization**
   - Verify `google-services.json` is correctly placed
   - Check Gradle sync completed successfully

---

## Foreground vs Background Issues

### Notifications Work in Foreground But Not Background

**iOS:**

Configure presentation options:
```swift
Airship.push.notificationOptions = [.alert, .badge, .sound]

// Customize foreground presentation
Airship.push.onExtendPresentationOptions = { notification, options in
    // Always show alerts even in foreground
    return options.union([.list, .banner])
}
```

**Android:**

```kotlin
// Notifications automatically work in background
// For foreground control:
Airship.addAirshipListener(object : AirshipListener {
    override fun onPushReceived(context: Context, pushMessage: PushMessage) {
        // Called when push received (foreground or background)
        Log.d("Airship", "Push: ${pushMessage.alert}")
    }
})
```

---

## Platform-Specific Issues

### iOS-Specific

**Critical Notification Alerts Not Working:**
- Ensure notification contains `"interruption-level": "critical"`
- Enable Critical Alerts entitlement in Xcode

**Badge Count Not Updating:**
```swift
// Manual badge update
Airship.push.badgeNumber = 5

// Auto-badge (set in notification payload)
// "badge": "+1" or "badge": "auto"
```

### Android-Specific

**Notification Channels:**
```kotlin
// Create custom notification channel
val channel = NotificationChannelCompat(
    id = "custom_channel",
    name = "Custom Notifications",
    importance = NotificationManagerCompat.IMPORTANCE_HIGH
)

NotificationChannelRegistry.shared.createNotificationChannel(channel)
```

**Notification Not Showing on Android 13+:**
- Must request `POST_NOTIFICATIONS` permission
- Check permission status:
```kotlin
val hasPermission = Airship.permissionsManager.checkPermissionStatus(
    Permission.POST_NOTIFICATIONS
) == PermissionsManager.PermissionStatus.GRANTED
```

---

## Datacenter Issues

### Wrong Datacenter Configuration

**Symptoms:**
- 401 Unauthorized errors
- Channel registration fails
- API calls fail

**Fix:**

**iOS (AirshipConfig.plist):**
```xml
<key>site</key>
<string>eu</string>  <!-- For EU datacenter -->
```

**Android (airshipconfig.properties):**
```properties
site = EU  # For EU datacenter
```

**Default is US datacenter** - only set `site` if using EU.

---

## Testing Checklist

1. ✅ SDK initialized with valid credentials
2. ✅ User notifications enabled (`userPushNotificationsEnabled = true`)
3. ✅ Privacy Manager has push features enabled
4. ✅ Channel ID created (check logs)
5. ✅ Device token/registration token generated
6. ✅ APNs/FCM credentials uploaded to Airship Dashboard
7. ✅ Correct datacenter configured (US vs EU)
8. ✅ Test notification sent to Channel ID from dashboard
9. ✅ Physical device used for testing (not simulator for iOS)
10. ✅ Network connectivity available

---

## Getting More Help

If issues persist:

1. Enable SDK logging:
   ```swift
   // iOS
   Airship.logLevel = .trace
   ```

   ```kotlin
   // Android - in airshipconfig.properties
   logLevel = VERBOSE
   ```

2. Check logs for errors during:
   - SDK initialization
   - Channel registration
   - Push registration

3. Contact Airship Support with:
   - Platform and SDK version
   - Channel ID
   - Error messages from logs
   - Steps to reproduce

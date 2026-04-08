# Flutter Push Notification Troubleshooting

This guide covers Flutter-specific push notification issues when using `airship_flutter`.

## Common Issues

### 1. Push Notifications Not Receiving

**Symptoms:**
- Device not receiving any push notifications
- Notifications work on one platform but not the other

**Checklist:**

1. **Verify Plugin Installation**

Check `pubspec.yaml`:
```yaml
dependencies:
  airship_flutter: ^8.0.0  # Use latest version
```

Install dependencies:
```bash
flutter pub get

# iOS: Install CocoaPods
cd ios && pod install && cd ..

# Rebuild
flutter clean
flutter run
```

2. **Enable User Notifications in Dart**
```dart
import 'package:airship_flutter/airship_flutter.dart';

// Enable user notifications
await Airship.push.setUserNotificationsEnabled(true);

// iOS: Enable foreground presentation
await Airship.push.iOS.setForegroundPresentationOptions([
  iOSForegroundPresentationOption.list,
  iOSForegroundPresentationOption.banner,
  iOSForegroundPresentationOption.sound,
]);

// Android 13+: Request permission
final permissionStatus = await Airship.push.android.requestPermission();
print('Permission status: $permissionStatus');
```

3. **Check Channel Registration**
```dart
// Listen for push token
Airship.push.onPushTokenReceived.listen((event) {
  print('✅ Push token: ${event.token}');
});

// Get channel ID
final channelId = await Airship.channel.channelId;
print('Channel ID: $channelId');
```

4. **Verify Native Configuration**

**iOS:**
- AirshipConfig.plist exists and is in the Xcode project
- APNs credentials uploaded to Airship dashboard
- iOS deployment target is 14.0+

**Android:**
- google-services.json in android/app/ directory
- FCM credentials uploaded to Airship dashboard
- Minimum SDK version is 23

### 2. iOS Build Errors

**Error:** `'AirshipKit/AirshipKit.h' file not found`

**Solutions:**

1. **Install CocoaPods dependencies**
```bash
cd ios
pod install
pod update
cd ..
```

2. **Clean build**
```bash
flutter clean
cd ios
rm -rf Pods Podfile.lock
pod install
cd ..
flutter build ios
```

3. **Verify Podfile minimum iOS version**
```ruby
# ios/Podfile
platform :ios, '14.0'
```

### 3. Android Build Errors

**Error:** `Could not find com.urbanairship.android:urbanairship-*`

**Solutions:**

1. **Verify google-services.json**
```bash
# Should exist in android/app/
ls -la android/app/google-services.json
```

2. **Check android/build.gradle**
```gradle
buildscript {
    dependencies {
        classpath 'com.google.gms:google-services:4.4.0'
    }
}

allprojects {
    repositories {
        google()
        mavenCentral()
    }
}
```

3. **Check android/app/build.gradle**
```gradle
// At the bottom of the file
apply plugin: 'com.google.gms.google-services'
```

4. **Clean and rebuild**
```bash
cd android
./gradlew clean
./gradlew --refresh-dependencies
cd ..
flutter clean
flutter build apk
```

### 4. MissingPluginException

**Error:** `MissingPluginException(No implementation found for method ...)`

**Solutions:**

1. **Hot restart instead of hot reload**
```bash
# In Flutter dev mode, press 'R' (capital R) for hot restart
# Or stop and restart:
flutter run
```

2. **Rebuild the app**
```bash
flutter clean
flutter pub get
flutter run
```

3. **Verify plugin registration (should be automatic)**

The plugin should auto-register. If using custom main.dart:
```dart
import 'package:flutter/material.dart';
import 'package:airship_flutter/airship_flutter.dart';

void main() {
  runApp(MyApp());
}
```

### 5. Channel ID Not Created

**Symptoms:**
- `Airship.channel.channelId` returns `null`
- Can't send notifications

**Solutions:**

1. **Enable required privacy features**
```dart
import 'package:airship_flutter/airship_flutter.dart';

// Enable features for channel creation
await Airship.privacyManager.setEnabledFeatures([
  Feature.push,
  Feature.analytics,
]);

// Listen for channel creation
Airship.channel.onChannelCreated.listen((event) {
  print('Channel created: ${event.channelId}');
});

// Check channel ID
final channelId = await Airship.channel.channelId;
if (channelId != null) {
  print('Channel ID: $channelId');
} else {
  print('Channel not created - check privacy features');
}
```

2. **Verify takeOff called early**
```dart
// In main.dart, before runApp
void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Configure and take off
  await Airship.takeOff();

  // Enable notifications
  await Airship.push.setUserNotificationsEnabled(true);

  runApp(MyApp());
}
```

### 6. iOS Notifications Not Showing in Foreground

**Solution:**

Enable foreground presentation options:

```dart
import 'package:airship_flutter/airship_flutter.dart';

await Airship.push.iOS.setForegroundPresentationOptions([
  iOSForegroundPresentationOption.list,
  iOSForegroundPresentationOption.banner,
  iOSForegroundPresentationOption.sound,
  iOSForegroundPresentationOption.badge,
]);
```

### 7. Android 13+ Permission Issues

**Symptoms:**
- Notifications not showing on Android 13+ devices
- Permission not requested

**Solution:**

Request POST_NOTIFICATIONS permission:

```dart
import 'package:airship_flutter/airship_flutter.dart';

// Android 13+ requires runtime permission
if (Platform.isAndroid) {
  final status = await Airship.push.android.requestPermission();
  print('Notification permission: $status');

  // Check current status
  final enabled = await Airship.push.android.isNotificationPermissionEnabled();
  print('Notifications enabled: $enabled');
}
```

### 8. Push Token Not Updating

**Symptoms:**
- Old push token still active
- Token not refreshing after reinstall

**Solutions:**

1. **Listen for token updates**
```dart
Airship.push.onPushTokenReceived.listen((event) {
  print('Updated token: ${event.token}');
  // Send to your backend if needed
});
```

2. **Force channel update**
```dart
// Not directly available - reinstall app or clear data
// iOS: Delete and reinstall app
// Android: Clear app data via settings
```

### 9. ProGuard/R8 Issues (Android Release Builds)

**Symptoms:**
- Push works in debug but not release builds
- Crashes in release mode

**Solution:**

The plugin includes ProGuard rules automatically, but if issues persist, add to `android/app/proguard-rules.pro`:

```proguard
-keep class com.urbanairship.** { *; }
-dontwarn com.urbanairship.**
```

### 10. Null Safety Issues

If using older Dart versions or encountering null safety errors:

```dart
// Use null-aware operators
final channelId = await Airship.channel.channelId;
if (channelId != null) {
  print('Channel: $channelId');
}

// Safe subscription cleanup
StreamSubscription? _tokenSubscription;

void setupListeners() {
  _tokenSubscription = Airship.push.onPushTokenReceived.listen((event) {
    print('Token: ${event.token}');
  });
}

@override
void dispose() {
  _tokenSubscription?.cancel();
  super.dispose();
}
```

## Platform-Specific Configuration

### iOS Configuration

**AirshipConfig.plist:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>developmentAppKey</key>
    <string>YOUR_DEV_APP_KEY</string>
    <key>developmentAppSecret</key>
    <string>YOUR_DEV_APP_SECRET</string>
    <key>productionAppKey</key>
    <string>YOUR_PROD_APP_KEY</string>
    <key>productionAppSecret</key>
    <string>YOUR_PROD_APP_SECRET</string>
    <key>inProduction</key>
    <false/>
</dict>
</plist>
```

**File location:** `ios/Runner/AirshipConfig.plist`

Ensure it's added to your Xcode project target.

### Android Configuration

**airshipconfig.properties:**
```properties
developmentAppKey = YOUR_DEV_APP_KEY
developmentAppSecret = YOUR_DEV_APP_SECRET
productionAppKey = YOUR_PROD_APP_KEY
productionAppSecret = YOUR_PROD_APP_SECRET
inProduction = false
```

**File location:** `android/app/src/main/assets/airshipconfig.properties`

**google-services.json:**
- Download from Firebase Console
- Place in `android/app/google-services.json`

## Testing Push Notifications

1. **Get Channel ID**
```dart
final channelId = await Airship.channel.channelId;
print('Test with Channel ID: $channelId');
```

2. **Send Test Push from Dashboard**
- Go to Airship Dashboard → Messages → Create Test Message
- Set audience to your Channel ID
- Send and verify receipt

3. **Check Logs**
```bash
# Run with verbose logging
flutter run -v

# iOS logs
flutter logs

# Android logs
flutter logs
# or
adb logcat -s flutter
```

4. **Debug Push Reception**
```dart
// Listen for all push events
Airship.push.onNotificationResponse.listen((event) {
  print('Notification response: ${event.actionId}');
  print('Notification: ${event.notification}');
});

Airship.push.onPushReceived.listen((event) {
  print('Push received: ${event.notification}');
});
```

## Common Configuration Mistakes

1. **❌ Missing google-services.json (Android)**
   - Place in `android/app/` directory, not `android/`

2. **❌ AirshipConfig.plist not in Xcode target (iOS)**
   - Right-click in Xcode → Add Files
   - Check "Add to targets"

3. **❌ Wrong credentials for environment**
   - Development credentials for debug builds
   - Production credentials for release builds
   - Set `inProduction` accordingly

4. **❌ Not calling takeOff early enough**
   - Call in `main()` before `runApp()`
   - Use `WidgetsFlutterBinding.ensureInitialized()` first

5. **❌ Privacy features not enabled**
   - Must enable `Feature.push` at minimum
   - Enable `Feature.analytics` for better tracking

## Additional Resources

- [Flutter Airship README](../setup/README.md)
- [Migration Guide](../setup/MIGRATION.md)
- [Airship Flutter Plugin Repo](https://github.com/urbanairship/airship-flutter)
- [Shared Push Troubleshooting Guide](../../shared/troubleshooting/push-troubleshooting.md)
- [Airship Flutter Documentation](https://docs.airship.com/platform/mobile/setup/sdk/flutter/)

## Getting Help

If issues persist:
1. Check GitHub issues: https://github.com/urbanairship/airship-flutter/issues
2. Contact Airship Support: https://support.airship.com
3. Review Flutter-specific docs: https://docs.airship.com/platform/mobile/setup/sdk/flutter/

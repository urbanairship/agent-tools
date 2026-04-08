# React Native Push Notification Troubleshooting

This guide covers React Native-specific push notification issues when using `@ua/react-native-airship`.

## Common Issues

### 1. Push Notifications Not Receiving

**Symptoms:**
- Device not receiving any push notifications
- Notifications work in one environment (dev/prod) but not the other

**Checklist:**

1. **Verify Plugin Installation**
```bash
npm list @ua/react-native-airship
# Should show installed version

# If not installed:
npm install @ua/react-native-airship

# Rebuild native projects
cd ios && pod install && cd ..
cd android && ./gradlew clean && cd ..
```

2. **Enable User Notifications in JavaScript**
```javascript
import Airship from '@ua/react-native-airship';

// Enable push notifications
Airship.push.setUserNotificationsEnabled(true);

// iOS: Set foreground presentation options
Airship.push.iOS.setForegroundPresentationOptions({
  alert: true,
  sound: true,
  badge: true
});

// Android 13+: Request permission
Airship.push.android.requestPermission();
```

3. **Check Channel Registration**
```javascript
// Listen for push token
Airship.push.onPushTokenReceived.subscribe((event) => {
  console.log('✅ Push token:', event.pushToken);
});

// Get channel ID
const channelId = await Airship.channel.getChannelId();
console.log('Channel ID:', channelId);
```

4. **Verify Native Configuration**

**iOS:**
- AirshipConfig.plist exists and is in the Xcode target
- APNs credentials uploaded to Airship dashboard
- App has notification capabilities enabled

**Android:**
- google-services.json in app/ directory
- FCM credentials uploaded to Airship dashboard
- google-services plugin applied in app/build.gradle

### 2. Module Not Found Errors

**Error:** `Unable to resolve module @ua/react-native-airship`

**Solutions:**

1. **Clear Metro bundler cache**
```bash
npm start -- --reset-cache
# or
npx react-native start --reset-cache
```

2. **Reinstall dependencies**
```bash
rm -rf node_modules package-lock.json
npm install
cd ios && pod install && cd ..
```

3. **Rebuild native projects**
```bash
# iOS
cd ios && rm -rf Pods Podfile.lock && pod install && cd ..
npx react-native run-ios

# Android
cd android && ./gradlew clean && cd ..
npx react-native run-android
```

### 3. iOS Build Errors After Installation

**Error:** `ld: framework not found AirshipKit`

**Solutions:**

1. **Install CocoaPods dependencies**
```bash
cd ios
pod install
cd ..
```

2. **Clean build folder in Xcode**
- Product → Clean Build Folder (Cmd+Shift+K)
- Rebuild the project

3. **Verify Podfile has correct source**
```ruby
source 'https://cdn.cocoapods.org/'
```

### 4. Android Build Errors

**Error:** `Could not find com.urbanairship.android:urbanairship-*`

**Solutions:**

1. **Verify Maven repositories in android/build.gradle**
```gradle
allprojects {
    repositories {
        google()
        mavenCentral()
    }
}
```

2. **Sync Gradle files**
```bash
cd android
./gradlew clean
./gradlew --refresh-dependencies
cd ..
```

3. **Check react-native.config.js**

The module should auto-link. If you have a react-native.config.js, ensure it doesn't exclude Airship:

```javascript
module.exports = {
  dependencies: {
    '@ua/react-native-airship': {
      // Should auto-link by default
    }
  }
};
```

### 5. Push Token Not Updating

**Symptoms:**
- Old push token still being used
- Token not refreshing after reinstall

**Solutions:**

1. **Force channel update**
```javascript
import Airship from '@ua/react-native-airship';

// Force channel update
await Airship.channel.updateRegistration();

// Get latest token
Airship.push.onPushTokenReceived.subscribe((event) => {
  console.log('Latest token:', event.pushToken);
});
```

2. **Clear app data and reinstall**
```bash
# iOS: Delete app from device and reinstall
npx react-native run-ios

# Android: Clear app data
adb shell pm clear com.your.package.name
npx react-native run-android
```

### 6. Channel ID Not Created

**Symptoms:**
- `Airship.channel.getChannelId()` returns `null`
- Can't send notifications

**Solutions:**

1. **Enable required privacy features**
```javascript
import Airship, { Feature } from '@ua/react-native-airship';

// Enable features required for channel creation
Airship.privacyManager.setEnabledFeatures([
  Feature.Push,
  Feature.Analytics
]);

// Wait for channel creation
Airship.channel.onChannelCreated.subscribe((event) => {
  console.log('Channel created:', event.channelId);
});
```

2. **Check configuration**
```javascript
// Verify takeOff was called
// Should be in index.js or App.js before app initialization

import Airship from '@ua/react-native-airship';

// Take off should happen before rendering
Airship.takeOff();

// Then enable notifications
Airship.push.setUserNotificationsEnabled(true);
```

### 7. Notifications Not Showing in Foreground

**iOS Specific:**

```javascript
import Airship from '@ua/react-native-airship';

// Enable foreground presentation
Airship.push.iOS.setForegroundPresentationOptions({
  alert: true,
  sound: true,
  badge: true
});
```

**Android Specific:**

Android shows notifications in foreground by default. If not showing:

1. Check notification channel creation (Android 8+)
2. Verify notification permissions granted
3. Check system notification settings

### 8. Expo Compatibility

**Important:** The native Airship SDK is **not compatible** with Expo Go. You must:

1. Use Expo with custom dev client (expo-dev-client)
2. Or eject to bare React Native workflow

```bash
# Option 1: Add custom dev client
npx expo install expo-dev-client
npx expo prebuild
npx expo run:ios  # or expo run:android

# Option 2: Eject (creates android/ and ios/ folders)
npx expo eject
```

## Platform-Specific Notes

### iOS

- Minimum iOS version: 14.0
- Xcode 15.2+ required
- Swift 5.0+
- CocoaPods required for native dependencies

### Android

- Minimum SDK: 23 (Android 6.0)
- Compile SDK: 34+
- Gradle 8.0+
- Kotlin 1.9.24+

## Testing Push Notifications

1. **Get Channel ID**
```javascript
const channelId = await Airship.channel.getChannelId();
console.log('Test with Channel ID:', channelId);
```

2. **Send Test Push from Dashboard**
- Go to Airship Dashboard → Messages → Create Test Message
- Set audience to your Channel ID
- Send and verify receipt

3. **Check Logs**
```bash
# iOS
npx react-native log-ios

# Android
npx react-native log-android
```

## Additional Resources

- [React Native Airship README](./setup/README.md)
- [Migration Guide](./setup/MIGRATION.md)
- [Airship React Native Repo](https://github.com/urbanairship/react-native-airship)
- [Shared Push Troubleshooting Guide](../../shared/troubleshooting/push-troubleshooting.md)

## Getting Help

If issues persist:
1. Check GitHub issues: https://github.com/urbanairship/react-native-airship/issues
2. Contact Airship Support: https://support.airship.com
3. Review React Native Airship documentation: https://docs.airship.com/platform/mobile/setup/sdk/react-native/

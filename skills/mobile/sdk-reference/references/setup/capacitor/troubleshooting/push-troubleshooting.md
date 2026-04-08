# Capacitor Push Notification Troubleshooting

This guide covers Capacitor-specific push notification issues when using `@ua/capacitor-airship`.

## Common Issues

### 1. Push Notifications Not Receiving

**Symptoms:**
- Device not receiving any push notifications
- Notifications work on one platform but not the other

**Checklist:**

1. **Verify Plugin Installation**

Check `package.json`:
```json
{
  "dependencies": {
    "@capacitor/core": "^6.0.0",
    "@capacitor/ios": "^6.0.0",
    "@capacitor/android": "^6.0.0",
    "@ua/capacitor-airship": "^2.0.0"
  }
}
```

Install and sync:
```bash
npm install @ua/capacitor-airship

# Sync native projects
npx cap sync

# iOS: Install pods
cd ios/App && pod install && cd ../..

# Rebuild
npx cap run ios  # or npx cap run android
```

2. **Enable User Notifications**
```typescript
import { Airship } from '@ua/capacitor-airship';

// Enable user notifications
await Airship.push.setUserNotificationsEnabled({ enabled: true });

// iOS: Enable foreground presentation
await Airship.push.iOS.setForegroundPresentationOptions({
  options: ['banner', 'list', 'sound', 'badge']
});

// Android 13+: Request permission
const result = await Airship.push.android.requestPermission();
console.log('Permission result:', result);
```

3. **Check Channel Registration**
```typescript
// Listen for push token
Airship.push.onPushTokenReceived((event: any) => {
  console.log('✅ Push token:', event.token);
});

// Get channel ID
const result = await Airship.channel.getChannelId();
console.log('Channel ID:', result.channelId);
```

4. **Verify Native Configuration**

**iOS:**
- AirshipConfig.plist in `ios/App/App/` directory
- APNs credentials uploaded to Airship dashboard
- Push capabilities enabled in Xcode

**Android:**
- google-services.json in `android/app/` directory
- FCM credentials uploaded to Airship dashboard
- google-services plugin applied

### 2. Plugin Not Found

**Error:** `Cannot find module '@ua/capacitor-airship'`

**Solutions:**

1. **Install plugin**
```bash
npm install @ua/capacitor-airship
```

2. **Sync Capacitor**
```bash
npx cap sync
```

3. **Clear node_modules and reinstall**
```bash
rm -rf node_modules package-lock.json
npm install
npx cap sync
```

### 3. iOS Build Errors

**Error:** `Module 'AirshipKit' not found`

**Solutions:**

1. **Install CocoaPods dependencies**
```bash
cd ios/App
pod install
cd ../..
```

2. **Clean and rebuild**
```bash
npx cap sync ios
cd ios/App
rm -rf Pods Podfile.lock
pod install
cd ../..
npx cap run ios
```

3. **Update Podfile iOS version**
```ruby
# ios/App/Podfile
platform :ios, '14.0'
```

### 4. Android Build Errors

**Error:** `Could not find com.urbanairship.android:urbanairship-*`

**Solutions:**

1. **Verify google-services.json location**
```bash
# Should be in android/app/
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
// At the bottom
apply plugin: 'com.google.gms.google-services'
```

4. **Sync and rebuild**
```bash
npx cap sync android
cd android
./gradlew clean
./gradlew build
cd ..
```

### 5. Web Platform Not Supported

**Important:** The Capacitor Airship plugin only supports **iOS** and **Android**. Web is not supported.

If you need web push:
- Use Airship Web SDK separately
- Conditional imports based on platform:

```typescript
import { Capacitor } from '@capacitor/core';

if (Capacitor.getPlatform() === 'web') {
  // Use Airship Web SDK
} else {
  // Use Capacitor plugin
  import { Airship } from '@ua/capacitor-airship';
}
```

### 6. Channel ID Not Created

**Symptoms:**
- `getChannelId()` returns `null` or empty
- Can't send notifications

**Solutions:**

1. **Enable privacy features**
```typescript
import { Airship, Feature } from '@ua/capacitor-airship';

// Enable required features
await Airship.privacyManager.setEnabledFeatures({
  features: [Feature.Push, Feature.Analytics]
});

// Listen for channel creation
Airship.channel.onChannelCreated((event: any) => {
  console.log('Channel created:', event.channelId);
});

// Check channel ID
const result = await Airship.channel.getChannelId();
console.log('Channel ID:', result.channelId);
```

2. **Verify takeOff configuration**

The plugin should auto-configure from config files, but you can also configure programmatically:

```typescript
// Usually not needed - plugin reads from config files
// But available if you need dynamic configuration
await Airship.takeOff({
  development: {
    appKey: 'YOUR_DEV_KEY',
    appSecret: 'YOUR_DEV_SECRET'
  },
  production: {
    appKey: 'YOUR_PROD_KEY',
    appSecret: 'YOUR_PROD_SECRET'
  },
  inProduction: false
});
```

### 7. TypeScript Errors

**Error:** `Property 'push' does not exist on type 'typeof Airship'`

**Solutions:**

1. **Ensure TypeScript types are installed**
```bash
npm install --save-dev @ua/capacitor-airship
```

2. **Check tsconfig.json**
```json
{
  "compilerOptions": {
    "moduleResolution": "node",
    "esModuleInterop": true
  }
}
```

3. **Use correct import**
```typescript
// Correct
import { Airship, Feature } from '@ua/capacitor-airship';

// Incorrect
import Airship from '@ua/capacitor-airship';
```

### 8. Events Not Firing

**Symptoms:**
- onPushReceived not triggering
- onNotificationResponse not working

**Solutions:**

1. **Register listeners early**
```typescript
// In app initialization (main.ts or App.vue/App.tsx)
import { Airship } from '@ua/capacitor-airship';

// Register listeners before other app logic
Airship.push.onPushReceived((event: any) => {
  console.log('Push received:', event.notification);
});

Airship.push.onNotificationResponse((event: any) => {
  console.log('Notification tapped:', event.actionId);
  console.log('Notification data:', event.notification);
});
```

2. **For Ionic/Angular, use Platform.ready()**
```typescript
import { Platform } from '@ionic/angular';
import { Airship } from '@ua/capacitor-airship';

constructor(private platform: Platform) {
  this.platform.ready().then(() => {
    this.setupAirship();
  });
}

async setupAirship() {
  await Airship.push.setUserNotificationsEnabled({ enabled: true });

  Airship.push.onNotificationResponse((event: any) => {
    console.log('Notification response:', event);
  });
}
```

3. **For Vue, use mounted() hook**
```typescript
import { Airship } from '@ua/capacitor-airship';

export default {
  async mounted() {
    await Airship.push.setUserNotificationsEnabled({ enabled: true });

    Airship.push.onNotificationResponse((event: any) => {
      console.log('Notification tapped:', event);
    });
  }
}
```

### 9. Android 13+ Permission Issues

**Symptoms:**
- Notifications not showing on Android 13+ devices

**Solution:**

Request POST_NOTIFICATIONS permission:

```typescript
import { Capacitor } from '@capacitor/core';
import { Airship } from '@ua/capacitor-airship';

if (Capacitor.getPlatform() === 'android') {
  const result = await Airship.push.android.requestPermission();
  console.log('Permission granted:', result.granted);

  // Check if permission is enabled
  const status = await Airship.push.android.isNotificationPermissionEnabled();
  console.log('Notifications enabled:', status.enabled);
}
```

### 10. Deep Links Not Working

**Symptoms:**
- App opens but doesn't navigate to correct screen
- Deep link URLs not being handled

**Solutions:**

1. **Handle notification response**
```typescript
Airship.push.onNotificationResponse((event: any) => {
  console.log('Notification response:', event);

  // Handle deep link
  if (event.notification.extras?.deepLink) {
    const url = event.notification.extras.deepLink;
    // Navigate using your router
    navigateTo(url);
  }

  // Or check action ID
  if (event.actionId === 'view_details') {
    // Navigate to details screen
  }
});
```

2. **For Ionic Router**
```typescript
import { Router } from '@angular/router';
import { Airship } from '@ua/capacitor-airship';

constructor(private router: Router) {}

setupDeepLinks() {
  Airship.push.onNotificationResponse((event: any) => {
    if (event.notification.extras?.route) {
      this.router.navigate([event.notification.extras.route]);
    }
  });
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

**File location:** `ios/App/App/AirshipConfig.plist`

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

## Framework-Specific Notes

### Ionic Angular

```typescript
// app.component.ts
import { Platform } from '@ionic/angular';
import { Airship } from '@ua/capacitor-airship';

constructor(private platform: Platform) {
  this.initializeApp();
}

async initializeApp() {
  await this.platform.ready();

  // Setup Airship
  await Airship.push.setUserNotificationsEnabled({ enabled: true });

  Airship.push.onNotificationResponse((event: any) => {
    // Handle notification tap
  });
}
```

### Ionic React

```tsx
// App.tsx
import { useEffect } from 'react';
import { Airship } from '@ua/capacitor-airship';
import { setupIonicReact } from '@ionic/react';

setupIonicReact();

function App() {
  useEffect(() => {
    setupAirship();
  }, []);

  const setupAirship = async () => {
    await Airship.push.setUserNotificationsEnabled({ enabled: true });

    Airship.push.onNotificationResponse((event: any) => {
      console.log('Notification tapped:', event);
    });
  };

  return <IonApp>...</IonApp>;
}
```

### Ionic Vue

```vue
<!-- App.vue -->
<script setup lang="ts">
import { onMounted } from 'vue';
import { Airship } from '@ua/capacitor-airship';

onMounted(async () => {
  await Airship.push.setUserNotificationsEnabled({ enabled: true });

  Airship.push.onNotificationResponse((event: any) => {
    console.log('Notification tapped:', event);
  });
});
</script>
```

## Testing Push Notifications

1. **Get Channel ID**
```typescript
const result = await Airship.channel.getChannelId();
console.log('Test with Channel ID:', result.channelId);
```

2. **Send Test Push from Dashboard**
- Go to Airship Dashboard → Messages → Create Test Message
- Set audience to your Channel ID
- Send and verify receipt

3. **Check Logs**
```bash
# iOS
npx cap run ios --livereload

# Android
npx cap run android --livereload

# View logs
npx cap open ios  # Then check Xcode console
npx cap open android  # Then check Android Studio logcat
```

4. **Enable debug logging**
```typescript
// In development, enable verbose logging
await Airship.push.setUserNotificationsEnabled({ enabled: true });

// Check push status
const enabled = await Airship.push.isUserNotificationsEnabled();
console.log('Notifications enabled:', enabled.enabled);
```

## Additional Resources

- [Capacitor Airship Plugin Repo](https://github.com/urbanairship/capacitor-airship)
- [Capacitor Documentation](https://capacitorjs.com/docs)
- [Shared Push Troubleshooting Guide](../../shared/troubleshooting/push-troubleshooting.md)
- [Airship Documentation](https://docs.airship.com)

## Getting Help

If issues persist:
1. Check GitHub issues: https://github.com/urbanairship/capacitor-airship/issues
2. Contact Airship Support: https://support.airship.com
3. Review Capacitor docs: https://capacitorjs.com/docs

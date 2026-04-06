# Configuration Troubleshooting Guide

Common Airship configuration issues and solutions.

## Missing AirshipConfig File

### iOS - AirshipConfig.plist

**Create the file:**
1. Xcode → File → New → File → Property List
2. Name: `AirshipConfig.plist`
3. Add to app target (check target membership)

**Required keys:**
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
</dict>
</plist>
```

### Android - airshipconfig.properties

**Create the file:**
- Path: `app/src/main/assets/airshipconfig.properties`

**Required properties:**
```properties
developmentAppKey = YOUR_DEV_APP_KEY
developmentAppSecret = YOUR_DEV_APP_SECRET
productionAppKey = YOUR_PROD_APP_KEY
productionAppSecret = YOUR_PROD_APP_SECRET
inProduction = false
```

## Invalid Credentials

**Symptoms:**
- 401 Unauthorized errors
- SDK initialization fails
- Channel creation fails

**Solutions:**

1. **Verify Credentials in Dashboard**
   - Log into Airship Dashboard
   - Settings → APIs & Integrations
   - Copy exact values (no extra spaces)

2. **Check Environment**
   - Development vs Production credentials
   - Ensure using correct set for build type

3. **Replace Placeholders**
   - Remove `YOUR_*` placeholder text
   - Use actual credentials from dashboard

## Wrong Datacenter

**Symptoms:**
- 401/403 errors despite valid credentials
- Registration failures

**Solution:**

If your Airship account is on **EU datacenter**, you MUST configure:

**iOS:**
```xml
<key>site</key>
<string>eu</string>
```

**Android:**
```properties
site = EU
```

**Default is US** - only set if using EU datacenter.

## SDK Not Initializing

### Check Initialization

**iOS:**
```swift
// In App initialization
import Airship
import AirshipKit

@main
struct MyApp: App {
    init() {
        Airship.takeOff()  // Should be called early
    }
}

// Verify it worked
if Airship.isFlying {
    print("✅ Airship initialized")
} else {
    print("❌ Airship failed to initialize")
}
```

**Android:**
```kotlin
class MyAutopilot : Autopilot() {
    override fun onAirshipReady(context: Context) {
        Log.d("Airship", "✅ SDK ready")
    }
}

// In AndroidManifest.xml
<meta-data
    android:name="com.urbanairship.autopilot"
    android:value="com.yourpackage.MyAutopilot" />
```

### Common Initialization Issues

1. **Missing Config File**
   - Verify file exists and is in correct location
   - Check file is included in app target (iOS)

2. **Invalid Format**
   - Validate XML/property syntax
   - No extra characters or encoding issues

3. **Timing Issues**
   - Call `takeOff()` early in app lifecycle
   - Don't delay initialization

## Build Configuration Errors

### iOS

**SPM Issues:**
- Clean build folder: Product → Clean Build Folder
- Reset package cache: File → Packages → Reset Package Caches
- Update packages: File → Packages → Update to Latest Package Versions

**CocoaPods Issues:**
```bash
cd ios
pod deintegrate
pod install
```

### Android

**Gradle Sync Issues:**
```bash
./gradlew clean
./gradlew --stop
./gradlew build
```

**ProGuard/R8 Issues:**
```groovy
// In proguard-rules.pro
-keep class com.urbanairship.** { *; }
-dontwarn com.urbanairship.**
```

## Configuration Validation

Use the `analyze_project` tool to automatically check for configuration issues:

```
Airship Doctor → analyze_project
Platform: iOS/Android
Path: /path/to/your/project
```

This will identify:
- Missing config files
- Invalid credentials
- Dependency issues
- Build configuration problems

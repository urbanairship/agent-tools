# Preference Center Troubleshooting Guide

Common Preference Center issues and solutions.

## Preference Center Not Displaying

### iOS (SDK 20+)

**Display Preference Center:**
```swift
import AirshipPreferenceCenter

// Full Preference Center with navigation
PreferenceCenterView(preferenceCenterID: "your-preference-center-id")

// Or programmatically
Airship.preferenceCenter.display("your-preference-center-id")
```

**SDK 20 Changes:**
- `PreferenceCenterList` → `PreferenceCenterContent`
- Use `PreferenceCenterView` for full UI with navigation
- Use `PreferenceCenterContent` for custom navigation

### Android

**Add Dependency:**
```groovy
dependencies {
    // Traditional View-based UI
    implementation 'com.urbanairship.android:urbanairship-preference-center:20.+'

    // OR Jetpack Compose
    implementation 'com.urbanairship.android:urbanairship-preference-center-compose:20.+'
}
```

**Display:**
```kotlin
// View-based
PreferenceCenter.shared().open("preference-center-id")

// Compose
@Composable
fun MySettings() {
    PreferenceCenterScreen("preference-center-id")
}
```

## Configuration Not Loading

**Common Causes:**

1. **Invalid Preference Center ID**
   - Verify ID matches dashboard configuration
   - Check for typos

2. **Network Issues**
   - Configuration fetched from Airship servers
   - Requires internet connectivity

3. **Privacy Manager**
   ```swift
   // iOS
   Airship.privacyManager.enabledFeatures.insert(.preferenceCenter)
   ```

   ```kotlin
   // Android
   Airship.privacyManager.setEnabledFeatures(PrivacyManager.FEATURE_PREFERENCE_CENTER)
   ```

## Preference Changes Not Saving

**Check:**

1. **Channel ID Valid**
   - Preferences tied to channel
   - Verify channel created

2. **Network Connectivity**
   - Changes sync to Airship servers

3. **SDK Version**
   - Ensure using latest SDK version
   - Check for known issues

## Customization

### iOS

```swift
PreferenceCenterView(preferenceCenterID: "my-center")
    .preferenceCenterContentStyle(CustomStyle())
```

### Android

See SDK documentation for Preference Center theming options.

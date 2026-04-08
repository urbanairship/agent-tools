# Preference Center Implementation Guide

Guide to implementing Airship Preference Center.

## Overview

Preference Center allows users to manage notification preferences.

## Setup in Airship Dashboard

1. Go to Airship Dashboard → Settings → Preference Center
2. Create new Preference Center configuration
3. Define preference options (subscription lists, notification types, etc.)
4. Note the Preference Center ID

## iOS Implementation

### 1. Display Preference Center

```swift
import AirshipPreferenceCenter

// Full Preference Center with navigation
PreferenceCenterView(preferenceCenterID: "your-preference-center-id")

// Programmatic display
Airship.preferenceCenter.display("your-preference-center-id")
```

### 2. Customize Styling

```swift
PreferenceCenterView(preferenceCenterID: "my-center")
    .preferenceCenterContentStyle(CustomStyle())
```

## Android Implementation

### 1. Add Dependency

```groovy
dependencies {
    // Traditional View-based UI
    implementation 'com.urbanairship.android:urbanairship-preference-center:20.+'

    // OR Jetpack Compose
    implementation 'com.urbanairship.android:urbanairship-preference-center-compose:20.+'
}
```

### 2. Display Preference Center

**View-based:**
```kotlin
import com.urbanairship.preferencecenter.PreferenceCenter

PreferenceCenter.shared().open("preference-center-id")
```

**Jetpack Compose:**
```kotlin
import com.urbanairship.preferencecenter.compose.ui.PreferenceCenterScreen

@Composable
fun MySettings() {
    PreferenceCenterScreen("preference-center-id")
}
```

## Testing

1. Configure Preference Center in Airship Dashboard
2. Open Preference Center in app
3. Modify preferences
4. Verify changes sync to Airship

# Preference Center Setup - Android

Preference Center allows users to opt in and out of subscription lists configured via the Airship Dashboard.

## Displaying a Preference Center

A Preference Center can be displayed in its own window with the provided Airship UI with a single method call. By wiring this method call to a button in your app, you can quickly produce a user-initiated Preference Center with no additional effort.

### Kotlin

```kotlin
PreferenceCenter.shared().open("my-first-pref-center")
```

### Java

```java
PreferenceCenter.shared().open("my-first-pref-center");
```

## Styling the Preference Center

Most developers will want to customize the look and feel to match their app's existing style and layout. Android supports customizing through a styling config. See the [Android custom style guide](https://docs.airship.com/platform/mobile/preference-center/custom/android/) for more information.

## Custom Preference Centers

If the provided preference center is insufficient for your app, you can build your own UI. Currently, preference center is limited to modifying subscription lists.

Example implementations are available in the [Android SDK repository](https://github.com/urbanairship/android-library-dev/blob/main/urbanairship-preference-center/src/main/java/com/urbanairship/preferencecenter/ui/PreferenceCenterActivity.kt).

### Fetching Preference Center Config

When creating a custom preference center, you will need to fetch the config from the Airship SDK. The config might not be available right away on first app start.

#### Kotlin

```kotlin
val configPendingResult = PreferenceCenter.shared().getConfig(preferenceCenterId)
```

#### Java

```java
PendingResult<PreferenceCenterConfig> configPendingResult = PreferenceCenter.shared().getConfig(preferenceCenterId);
```

### Overriding the Open Behavior

To override the default preference center handling, set a listener to handle displaying the preference center and to prevent the Airship SDK from displaying the OOTB UI.

Set the `PreferenceCenterOpenListener` during the onAirshipReady callback:

#### Kotlin

```kotlin
PreferenceCenter.shared().openListener =  object : PreferenceCenter.OnOpenListener {
    override fun onOpenPreferenceCenter(preferenceCenterId: String): Boolean {
      // Navigate to custom preference center UI

      // true to prevent default behavior
      // false for default Airship handling
      return true
    }
}
```

#### Java

```java
PreferenceCenter.shared().setOpenListener(preferenceCenterId -> {
    // Navigate to custom preference center UI

    // true to prevent default behavior
    // false for default Airship handling
    return true;
});
```

## Related Resources

- [Android SDK Documentation](https://docs.airship.com/platform/mobile/setup/sdk/android/)
- [Preference Center User Guide](https://docs.airship.com/guides/messaging/features/preference-centers/)
- [Subscription Lists](https://docs.airship.com/platform/mobile/audience/#subscription-lists)

# Feature Flags Setup - Flutter

Feature Flags in Airship allow you to remotely control feature availability and configuration in your Flutter app.

**Requirements**: Airship Flutter SDK 17.1+

## Accessing Flags

The Airship SDK will refresh feature flags when the app is brought to the foreground. If a feature flag is accessed before the foreground refresh completes, or after the foreground refresh has failed, feature flags will be refreshed during flag access. Feature flags will only be updated once per session and will persist for the duration of each session.

Once defined in the dashboard, a feature flag can be accessed by its name in the SDK after `takeOff`.

### Basic Flag Access

```dart
var flag = await Airship.featureFlagManager.flag("my-flag");
if (flag.isEligible) {
    // Do something with the flag
} else {
    // Disable feature or use default behavior
}
```

## Tracking Interaction

To generate the Feature Flag Interaction Event, you must manually call `trackInteraction` with the feature flag. Analytics must be enabled.

```dart
Airship.featureFlagManager.trackInteraction(flag)
```

## Error Handling

If a feature flag allows evaluation with stale data, the SDK will evaluate the flag if a definition for the flag is found. Otherwise, feature flag evaluation will depend on updated local state. If the SDK is unable to evaluate a flag due to data not being able to fetched, an error will be returned or raised. The app can either treat the error as the flag being ineligible or retry again at a later time.

```dart
Airship.featureFlagManager.flag("another_rad_flag").then((flag) => {
    if (flag.isEligible) {
        // Do something with the flag
    }
}).catchError((error) => {
    debugPrint("flag error: $error")
});
```

## Related Resources

- [Feature Flags Dashboard Guide](https://docs.airship.com/guides/messaging/experimentation/feature-flags/)
- [Flutter SDK Documentation](https://docs.airship.com/platform/mobile/setup/sdk/flutter/)

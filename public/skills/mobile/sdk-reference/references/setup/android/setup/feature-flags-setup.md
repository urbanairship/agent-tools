# Feature Flags Setup - Android

Feature Flags in Airship allow you to remotely control feature availability and configuration in your Android app.

**Requirements**: Android SDK 17.1+

## Accessing Flags

The Airship SDK will refresh feature flags when the app is brought to the foreground. If a feature flag is accessed before the foreground refresh completes, or after the foreground refresh has failed, feature flags will be refreshed during flag access. Feature flags will only be updated once per session and will persist for the duration of each session.

Once defined in the dashboard, a feature flag can be accessed by its name in the SDK after `takeOff`.

### Kotlin

The SDK provides asynchronous access to feature flags using Kotlin suspend functions, which is intended to be called from a coroutine. For more info, see [Coroutines Overview guide](https://kotlinlang.org/docs/coroutines-overview.html).

```kotlin
// Get the FeatureFlag result
val result: Result<FeatureFlag> = FeatureFlagManager.shared().flag("YOUR_FLAG_NAME")

// Check if the app is eligible or not
if (result.getOrNull()?.isEligible == true) {
    // Do something with the flag
} else {
    // Disable feature or use default behavior
}
```

### Java

```java
// Get the FeatureFlag
FeatureFlag featureFlag = FeatureFlagManager.shared().flagAsPendingResult("YOUR_FLAG_NAME").getResult();

// Check if the app is eligible or not
if (featureFlag != null && featureFlag.isEligible()) {
    // Do something with the flag
} else {
    // Disable feature or use default behavior
}
```

## Tracking Interaction

To generate the Feature Flag Interaction Event, you must manually call `trackInteraction` with the feature flag. Analytics must be enabled.

### Kotlin

```kotlin
FeatureFlagManager.shared().trackInteraction(featureFlag)
```

### Java

```java
FeatureFlagManager.shared().trackInteraction(featureFlag)
```

## Error Handling

If a feature flag allows evaluation with stale data, the SDK will evaluate the flag if a definition for the flag is found. Otherwise, feature flag evaluation will depend on updated local state. If the SDK is unable to evaluate a flag due to data not being able to fetched, an error will be returned or raised. The app can either treat the error as the flag being ineligible or retry again at a later time.

### Kotlin

```kotlin
FeatureFlagManager.shared().flag("YOUR_FLAG_NAME").fold(
        onSuccess = { flag ->
            // do something with the flag
        },
        onFailure = {error ->
            // do something with the error
        }
)
```

### Java

```java
FeatureFlag featureFlag = FeatureFlagManager.shared().flagAsPendingResult("YOUR_FLAG_NAME").getResult();
if (featureFlag == null) {
    // error
} else if (featureFlag.isEligible()) {
    // Do something with the flag
}
```

## Related Resources

- [Feature Flags Dashboard Guide](https://docs.airship.com/guides/messaging/experimentation/feature-flags/)
- [Android SDK API Reference](https://docs.airship.com/reference/libraries/android/)

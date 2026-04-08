# Feature Flags Setup - React Native

Feature Flags in Airship allow you to remotely control feature availability and configuration in your React Native app.

**Requirements**: Airship React Native SDK 17.1+

## Accessing Flags

The Airship SDK will refresh feature flags when the app is brought to the foreground. If a feature flag is accessed before the foreground refresh completes, or after the foreground refresh has failed, feature flags will be refreshed during flag access. Feature flags will only be updated once per session and will persist for the duration of each session.

Once defined in the dashboard, a feature flag can be accessed by its name in the SDK after `takeOff`.

### Basic Flag Access

```typescript
const flag = await Airship.featureFlagManager.flag("YOUR_FLAG_NAME");
if (flag.isEligible) {
    // Do something with the flag
} else {
    // Disable feature or use default behavior
}
```

## Tracking Interaction

To generate the Feature Flag Interaction Event, you must manually call `trackInteraction` with the feature flag. Analytics must be enabled.

```typescript
await Airship.featureFlagManager.trackInteraction(flag);
```

## Error Handling

If a feature flag allows evaluation with stale data, the SDK will evaluate the flag if a definition for the flag is found. Otherwise, feature flag evaluation will depend on updated local state. If the SDK is unable to evaluate a flag due to data not being able to fetched, an error will be returned or raised. The app can either treat the error as the flag being ineligible or retry again at a later time.

```typescript
try {
    await Airship.featureFlagManager.flag("YOUR_FLAG_NAME");
} catch(error) {
    // Do something with the error
}
```

## Related Resources

- [Feature Flags Dashboard Guide](https://docs.airship.com/guides/messaging/experimentation/feature-flags/)
- [React Native SDK Documentation](https://docs.airship.com/platform/mobile/setup/sdk/react-native/)

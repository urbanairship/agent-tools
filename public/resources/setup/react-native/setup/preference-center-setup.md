# Preference Center Setup - React Native

Preference Center allows users to opt in and out of subscription lists configured via the Airship Dashboard.

## Displaying a Preference Center

A Preference Center can be displayed in its own window with the provided Airship UI with a single method call.

```typescript
await Airship.preferenceCenter.display("my-first-pref-center");
```

## Custom Preference Centers

If the provided preference center is insufficient for your app, you can build your own UI. Currently, preference center is limited to modifying subscription lists.

Example implementations are available in the [React Native SDK repository](https://github.com/urbanairship/react-native-airship/blob/main/example/src/screens/PreferenceCenterScreen.tsx).

### Fetching Preference Center Config

When creating a custom preference center, you will need to fetch the config from the Airship SDK. The config might not be available right away on first app start.

```typescript
const config = await Airship.preferenceCenter.getConfig(preferenceCenterId);
```

## Related Resources

- [React Native SDK Documentation](https://docs.airship.com/platform/mobile/setup/sdk/react-native/)
- [Preference Center User Guide](https://docs.airship.com/guides/messaging/features/preference-centers/)
- [Subscription Lists](https://docs.airship.com/platform/mobile/audience/#subscription-lists)

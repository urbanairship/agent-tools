# Preference Center Setup - Flutter

Preference Center allows users to opt in and out of subscription lists configured via the Airship Dashboard.

## Displaying a Preference Center

A Preference Center can be displayed in its own window with the provided Airship UI with a single method call.

```dart
Airship.preferenceCenter.display("my-first-pref-center");
```

## Custom Preference Centers

If the provided preference center is insufficient for your app, you can build your own UI. Currently, preference center is limited to modifying subscription lists.

Example implementations are available in the [Flutter SDK repository](https://github.com/urbanairship/airship-flutter/blob/main/example/lib/screens/preference_center.dart).

### Fetching Preference Center Config

When creating a custom preference center, you will need to fetch the config from the Airship SDK. The config might not be available right away on first app start.

```dart
PreferenceCenterConfig preferenceCenterConfig = await Airship.preferenceCenter.getConfig(preferenceCenterId)
```

## Related Resources

- [Flutter SDK Documentation](https://docs.airship.com/platform/mobile/setup/sdk/flutter/)
- [Preference Center User Guide](https://docs.airship.com/guides/messaging/features/preference-centers/)
- [Subscription Lists](https://docs.airship.com/platform/mobile/audience/#subscription-lists)

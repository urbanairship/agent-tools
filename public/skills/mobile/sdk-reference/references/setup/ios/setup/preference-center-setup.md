# Preference Center Setup - iOS

Preference Center allows users to opt in and out of subscription lists configured via the Airship Dashboard.

## Displaying a Preference Center

A Preference Center can be displayed in its own window with the provided Airship UI with a single method call. By wiring this method call to a button in your app, you can quickly produce a user-initiated Preference Center with no additional effort.

### Swift

```swift
Airship.preferenceCenter.open("my-first-pref-center")
```

### Objective-C

```objc
[UAirship.preferenceCenter openPreferenceCenter:@"my-first-pref-center"];
```

## Styling the Preference Center

Most developers will want to customize the look and feel to match their app's existing style and layout. iOS supports customizing through a styling config. See the [iOS custom style guide](https://docs.airship.com/platform/mobile/preference-center/custom/ios/) for more information.

## Custom Preference Centers

If the provided preference center is insufficient for your app, you can build your own UI. Currently, preference center is limited to modifying subscription lists.

Example implementations are available in the [iOS SDK repository](https://github.com/urbanairship/ios-library/blob/main/Airship/AirshipPreferenceCenter/Source/view/PreferenceCenterView.swift).

### Fetching Preference Center Config

When creating a custom preference center, you will need to fetch the config from the Airship SDK. The config might not be available right away on first app start.

#### Swift

```swift
Airship.preferenceCenter.config(preferenceCenterID: preferenceCenterId) { config in
    // Use the preference center config
}
```

#### Objective-C

```objc
[UAirship.preferenceCenter jsonConfigWithPreferenceCenterID:@"my-first-pref-center"
                                          completionHandler:^(NSData *data, NSError * error) {
    // Use the preference center config
}];
```

### Overriding the Open Behavior

To override the default preference center handling, set a delegate to handle displaying the preference center and to prevent the Airship SDK from displaying the OOTB UI.

Set the delegate after takeOff:

#### Swift

```swift
@UIApplicationMain
class AppDelegate: UIResponder, UIApplicationDelegate, PreferenceCenterOpenDelegate, ... {

    ...

    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey : Any]? = nil) -> Bool {

        ...

        // Call takeOff
        Airship.takeOff(config, launchOptions: launchOptions)

        // Set the Preference Center open delegate
        Airship.preferenceCenter.openDelegate = self

        return true
    }

    func openPreferenceCenter(_ preferenceCenterID: String) -> Bool {
        // Navigate to custom preference center UI

        // true to prevent default behavior
        // false for default Airship handling
        return true
    }

    ...
}
```

## Related Resources

- [iOS SDK Documentation](https://docs.airship.com/platform/mobile/setup/sdk/ios/)
- [Preference Center User Guide](https://docs.airship.com/guides/messaging/features/preference-centers/)
- [Subscription Lists](https://docs.airship.com/platform/mobile/audience/#subscription-lists)

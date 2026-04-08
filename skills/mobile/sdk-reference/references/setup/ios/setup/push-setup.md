# Push Notifications Setup - iOS

How to configure your iOS application to receive and respond to push notifications.

## Enabling User Notifications

Enabling `userPushNotificationsEnabled` will prompt the user for permission to send notifications. To increase the likelihood that the user will accept, you should avoid prompting the user for permission immediately, and instead wait for a more appropriate time in the app.

The Airship SDK makes a distinction between `user notifications`, which can be seen by the user, and other forms of push that allow you to send data to your app silently, or in the background. Enabling or disabling user notifications is a preference often best left up to the user, so by default, user notifications are disabled.

### Swift

```swift
UAirship.push.userPushNotificationsEnabled = true
```

### Objective-C

```objc
UAirship.push.userPushNotificationsEnabled = YES;
```

## Notification Callbacks

The Airship SDK provides several callbacks for when a push is received or a notification is interacted with. Apps can use these callbacks to do custom push processing. Registering for a callback is optional, the SDK will automatically launch the application without the need to set a callback.

### Swift

```swift
@MainActor
final class CustomPushHandler: PushNotificationDelegate {
    func receivedForegroundNotification(_ userInfo: [AnyHashable : Any]) async {
        // Foreground notification
    }

    func receivedBackgroundNotification(_ userInfo: [AnyHashable : Any]) async -> UIBackgroundFetchResult {
        // Background content-available notification
        return .noData
    }

    func receivedNotificationResponse(_ notificationResponse: UNNotificationResponse) async {
        // Notification response
    }

    func extendPresentationOptions(_ options: UNNotificationPresentationOptions, notification: UNNotification) async -> UNNotificationPresentationOptions {
        // Presentation options to show notification when app is in the foreground
        return [.badge, .list, .banner, .sound]
    }
}
```

```swift
Airship.push.pushNotificationDelegate = customPushHandler
```

### Objective-C

```objc
@implementation CustomPushHandler

-(void)receivedBackgroundNotification:(UNNotificationContent *)notificationContent completionHandler:(void (^)(UIBackgroundFetchResult))completionHandler {
    // Background content-available notification
    completionHandler(UIBackgroundFetchResultNoData);
}

-(void)receivedForegroundNotification:(UNNotificationContent *)notificationContent completionHandler:(void (^)(void))completionHandler {
    // Foreground notification
    completionHandler();
}

-(void)receivedNotificationResponse:(UNNotificationResponse *)notificationResponse completionHandler:(void (^)(void))completionHandler {
    // Notification response
    completionHandler();
}

- (void)extendPresentationOptions:(UNNotificationPresentationOptions)options
                     notification:(UNNotification * _Nonnull)notification
                completionHandler:(void (^ _Nonnull)(UNNotificationPresentationOptions))completionHandler {
    // Foreground presentation options
    completionHandler(UNNotificationPresentationOptionList | UNNotificationPresentationOptionBadge | UNNotificationPresentationOptionSound);
}

@end
```

Set the PushNotificationDelegate:

```objc
UAirship.push.pushNotificationDelegate = customPushHandler;
```

## Notification Options

By default, the Airship SDK will request `Alert`, `Badge`, and `Sound` notification options for remote notifications. This can be configured by setting notification options before enabling user notifications.

### Swift

```swift
Airship.push.notificationOptions = [.alert, .badge, .sound]
```

### Objective-C

```objc
UAirship.push.notificationOptions = (UNAuthorizationOptionBadge | UNAuthorizationOptionSound | UNAuthorizationOptionAlert);
```

## Silent Notifications

Silent notifications are push messages that do not present a notification to the user. These are typically used to briefly wake the app from a background state to perform processing tasks or fetch remote content.

To send a silent notification on iOS, set the `content_available` property to `true` in the iOS override object.

**Important**: Pushes sent with the `content_available` property do not have guaranteed delivery. Factors affecting delivery include battery life, whether the device is connected to WiFi, and the number of `content_available` pushes sent within a recent time period. These metrics are determined solely by iOS and APNs.

## Related Resources

- [iOS SDK Documentation](https://docs.airship.com/platform/mobile/setup/sdk/ios/)
- [Push API Reference](https://docs.airship.com/api/ua/)

# Push Notifications Setup - Flutter

How to configure your Flutter application to receive and respond to push notifications.

## Enabling User Notifications

Enabling `userPushNotificationsEnabled` will prompt the user for permission to send notifications. To increase the likelihood that the user will accept, you should avoid prompting the user for permission immediately, and instead wait for a more appropriate time in the app.

The Airship SDK makes a distinction between `user notifications`, which can be seen by the user, and other forms of push that allow you to send data to your app silently, or in the background. Enabling or disabling user notifications is a preference often best left up to the user, so by default, user notifications are disabled.

```dart
Airship.push.setUserNotificationsEnabled(true);
```

## Notification Callbacks

The Airship SDK provides several callbacks for when a push is received or a notification is interacted with. Apps can use these callbacks to do custom push processing.

```dart
// Push received. Will not be called on Android when the app is terminated. Use a background
// message handler instead.
Airship.push.onPushReceived.listen((event) => debugPrint('Push Received $event'));

Airship.push.onNotificationResponse.listen((event) => debugPrint('Notification Response $event'));
```

### Android Background Push Handler

```dart
Future<void> backgroundMessageHandler(PushReceivedEvent event) async {
  // Handle the message
  debugPrint("Received background message: $event");
}

void main() {
  Airship.push.android.setBackgroundPushReceivedHandler(backgroundMessageHandler);
  runApp(MyApp());
}
```

## iOS Notification Options

By default, the Airship SDK will request `Alert`, `Badge`, and `Sound` notification options for remote notifications on iOS. This can be configured by setting notification options before enabling user notifications.

```dart
Airship.push.iOS.setNotificationOptions([
    IOSNotificationOption.alert,
    IOSNotificationOption.badge,
    IOSNotificationOption.sound,
  ]);
```

## Silent Notifications

Silent notifications are push messages that do not present a notification to the user. These are typically used to briefly wake the app from a background state to perform processing tasks or fetch remote content.

- **iOS**: Set the `content_available` property to `true` in the iOS override object
- **Android**: All push messages are delivered in the background, but Airship will treat messages without an `alert` as silent

## Related Resources

- [Flutter SDK Documentation](https://docs.airship.com/platform/mobile/setup/sdk/flutter/)
- [Push API Reference](https://docs.airship.com/api/ua/)

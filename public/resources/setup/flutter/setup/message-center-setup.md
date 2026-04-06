# Message Center Setup - Flutter

The Message Center provides a customizable inbox for in-app messages.

## Displaying Message Center

```dart
Airship.messageCenter.display()
```

## Custom Display Implementation

First disable the OOTB UI for Message Center:

```dart
Airship.messageCenter.setAutoLaunchDefaultMessageCenter(false);
```

When disabled, the plugin will generate display events instead of showing any OOTB UI when the Message Center is requested to display.

Next, add a listener to handle the display events:

```dart
Airship.messageCenter.onDisplay
    .listen((event) => debugPrint('Navigate to app\'s inbox $event'));
```

## Fetching Messages

```dart
List<InboxMessage> messages = await Airship.messageCenter.messages;
```

## Refreshing Messages

```dart
await Airship.messageCenter.refreshMessages();
```

## Related Resources

- [Flutter SDK Documentation](https://docs.airship.com/platform/mobile/setup/sdk/flutter/)
- [Message Center User Guide](https://docs.airship.com/guides/messaging/features/message-center/)

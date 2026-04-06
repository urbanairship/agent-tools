# Message Center Setup - iOS

The default Message Center is available for iOS. Minimal integration is required, and basic theming options are supported.

## Displaying Message Center

By default, when the app receives a push notification carrying a Message Center Action, the Message Center will be automatically displayed in a modal view controller. The Message Center can also be displayed manually with a simple method call.

### Swift

```swift
Airship.messageCenter.display()
```

### Objective-C

```objc
[UAirship.messageCenter display];
```

## Custom Display Implementation

For custom Message Center implementations, initialize the `MessageCenterDisplayDelegate` (Swift) or `UAMessageCenterDisplayDelegate` (Objective-C) with the custom Message Center implementation's view controller. This is necessary to ensure that the modal Message Center is not displayed on top of the custom Message Center when a message is received.

## Fetching Messages

### Swift

```swift
let messages = await Airship.messageCenter.inbox.messages
```

### Objective-C

```objc
[UAirship.messageCenter.inbox getMessagesWithCompletionHandler:^(NSArray<UAMessageCenterMessage *> *messages) {
    // handle messages
}];
```

## Refreshing Messages

### Swift

```swift
let refreshed = await Airship.messageCenter.inbox.refreshMessages()
```

### Objective-C

```objc
[UAirship.messageCenter refreshMessagesWithCompletionHandler:^(BOOL result) {
    // handle result
}];
```

## Related Resources

- [iOS SDK Documentation](https://docs.airship.com/platform/mobile/setup/sdk/ios/)
- [Message Center User Guide](https://docs.airship.com/guides/messaging/features/message-center/)

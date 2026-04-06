# Message Center Setup - Android

The default Message Center is available for Android. Minimal integration is required, and basic theming options are supported.

## Displaying Message Center

By default, when the app receives a push notification carrying a Message Center Action, the Message Center will be automatically displayed. The Message Center can also be displayed manually with a simple method call.

### Kotlin

```kotlin
MessageCenter.shared().showMessageCenter()
```

### Java

```java
MessageCenter.shared().showMessageCenter();
```

## Custom Display Implementation

The Airship SDK will default to showing the provided `MessageCenterActivity`. A custom show behavior can be accomplished by providing a `MessageCenter.OnShowMessageCenterListener` listener during takeOff:

### Kotlin

```kotlin
MessageCenter.shared().setOnShowMessageCenterListener { messageId: String? ->
    // Show the message center (messageId is optional)
    true
}
```

### Java

```java
MessageCenter.shared().setOnShowMessageCenterListener(messageId -> {
    // Show the message center (messageId is optional)
    return true;
});
```

## Fetching Messages

### Kotlin

```kotlin
// Suspending call
scope.launch {
    val messages = MessagesCenter.shared().inbox.getMessages()
}

// Flow
scope.launch {
    // Collect the messages flow, which emits a new list whenever the inbox is updated
    MessagesCenter.shared().inbox.getMessagesFlow().collect { messages ->
        // ...
    }
}
```

### Java

```java
PendingResult<List<Message>> messagesResult = MessageCenter.shared().getInbox().getMessagesPendingResult();
messagesResult.addResultCallback(messages -> {
    // Handle messages
});
```

## Refreshing Messages

### Kotlin

```kotlin
MessageCenter.shared().inbox.fetchMessages { success ->

}
```

### Java

```java
MessageCenter.shared().getInbox().fetchMessages(new Inbox.FetchMessagesCallback() {
    @Override
    public void onFinished(boolean success) {
        // Handle the result
    }
});
```

## Related Resources

- [Android SDK Documentation](https://docs.airship.com/platform/mobile/setup/sdk/android/)
- [Message Center User Guide](https://docs.airship.com/guides/messaging/features/message-center/)

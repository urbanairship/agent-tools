# Push Notifications Setup - Android

How to configure your Android application to receive and respond to push notifications.

## Enabling User Notifications

Enabling `userPushNotificationsEnabled` will prompt the user for permission to send notifications. To increase the likelihood that the user will accept, you should avoid prompting the user for permission immediately, and instead wait for a more appropriate time in the app.

The Airship SDK makes a distinction between `user notifications`, which can be seen by the user, and other forms of push that allow you to send data to your app silently, or in the background. Enabling or disabling user notifications is a preference often best left up to the user, so by default, user notifications are disabled.

**Note**: For apps that target Android 13 (API 33) and above, enabling user notifications will display a runtime permission prompt to allow notifications to be sent. To increase the likelihood that the user will accept, you should avoid prompting the user for permission immediately on app startup, and instead wait for a more appropriate time to prompt for notification permission.

### Kotlin

```kotlin
UAirship.shared().pushManager.userNotificationsEnabled = true
```

### Java

```java
UAirship.shared().getPushManager().setUserNotificationsEnabled(true);
```

## Notification Callbacks

The Airship SDK provides several callbacks for when a push is received or a notification is interacted with. Apps can use these callbacks to do custom push processing. Registering for a callback is optional, the SDK will automatically launch the application without the need to set a callback.

### Kotlin

```kotlin
airship.pushManager.addPushListener { message: PushMessage, notificationPosted: Boolean ->
    // Called when a message is received
}

airship.pushManager.notificationListener = object : NotificationListener {
    override fun onNotificationPosted(notificationInfo: NotificationInfo) {
        // Called when a notification is posted
    }

    override fun onNotificationOpened(notificationInfo: NotificationInfo): Boolean {
        // Called when a notification is tapped.
        // Return false here to allow Airship to auto launch the launcher activity
        return false
    }

    override fun onNotificationForegroundAction(
        notificationInfo: NotificationInfo,
        actionButtonInfo: NotificationActionButtonInfo
    ): Boolean {
        // Called when a notification action button is tapped.
        // Return false here to allow Airship to auto launch the launcher activity
        return false
    }

    override fun onNotificationBackgroundAction(
        notificationInfo: NotificationInfo,
        actionButtonInfo: NotificationActionButtonInfo
    ) {
        // Called when a background notification action button is tapped.
    }

    override fun onNotificationDismissed(notificationInfo: NotificationInfo) {
        // Called when a notification is dismissed
    }
}
```

### Java

```java
airship.getPushManager().addPushListener((message, notificationPosted) -> {
    // Called when any push is received
});

airship.getPushManager().setNotificationListener(new NotificationListener() {
    @Override
    public void onNotificationPosted(@NonNull NotificationInfo notificationInfo) {
        // Called when a notification is posted
    }

    @Override
    public boolean onNotificationOpened(@NonNull NotificationInfo notificationInfo) {
        // Called when a notification is tapped.
        // Return false here to allow Airship to auto launch the launcher activity
        return false;
    }

    @Override
    public boolean onNotificationForegroundAction(@NonNull NotificationInfo notificationInfo, @NonNull NotificationActionButtonInfo actionButtonInfo) {
        // Called when a notification action button is tapped.
        // Return false here to allow Airship to auto launch the launcher activity
        return false;
    }

    @Override
    public void onNotificationBackgroundAction(@NonNull NotificationInfo notificationInfo, @NonNull NotificationActionButtonInfo actionButtonInfo) {
        // Called when a background notification action button is tapped.
    }

    @Override
    public void onNotificationDismissed(@NonNull NotificationInfo notificationInfo) {
        // Called when a notification is dismissed
    }
});
```

## Silent Notifications

Silent notifications are push messages that do not present a notification to the user. These are typically used to briefly wake the app from a background state to perform processing tasks or fetch remote content.

For Android, all push messages are delivered in the background, but default Airship will treat messages without an `alert` as silent.

## Related Resources

- [Android SDK Documentation](https://docs.airship.com/platform/mobile/setup/sdk/android/)
- [Push API Reference](https://docs.airship.com/api/ua/)

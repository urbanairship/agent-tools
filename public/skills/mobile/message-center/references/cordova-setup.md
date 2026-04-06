# Message Center Setup - Cordova

The Message Center provides a customizable inbox for in-app messages.

## Displaying Message Center

```javascript
Airship.messageCenter.display();
```

## Custom Display Implementation

First disable the OOTB UI for Message Center:

```javascript
Airship.messageCenter.setAutoLaunchDefaultMessageCenter(false);
```

When disabled, the plugin will generate `DisplayMessageCenter` events instead of showing any OOTB UI when the Message Center is requested to display. Use `Airship.messageCenter.showMessageView` to show the actual content of the message in an overlay.

Next, add a listener to handle the display events:

```javascript
Airship.messageCenter.onDisplay((event) => {
  if (event.messageId) {
    // deep link to message
  } else {
    // deep link to message center
  }
});
```

## Fetching Messages

```javascript
Airship.messageCenter.getMessages((messages) => {
  console.log('Inbox messages: + messages);
});
```

## Refreshing Messages

```javascript
Airship.messageCenter.refreshMessages();
```

## Related Resources

- [Cordova SDK Documentation](https://docs.airship.com/platform/mobile/setup/sdk/cordova/)
- [Message Center User Guide](https://docs.airship.com/guides/messaging/features/message-center/)

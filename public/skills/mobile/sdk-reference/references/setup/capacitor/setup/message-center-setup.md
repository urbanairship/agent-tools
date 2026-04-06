# Message Center Setup - Capacitor

The Message Center provides a customizable inbox for in-app messages.

## Displaying Message Center

```javascript
await Airship.messageCenter.display()
```

## Custom Display Implementation

First disable the OOTB UI for Message Center:

```javascript
await Airship.messageCenter.setAutoLaunchDefaultMessageCenter(false)
```

When disabled, the plugin will generate `DisplayMessageCenter` events instead of showing any OOTB UI when the Message Center is requested to display. Use `Airship.messageCenter.showMessageView` to show the actual content of the message in an overlay.

Next, add a listener to handle the display events:

```javascript
await Airship.messageCenter.onDisplay(event => {
    if (event.messageId) {
        // deep link to message
    } else {
        // deep link to message center
    }
});
```

## Fetching Messages

```javascript
const messages = await Airship.messageCenter.getMessages()
```

## Refreshing Messages

```javascript
await Airship.messageCenter.refreshMessages()
```

## Related Resources

- [Capacitor SDK Documentation](https://docs.airship.com/platform/mobile/setup/sdk/capacitor/)
- [Message Center User Guide](https://docs.airship.com/guides/messaging/features/message-center/)

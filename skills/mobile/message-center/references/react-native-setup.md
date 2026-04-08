# Message Center Setup - React Native

The Message Center provides a customizable inbox for in-app messages.

## Displaying Message Center

```typescript
await Airship.messageCenter.display();
```

## Custom Display Implementation

First disable the OOTB UI for Message Center:

```typescript
Airship.messageCenter.setAutoLaunchDefaultMessageCenter(false);
```

When disabled, the plugin will generate `DisplayMessageCenter` events instead of showing any OOTB UI when the Message Center is requested to display.

Next, add a listener to handle the display events:

```typescript
Airship.addListener(EventType.DisplayMessageCenter, (event) => {
  if (event.messageId) {
    // deep link to message
  } else {
    // deep link to message center
  }
});
```

## Fetching Messages

```typescript
const messages = await Airship.messageCenter.getMessages();
```

## Refreshing Messages

```typescript
await Airship.messageCenter.refreshMessages();
```

## Related Resources

- [React Native SDK Documentation](https://docs.airship.com/platform/mobile/setup/sdk/react-native/)
- [Message Center User Guide](https://docs.airship.com/guides/messaging/features/message-center/)

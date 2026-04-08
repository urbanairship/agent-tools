# iOS Custom Views Implementation Guide

## Overview

Airship Custom Views allow you to embed your own SwiftUI views inside Thomas scenes (Airship's declarative layout engine for in-app messages and experiences).

## How It Works

1. **Register** your custom view with `AirshipCustomViewManager`
2. **Reference** it in Thomas scene YAML files
3. **Properties** from the scene are passed to your view

## Registration

Register custom views during app initialization:

```swift
import AirshipCore

// In your App struct init() or AppDelegate
AirshipCustomViewManager.shared.register(name: "my_custom_view") { args in
    MyCustomView(properties: args.properties)
}
```

### Arguments

Your builder receives `AirshipCustomViewArguments`:
- `name: String` - The view's registration name
- `properties: AirshipJSON?` - Optional properties from the scene
- `sizeInfo: SizeInfo` - Sizing information
  - `isAutoHeight: Bool` - If height is `auto` or not
  - `isAutoWidth: Bool` - If width is `auto` or not

## Implementing Your View

```swift
struct MyCustomView: View {
    let properties: AirshipJSON?

    var body: some View {
        // Access properties
        let title = properties?["title"]?.unWrap() as? String
        let count = properties?["count"]?.unWrap() as? Int
        let enabled = properties?["enabled"]?.unWrap() as? Bool

        VStack {
            if let title {
                Text(title)
            }
            // Your custom implementation
        }
    }
}
```

## Using in Thomas Scenes

Reference your custom view in YAML:

```yaml
version: 1
presentation:
  type: modal
view:
  type: custom_view
  name: my_custom_view
  properties:
    title: "Hello"
    count: 42
    enabled: true
```

## Property Access

Properties are passed as `AirshipJSON?`. Use `unWrap()` to access values:

```swift
// String
let location = properties?["location"]?.unWrap() as? String

// Number
let temperature = properties?["temperature"]?.unWrap() as? Double
let count = properties?["count"]?.unWrap() as? Int

// Boolean
let isEnabled = properties?["isEnabled"]?.unWrap() as? Bool

// Array
let items = properties?["items"]?.unWrap() as? [AirshipJSON]

// Object
let config = properties?["config"]?.unWrap() as? AirshipJSON
```

## Sizing

Custom views can have fixed or auto sizing:

```yaml
view:
  type: custom_view
  name: my_view
  size:
    width: 100%    # or specific size like "200"
    height: auto   # or specific size like "300"
```

## Scene Integration

Custom views can be used anywhere in a Thomas layout:

```yaml
view:
  type: container
  items:
    - view:
        type: label
        text: "Header"
    - view:
        type: custom_view
        name: my_custom_view
    - view:
        type: label_button
        label:
          text: "Continue"
```

## Examples

### Camera View

```swift
AirshipCustomViewManager.shared.register(name: "camera_view") { args in
    CameraView(properties: args.properties)
}

struct CameraView: View {
    let properties: AirshipJSON?

    var body: some View {
        // Your camera implementation
        Text("Camera View")
    }
}
```

### Map View

```swift
AirshipCustomViewManager.shared.register(name: "map_view") { args in
    MapView(properties: args.properties)
}

struct MapView: View {
    let properties: AirshipJSON?

    var body: some View {
        let latitude = properties?["latitude"]?.unWrap() as? Double ?? 0
        let longitude = properties?["longitude"]?.unWrap() as? Double ?? 0

        // Your map implementation
        Text("Map: \\(latitude), \\(longitude)")
    }
}
```

## Scene Controller Access

Custom views have access to `AirshipSceneController` for dismissing or navigating:

```swift
struct MyCustomView: View {
    @EnvironmentObject var controller: AirshipSceneController

    var body: some View {
        Button("Close") {
            controller.dismiss()
        }
    }
}
```

## Best Practices

1. **Always handle nil properties** - Properties are optional
2. **Provide sensible defaults** - Use `??` for fallback values
3. **Keep views reusable** - Design for different property combinations
4. **Test with different sizes** - Ensure views work with auto and fixed sizing
5. **Document your properties** - Make it clear what properties your view expects

## Troubleshooting

### View Not Appearing

1. Check registration is called during app initialization
2. Verify the `name:` in YAML matches your registration
3. Ensure `AirshipCore` is imported

### Properties Not Working

1. Check property names match exactly (case-sensitive)
2. Use `unWrap()` to access values
3. Cast to appropriate Swift types
4. Provide defaults for optional properties

### Sizing Issues

1. For scrollable content, use `auto` height
2. For fixed layouts, specify exact dimensions
3. Test with different device sizes
4. Use constraints in your SwiftUI views

## Related Documentation

- [Thomas Scene Specification](https://docs.airship.com)
- [Airship iOS SDK](https://docs.airship.com/platform/mobile/setup/sdk/ios/)
- [SwiftUI Documentation](https://developer.apple.com/documentation/swiftui)

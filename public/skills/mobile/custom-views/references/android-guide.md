# Android Custom Views Implementation Guide

## Overview

Airship Custom Views allow you to embed your own Compose or View-based UI components inside Thomas scenes (Airship's declarative layout engine for in-app messages and experiences).

## How It Works

1. **Register** your custom view with `AirshipCustomViewManager`
2. **Reference** it in Thomas scene YAML files
3. **Properties** from the scene are passed to your view

## Registration

Register custom views during app initialization:

```kotlin
import com.urbanairship.android.layout.ui.AirshipCustomViewManager

// In your Application.onCreate()
AirshipCustomViewManager.shared().register("my_custom_view") { args ->
    MyCustomView(properties = args.properties)
}
```

### Arguments

Your builder receives `AirshipCustomViewArguments`:
- `name: String` - The view's registration name
- `properties: JsonMap?` - Optional properties from the scene
- `sizeInfo: SizeInfo` - Sizing information
  - `isAutoHeight: Boolean` - If height is `auto` or not
  - `isAutoWidth: Boolean` - If width is `auto` or not

## Implementing Your View (Compose)

```kotlin
@Composable
fun MyCustomView(properties: JsonMap?) {
    // Access properties
    val title = properties?.get("title")?.string
    val count = properties?.get("count")?.int ?: 0
    val enabled = properties?.get("enabled")?.boolean ?: false

    Column {
        title?.let {
            Text(text = it)
        }
        // Your custom implementation
    }
}
```

## Implementing Your View (View-based)

```kotlin
class MyCustomView(
    context: Context,
    properties: JsonMap?
) : FrameLayout(context) {

    init {
        val title = properties?.get("title")?.string
        val count = properties?.get("count")?.int ?: 0

        // Inflate and configure your view
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

Properties are passed as `JsonMap?`. Use type-specific accessors:

```kotlin
// String
val location = properties?.get("location")?.string

// Number
val temperature = properties?.get("temperature")?.double
val count = properties?.get("count")?.int

// Boolean
val isEnabled = properties?.get("isEnabled")?.boolean ?: false

// Array
val items = properties?.get("items")?.list

// Object
val config = properties?.get("config")?.map
```

### Providing Defaults

```kotlin
// With Elvis operator
val count = properties?.get("count")?.int ?: 10
val title = properties?.get("title")?.string ?: "Default Title"
val enabled = properties?.get("enabled")?.boolean ?: false
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

### Camera View (Compose)

```kotlin
AirshipCustomViewManager.shared().register("camera_view") { args ->
    CameraView(properties = args.properties)
}

@Composable
fun CameraView(properties: JsonMap?) {
    // Your camera implementation
    Text("Camera View")
}
```

### Map View (Compose)

```kotlin
AirshipCustomViewManager.shared().register("map_view") { args ->
    MapView(properties = args.properties)
}

@Composable
fun MapView(properties: JsonMap?) {
    val latitude = properties?.get("latitude")?.double ?: 0.0
    val longitude = properties?.get("longitude")?.double ?: 0.0

    // Your map implementation
    Text("Map: $latitude, $longitude")
}
```

### Web View (View-based)

```kotlin
AirshipCustomViewManager.shared().register("web_view") { args ->
    CustomWebView(args.properties)
}

class CustomWebView(properties: JsonMap?) : WebView(context) {
    init {
        val url = properties?.get("url")?.string ?: "about:blank"
        loadUrl(url)
    }
}
```

## Scene Controller Access

Custom views have access to `AirshipSceneController` for dismissing or navigating:

```kotlin
@Composable
fun MyCustomView(properties: JsonMap?) {
    val controller = LocalAirshipSceneController.current

    Button(onClick = { controller.dismiss() }) {
        Text("Close")
    }
}
```

## Best Practices

1. **Always handle null properties** - Properties are nullable
2. **Provide sensible defaults** - Use Elvis operator `?:` for fallback values
3. **Keep views reusable** - Design for different property combinations
4. **Test with different sizes** - Ensure views work with auto and fixed sizing
5. **Document your properties** - Make it clear what properties your view expects
6. **Use Compose when possible** - More flexible and modern than View-based

## Lifecycle Considerations

### Compose

Compose handles lifecycle automatically. Use appropriate effects:

```kotlin
@Composable
fun MyCustomView(properties: JsonMap?) {
    LaunchedEffect(Unit) {
        // One-time initialization
    }

    DisposableEffect(Unit) {
        onDispose {
            // Cleanup
        }
    }
}
```

### View-based

Override lifecycle methods:

```kotlin
class MyCustomView(context: Context, properties: JsonMap?) : FrameLayout(context) {
    override fun onAttachedToWindow() {
        super.onAttachedToWindow()
        // Start operations
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        // Cleanup
    }
}
```

## Troubleshooting

### View Not Appearing

1. Check registration is called in `Application.onCreate()`
2. Verify the `name:` in YAML matches your registration
3. Ensure required imports are present
4. Check Logcat for errors

### Properties Not Working

1. Check property names match exactly (case-sensitive)
2. Use correct type accessor (`.string`, `.int`, `.boolean`)
3. Provide defaults for nullable properties
4. Log properties to verify values: `Log.d("Airship", "Props: $properties")`

### Sizing Issues

1. For scrollable content, use `auto` height
2. For fixed layouts, specify exact dimensions
3. Test with different device sizes
4. Ensure your view respects constraints

### Compose vs View-based

**Use Compose when:**
- Building new views
- Want modern, declarative UI
- Need state management integration

**Use View-based when:**
- Integrating existing Views
- Need specific View APIs (WebView, MapView)
- Working with legacy code

## Dependencies

### Compose

```gradle
dependencies {
    implementation 'com.urbanairship.android:urbanairship-layout:20.+'
    implementation 'androidx.compose.ui:ui:1.5.0'
    implementation 'androidx.compose.material:material:1.5.0'
}
```

### View-based

```gradle
dependencies {
    implementation 'com.urbanairship.android:urbanairship-layout:20.+'
}
```

## Related Documentation

- [Thomas Scene Specification](https://docs.airship.com)
- [Airship Android SDK](https://docs.airship.com/platform/mobile/setup/sdk/android/)
- [Jetpack Compose Documentation](https://developer.android.com/jetpack/compose)

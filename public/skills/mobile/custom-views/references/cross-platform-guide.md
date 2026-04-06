# Cross-Platform Custom Views Guide

Custom views for React Native, Flutter, Capacitor, and Cordova require native iOS and Android implementations.

## Why Native Code?

Thomas scenes render using native UI frameworks:
- iOS: SwiftUI
- Android: Jetpack Compose or View-based

Cross-platform frameworks (React Native, Flutter, etc.) cannot directly render in Thomas scenes. You must implement the view natively on each platform.

## React Native

### iOS Setup

Create `ios/AirshipExtender.swift`:

```swift
import AirshipKit

@objc(AirshipExtender)
class AirshipExtender: NSObject, AirshipPluginExtenderDelegate {
    func onAirshipReady() {
        AirshipCustomViewManager.shared.register(name: "my_view") { args in
            MyCustomView(properties: args.properties)
        }
    }
}

struct MyCustomView: View {
    let properties: AirshipJSON?

    var body: some View {
        // Your SwiftUI implementation
        Text("Custom View")
    }
}
```

Add to Xcode project:
1. Open `ios/YourApp.xcworkspace`
2. Add `AirshipExtender.swift` to your app target
3. Ensure it's in Compile Sources

### Android Setup

Create `android/app/src/main/java/com/yourapp/AirshipExtender.kt`:

```kotlin
import com.urbanairship.android.framework.proxy.AirshipPluginExtender
import com.urbanairship.AirshipCustomViewManager
import android.content.Context
import androidx.compose.runtime.Composable
import androidx.compose.material.Text
import com.urbanairship.json.JsonMap

class AirshipExtender : AirshipPluginExtender {
    override fun onAirshipReady(context: Context) {
        AirshipCustomViewManager.register("my_view") { ctx, args ->
            MyCustomView(args.properties)
        }
    }
}

@Composable
fun MyCustomView(properties: JsonMap?) {
    // Your Compose implementation
    Text("Custom View")
}
```

Replace `com.yourapp` with your actual package name.

## Flutter

### iOS Setup

Create `ios/Runner/AirshipPluginExtender.swift`:

```swift
import AirshipKit

@objc(AirshipPluginExtender)
public class AirshipPluginExtender: NSObject, AirshipPluginExtenderProtocol {
    @MainActor
    public static func onAirshipReady() {
        AirshipCustomViewManager.shared.register(name: "my_view") { args in
            MyCustomView(properties: args.properties)
        }
    }
}

struct MyCustomView: View {
    let properties: AirshipJSON?

    var body: some View {
        Text("Custom View")
    }
}
```

**Note:** Flutter uses `AirshipPluginExtenderProtocol` (different from React Native).

### Android Setup

Create `android/app/src/main/kotlin/com/yourapp/AirshipExtender.kt`:

```kotlin
import com.urbanairship.android.framework.proxy.AirshipPluginExtender
import com.urbanairship.AirshipCustomViewManager
import android.content.Context
import androidx.compose.runtime.Composable
import androidx.compose.material.Text
import com.urbanairship.json.JsonMap

class AirshipExtender : AirshipPluginExtender {
    override fun onAirshipReady(context: Context) {
        AirshipCustomViewManager.register("my_view") { ctx, args ->
            MyCustomView(args.properties)
        }
    }
}

@Composable
fun MyCustomView(properties: JsonMap?) {
    Text("Custom View")
}
```

**Note:** Place in `kotlin/` directory, not `java/`.

## Capacitor

### iOS Setup

Create `ios/App/AirshipExtender.swift`:

```swift
import AirshipKit

@objc(AirshipExtender)
class AirshipExtender: NSObject, AirshipPluginExtenderDelegate {
    func onAirshipReady() {
        AirshipCustomViewManager.shared.register(name: "my_view") { args in
            MyCustomView(properties: args.properties)
        }
    }
}

struct MyCustomView: View {
    let properties: AirshipJSON?

    var body: some View {
        Text("Custom View")
    }
}
```

### Android Setup

Create `android/app/src/main/java/your/package/AirshipExtender.kt`:

Same as React Native Android setup.

## Cordova

### iOS Setup

Create `platforms/ios/YourApp/Classes/AirshipExtender.swift`:

Same structure as Capacitor iOS setup.

**Note:** Cordova builds may overwrite `platforms/` directory. Consider using a hook to preserve native code.

### Android Setup

Create `platforms/android/app/src/main/java/your/package/AirshipExtender.kt`:

Same as React Native Android setup.

## Important Notes

1. **Custom views render in Thomas scenes**, not in your JavaScript/Dart code
2. **Properties come from Thomas scene definitions**, not from your app code
3. **Test by triggering a Thomas scene** that uses your custom view
4. **Both iOS and Android** implementations are required for cross-platform

## Documentation

- [React Native Custom Views](https://docs.airship.com/platform/react-native/in-app-experiences/custom-views/)
- [Flutter Custom Views](https://docs.airship.com/platform/flutter/in-app-experiences/custom-views/)
- [Capacitor Documentation](https://docs.airship.com/platform/capacitor/)
- [Cordova Documentation](https://docs.airship.com/platform/cordova/)

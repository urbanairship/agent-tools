// Android Custom View Registration Template (Compose)
// Replace CLASS_NAME and IDENTIFIER with your values

import com.urbanairship.android.layout.ui.AirshipCustomViewManager
import com.urbanairship.json.JsonMap
import androidx.compose.runtime.Composable
import androidx.compose.material.Text
import androidx.compose.foundation.layout.Column

// MARK: - Registration (add to Application.onCreate())

AirshipCustomViewManager.shared().register("IDENTIFIER") { args ->
    CLASS_NAME(properties = args.properties)
}

// MARK: - Custom View Implementation (Compose)

@Composable
fun CLASS_NAME(properties: JsonMap?) {
    // Access properties like this:
    // val title = properties?.get("title")?.string ?: "Default"
    // val count = properties?.get("count")?.int ?: 0
    // val enabled = properties?.get("enabled")?.boolean ?: false

    Column {
        Text("Custom View")
    }
}

// MARK: - Scene Controller Access (optional)

// If you need to dismiss the scene or navigate:
// @Composable
// fun CLASS_NAME(properties: JsonMap?) {
//     val controller = LocalAirshipSceneController.current
//
//     Button(onClick = { controller.dismiss() }) {
//         Text("Close")
//     }
// }

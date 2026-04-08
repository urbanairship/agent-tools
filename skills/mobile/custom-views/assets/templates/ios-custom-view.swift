// iOS Custom View Registration Template
// Replace CLASS_NAME and IDENTIFIER with your values

import AirshipCore
import SwiftUI

// MARK: - Registration (add to App.init() or AppDelegate)

AirshipCustomViewManager.shared.register(name: "IDENTIFIER") { args in
    CLASS_NAME(properties: args.properties)
}

// MARK: - Custom View Implementation

struct CLASS_NAME: View {
    let properties: AirshipJSON?

    var body: some View {
        // Access properties like this:
        // let title = properties?["title"]?.unWrap() as? String ?? "Default"
        // let count = properties?["count"]?.unWrap() as? Int ?? 0
        // let enabled = properties?["enabled"]?.unWrap() as? Bool ?? false

        VStack {
            Text("Custom View")
        }
    }
}

// MARK: - Scene Controller Access (optional)

// If you need to dismiss the scene or navigate:
// struct CLASS_NAME: View {
//     @EnvironmentObject var controller: AirshipSceneController
//
//     var body: some View {
//         Button("Close") {
//             controller.dismiss()
//         }
//     }
// }

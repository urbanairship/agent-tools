// iOS Message Center Customization Template

import AirshipMessageCenter
import SwiftUI

// MARK: - Custom Message Center Display Delegate

class CustomMessageCenterHandler: NSObject, MessageCenterDisplayDelegate {

    func displayMessageCenter(messages: [MessageCenterMessage]) {
        // Present your custom message list UI
        // Each message has: id, title, sentDate, isRead, extras

        // Example: Present a SwiftUI view
        // let hostingController = UIHostingController(rootView: CustomMessageListView(messages: messages))
        // UIApplication.shared.keyWindow?.rootViewController?.present(hostingController, animated: true)
    }

    func displayMessage(messageID: String) {
        // Present your custom message detail view

        // Example: Fetch message and display
        // MessageCenter.shared.inbox.message(forID: messageID) { message in
        //     // Present detail view with message content
        // }
    }

    func dismissMessageCenter() {
        // Dismiss your custom UI
        // UIApplication.shared.keyWindow?.rootViewController?.dismiss(animated: true)
    }
}

// MARK: - Registration (add to app initialization)

// MessageCenter.shared.displayDelegate = CustomMessageCenterHandler()

// MARK: - Custom Message List View (Example)

struct CustomMessageListView: View {
    let messages: [MessageCenterMessage]

    var body: some View {
        NavigationView {
            List(messages, id: \.id) { message in
                VStack(alignment: .leading) {
                    Text(message.title)
                        .font(.headline)
                        .foregroundColor(message.isRead ? .secondary : .primary)
                    Text(message.sentDate, style: .date)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            .navigationTitle("Messages")
        }
    }
}

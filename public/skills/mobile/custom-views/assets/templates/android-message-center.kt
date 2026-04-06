// Android Message Center Customization Template

import com.urbanairship.messagecenter.MessageCenter
import com.urbanairship.messagecenter.Message
import android.content.Context

// MARK: - Custom Message Center Listener

class CustomMessageCenterHandler(private val context: Context) : MessageCenter.OnShowMessageCenterListener {

    override fun onShowMessageCenter(messageId: String?): Boolean {
        // Return true if you handle the display yourself
        // messageId is null for inbox, non-null for specific message

        if (messageId != null) {
            // Show specific message detail
            showMessageDetail(messageId)
        } else {
            // Show message list
            showMessageList()
        }

        return true // We handled it
    }

    private fun showMessageList() {
        // Launch your custom message list activity or composable
        // Example:
        // val intent = Intent(context, CustomMessageListActivity::class.java)
        // context.startActivity(intent)
    }

    private fun showMessageDetail(messageId: String) {
        // Launch your custom message detail activity
        // Example:
        // val intent = Intent(context, CustomMessageDetailActivity::class.java)
        // intent.putExtra("messageId", messageId)
        // context.startActivity(intent)
    }
}

// MARK: - Registration (add to Application.onCreate())

// MessageCenter.shared().setOnShowMessageCenterListener(CustomMessageCenterHandler(applicationContext))

// MARK: - Accessing Messages

// To get all messages:
// val messages = MessageCenter.shared().inbox.messages

// Each message has:
// - message.messageId
// - message.title
// - message.sentDate
// - message.isRead
// - message.extras
// - message.bodyUrl (for HTML content)

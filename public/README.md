# Airship Agent Tools — MCP Server

Unified MCP server for Airship SDK development.

## Capabilities

- **Push API**: Send notifications, manage channels, segments, and message center
- **Build Verification**: Build iOS/Android projects and analyze errors
- **SDK Migration**: Guided migration between SDK versions
- **Documentation**: Access Airship documentation as MCP resources
- **Skills**: All Airship skills available as MCP prompts

## Installation

```bash
uv run airship-mcp
```

## Environment Variables

**Required for Push API tools:**
- `AIRSHIP_APP_KEY` - Your Airship app key
- `AIRSHIP_MASTER_SECRET` - Your master secret
- `AIRSHIP_API_URL` - Optional, defaults to https://go.urbanairship.com

**Optional:**
- `AIRSHIP_MCP_MOUNT_XCODE=true` - Mount XcodeBuildMCP for iOS simulator tools

## MCP Configuration

```json
{
  "mcpServers": {
    "airship-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/internal-agent-tools/public", "airship-mcp"],
      "env": {
        "AIRSHIP_APP_KEY": "your_key",
        "AIRSHIP_MASTER_SECRET": "your_secret"
      }
    }
  }
}
```

## Tools

### Push API
- `send_push_to_tag` - Send notification to a tag
- `send_push_to_channel` - Send to specific device
- `send_custom_push` - Send any push payload
- `send_message_center_message` - Send inbox message
- `lookup_channel` - Get channel info
- `list_segments` / `create_segment` - Manage segments

### Build & Verification
- `verify_build` - Build iOS/Android project
- `check_build_tools` - Show available tools

### Migration
- `start_migration` - Interactive migration wizard
- `migrate_sdk` - Non-interactive migration

## Resources

- `airship://docs/api/push-spec` - Push API specification
- `airship://docs/api/examples` - Payload examples
- `airship://docs/setup/{platform}/{feature}` - Setup guides

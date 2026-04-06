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

**Authentication** (at least one method required, in priority order):
- `AIRSHIP_CLIENT_ID` + `AIRSHIP_CLIENT_SECRET` + `AIRSHIP_APP_KEY` — **recommended for production**; OAuth 2.0 client credentials obtained from go.airship.com > Settings > APIs & Integrations > OAuth. All three are required: the app key is the token subject (`sub=app:<key>`) in the token request.
- `AIRSHIP_BEARER_TOKEN` — dashboard-generated Bearer token; simpler alternative to OAuth
- `AIRSHIP_APP_KEY` + `AIRSHIP_MASTER_SECRET` — Basic Auth fallback

**Region:**
- `AIRSHIP_REGION` — `us` (default) or `eu`

**Overrides:**
- `AIRSHIP_API_URL` — override the Go API base URL entirely (staging, proxies, etc.)

**Optional integrations:**
- `AIRSHIP_MCP_MOUNT_XCODE=true` — mount XcodeBuildMCP for iOS simulator tools

## MCP Configuration

```json
{
  "mcpServers": {
    "airship-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/internal-agent-tools/public", "airship-mcp"],
      "env": {
        "AIRSHIP_BEARER_TOKEN": "your_bearer_token",
        "AIRSHIP_APP_KEY": "your_app_key",
        "AIRSHIP_REGION": "us"
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

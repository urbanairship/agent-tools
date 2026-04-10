# Airship Agent Tools

Airship tools and skills for AI assistants.

> **Warning:** Only install plugins and extensions from sources you trust. Airship does not guarantee compatibility with all AI assistant versions.

## What's included

- **MCP server** - push API, channel management, SDK migration, build verification, and all Airship skills exposed as prompts
- **Skills** (`skills/`) - standalone skill files for any assistant that supports them (push, message center, RTDS, wallet, workflows, and more)

---

## Install as a Claude Code Plugin

Claude Code plugins expose skills as slash commands and also run the MCP server automatically.

### Via marketplace (recommended)

```bash
claude plugin marketplace add /path/to/agent-tools
claude plugin install airship
```

Skills are available as `/airship:<skill-name>`.

### Manual (direct plugin dir)

Load without installing - useful for development:

```bash
claude --plugin-dir /path/to/agent-tools
```

---

## Install the MCP Server

The MCP server provides tools for push notifications, channel management, SDK migration, and build verification. Requires [uv](https://docs.astral.sh/uv/).

### Configuration

Add to your assistant's MCP config file:

```json
{
  "mcpServers": {
    "airship-mcp": {
      "command": "uv",
      "args": [
        "run",
        "--directory", "/path/to/agent-tools",
        "airship-mcp"
      ],
      "env": {
        "AIRSHIP_APP_KEY": "your_app_key",
        "AIRSHIP_CLIENT_ID": "your_client_id",
        "AIRSHIP_CLIENT_SECRET": "your_client_secret",
        "AIRSHIP_REGION": "us"
      }
    }
  }
}
```

Create OAuth client credentials in the Airship dashboard: next to your project name, select the dropdown menu, then **Settings**. Under **Project settings**, select **OAuth**. Enable **Allow Basic Auth** when creating credentials to generate a Client Secret. Enable the **Push**, **Channels**, and **Named Users** scopes at minimum.

### Config file locations by assistant

| Assistant | Config file |
|---|---|
| Claude Code | `.mcp.json` in project root, or `~/.claude/mcp.json` globally |
| Cursor | `.cursor/mcp.json` in project, or `~/.cursor/mcp.json` globally |
| Windsurf | `~/.codeium/windsurf/mcp_config.json` |
| Other | See your assistant's MCP documentation |

### Run directly

```bash
cd /path/to/agent-tools
AIRSHIP_APP_KEY=your_key AIRSHIP_CLIENT_ID=your_client_id AIRSHIP_CLIENT_SECRET=your_client_secret AIRSHIP_REGION=us uv run airship-mcp
```

---

## Install Individual Skills

Skills are Markdown files that give your assistant guided workflows for specific Airship features. Copy any skill folder into the directory your assistant reads for skills or rules.

### Skills location

```
skills/
├── api/           push-notification, email-registration, sms-registration, tags, ...
├── mobile/        push, message-center, migration, custom-views, sdk-reference
├── rtds/          rtds-connection
├── wallet/        update-wallet-pass
└── workflows/     complete-user-onboarding, register-associate-email, ...
```

### Install by assistant

| Assistant | Skills directory |
|---|---|
| Claude Code | `.claude/skills/<skill-name>/` in project, or `~/.claude/skills/` globally |
| Cursor | `.cursor/skills/<skill-name>/` in project |
| Windsurf | `.windsurf/rules/<skill-name>/` in project |
| Other | See your assistant's documentation for custom instructions or rules |

### Example - install the push-notification skill

```bash
# Claude Code
cp -r skills/api/push-notification .claude/skills/

# Cursor
cp -r skills/api/push-notification .cursor/skills/
```

Then invoke it with `/push-notification` in chat (exact command syntax varies by assistant).

### Install all public skills at once

```bash
cp -r skills/api/* .cursor/skills/
cp -r skills/mobile/* .cursor/skills/
cp -r skills/workflows/* .cursor/skills/
# etc.
```

Or use the MCP server's `install_skills` tool to install them interactively once the server is connected.

---

## Install as a Claude Desktop Extension

The extension bundles the MCP server and skills into a single file for one-click installation.

1. Double-click `airship-mcp.mcpb`, or drag it into **Claude Desktop -> Settings -> Extensions**.
2. Enter your credentials when prompted: App Key, OAuth Client ID, and OAuth Client Secret.

---

## Keeping up to date

How you update depends on how you installed:

| Installation method | How to update |
|---|---|
| Git clone + MCP config (any client) | `git pull` in the repo directory, then restart your client |
| Claude Code plugin (marketplace) | Claude Code checks at startup and notifies you — run `/reload-plugins` to apply |
| Claude Desktop extension (`.mcpb`) | Download the latest `.mcpb` from the releases page and reinstall |
| Skills only | `git pull`, then copy updated skill files into your assistant's skills/rules directory |

For git-based installs, `uv` automatically picks up dependency updates on the next run — no manual reinstall needed.

---

## License

Apache 2.0 - see [LICENSE](LICENSE).

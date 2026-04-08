"""
Airship MCP Server - Unified server for Airship SDK development.

Provides:
- Push API tools (notifications, channels, segments)
- Build verification (iOS/Android)
- SDK migration assistance
- Documentation resources
"""

import asyncio
import os
import re
import sys
import json
import tempfile
import subprocess
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict, Any, Optional, List

from fastmcp import FastMCP, Context
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware

# Import tool modules
from tools import api as api_tools
from tools.build import (
    check_xcode_mcp_available,
    get_xcode_mcp_command,
    get_ios_build_instructions,
    get_android_build_instructions,
    parse_xcode_build_errors,
    analyze_build_error,
    BuildToolsStatus,
)
from tools.constants import SUPPORTED_PLATFORMS, PLATFORM_TO_REPO_ID, SDK_REPOS
from tools.migration_fetcher import MigrationFetcher
from tools.migration_parser import (
    normalize_version, get_major_version, get_migration_path,
    extract_version_section, parse_migration_steps, generate_rollback_hint,
    extract_replacements, categorize_replacements
)
from tools.elicitation import elicit_with_fallback

# Resource paths
RESOURCES_DIR = Path(__file__).parent / "resources"
SKILLS_DIR = Path(__file__).parent / "skills"

# Cache fallback for install_skills / update_skills tools
_SKILLS_CACHE_DIR = Path.home() / ".cache" / "agent-tools" / "skills"
_SKILLS_REPO_URL = "https://github.com/urbanairship/agent-tools.git"

# Internal skills (only present when running from source, never in published package)
_INTERNAL_SKILLS_DIR = Path(__file__).parent.parent / "internal"


def _resolve_skills_src() -> Optional[Path]:
    """Return skills source dir for install_skills tool."""
    if SKILLS_DIR.exists() and any(SKILLS_DIR.iterdir()):
        return SKILLS_DIR
    if _SKILLS_CACHE_DIR.exists() and any(_SKILLS_CACHE_DIR.iterdir()):
        return _SKILLS_CACHE_DIR
    return None


def _iter_skill_dirs(base: Path):
    """Yield (skill_name, skill_path) for all skills under a categorized or flat skills dir."""
    if not base.exists():
        return
    for entry in sorted(base.iterdir()):
        if not entry.is_dir() or entry.name.startswith('.'):
            continue
        skill_md = entry / "SKILL.md"
        if skill_md.exists():
            # Flat layout: skills/push-notification/SKILL.md
            yield entry.name, entry
        else:
            # Categorized layout: skills/api/push-notification/SKILL.md
            for sub in sorted(entry.iterdir()):
                if sub.is_dir() and (sub / "SKILL.md").exists():
                    yield sub.name, sub


async def _fetch_skills(ctx=None) -> Dict[str, Any]:
    """Clone or update skills from the public GitHub repo."""
    if ctx:
        await ctx.info("Fetching Airship skills from GitHub...")

    try:
        proc = await asyncio.create_subprocess_exec(
            "git", "--version",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
        )
        await proc.communicate()
        if proc.returncode != 0:
            return {"status": "error", "message": "git is not available on PATH"}
    except FileNotFoundError:
        return {"status": "error", "message": "git is not installed"}

    if (_SKILLS_CACHE_DIR / ".git").exists():
        cmd = ["git", "pull", "--ff-only"]
        cwd = _SKILLS_CACHE_DIR
        action = "updated"
    else:
        import shutil
        if _SKILLS_CACHE_DIR.exists():
            shutil.rmtree(_SKILLS_CACHE_DIR)
        _SKILLS_CACHE_DIR.parent.mkdir(parents=True, exist_ok=True)
        cmd = ["git", "clone", _SKILLS_REPO_URL, str(_SKILLS_CACHE_DIR)]
        cwd = _SKILLS_CACHE_DIR.parent
        action = "cloned"

    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT, cwd=cwd
    )
    stdout, _ = await proc.communicate()
    output = stdout.decode().strip()

    if proc.returncode != 0:
        return {"status": "error", "message": f"git {action} failed: {output}"}

    if ctx:
        await ctx.info(f"Skills {action} successfully.")
    return {"status": "success", "action": action, "path": str(_SKILLS_CACHE_DIR)}


@asynccontextmanager
async def lifespan(app):
    """Server lifespan: initialize OAuth on startup; clean up clients on shutdown."""
    if os.environ.get("AIRSHIP_CLIENT_ID"):
        try:
            await api_tools.init_oauth()
        except Exception as e:
            print(f"OAuth initialization failed: {e}")
            raise
    yield
    await api_tools.cleanup()


# Create FastMCP server
mcp = FastMCP(
    name="Airship MCP",
    instructions="""Unified Airship SDK development server.

    ## Tool Selection (IMPORTANT)

    Choose the right tool based on user intent:
    - "migrate", "upgrade SDK", "update SDK" → `start_migration()`
    - "send push", "notification" → `send_push_to_tag()` or `send_push_to_channel()`
    - "create presentation", "slide deck", "slides" → `start()` (routes to airship-slides skill)
    - "lookup channel", "find device" → `lookup_channel()`
    - "build", "verify" → `verify_build()`
    - unclear/generic request → `start()`

    DO NOT call `start()` when user intent is already clear.

    ## Capabilities

    ### Push API
    Send notifications, manage channels, segments, and message center.
    - `send_push_to_tag` - Send to devices with a tag
    - `send_push_to_channel` - Send to specific device
    - `send_message_center_message` - Send inbox message with HTML
    - `lookup_channel` - Get channel info and opt-in status
    - `list_segments` / `create_segment` - Manage audience segments

    ### Build & Verification
    Build projects and verify Airship integration.
    - `verify_build` - Build iOS/Android project
    - `check_build_tools` - Show available build tools

    ### SDK Migration
    Guided migration between SDK versions.
    - `start_migration` - Interactive migration wizard
    - `migrate_sdk` - Non-interactive migration with parameters

    ### Documentation Resources
    Access Airship documentation via resources:
    - `airship://docs/api/push-spec` - Push API specification
    - `airship://docs/api/examples` - Payload examples
    - `airship://docs/setup/{platform}/{feature}` - Setup guides
    - `airship://docs/troubleshooting/{topic}` - Troubleshooting

    ## Environment Variables

    **Required for Push API tools:**
    - `AIRSHIP_APP_KEY` - Your Airship app key
    - `AIRSHIP_MASTER_SECRET` - Your master secret
    - `AIRSHIP_API_URL` - Optional, defaults to https://go.urbanairship.com

    **Optional integrations:**
    - `AIRSHIP_MCP_MOUNT_XCODE=true` - Mount XcodeBuildMCP for iOS simulator

    ## Platform Support

    iOS, Android, React Native, Flutter, Capacitor, Cordova, .NET
    """,
    version="1.0.0",
    lifespan=lifespan,
)

mcp.add_middleware(ErrorHandlingMiddleware(
    include_traceback=False,
    transform_errors=True,
))


# =============================================================================
# Entry Point / Router
# =============================================================================

@mcp.tool
async def start(ctx: Context) -> Dict[str, Any]:
    """
    Start the Airship assistant. Only call this when the user's intent is unclear.

    DO NOT call this if the user's intent is already clear:
    - For migration/upgrade → call start_migration() directly
    - For sending push → call send_push_to_tag() or send_push_to_channel() directly
    - For channel lookup → call lookup_channel() directly

    Only use start() when user says something generic like "help me with Airship".
    """
    from fastmcp.server.elicitation import AcceptedElicitation, DeclinedElicitation, CancelledElicitation

    await ctx.info("Welcome to Airship MCP!")

    # Define the main capabilities
    capabilities = [
        "Implement a Feature",
        "Send Push Notification",
        "Create Presentation",
        "Migrate SDK Version",
        "Lookup Channel/User",
        "Install Skills",
        "View Documentation",
    ]

    try:
        result = await ctx.elicit(
            "What would you like to do?",
            response_type=capabilities
        )

        if isinstance(result, (DeclinedElicitation, CancelledElicitation)):
            return {"status": "cancelled", "message": "No problem! Call any tool directly when ready."}

        choice = result.data if isinstance(result, AcceptedElicitation) else None

    except Exception:
        # Elicitation not supported - return capabilities list
        return {
            "status": "info",
            "message": "Elicitation not supported. Here are the available capabilities:",
            "capabilities": {
                "implement_feature": {
                    "description": "Use skills to implement Airship features with guided workflows",
                    "skills": ["push", "message-center", "migration", "airship-custom-views"],
                    "usage": "Type /push, /message-center, /migration, or /airship-custom-views in chat",
                },
                "push_notifications": {
                    "description": "Send push notifications to tags, channels, or named users",
                    "tools": ["send_push_to_tag", "send_push_to_channel", "send_custom_push", "send_message_center_message"],
                },
                "create_presentation": {
                    "description": "Generate branded Airship presentations as editable PPTX files",
                    "skill": "/airship-slides",
                    "usage": "Type /airship-slides in chat or ask to create a presentation",
                },
                "migration": {
                    "description": "Guided SDK version migration with rollback instructions",
                    "tools": ["start_migration", "migrate_sdk"],
                },
                "lookup": {
                    "description": "Look up channels, named users, and segments",
                    "tools": ["lookup_channel", "lookup_named_user", "list_segments", "get_segment_info"],
                },
                "documentation": {
                    "description": "Access setup guides, API specs, and troubleshooting",
                    "skill": "/airship-docs",
                    "resources": [
                        "airship://docs/api/push-spec",
                        "airship://docs/api/examples",
                        "airship://docs/setup/{platform}/{feature}",
                    ],
                },
            },
            "skills_info": {
                "location": "agent-tools (https://github.com/urbanairship/agent-tools)",
                "invocation": "Type /<skill-name> in chat or let the agent auto-select based on context",
                "available": ["push", "message-center", "migration", "airship-custom-views", "airship-docs", "airship-slides"],
            },
            "hint": "Call any tool directly, e.g., send_push_to_tag(tag='test', alert='Hello!')",
        }

    # Route based on choice
    if choice == "Implement a Feature":
        return await _start_feature_flow(ctx)
    elif choice == "Send Push Notification":
        return await _start_push_flow(ctx)
    elif choice == "Create Presentation":
        return _start_slides_flow()
    elif choice == "Migrate SDK Version":
        return await _start_migration_flow(ctx)
    elif choice == "Lookup Channel/User":
        return await _start_lookup_flow(ctx)
    elif choice == "Install Skills":
        return await _start_install_skills_flow(ctx)
    elif choice == "View Documentation":
        return await _start_docs_flow(ctx)
    else:
        return {"status": "info", "message": f"Selected: {choice}. Call the appropriate tool to continue."}


async def _start_push_flow(ctx: Context) -> Dict[str, Any]:
    """Guide user through sending a push notification."""
    from fastmcp.server.elicitation import AcceptedElicitation, DeclinedElicitation, CancelledElicitation

    push_types = ["Send to Tag", "Send to Channel", "Send to Named User", "Send Message Center Message"]

    try:
        result = await ctx.elicit("What type of push?", response_type=push_types)
        if isinstance(result, (DeclinedElicitation, CancelledElicitation)):
            return {"status": "cancelled"}
        push_type = result.data if isinstance(result, AcceptedElicitation) else None
    except Exception:
        return {
            "status": "info",
            "tools": {
                "send_push_to_tag": "send_push_to_tag(tag='users', alert='Hello!', title='Greeting')",
                "send_push_to_channel": "send_push_to_channel(channel_id='...', platform='ios', alert='Hello!')",
                "send_message_center_message": "send_message_center_message(title='Welcome', body_html='<h1>Hi</h1>', tag='users')",
            }
        }

    if push_type == "Send to Tag":
        # Get tag
        result = await ctx.elicit("Enter the tag to target:", response_type=str)
        if isinstance(result, (DeclinedElicitation, CancelledElicitation)):
            return {"status": "cancelled"}
        tag = result.data

        # Get message
        result = await ctx.elicit("Enter the notification message:", response_type=str)
        if isinstance(result, (DeclinedElicitation, CancelledElicitation)):
            return {"status": "cancelled"}
        alert = result.data

        # Get optional title
        result = await ctx.elicit("Enter title (optional, press enter to skip):", response_type=str)
        title = result.data if isinstance(result, AcceptedElicitation) and result.data else None

        # Send the push
        return await api_tools.send_push_to_tag(tag, alert, title)

    elif push_type == "Send to Channel":
        result = await ctx.elicit("Enter the channel ID:", response_type=str)
        if isinstance(result, (DeclinedElicitation, CancelledElicitation)):
            return {"status": "cancelled"}
        channel_id = result.data

        platforms = ["ios", "android", "web"]
        result = await ctx.elicit("Select platform:", response_type=platforms)
        if isinstance(result, (DeclinedElicitation, CancelledElicitation)):
            return {"status": "cancelled"}
        platform = result.data

        result = await ctx.elicit("Enter the notification message:", response_type=str)
        if isinstance(result, (DeclinedElicitation, CancelledElicitation)):
            return {"status": "cancelled"}
        alert = result.data

        return await api_tools.send_push_to_channel(channel_id, platform, alert)

    elif push_type == "Send to Named User":
        return {
            "status": "info",
            "message": "Use send_custom_push with named_user audience",
            "example": {
                "audience": {"named_user": "user_123"},
                "notification": {"alert": "Hello!"},
                "device_types": ["ios", "android"]
            },
            "tool": "send_custom_push(payload={...})"
        }

    elif push_type == "Send Message Center Message":
        result = await ctx.elicit("Enter message title:", response_type=str)
        if isinstance(result, (DeclinedElicitation, CancelledElicitation)):
            return {"status": "cancelled"}
        title = result.data

        result = await ctx.elicit("Enter HTML body (e.g., <h1>Welcome</h1><p>Hello!</p>):", response_type=str)
        if isinstance(result, (DeclinedElicitation, CancelledElicitation)):
            return {"status": "cancelled"}
        body_html = result.data

        result = await ctx.elicit("Enter target tag:", response_type=str)
        if isinstance(result, (DeclinedElicitation, CancelledElicitation)):
            return {"status": "cancelled"}
        tag = result.data

        return await api_tools.send_message_center_message(title, body_html, tag=tag)

    return {"status": "info", "message": "Select a push type to continue."}


async def _start_feature_flow(ctx: Context) -> Dict[str, Any]:
    """Guide user to implement an Airship feature using skills."""
    from fastmcp.server.elicitation import AcceptedElicitation, DeclinedElicitation, CancelledElicitation

    # First, elicit the working directory
    try:
        result = await ctx.elicit(
            "Enter your project directory path:",
            response_type=str
        )
        if isinstance(result, (DeclinedElicitation, CancelledElicitation)):
            return {"status": "cancelled"}
        project_path = result.data.strip().strip('"\'').replace("\\ ", " ") if isinstance(result, AcceptedElicitation) else "."
    except Exception:
        return _get_skills_info()

    project = Path(project_path).expanduser().resolve()
    if not project.exists():
        return {"status": "error", "message": f"Project directory does not exist: {project_path}"}

    await ctx.info(f"Project: {project}")

    # Check if skills are installed
    cursor_skills = project / ".cursor" / "skills"
    skills_installed = cursor_skills.exists() and any(cursor_skills.iterdir()) if cursor_skills.exists() else False

    if not skills_installed:
        # Offer to install skills
        try:
            result = await ctx.elicit(
                "Airship skills are not installed in this project. Install them now?",
                response_type=["Yes, install skills", "No, continue without skills"]
            )
            if isinstance(result, AcceptedElicitation) and result.data == "Yes, install skills":
                # Install skills
                skills_src = _resolve_skills_src()
                if skills_src is None:
                    await ctx.info("Downloading Airship skills...")
                    fetch_result = await _fetch_skills(ctx)
                    if fetch_result["status"] != "error":
                        skills_src = _SKILLS_CACHE_DIR
                if skills_src is not None:
                    cursor_skills.mkdir(parents=True, exist_ok=True)
                    available_skills = [d.name for d in skills_src.iterdir() if d.is_dir() and not d.name.startswith('.')]
                    for skill_name in available_skills:
                        skill_dest = cursor_skills / skill_name
                        if skill_dest.exists() or skill_dest.is_symlink():
                            skill_dest.unlink()
                        skill_dest.symlink_to(skills_src / skill_name)
                        await ctx.info(f"  ✓ Installed: {skill_name}")
                    skills_installed = True
        except Exception:
            pass

    # Now ask which feature
    features = [
        "Push Notifications",
        "Message Center (Inbox)",
        "Preference Center",
        "In-App Messages",
        "Custom Views (Thomas)",
    ]

    try:
        result = await ctx.elicit("Which feature do you want to implement?", response_type=features)
        if isinstance(result, (DeclinedElicitation, CancelledElicitation)):
            return {"status": "cancelled"}
        feature = result.data if isinstance(result, AcceptedElicitation) else None
    except Exception:
        return _get_skills_info()

    # Map feature to skill
    skill_map = {
        "Push Notifications": "push",
        "Message Center (Inbox)": "message-center",
        "Preference Center": "preference-center",
        "In-App Messages": "in-app-automation",
        "Custom Views (Thomas)": "airship-custom-views",
    }

    skill_name = skill_map.get(feature, "airship-docs")

    response = {
        "status": "use_skill",
        "feature": feature,
        "skill": skill_name,
        "project_path": str(project),
        "skills_installed": skills_installed,
        "instructions": {
            "step_1": f"Type /{skill_name} in Cursor chat to start the guided workflow",
            "step_2": "The skill will guide you through implementation",
            "step_3": f"Use verify_build(project_path='{project}') to test",
        },
        "mcp_tools_for_testing": {
            "Push Notifications": ["send_push_to_tag", "send_push_to_channel", "lookup_channel"],
            "Message Center (Inbox)": ["send_message_center_message"],
            "Preference Center": ["lookup_channel", "get_channel_tags"],
            "In-App Messages": ["verify_build"],
            "Custom Views (Thomas)": ["verify_build"],
        }.get(feature, []),
    }

    if not skills_installed:
        response["warning"] = "Skills not installed. Run install_skills(project_path='...') or use 'Install Skills' from the main menu."

    return response


def _get_skills_info() -> Dict[str, Any]:
    """Return information about available skills."""
    return {
        "status": "info",
        "message": "Use skills to implement Airship features with guided workflows.",
        "available_skills": {
            "push": {
                "description": "Implement push notifications",
                "invoke": "/push",
                "includes": ["Setup guides for all platforms", "Configuration validation", "Testing with MCP tools"],
            },
            "message-center": {
                "description": "Implement Message Center (app inbox)",
                "invoke": "/message-center",
                "includes": ["Inbox UI setup", "HTML message formatting", "Customization options"],
            },
            "migration": {
                "description": "Upgrade Airship SDK versions",
                "invoke": "/migration",
                "includes": ["Version detection", "Step-by-step migration", "Rollback instructions"],
            },
            "airship-custom-views": {
                "description": "Register custom views for Thomas scenes",
                "invoke": "/airship-custom-views",
                "includes": ["iOS/Android registration code", "Property handling", "Scene YAML examples"],
            },
            "airship-docs": {
                "description": "Comprehensive Airship documentation",
                "invoke": "/airship-docs",
                "includes": ["API specs", "Setup guides", "Troubleshooting"],
            },
            "airship-slides": {
                "description": "Generate branded Airship presentations (PPTX)",
                "invoke": "/airship-slides",
                "includes": ["28 brand layouts", "Icon/photo assets", "Auto-remediation"],
            },
        },
        "how_to_use": {
            "option_1": "Type /<skill-name> in chat (e.g., /push)",
            "option_2": "Ask about a feature - agent will auto-load relevant skill",
            "option_3": "Skills reference MCP tools for building and testing",
        },
        "skill_locations": {
            "primary": "~/.cache/agent-tools/skills/",
            "cursor_symlinks": ".cursor/skills/",
        },
    }


async def _start_migration_flow(ctx: Context) -> Dict[str, Any]:
    """Run the interactive migration wizard."""
    # Directly run the migration flow with elicitation
    return await _run_migration_flow(ctx)


async def _start_lookup_flow(ctx: Context) -> Dict[str, Any]:
    """Guide user through channel/user lookup."""
    from fastmcp.server.elicitation import AcceptedElicitation, DeclinedElicitation, CancelledElicitation

    lookup_types = ["Lookup Channel", "Lookup Named User", "List Segments"]

    try:
        result = await ctx.elicit("What do you want to look up?", response_type=lookup_types)
        if isinstance(result, (DeclinedElicitation, CancelledElicitation)):
            return {"status": "cancelled"}
        lookup_type = result.data
    except Exception:
        return {
            "status": "info",
            "tools": {
                "lookup_channel": "lookup_channel(channel_id='...')",
                "lookup_named_user": "lookup_named_user(named_user_id='...')",
                "list_segments": "list_segments()",
            }
        }

    if lookup_type == "Lookup Channel":
        result = await ctx.elicit("Enter the channel ID:", response_type=str)
        if isinstance(result, (DeclinedElicitation, CancelledElicitation)):
            return {"status": "cancelled"}
        channel_id = result.data
        return await api_tools.lookup_channel(channel_id)

    elif lookup_type == "Lookup Named User":
        result = await ctx.elicit("Enter the named user ID:", response_type=str)
        if isinstance(result, (DeclinedElicitation, CancelledElicitation)):
            return {"status": "cancelled"}
        named_user_id = result.data
        return await api_tools.lookup_named_user(named_user_id)

    elif lookup_type == "List Segments":
        return await api_tools.list_segments()

    return {"status": "info", "message": "Select a lookup type."}


async def _start_docs_flow(ctx: Context) -> Dict[str, Any]:
    """Guide user to documentation via skills and MCP resources."""
    return {
        "status": "info",
        "message": "Documentation is available via skills and MCP resources.",
        "skills": {
            "airship-docs": {
                "description": "Comprehensive documentation skill",
                "invoke": "/airship-docs",
                "contents": ["API specs", "Setup guides", "Troubleshooting", "Platform guides"],
            },
        },
        "mcp_resources": {
            "Push API Spec": "airship://docs/api/push-spec",
            "Payload Examples": "airship://docs/api/examples",
            "HTML Reference": "airship://docs/api/html-reference",
            "Setup Guides": "airship://docs/setup/{platform}/{feature}",
        },
        "platforms": ["ios", "android", "react-native", "flutter", "capacitor", "cordova"],
        "features": ["push", "message-center", "preference-center", "feature-flags"],
        "examples": [
            "Type /airship-docs in chat for guided documentation",
            "Read resource: airship://docs/api/push-spec",
            "Read resource: airship://docs/setup/ios/push",
        ],
    }


def _start_slides_flow() -> Dict[str, Any]:
    """Direct user to the airship-slides skill for presentation generation."""
    return {
        "status": "use_skill",
        "skill": "airship-slides",
        "instructions": {
            "step_1": "Type /airship-slides in chat to start the presentation workflow",
            "step_2": "Describe the presentation topic, audience, and key messages",
            "step_3": "The skill generates a branded PPTX using the Airship master template",
        },
        "prerequisites": "Python 3 with python-pptx installed (pip3 install python-pptx)",
        "output": "Fully editable PPTX file compatible with PowerPoint, Google Slides, and Keynote",
    }


async def _start_install_skills_flow(ctx: Context) -> Dict[str, Any]:
    """Install Airship skills into a project directory for use with Cursor, Windsurf, or any AI assistant that supports skill files."""
    from fastmcp.server.elicitation import AcceptedElicitation, DeclinedElicitation, CancelledElicitation

    await ctx.info("Installing Airship skills...")

    # Get the skills source directory
    skills_src = _resolve_skills_src()
    if skills_src is None:
        await ctx.info("Downloading Airship skills...")
        result = await _fetch_skills(ctx)
        if result["status"] == "error":
            return result
        skills_src = _SKILLS_CACHE_DIR

    available_skills = [d.name for d in skills_src.iterdir() if d.is_dir() and not d.name.startswith('.')]
    await ctx.info(f"Available skills: {', '.join(available_skills)}")

    # Elicit target project directory
    try:
        result = await ctx.elicit(
            "Enter the project directory where you want to install skills:",
            response_type=str
        )
        if isinstance(result, (DeclinedElicitation, CancelledElicitation)):
            return {"status": "cancelled", "message": "Installation cancelled"}
        project_path = result.data.strip().strip('"\'').replace("\\ ", " ") if isinstance(result, AcceptedElicitation) else "."
    except Exception:
        return {
            "status": "error",
            "message": "Elicitation not supported. Use install_skills(project_path='...') directly.",
        }

    project = Path(project_path).expanduser().resolve()
    if not project.exists():
        return {"status": "error", "message": f"Project directory does not exist: {project_path}"}

    # Create .cursor/skills directory (compatible with Cursor, Windsurf, and similar tools)
    cursor_skills = project / ".cursor" / "skills"
    cursor_skills.mkdir(parents=True, exist_ok=True)
    await ctx.info(f"Created: {cursor_skills}")

    # Symlink each skill
    installed = []
    for skill_name in available_skills:
        skill_src = skills_src / skill_name
        skill_dest = cursor_skills / skill_name

        if skill_dest.exists() or skill_dest.is_symlink():
            skill_dest.unlink()  # Remove existing symlink

        try:
            skill_dest.symlink_to(skill_src)
            installed.append(skill_name)
            await ctx.info(f"  ✓ Installed: {skill_name}")
        except Exception as e:
            await ctx.info(f"  ✗ Failed: {skill_name} - {e}")

    await ctx.info(f"\nInstalled {len(installed)} skills to {cursor_skills}")

    # Ask what they want to do next
    next_options = [
        "Implement Custom Views",
        "Set Up Push Notifications",
        "Set Up Message Center",
        "Create Presentation",
        "Migrate SDK Version",
        "Done",
    ]

    try:
        result = await ctx.elicit(
            "Skills installed! What would you like to do next?",
            response_type=next_options
        )
        if isinstance(result, (DeclinedElicitation, CancelledElicitation)):
            next_choice = "Done"
        else:
            next_choice = result.data if isinstance(result, AcceptedElicitation) else "Done"
    except Exception:
        next_choice = "Done"

    response = {
        "status": "success",
        "installed_skills": installed,
        "project_path": str(project),
        "cursor_skills_path": str(cursor_skills),
        "usage": {
            "instructions": "Type /<skill-name> in your AI assistant's chat (e.g., /airship-custom-views, /push, /airship-slides).",
            "available_skills": installed,
        },
    }

    # Route to next action
    if next_choice == "Implement Custom Views":
        response["next_action"] = {
            "skill": "airship-custom-views",
            "instruction": "Type /airship-custom-views in chat to start the custom views workflow.",
        }
    elif next_choice == "Set Up Push Notifications":
        response["next_action"] = {
            "skill": "push",
            "instruction": "Type /push in chat to start push notification setup.",
        }
    elif next_choice == "Set Up Message Center":
        response["next_action"] = {
            "skill": "message-center",
            "instruction": "Type /message-center in chat to start Message Center setup.",
        }
    elif next_choice == "Create Presentation":
        response["next_action"] = {
            "skill": "airship-slides",
            "instruction": "Type /airship-slides in chat to create a branded presentation.",
        }
    elif next_choice == "Migrate SDK Version":
        return await _start_migration_flow(ctx)
    else:
        response["message"] = "Skills installed. Type /<skill-name> in your AI assistant to get started."

    return response


@mcp.tool
async def install_skills(ctx: Context, project_path: str) -> Dict[str, Any]:
    """
    Install Airship skills into a project directory for use with Cursor, Windsurf, or any AI assistant that supports skill files.

    Skills provide guided workflows for implementing Airship features:
    - airship-custom-views: Register custom native views for Thomas scenes
    - push: Set up push notifications
    - message-center: Implement Message Center (inbox)
    - migration: Upgrade SDK versions
    - airship-slides: Generate branded Airship presentations (PPTX)

    Args:
        project_path: Path to the project directory
    """
    skills_src = _resolve_skills_src()
    if skills_src is None:
        if ctx:
            await ctx.info("Downloading Airship skills...")
        result = await _fetch_skills(ctx)
        if result["status"] == "error":
            return result
        skills_src = _SKILLS_CACHE_DIR

    available_skills = [d.name for d in skills_src.iterdir() if d.is_dir() and not d.name.startswith('.')]

    project = Path(project_path).expanduser().resolve()
    if not project.exists():
        return {"status": "error", "message": f"Project directory does not exist: {project_path}"}

    cursor_skills = project / ".cursor" / "skills"
    cursor_skills.mkdir(parents=True, exist_ok=True)

    installed = []
    for skill_name in available_skills:
        skill_src_path = skills_src / skill_name
        skill_dest = cursor_skills / skill_name

        if skill_dest.exists() or skill_dest.is_symlink():
            skill_dest.unlink()

        try:
            skill_dest.symlink_to(skill_src_path)
            installed.append(skill_name)
            await ctx.info(f"Installed: {skill_name}")
        except Exception as e:
            await ctx.info(f"Failed: {skill_name} - {e}")

    return {
        "status": "success",
        "installed_skills": installed,
        "project_path": str(project),
        "skills_path": str(cursor_skills),
        "usage": "Type /<skill-name> in your AI assistant's chat (e.g., /airship-custom-views, /push).",
    }


@mcp.tool
async def update_skills(ctx: Context) -> Dict[str, Any]:
    """
    Download or update Airship skills from GitHub.

    Fetches the latest skills into ~/.cache/agent-tools/skills/.
    Use this to get skills when they are not available locally, or to update an existing cached copy.
    Once downloaded, run install_skills(project_path='...') to install them into your project.
    """
    result = await _fetch_skills(ctx)
    if result["status"] == "error":
        return result

    skills_path = Path(result["path"])
    available = [d.name for d in skills_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
    result["available_skills"] = available
    result["next_step"] = "Run install_skills(project_path='...') to install skills into your project."
    return result


# =============================================================================
# Documentation Resources
# =============================================================================

def _read_resource(path: str) -> str:
    """Read a resource file."""
    full_path = RESOURCES_DIR / path
    if not full_path.resolve().is_relative_to(RESOURCES_DIR.resolve()):
        return f"Resource not found: {path}"
    if full_path.exists():
        return full_path.read_text()
    return f"Resource not found: {path}"


@mcp.resource("airship://docs/api/push-spec")
def get_push_api_spec() -> str:
    """Complete Push API specification."""
    return _read_resource("push-api-spec.md")


@mcp.resource("airship://docs/api/examples")
def get_push_examples() -> str:
    """Working payload examples for all use cases."""
    return _read_resource("push-examples.md")


@mcp.resource("airship://docs/api/html-reference")
def get_html_reference() -> str:
    """HTML formatting guide for Message Center."""
    return _read_resource("html-reference.md")


@mcp.resource("airship://docs/setup/{platform}/{feature}")
def get_setup_guide(platform: str, feature: str) -> str:
    """Get setup guide for a platform and feature.

    Platforms: ios, android, react-native, flutter, capacitor, cordova
    Features: push, message-center, preference-center, feature-flags
    """
    path = f"setup/{platform}/setup/{feature}-setup.md"
    return _read_resource(path)


@mcp.resource("airship://docs/troubleshooting/{topic}")
def get_troubleshooting(topic: str) -> str:
    """Get troubleshooting guide for a topic."""
    # Try common locations
    for platform in ["ios", "android", "react-native", "flutter", "capacitor", "cordova"]:
        path = f"troubleshooting/{platform}/{topic}-troubleshooting.md"
        content = _read_resource(path)
        if not content.startswith("Resource not found"):
            return content
    return f"Troubleshooting guide not found for: {topic}"


# =============================================================================
# Skill Prompts (Claude Desktop access to skills)
# =============================================================================

def _register_skill_prompts():
    """Dynamically register all bundled skills as MCP prompts."""
    skill_dirs = [SKILLS_DIR]
    if _INTERNAL_SKILLS_DIR.exists():
        skill_dirs.append(_INTERNAL_SKILLS_DIR)

    seen: set[str] = set()

    for base in skill_dirs:
        for skill_name, skill_path in _iter_skill_dirs(base):
            if skill_name in seen:
                continue
            seen.add(skill_name)

            try:
                skill_content = (skill_path / "SKILL.md").read_text()
            except OSError:
                continue

            # Extract description from frontmatter
            description = f"Airship skill: {skill_name}"
            for line in skill_content.splitlines():
                if line.startswith("description:"):
                    description = line.split(":", 1)[1].strip().strip('"')
                    break

            def make_prompt_fn(content):
                def prompt_fn() -> str:
                    return content
                return prompt_fn

            mcp.prompt(make_prompt_fn(skill_content), name=skill_name, description=description)

_register_skill_prompts()


# =============================================================================
# Push API Tools
# =============================================================================

@mcp.tool
async def send_push_to_tag(
    tag: str,
    alert: str,
    title: str = None,
    platforms: list = None
) -> Dict[str, Any]:
    """
    Send a push notification to all devices with a specific tag.

    Args:
        tag: Tag to target (e.g., "news_subscribers")
        alert: Message body
        title: Optional title (recommended for Android/Web)
        platforms: Target platforms. Defaults to ["ios", "android"]
    """
    return await api_tools.send_push_to_tag(tag, alert, title, platforms)


@mcp.tool
async def send_push_to_channel(
    channel_id: str,
    platform: str,
    alert: str,
    title: str = None
) -> Dict[str, Any]:
    """
    Send a push notification to a specific channel (device).

    Args:
        channel_id: The Airship channel ID
        platform: Platform: "ios", "android", "web"
        alert: Message body
        title: Optional title
    """
    return await api_tools.send_push_to_channel(channel_id, platform, alert, title)


@mcp.tool
async def send_custom_push(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Universal tool for sending ANY push notification.

    See airship://docs/api/examples for payload examples.
    """
    return await api_tools.send_custom_push(payload)


@mcp.tool
async def send_message_center_message(
    title: str,
    body_html: str,
    tag: str = None,
    channel_id: str = None,
    named_user: str = None,
    send_alert: bool = False,
    alert_text: str = None,
    expiry: str = None
) -> Dict[str, Any]:
    """
    Send a message center message with HTML content.

    Args:
        title: Message title (shown in inbox list)
        body_html: HTML content (see airship://docs/api/html-reference)
        tag: Target tag (provide one of: tag, channel_id, named_user)
        channel_id: Target channel ID
        named_user: Target named user
        send_alert: Whether to also send a push notification
        alert_text: Push text (required if send_alert=True)
        expiry: Message expiry (e.g., "+7d", ISO timestamp)
    """
    return await api_tools.send_message_center_message(
        title, body_html, tag, channel_id, named_user,
        send_alert, alert_text, expiry
    )


@mcp.tool
async def validate_push_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a push payload without sending (test mode)."""
    return await api_tools.validate_push_payload(payload)


@mcp.tool
async def lookup_channel(channel_id: str) -> Dict[str, Any]:
    """Look up channel information by channel ID."""
    return await api_tools.lookup_channel(channel_id)


@mcp.tool
async def get_channel_tags(channel_id: str) -> Dict[str, Any]:
    """Get all tags applied to a specific channel."""
    return await api_tools.get_channel_tags(channel_id)


@mcp.tool
async def get_channel_attributes(channel_id: str) -> Dict[str, Any]:
    """Get custom attributes for a specific channel."""
    return await api_tools.get_channel_attributes(channel_id)


@mcp.tool
async def lookup_named_user(named_user_id: str) -> Dict[str, Any]:
    """Look up a named user and their associated channels."""
    return await api_tools.lookup_named_user(named_user_id)


@mcp.tool
async def list_segments() -> Dict[str, Any]:
    """List all audience segments."""
    return await api_tools.list_segments()


@mcp.tool
async def get_segment_info(segment_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific segment."""
    return await api_tools.get_segment_info(segment_id)


@mcp.tool
async def create_segment(name: str, criteria: Dict[str, Any]) -> Dict[str, Any]:
    """Create an audience segment for reusable targeting."""
    return await api_tools.create_segment(name, criteria)


@mcp.tool
async def delete_segment(segment_id: str) -> Dict[str, Any]:
    """Delete an audience segment."""
    return await api_tools.delete_segment(segment_id)


# =============================================================================
# Build & Verification Tools
# =============================================================================

_build_tools_status = BuildToolsStatus()
_xcode_mcp_mounted = False


def _try_mount_xcode_mcp():
    """Attempt to mount XcodeBuildMCP as a proxy."""
    global _xcode_mcp_mounted, _build_tools_status

    if not check_xcode_mcp_available():
        return False

    try:
        command, args = get_xcode_mcp_command()
        xcode_proxy = FastMCP.as_proxy(
            "stdio",
            command=command,
            args=args,
        )
        mcp.mount(xcode_proxy, prefix="xcode")
        _xcode_mcp_mounted = True
        _build_tools_status.ios_available = True
        _build_tools_status.ios_tool_prefix = "xcode"
        return True
    except Exception as e:
        print(f"Note: XcodeBuildMCP not mounted: {e}")
        return False


# Mount XcodeBuildMCP if enabled
if os.environ.get("AIRSHIP_MCP_MOUNT_XCODE", "").lower() == "true":
    _try_mount_xcode_mcp()


@mcp.tool
async def check_build_tools(ctx: Context) -> Dict[str, Any]:
    """
    Check which build verification tools are available.

    Returns status of iOS and Android build capabilities.
    """
    global _build_tools_status, _xcode_mcp_mounted

    result = {
        "status": "success",
        "tools": _build_tools_status.to_dict(),
        "xcode_mcp_mounted": _xcode_mcp_mounted,
    }

    if not _xcode_mcp_mounted:
        result["ios_instructions"] = get_ios_build_instructions()

    result["android_instructions"] = get_android_build_instructions()

    messages = []
    if _xcode_mcp_mounted:
        messages.append("XcodeBuildMCP is mounted (xcode_* tools available)")
    else:
        messages.append("XcodeBuildMCP not mounted - set AIRSHIP_MCP_MOUNT_XCODE=true to enable")

    result["message"] = ". ".join(messages)
    return result


async def _verify_build_impl(
    ctx: Context,
    project_path: str,
    platform: Optional[str] = None,
    scheme: Optional[str] = None,
    clean: bool = False,
) -> Dict[str, Any]:
    """Internal build verification logic - callable from other functions."""
    project = Path(project_path)

    # Auto-detect platform
    if not platform:
        if project.suffix in [".xcodeproj", ".xcworkspace"]:
            platform = "iOS"
        elif project.is_dir():
            if list(project.glob("*.xcodeproj")) or list(project.glob("*.xcworkspace")):
                platform = "iOS"
            elif list(project.glob("build.gradle*")) or list(project.glob("*/build.gradle*")):
                platform = "Android"
            else:
                return {
                    "status": "error",
                    "message": f"Could not detect platform for: {project_path}",
                    "hint": "Specify platform='iOS' or platform='Android'"
                }
        else:
            return {"status": "error", "message": f"Project path does not exist: {project_path}"}

    await ctx.info(f"Building {platform} project: {project_path}")

    if platform == "iOS":
        return await _build_ios(ctx, project, scheme, clean)
    elif platform == "Android":
        return await _build_android(ctx, project, scheme, clean)
    else:
        return {"status": "error", "message": f"Unsupported platform: {platform}"}


@mcp.tool
async def verify_build(
    ctx: Context,
    project_path: str,
    platform: Optional[str] = None,
    scheme: Optional[str] = None,
    clean: bool = False,
) -> Dict[str, Any]:
    """
    Build the project to verify integration.

    Args:
        project_path: Path to project directory or file
        platform: Platform (iOS, Android). Auto-detected if not provided.
        scheme: Build scheme (iOS) or variant (Android)
        clean: Whether to clean before building
    """
    return await _verify_build_impl(ctx, project_path, platform, scheme, clean)


async def _build_ios(ctx: Context, project_path: Path, scheme: Optional[str], clean: bool) -> Dict[str, Any]:
    """Build iOS project using xcodebuild."""
    start_time = time.time()

    if project_path.is_dir():
        workspaces = [w for w in project_path.glob("*.xcworkspace") if not w.name.startswith(".")]
        projects = list(project_path.glob("*.xcodeproj"))

        if workspaces:
            project_file = workspaces[0]
            is_workspace = True
        elif projects:
            project_file = projects[0]
            is_workspace = False
        else:
            return {"status": "error", "message": f"No Xcode project found in: {project_path}"}
    else:
        project_file = project_path
        is_workspace = project_file.suffix == ".xcworkspace"

    await ctx.info(f"Project: {project_file}")

    if not scheme:
        scheme = await _get_first_scheme(project_file, is_workspace)
        if scheme:
            await ctx.info(f"Using scheme: {scheme}")
        else:
            return {"status": "error", "message": "Could not detect scheme. Please provide scheme parameter."}

    # Resolve dependencies
    await ctx.info("Resolving package dependencies...")
    resolve_cmd = ["xcodebuild", "-resolvePackageDependencies"]
    resolve_cmd.extend(["-workspace" if is_workspace else "-project", str(project_file)])

    try:
        proc = await asyncio.create_subprocess_exec(
            *resolve_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT, cwd=project_file.parent
        )
        await proc.communicate()
    except Exception as e:
        await ctx.info(f"Package resolution warning: {e}")

    # Build
    build_cmd = ["xcodebuild"]
    if clean:
        build_cmd.append("clean")
    build_cmd.append("build")
    build_cmd.extend(["-workspace" if is_workspace else "-project", str(project_file)])
    build_cmd.extend(["-scheme", scheme, "-configuration", "Debug"])
    build_cmd.extend(["-destination", "generic/platform=iOS Simulator"])

    await ctx.info(f"Building{' (clean)' if clean else ''}...")

    try:
        proc = await asyncio.create_subprocess_exec(
            *build_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT, cwd=project_file.parent
        )
        stdout, _ = await proc.communicate()
        output = stdout.decode()
        success = proc.returncode == 0
        build_time = time.time() - start_time

        if success:
            return {
                "status": "success", "platform": "iOS", "project": str(project_file),
                "scheme": scheme, "build_time_seconds": round(build_time, 1),
                "message": f"Build succeeded in {build_time:.1f}s"
            }
        else:
            errors = parse_xcode_build_errors(output)
            return {
                "status": "build_failed", "platform": "iOS", "project": str(project_file),
                "scheme": scheme, "build_time_seconds": round(build_time, 1),
                "error_count": len(errors), "errors": errors[:10],
                "message": f"Build failed with {len(errors)} error(s)",
                "raw_output_tail": output[-3000:] if len(output) > 3000 else output,
            }
    except Exception as e:
        return {"status": "error", "message": f"Build failed: {e}"}


async def _get_first_scheme(project_file: Path, is_workspace: bool) -> Optional[str]:
    """Get the first available scheme."""
    flag = "-workspace" if is_workspace else "-project"
    cmd = ["xcodebuild", "-list", flag, str(project_file)]

    try:
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, _ = await proc.communicate()
        output = stdout.decode()

        in_schemes = False
        for line in output.split("\n"):
            line = line.strip()
            if line == "Schemes:":
                in_schemes = True
                continue
            if in_schemes and line and not line.endswith(":"):
                return line
            if in_schemes and line.endswith(":"):
                break
    except Exception:
        pass
    return None


async def _build_android(ctx: Context, project_path: Path, variant: Optional[str], clean: bool) -> Dict[str, Any]:
    """Build Android project using Gradle."""
    start_time = time.time()
    project_dir = project_path.parent if project_path.is_file() else project_path

    gradlew = project_dir / "gradlew"
    if not gradlew.exists():
        gradlew = project_dir.parent / "gradlew"
        if gradlew.exists():
            project_dir = project_dir.parent
        else:
            return {"status": "error", "message": f"gradlew not found in: {project_path}"}

    variant = variant or "debug"
    task = f"assemble{variant.capitalize()}"

    await ctx.info(f"Building Android ({variant})...")

    cmd = [str(gradlew)]
    if clean:
        cmd.append("clean")
    cmd.append(task)

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT, cwd=project_dir
        )
        stdout, _ = await proc.communicate()
        output = stdout.decode()
        success = proc.returncode == 0
        build_time = time.time() - start_time

        if success:
            return {
                "status": "success", "platform": "Android", "project": str(project_dir),
                "variant": variant, "build_time_seconds": round(build_time, 1),
                "message": f"Build succeeded in {build_time:.1f}s"
            }
        else:
            errors = _parse_gradle_errors(output)
            return {
                "status": "build_failed", "platform": "Android", "project": str(project_dir),
                "variant": variant, "build_time_seconds": round(build_time, 1),
                "error_count": len(errors), "errors": errors[:10],
                "message": f"Build failed with {len(errors)} error(s)",
                "raw_output_tail": output[-3000:] if len(output) > 3000 else output,
            }
    except Exception as e:
        return {"status": "error", "message": f"Build failed: {e}"}


def _parse_gradle_errors(output: str) -> List[Dict[str, Any]]:
    """Parse Gradle output for errors."""
    errors = []
    patterns = [
        r'e:\s*(?:file://)?(.+?):(\d+):(\d+)\s+(.+)',
        r'(.+?):(\d+):\s*error:\s*(.+)',
    ]

    for line in output.split('\n'):
        for pattern in patterns:
            match = re.match(pattern, line.strip())
            if match:
                groups = match.groups()
                if len(groups) == 4:
                    file_path, line_num, col, message = groups
                else:
                    file_path, line_num, message = groups
                    col = "0"
                errors.append({
                    "file": file_path, "line": int(line_num), "column": int(col),
                    "message": message, "analysis": analyze_build_error(message),
                })
                break

    if not errors and "FAILURE:" in output:
        in_failure = False
        failure_lines = []
        for line in output.split('\n'):
            if "FAILURE:" in line or "What went wrong:" in line:
                in_failure = True
                continue
            if in_failure:
                if line.strip().startswith(">"):
                    failure_lines.append(line.strip())
                elif line.strip() == "":
                    break
        if failure_lines:
            errors.append({"file": None, "line": None, "message": "\n".join(failure_lines)})

    return errors


# =============================================================================
# Migration Tools
# =============================================================================

_fetcher: Optional[MigrationFetcher] = None


def get_fetcher() -> MigrationFetcher:
    """Get or create the migration fetcher singleton."""
    global _fetcher
    if _fetcher is None:
        _fetcher = MigrationFetcher()
    return _fetcher


def _detect_sdk_version(project_path: str, platform: str) -> Optional[str]:
    """Detect current Airship SDK version from project files."""
    path = Path(project_path)
    if not path.is_dir():
        path = path.parent

    if platform == "iOS":
        podfile_lock = path / "Podfile.lock"
        if podfile_lock.exists():
            try:
                content = podfile_lock.read_text()
                match = re.search(r'-\s+Airship(?:/\w+)?\s+\((\d+\.\d+\.\d+)\)', content)
                if match:
                    return match.group(1)
            except Exception:
                pass

        for proj in list(path.glob("*.xcodeproj")) + list(path.glob("*.xcworkspace")):
            resolved = proj / "project.xcworkspace" / "xcshareddata" / "swiftpm" / "Package.resolved"
            if resolved.exists():
                try:
                    content = json.loads(resolved.read_text())
                    for pin in content.get("pins", []):
                        if pin.get("identity", "").lower() in ["ios-library", "airship-ios"]:
                            return pin.get("state", {}).get("version")
                except Exception:
                    pass

    elif platform == "Android":
        for gradle_file in ["build.gradle", "build.gradle.kts", "app/build.gradle", "app/build.gradle.kts"]:
            gradle_path = path / gradle_file
            if gradle_path.exists():
                try:
                    content = gradle_path.read_text()
                    match = re.search(r'com\.urbanairship\.android:urbanairship[^:]*:(\d+\.\d+\.\d+)', content)
                    if match:
                        return match.group(1)
                except Exception:
                    pass

    elif platform == "React Native":
        package_json = path / "package.json"
        if package_json.exists():
            try:
                content = json.loads(package_json.read_text())
                deps = {**content.get("dependencies", {}), **content.get("devDependencies", {})}
                for pkg in ["@ua/react-native-airship", "urbanairship-react-native"]:
                    if pkg in deps:
                        version = re.sub(r'^[\^~]', '', deps[pkg])
                        if re.match(r'\d+\.\d+\.\d+', version):
                            return version
            except Exception:
                pass

    elif platform == "Flutter":
        pubspec_lock = path / "pubspec.lock"
        if pubspec_lock.exists():
            try:
                content = pubspec_lock.read_text()
                match = re.search(r'airship_flutter:\s+[^v]*version:\s*["\']?(\d+\.\d+\.\d+)', content)
                if match:
                    return match.group(1)
            except Exception:
                pass

    return None


def _infer_platform_from_path(project_path: str) -> Optional[str]:
    """Infer the SDK platform from the project path."""
    path = Path(project_path)

    if path.suffix in [".xcodeproj", ".xcworkspace"]:
        return "iOS"

    if path.is_dir():
        if list(path.glob("*.xcodeproj")) or list(path.glob("*.xcworkspace")) or (path / "Podfile").exists():
            return "iOS"
        if (path / "build.gradle").exists() or (path / "build.gradle.kts").exists():
            return "Android"
        if (path / "package.json").exists():
            try:
                content = json.loads((path / "package.json").read_text())
                deps = {**content.get("dependencies", {}), **content.get("devDependencies", {})}
                if "react-native" in deps:
                    return "React Native"
            except Exception:
                pass
        if (path / "pubspec.yaml").exists():
            return "Flutter"
        if (path / "capacitor.config.ts").exists() or (path / "capacitor.config.json").exists():
            return "Capacitor"
        if (path / "config.xml").exists() and (path / "platforms").exists():
            return "Cordova"
        if list(path.glob("*.csproj")) or list(path.glob("*.sln")):
            return ".NET"

    return None


async def _run_migration_flow(ctx: Context) -> Dict[str, Any]:
    """Core migration flow with elicitation - shared by menu and tool."""
    from fastmcp.server.elicitation import AcceptedElicitation, DeclinedElicitation, CancelledElicitation

    await ctx.info("Starting Airship SDK migration assistant...")

    try:
        result = await ctx.elicit(
            "Enter the full path to your project (e.g., /Users/you/Projects/MyApp)",
            response_type=str
        )
        if isinstance(result, (DeclinedElicitation, CancelledElicitation)):
            return {"status": "cancelled", "message": "Migration cancelled by user"}
        project_path = result.data if isinstance(result, AcceptedElicitation) else "."
    except Exception:
        return {
            "status": "error",
            "message": "Elicitation not supported. Use migrate_sdk() with explicit parameters.",
            "hint": "migrate_sdk(project_path='...', platform='iOS', from_version='19.0.0', to_version='20.0.0')"
        }

    if not project_path or project_path.strip() == "":
        project_path = "."
    else:
        project_path = project_path.strip().strip('"\'').replace("\\ ", " ")

    await ctx.info(f"Project path: {project_path}")

    inferred_platform = _infer_platform_from_path(project_path)
    if inferred_platform:
        await ctx.info(f"Detected platform: {inferred_platform}")

    detected_version = None
    if inferred_platform:
        detected_version = _detect_sdk_version(project_path, inferred_platform)
        if detected_version:
            await ctx.info(f"Detected SDK version: {detected_version}")

    platform_msg = f"Which SDK platform? (detected: {inferred_platform})" if inferred_platform else "Which SDK platform?"
    platform_value, status = await elicit_with_fallback(ctx, platform_msg, SUPPORTED_PLATFORMS, inferred_platform, "platform")
    if status in ("declined", "cancelled"):
        return {"status": status, "message": "Migration cancelled"}

    if platform_value != inferred_platform:
        detected_version = _detect_sdk_version(project_path, platform_value)

    version_msg = f"Current SDK version? (detected: {detected_version})" if detected_version else "Current SDK version?"
    from_version, status = await elicit_with_fallback(ctx, version_msg, str, detected_version, "from_version")
    if status in ("declined", "cancelled"):
        return {"status": status, "message": "Migration cancelled"}

    fetcher = get_fetcher()
    await ctx.info(f"Fetching latest {platform_value} SDK version...")
    latest_version = await fetcher.fetch_latest_version(platform_value)

    to_msg = f"Target version? (latest: {latest_version})" if latest_version else "Target version?"
    to_version, status = await elicit_with_fallback(ctx, to_msg, str, latest_version, "to_version")
    if status in ("declined", "cancelled"):
        return {"status": status, "message": "Migration cancelled"}

    if to_version.lower() == "latest" and latest_version:
        to_version = latest_version

    return await _perform_migration(ctx, platform_value, from_version, to_version, project_path)


@mcp.tool
async def start_migration(ctx: Context) -> Dict[str, Any]:
    """
    Start an interactive SDK migration. USE THIS when user mentions "migrate", "migration", "upgrade SDK", or "update SDK version".

    Guides you through:
    1. Project path selection
    2. Platform auto-detection
    3. Version detection
    4. Applies code changes from migration guides
    5. Builds to verify

    Call this directly instead of start() when user intent is migration.
    """
    return await _run_migration_flow(ctx)


@mcp.tool
async def migrate_sdk(
    ctx: Context,
    project_path: str,
    platform: Optional[str] = None,
    from_version: Optional[str] = None,
    to_version: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Migrate Airship SDK with explicit parameters.

    Args:
        project_path: Path to project directory
        platform: SDK platform (auto-detected if not provided)
        from_version: Current version (auto-detected if not provided)
        to_version: Target version (uses latest if not provided)
    """
    await ctx.info("Starting Airship SDK migration...")

    project_path = (project_path or ".").strip().strip('"\'').replace("\\ ", " ")
    await ctx.info(f"Project path: {project_path}")

    if not platform:
        platform = _infer_platform_from_path(project_path)
        if platform:
            await ctx.info(f"Auto-detected platform: {platform}")
        else:
            return {"status": "error", "message": "Could not detect platform", "supported": SUPPORTED_PLATFORMS}

    if platform not in SUPPORTED_PLATFORMS:
        return {"status": "error", "message": f"Unsupported platform: {platform}", "supported": SUPPORTED_PLATFORMS}

    if not from_version:
        from_version = _detect_sdk_version(project_path, platform)
        if from_version:
            await ctx.info(f"Auto-detected version: {from_version}")
        else:
            return {"status": "error", "message": "Could not detect SDK version. Specify from_version."}

    fetcher = get_fetcher()
    if not to_version or to_version.lower() == "latest":
        await ctx.info(f"Fetching latest {platform} SDK version...")
        to_version = await fetcher.fetch_latest_version(platform)
        if not to_version:
            return {"status": "error", "message": "Could not determine latest version. Specify to_version."}
        await ctx.info(f"Target version: {to_version}")

    return await _perform_migration(ctx, platform, from_version, to_version, project_path)


async def _perform_migration(
    ctx: Context,
    platform: str,
    from_version: str,
    to_version: str,
    project_path: str,
) -> Dict[str, Any]:
    """
    Core migration logic - fetches guides and returns migration steps.

    Returns guidance for the agent to apply, rather than trying to
    automate everything (which can cause issues with SPM, permissions, etc).
    """
    # Normalize versions
    from_normalized = normalize_version(from_version)
    to_normalized = normalize_version(to_version)

    # Check if migration is needed
    from_major = get_major_version(from_normalized)
    to_major = get_major_version(to_normalized)

    if from_major > to_major:
        return {
            "status": "no_migration_needed",
            "platform": platform,
            "from_version": from_normalized,
            "to_version": to_normalized,
            "message": f"Current version {from_normalized} is already newer than target {to_normalized}.",
        }

    if from_major == to_major:
        return {
            "status": "no_migration_needed",
            "platform": platform,
            "from_version": from_normalized,
            "to_version": to_normalized,
            "message": (
                f"Both {from_normalized} and {to_normalized} are in the {from_major}.x series. "
                "No major API migration is required. Consult the CHANGELOG for any patch-level changes."
            ),
        }

    # Calculate migration path
    migration_path = get_migration_path(from_normalized, to_normalized)
    await ctx.info(f"Migration path: {len(migration_path)} step(s)")

    # Validate platform
    repo_id = PLATFORM_TO_REPO_ID.get(platform)
    if not repo_id:
        return {
            "status": "error",
            "message": f"Unsupported platform: {platform}",
            "supported_platforms": SUPPORTED_PLATFORMS
        }

    # Fetch and parse migration guides for each step
    fetcher = get_fetcher()
    all_steps: List[Dict[str, Any]] = []
    all_replacements: List[Dict[str, Any]] = []
    raw_guides: Dict[str, str] = {}
    warnings: List[str] = []
    fetch_errors: List[str] = []

    for step_from, step_to in migration_path:
        await ctx.info(f"Fetching migration guide: {step_from}.x -> {step_to}.x")

        try:
            content = await fetcher.fetch_migration_guide(
                platform=platform,
                from_version=f"{step_from}.0.0",
                to_version=f"{step_to}.0.0"
            )

            if not content:
                fetch_errors.append(f"Migration guide not found for {step_from}.x -> {step_to}.x")
                continue

            # Extract the relevant section
            section = extract_version_section(content, step_from, step_to)
            if not section:
                section = content

            # Parse into steps
            parsed_steps = parse_migration_steps(section)

            # Add rollback hints and version context
            for step in parsed_steps:
                step["rollback"] = generate_rollback_hint(step)
                step["version_transition"] = f"{step_from}.x -> {step_to}.x"
                all_steps.append(step)

            # Extract find/replace patterns from the guide
            replacements = extract_replacements(section, step_from, step_to)
            all_replacements.extend(replacements)
            await ctx.info(f"Extracted {len(replacements)} replacement patterns for {step_from}.x -> {step_to}.x")

            raw_guides[f"{step_from}.x -> {step_to}.x"] = section

        except Exception as e:
            fetch_errors.append(f"Error for {step_from}.x -> {step_to}.x: {str(e)}")

    # Add warning for multi-version migrations
    if len(migration_path) > 1:
        warnings.insert(0,
            f"Multi-version migration ({from_major}.x -> {to_major}.x) - "
            "Complete each step sequentially before proceeding to the next."
        )

    # Categorize replacements into simple/complex/removals
    categorized = categorize_replacements(all_replacements)

    # Build response
    response: Dict[str, Any] = {
        "status": "success" if all_steps else "partial",
        "platform": platform,
        "from_version": from_normalized,
        "to_version": to_normalized,
        "migration_path": [{"from": f"{f}.x", "to": f"{t}.x"} for f, t in migration_path],
        "total_steps": len(all_steps),
        "steps": all_steps,
    }

    # Add find/replace patterns for systematic migration
    if all_replacements:
        response["replacements"] = {
            "total": len(all_replacements),
            "simple": categorized["simple"],
            "complex": categorized["complex"],
            "removals": categorized["removals"],
        }
        response["simple_replacement_count"] = len(categorized["simple"])
        response["complex_replacement_count"] = len(categorized["complex"])

    if warnings:
        response["warnings"] = warnings

    if fetch_errors:
        response["fetch_errors"] = fetch_errors
        if not all_steps:
            response["status"] = "error"
            response["message"] = "Could not fetch migration guides."

    response["project_path"] = project_path

    # Platform-specific version update instructions
    version_update_instructions = {
        "iOS": f"Update Package.swift or Podfile to version {to_normalized}, then run 'swift package update' or 'pod install'",
        "Android": f"Update build.gradle to version {to_normalized}, then sync Gradle",
        "React Native": f"Run 'npm install @ua/react-native-airship@{to_normalized}' or update package.json",
        "Flutter": f"Update pubspec.yaml to airship_flutter: ^{to_normalized}, then run 'flutter pub get'",
        "Capacitor": f"Run 'npm install @ua/capacitor-airship@{to_normalized}' or update package.json",
        "Cordova": f"Run 'cordova plugin rm urbanairship-cordova && cordova plugin add urbanairship-cordova@{to_normalized}'",
        ".NET": f"Update PackageReference to Airship.Net version {to_normalized}",
    }.get(platform, f"Update your dependency file to SDK version {to_normalized}")

    response["version_update"] = {
        "target_version": to_normalized,
        "instruction": version_update_instructions,
        "note": "THIS MUST BE DONE FIRST before any API changes"
    }

    response["workflow"] = f"""
## REQUIRED Migration Workflow

### Phase 1: UPDATE SDK VERSION FIRST
{version_update_instructions}

### Phase 2: Apply Pattern Replacements
For EACH pattern in 'replacements.simple' ({len(categorized['simple'])} patterns):
1. Search the codebase for the pattern
2. Replace ALL occurrences

### Phase 3: Complex Changes
For EACH item in 'replacements.complex' ({len(categorized['complex'])} patterns):
1. Review the context and apply the appropriate fix

### Phase 4: Build Verification
Run verify_build(project_path='{project_path}')
"""

    response["next_steps"] = [
        f"1. UPDATE SDK VERSION FIRST: {version_update_instructions}",
        f"2. Search and replace ALL {len(categorized['simple'])} simple patterns",
        f"3. Address ALL {len(categorized['complex'])} complex changes",
        f"4. Run verify_build(project_path='{project_path}')",
    ]

    if all_steps:
        response["message"] = (
            f"Migration checklist: {len(all_steps)} steps for {platform} "
            f"{from_normalized} → {to_normalized}. "
            f"Found {len(categorized['simple'])} simple and {len(categorized['complex'])} complex patterns."
        )

    return response


# =============================================================================
# Internal-only Tools (registered only when internal skills dir is present)
# =============================================================================

if _INTERNAL_SKILLS_DIR.exists():
    _SLIDES_SCRIPT = _INTERNAL_SKILLS_DIR / "slides" / "scripts" / "generate.py"

    @mcp.tool
    async def generate_slides(ctx: Context, slides_json: str, output_path: str) -> Dict[str, Any]:
        """
        Generate a branded Airship presentation (.pptx) from a JSON slide spec.

        IMPORTANT: Before building the slides_json, invoke the MCP prompt named "slides" to load
        the full layout reference, brand rules, and JSON schema. Do not guess at layouts or field
        names — read the skill first, then build the spec.

        Args:
            slides_json: JSON string with a "slides" array. Each slide requires a "layout" field
                         plus layout-specific fields. Full schema is in the "slides" MCP prompt.
            output_path: Absolute path where the .pptx file should be saved (e.g. ~/Desktop/deck.pptx).
        """
        if not _SLIDES_SCRIPT.exists():
            return {
                "status": "error",
                "message": "Slides script not found. This tool requires the internal slides skill to be installed.",
            }

        # Validate JSON
        try:
            slides_data = json.loads(slides_json)
        except json.JSONDecodeError as e:
            return {"status": "error", "message": f"Invalid JSON: {e}"}

        output = Path(output_path).expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            json.dump(slides_data, tmp, indent=2)
            tmp_path = tmp.name

        try:
            proc = await asyncio.create_subprocess_exec(
                sys.executable, str(_SLIDES_SCRIPT), tmp_path, str(output), "--auto-fit-headings",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(_SLIDES_SCRIPT.parent),
            )
            stdout_bytes, stderr_bytes = await proc.communicate()
        finally:
            Path(tmp_path).unlink(missing_ok=True)

        if proc.returncode == 0:
            return {
                "status": "success",
                "output_path": str(output),
                "logs": stdout_bytes.decode(),
            }
        else:
            return {
                "status": "error",
                "logs": stdout_bytes.decode(),
                "stderr": stderr_bytes.decode(),
                "message": "Generation failed. Review logs and fix the slide spec, then try again.",
            }


# =============================================================================
# Entry Point
# =============================================================================

def main():
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()

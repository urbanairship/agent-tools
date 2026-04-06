"""
Tools for Airship API operations.
All tools that perform API operations (non-informational).

IMPORTANT: The httpx.AsyncClient is created lazily and persists for the server lifetime.
When the MCP server shuts down, call cleanup() to properly close the client.
"""

# =============================================================================
# OpenAPI Coverage Documentation
# =============================================================================
# This module implements a selective subset of the Airship API, following the
# "selective, not 1:1" approach from project requirements (API-01).
#
# COVERED OPERATIONS (from OpenAPI /api/push, /api/segments, /api/channels):
#   POST   /api/push                          -> send_custom_push, send_message_center_message
#   POST   /api/push/validate                 -> validate_push_payload
#   GET    /api/channels/{channel_id}         -> lookup_channel
#   GET    /api/channels/{channel_id}/tags    -> get_channel_tags
#   GET    /api/channels/{channel_id}/attributes -> get_channel_attributes
#   GET    /api/segments                      -> list_segments
#   GET    /api/segments/{segment_id}         -> get_segment_info
#   POST   /api/segments                      -> create_segment
#   DELETE /api/segments/{segment_id}         -> delete_segment
#   GET    /api/named_users/{named_user_id}   -> lookup_named_user
#
# NOT YET IMPLEMENTED (candidates for future phases):
#   POST   /api/schedules                     -> scheduled push
#   GET    /api/schedules                     -> list scheduled pushes
#   DELETE /api/schedules/{id}                -> cancel scheduled push
#   POST   /api/channels/tags                 -> bulk tag management
#   POST   /api/named_users/associate         -> associate channel to named user
#   POST   /api/named_users/disassociate      -> disassociate channel
#   POST   /api/named_users/uninstall         -> channel uninstall
#
# Design rationale: Focus on high-value operations that LLMs need most frequently
# for push notification workflows. Bulk operations and advanced features can be
# added incrementally based on usage patterns.
# =============================================================================

import os
import httpx
from typing import Dict, Any, Optional
from pydantic import ValidationError
from .auth import AirshipAuth, validate_credentials
from .validators import PushToTagPayload, PushToChannelPayload, MessageCenterPayload, transform_validation_error
from .errors import transform_api_error


# Global auth and clients (initialized lazily).
#
# Two clients are maintained to ensure the correct auth method is used
# regardless of which credentials are configured:
#
#   client       — preferred auth (Bearer if available, Basic otherwise).
#                  Use this for all endpoints that accept both.
#
#   basic_client — always Basic Auth. Use this ONLY for endpoints that
#                  explicitly require it (e.g. message deletion, Connect
#                  compliance events). Will be None if Basic Auth credentials
#                  are not configured; callers must handle that case.
auth: Optional[AirshipAuth] = None
client: Optional[httpx.AsyncClient] = None
basic_client: Optional[httpx.AsyncClient] = None


def init_auth():
    """Initialize authentication when first needed."""
    global auth, client, basic_client
    if auth is None:
        if not validate_credentials():
            raise ValueError(
                "Airship credentials not configured. "
                "Use the 'get_setup_instructions' tool for setup help. "
                "Set AIRSHIP_BEARER_TOKEN (preferred) or both AIRSHIP_APP_KEY and "
                "AIRSHIP_MASTER_SECRET in your MCP configuration."
            )
        auth = AirshipAuth()
        client = auth.create_client(api="go")

        # Provision the basic_client if Basic Auth credentials are available.
        # This is required for endpoints that do not accept Bearer tokens.
        if auth.app_key and auth.master_secret:
            basic_client = auth.create_client(api="go", force_basic=True)

        if not auth.using_bearer:
            import warnings
            warnings.warn(
                "Authenticating with Basic Auth (app key + master secret). "
                "Set AIRSHIP_BEARER_TOKEN for the preferred auth method.",
                stacklevel=2,
            )


async def cleanup():
    """
    Clean up resources (close HTTP clients).
    Should be called when MCP server shuts down.
    """
    global client, basic_client
    if client is not None:
        await client.aclose()
        client = None
    if basic_client is not None:
        await basic_client.aclose()
        basic_client = None


# Helper functions for API calls
async def _create_segment(name: str, criteria: Dict[str, Any]) -> Dict[str, Any]:
    """Create audience segment via Airship API."""

    payload = {
        "display_name": name,
        "criteria": criteria
    }

    response = await client.post("/api/segments", json=payload)
    response.raise_for_status()
    return response.json()


async def _get_segment(segment_id: str) -> Optional[Dict[str, Any]]:
    """Get segment details via Airship API. Returns None only on 404; re-raises all other errors."""
    try:
        response = await client.get(f"/api/segments/{segment_id}")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return None
        raise


async def _delete_segment(segment_id: str) -> None:
    """Delete segment via Airship API."""

    response = await client.delete(f"/api/segments/{segment_id}")
    response.raise_for_status()


# Tool functions
async def create_segment(
    name: str,
    criteria: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create an audience segment.

    Args:
        name: Segment name
        criteria: Segment criteria definition
    """

    # Initialize auth if needed
    try:
        init_auth()
    except ValueError as e:
        return {"status": "error", "message": str(e)}

    # Create segment
    result = await _create_segment(name, criteria)

    return {
        "status": "created",
        "segment_id": result.get("segment_id"),
        "name": name
    }


async def delete_segment(
    segment_id: str
) -> Dict[str, Any]:
    """
    Delete an audience segment.

    Args:
        segment_id: ID of segment to delete
    """

    # Initialize auth if needed
    try:
        init_auth()
    except ValueError as e:
        return {"status": "error", "message": str(e)}

    # Get segment details first
    segment = await _get_segment(segment_id)

    if not segment:
        return {"status": "error", "reason": "Segment not found"}

    # Delete the segment
    await _delete_segment(segment_id)

    return {
        "status": "deleted",
        "segment_id": segment_id,
        "name": segment.get("name")
    }


async def lookup_channel(channel_id: str) -> Dict[str, Any]:
    """
    Look up channel information by channel ID.

    Retrieves comprehensive channel data including:
    - Platform (iOS, Android, Web, etc.)
    - Opt-in status for push notifications
    - Channel tags
    - Custom attributes
    - Creation and last registration timestamps

    Args:
        channel_id: The Airship channel ID to look up

    Returns:
        Dictionary with channel information or error status
    """
    # Initialize auth if needed
    try:
        init_auth()
    except ValueError as e:
        return {"status": "error", "message": str(e)}

    try:
        response = await client.get(f"/api/channels/{channel_id}")
        response.raise_for_status()
        channel_data = response.json()

        return {
            "status": "found",
            "channel_id": channel_id,
            "channel": channel_data.get("channel", {}),
            "platform": channel_data.get("channel", {}).get("channel_type"),
            "opt_in": channel_data.get("channel", {}).get("opt_in"),
            "tags": channel_data.get("channel", {}).get("tags", []),
            "created": channel_data.get("channel", {}).get("created"),
            "last_registration": channel_data.get("channel", {}).get("last_registration")
        }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {
                "status": "not_found",
                "channel_id": channel_id,
                "message": f"Channel {channel_id} not found. The channel may not be registered or the ID may be incorrect."
            }
        error_response = transform_api_error(e)
        error_response["channel_id"] = channel_id
        return error_response
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


async def get_channel_tags(channel_id: str) -> Dict[str, Any]:
    """
    Get tags for a specific channel.

    Args:
        channel_id: The Airship channel ID

    Returns:
        Dictionary with list of tags or error status
    """
    # Initialize auth if needed
    try:
        init_auth()
    except ValueError as e:
        return {"status": "error", "message": str(e)}

    try:
        response = await client.get(f"/api/channels/{channel_id}/tags")
        response.raise_for_status()
        data = response.json()

        return {
            "status": "success",
            "channel_id": channel_id,
            "tags": data.get("tags", [])
        }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {
                "status": "not_found",
                "channel_id": channel_id,
                "message": "Channel not found"
            }
        error_response = transform_api_error(e)
        error_response["channel_id"] = channel_id
        return error_response
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


async def get_channel_attributes(channel_id: str) -> Dict[str, Any]:
    """
    Get custom attributes for a specific channel.

    Args:
        channel_id: The Airship channel ID

    Returns:
        Dictionary with attributes or error status
    """
    # Initialize auth if needed
    try:
        init_auth()
    except ValueError as e:
        return {"status": "error", "message": str(e)}

    try:
        response = await client.get(f"/api/channels/{channel_id}/attributes")
        response.raise_for_status()
        data = response.json()

        return {
            "status": "success",
            "channel_id": channel_id,
            "attributes": data.get("attributes", {})
        }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {
                "status": "not_found",
                "channel_id": channel_id,
                "message": "Channel not found"
            }
        error_response = transform_api_error(e)
        error_response["channel_id"] = channel_id
        return error_response
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


async def list_segments() -> Dict[str, Any]:
    """
    List all audience segments.

    Returns:
        Dictionary with array of segments or error status
    """
    # Initialize auth if needed
    try:
        init_auth()
    except ValueError as e:
        return {"status": "error", "message": str(e)}

    try:
        response = await client.get("/api/segments")
        response.raise_for_status()
        data = response.json()

        segments = data.get("segments", [])

        return {
            "status": "success",
            "count": len(segments),
            "segments": [
                {
                    "id": seg.get("id"),
                    "display_name": seg.get("display_name"),
                    "creation_date": seg.get("creation_date"),
                    "modification_date": seg.get("modification_date")
                }
                for seg in segments
            ]
        }
    except httpx.HTTPStatusError as e:
        return transform_api_error(e)
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


async def get_segment_info(segment_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific segment.

    Args:
        segment_id: The segment ID to look up

    Returns:
        Dictionary with segment details including criteria or error status
    """
    # Initialize auth if needed
    try:
        init_auth()
    except ValueError as e:
        return {"status": "error", "message": str(e)}

    try:
        segment = await _get_segment(segment_id)

        if not segment:
            return {
                "status": "not_found",
                "segment_id": segment_id,
                "message": "Segment not found"
            }

        return {
            "status": "found",
            "segment_id": segment_id,
            "display_name": segment.get("display_name"),
            "criteria": segment.get("criteria", {}),
            "creation_date": segment.get("creation_date"),
            "modification_date": segment.get("modification_date")
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


async def lookup_named_user(named_user_id: str) -> Dict[str, Any]:
    """
    Look up a named user and their associated channels.

    Args:
        named_user_id: The named user ID to look up

    Returns:
        Dictionary with named user information and channels or error status
    """
    # Initialize auth if needed
    try:
        init_auth()
    except ValueError as e:
        return {"status": "error", "message": str(e)}

    try:
        response = await client.get("/api/named_users", params={"id": named_user_id})
        response.raise_for_status()
        data = response.json()

        named_user = data.get("named_user", {})

        return {
            "status": "found",
            "named_user_id": named_user_id,
            "channels": named_user.get("channels", []),
            "tags": named_user.get("tags", []),
            "attributes": named_user.get("attributes", {})
        }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {
                "status": "not_found",
                "named_user_id": named_user_id,
                "message": f"Named user {named_user_id} not found"
            }
        error_response = transform_api_error(e)
        error_response["named_user_id"] = named_user_id
        return error_response
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


async def send_custom_push(
    payload: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Send a push notification with a custom payload.

    This is the universal tool for sending ANY push notification supported by the Airship API.
    For payload examples and documentation, refer to the push-examples resource.

    Supports:
    - All audience types: tags, channel IDs, named users, segments, complex AND/OR logic
    - Platform-specific notifications (iOS, Android)
    - Actions: landing pages, deep links, URLs
    - Message Center messages with HTML
    - Media attachments, interactive buttons, localization
    - Test mode, scheduled sends, transactional messages

    Common Audience Formats:
    - Tag: {"audience": {"tag": "users"}}
    - iOS Channel: {"audience": {"ios_channel": "channel-id"}}
    - Android Channel: {"audience": {"android_channel": "channel-id"}}
    - Named User: {"audience": {"named_user": "user_123"}}
    - Multiple: {"audience": {"or": [{"ios_channel": "id1"}, {"android_channel": "id2"}]}}

    Args:
        payload: Complete push payload dictionary (sent to /api/push endpoint)

    Returns:
        Dictionary with status, app_key, push_ids, admin_urls, and full API response

    Note: For complete payload examples, consult the push-examples resource which includes
    examples for all audience types, actions, and special features.
    """

    # Initialize auth if needed
    try:
        init_auth()
    except ValueError as e:
        return {
            "status": "error",
            "error": "credentials_not_configured",
            "message": "AIRSHIP_APP_KEY and AIRSHIP_MASTER_SECRET must be set in MCP server environment configuration"
        }

    audience = payload.get("audience")
    if audience == "all" or audience == {"all": True}:
        return {
            "status": "error",
            "error": "broadcast_blocked",
            "message": "send_custom_push does not allow broadcast audience. Use send_push_to_tag or send_push_to_channel for targeted sends."
        }

    try:
        response = await client.post("/api/push", json=payload)
        response.raise_for_status()
        result = response.json()

        # Extract push IDs and create URLs
        push_ids = result.get("push_ids", [])
        admin_urls = []
        if push_ids and auth.app_key:
            for push_id in push_ids:
                admin_urls.append(f"https://go-admin.urbanairship.com/admin/flight_deck/apps/{auth.app_key}/messages/{push_id}")

        return {
            "status": "sent",
            "app_key": auth.app_key or "(bearer token — app key not configured)",
            "base_url": str(client.base_url),
            "payload": payload,
            "push_ids": push_ids,
            "admin_urls": admin_urls,
            "result": result
        }
    except httpx.HTTPStatusError as e:
        # Use centralized error transformation
        error_response = transform_api_error(e, payload)
        error_response["app_key"] = auth.app_key or "(bearer token — app key not configured)"

        # Add extra debug info for 401 errors
        if e.response.status_code == 401:
            error_response["base_url"] = str(client.base_url)
            error_response["auth_method"] = "bearer" if auth.using_bearer else "basic"

        return error_response
    except Exception as e:
        return {
            "status": "error",
            "error": "unexpected_error",
            "app_key": (auth.app_key if auth else None) or "unknown",
            "message": str(e),
            "payload": payload
        }


async def send_push_to_tag(
    tag: str,
    alert: str,
    title: str = None,
    platforms: list = None
) -> Dict[str, Any]:
    """
    Send a push notification to all devices with a specific tag.

    This is a convenience wrapper around send_custom_push for the most common
    use case: sending a simple notification to a tag group.

    Args:
        tag: The tag to send to (e.g., "news_subscribers", "premium_users")
        alert: The notification message body
        title: Optional notification title (recommended for Android/Web)
        platforms: List of platforms to target. Defaults to ["ios", "android"].
                   Options: "ios", "android", "web", "sms", "email", "open"

    Returns:
        Dictionary with status, push_ids, and admin_urls

    Example:
        send_push_to_tag("breaking_news", "New article published!", title="Breaking News")
    """
    # Validate inputs before building payload
    try:
        validated = PushToTagPayload(
            tag=tag,
            alert=alert,
            title=title,
            platforms=platforms or ["ios", "android"]
        )
    except ValidationError as e:
        return transform_validation_error(e)

    # Use validated fields
    tag = validated.tag
    alert = validated.alert
    title = validated.title
    platforms = validated.platforms

    # Build platform-specific notification
    notification = {}

    # iOS can use object alert
    if "ios" in platforms:
        ios_alert = {"body": alert}
        if title:
            ios_alert["title"] = title
        notification["ios"] = {"alert": ios_alert}

    # Android MUST use string alert with separate title (per research pitfall #1)
    if "android" in platforms:
        notification["android"] = {"alert": alert}
        if title:
            notification["android"]["title"] = title

    # Web MUST use string alert with separate title
    if "web" in platforms:
        notification["web"] = {"alert": alert}
        if title:
            notification["web"]["title"] = title

    # Fallback alert for any other platforms
    notification["alert"] = alert

    payload = {
        "audience": {"tag": tag},
        "device_types": platforms,
        "notification": notification
    }

    return await send_custom_push(payload)


async def send_push_to_channel(
    channel_id: str,
    platform: str,
    alert: str,
    title: str = None
) -> Dict[str, Any]:
    """
    Send a push notification to a specific channel ID.

    This is a convenience wrapper for sending to a single device/channel.

    Args:
        channel_id: The Airship channel ID
        platform: Platform type: "ios", "android", "web", "sms", "email", "open"
        alert: The notification message body
        title: Optional notification title (recommended for Android/Web)

    Returns:
        Dictionary with status, push_ids, and admin_urls

    Example:
        send_push_to_channel("abc123...", "ios", "Your order shipped!", title="Order Update")
    """
    # Validate inputs before building payload
    try:
        validated = PushToChannelPayload(
            channel_id=channel_id,
            platform=platform,
            alert=alert,
            title=title
        )
    except ValidationError as e:
        return transform_validation_error(e)

    # Use validated fields
    channel_id = validated.channel_id
    platform = validated.platform
    alert = validated.alert
    title = validated.title

    # Build audience selector based on platform
    audience_key = f"{platform}_channel"
    if platform == "web":
        audience_key = "web_channel"

    # Build platform-specific notification
    notification = {"alert": alert}

    if platform == "ios":
        ios_alert = {"body": alert}
        if title:
            ios_alert["title"] = title
        notification["ios"] = {"alert": ios_alert}
    elif platform in ["android", "web"]:
        # Android/Web MUST use string alert with separate title
        notification[platform] = {"alert": alert}
        if title:
            notification[platform]["title"] = title

    payload = {
        "audience": {audience_key: channel_id},
        "device_types": [platform],
        "notification": notification
    }

    return await send_custom_push(payload)


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

    Message center messages appear in the app's inbox/message center and can contain
    rich HTML content. Optionally send a push notification to alert users.

    Args:
        title: Message title (shown in inbox list)
        body_html: HTML content for message body (see html-reference resource for supported tags)
        tag: Target tag (provide one of: tag, channel_id, named_user)
        channel_id: Target channel ID
        named_user: Target named user
        send_alert: Whether to also send a push notification
        alert_text: Push notification text (required if send_alert=True)
        expiry: Message expiry (e.g., "+7d" for 7 days, ISO timestamp)

    Returns:
        Dictionary with status, push_ids, and admin_urls

    Example:
        send_message_center_message(
            title="Welcome!",
            body_html="<h1>Hello</h1><p>Thanks for joining.</p>",
            tag="new_users",
            send_alert=True,
            alert_text="You have a new message"
        )
    """
    # Validate inputs
    try:
        validated = MessageCenterPayload(
            title=title, body_html=body_html,
            tag=tag, channel_id=channel_id, named_user=named_user,
            send_alert=send_alert, alert_text=alert_text, expiry=expiry
        )
    except ValidationError as e:
        return transform_validation_error(e)

    # Build audience — use the generic "channel" selector so any platform's
    # channel_id is routed correctly without needing to know the device type.
    if validated.tag:
        audience = {"tag": validated.tag}
    elif validated.channel_id:
        audience = {"channel": validated.channel_id}
    else:
        audience = {"named_user": validated.named_user}

    # Build payload
    payload = {
        "audience": audience,
        "device_types": ["ios", "android"],
        "message": {
            "title": validated.title,
            "body": validated.body_html,
            "content_type": "text/html"
        }
    }

    if validated.expiry:
        payload["message"]["expiry"] = validated.expiry

    if validated.send_alert:
        payload["notification"] = {"alert": validated.alert_text}

    return await send_custom_push(payload)


async def validate_push_payload(
    payload: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Validate a push payload without sending.

    Uses Airship's /api/push/validate endpoint to check payload validity.
    This is TEST MODE - no pushes will be sent.

    Args:
        payload: Complete push payload to validate

    Returns:
        Dictionary with validation result and clear test_mode indicator

    Example:
        validate_push_payload({
            "audience": {"tag": "test"},
            "device_types": ["ios"],
            "notification": {"alert": "Test"}
        })
    """
    # Initialize auth if needed
    try:
        init_auth()
    except ValueError as e:
        return {
            "status": "error",
            "test_mode": True,
            "error": "credentials_not_configured",
            "message": str(e)
        }

    try:
        response = await client.post("/api/push/validate", json=payload)
        response.raise_for_status()

        return {
            "status": "valid",
            "test_mode": True,
            "message": "Payload is VALID. This was VALIDATION ONLY - no pushes were sent.",
            "payload": payload,
            "ok": True
        }
    except httpx.HTTPStatusError as e:
        error_response = transform_api_error(e, payload)
        error_response["test_mode"] = True
        error_response["message"] = f"VALIDATION FAILED (no push sent): {error_response.get('message', 'See api_error for details')}"
        return error_response
    except Exception as e:
        return {
            "status": "error",
            "test_mode": True,
            "error": "unexpected_error",
            "message": f"Validation request failed: {str(e)}",
            "payload": payload
        }
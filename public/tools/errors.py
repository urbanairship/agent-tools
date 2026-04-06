"""
HTTP error transformation for Airship API responses.
Transforms API errors into actionable messages with suggested fixes.
"""

import httpx
from typing import Optional


def extract_error_message(api_error: dict) -> str:
    """
    Extract human-readable message from Airship API error.

    Airship API errors have structure:
    {
        "error": "error description",
        "error_code": 40001,
        "details": {"path": "notification.android.alert", "error": "..."}
    }

    Args:
        api_error: Parsed JSON from Airship API error response

    Returns:
        Human-readable error message
    """
    error = api_error.get("error", "Unknown error")
    details = api_error.get("details", {})

    if "path" in details:
        field_path = details["path"]
        field_error = details.get("error", "")
        return f"Error in {field_path}: {field_error}" if field_error else f"Error in {field_path}: {error}"

    return error


def suggest_fix(api_error: dict) -> str:
    """
    Generate actionable fix suggestion for API errors.

    Args:
        api_error: Parsed JSON from Airship API error response

    Returns:
        Suggestion string for fixing the error
    """
    details = api_error.get("details", {})
    path = details.get("path", "")
    error_text = str(api_error.get("error", "")).lower()
    detail_error = str(details.get("error", "")).lower()

    # Platform-specific alert format (Research Pitfall 1)
    if "android.alert" in path or "web.alert" in path:
        platform = "Android" if "android" in path else "Web"
        return f'{platform} alert must be a STRING with separate "title" field. Use {{"alert": "body", "title": "title"}}, not {{"alert": {{"title": "...", "body": "..."}}}}'

    # Missing required field
    if "missing" in error_text or "missing" in detail_error:
        return f"Required field missing: {path}. Check the push-api-spec resource for required fields."

    # Invalid field value
    if "invalid" in error_text or "invalid" in detail_error:
        return f"Invalid value for {path}. Consult the push-examples resource for valid examples."

    # Default suggestion
    return "Check your payload against the push-api-spec resource and ensure all required fields are present."


def transform_api_error(exc: httpx.HTTPStatusError, payload: dict = None) -> dict:
    """
    Transform HTTP status errors into actionable error responses.

    Args:
        exc: httpx.HTTPStatusError exception
        payload: Optional payload that was sent (for context in error response)

    Returns:
        Dictionary with structured error information and suggestions
    """
    base = {
        "status": "error",
        "http_status": exc.response.status_code,
    }

    if payload is not None:
        base["payload"] = payload

    if exc.response.status_code == 400:
        try:
            api_error = exc.response.json()
            base["error"] = "invalid_payload"
            base["api_error"] = api_error
            base["message"] = extract_error_message(api_error)
            base["suggestion"] = suggest_fix(api_error)
        except Exception:
            base["error"] = "invalid_payload"
            base["message"] = f"Airship rejected the payload: {exc.response.text}"
            base["suggestion"] = "Check your payload against the push-api-spec resource."

    elif exc.response.status_code == 401:
        base["error"] = "authentication_failed"
        base["message"] = "API credentials are invalid or expired"
        base["suggestion"] = "Check AIRSHIP_APP_KEY and AIRSHIP_MASTER_SECRET in your MCP configuration"

    elif exc.response.status_code == 404:
        # Try to extract resource info from URL
        url_path = str(exc.request.url.path) if exc.request else ""
        resource_info = _extract_resource_from_url(url_path)
        base["error"] = "not_found"
        base["message"] = f"Resource not found: {resource_info}" if resource_info else "Requested resource not found"
        base["suggestion"] = "Verify the resource ID is correct and exists in your Airship project"

    elif exc.response.status_code == 429:
        base["error"] = "rate_limited"
        base["message"] = "API rate limit exceeded"
        try:
            retry_after = exc.response.headers.get("Retry-After")
            if retry_after:
                base["retry_after_seconds"] = int(retry_after)
                base["suggestion"] = f"Wait {retry_after} seconds before retrying"
            else:
                base["suggestion"] = "Wait a moment and retry the request"
        except (ValueError, TypeError):
            base["suggestion"] = "Wait a moment and retry the request"

    else:
        base["error"] = "api_error"
        base["message"] = f"Airship API error: {exc.response.status_code}"
        try:
            base["response_text"] = exc.response.text
        except Exception:
            pass
        base["suggestion"] = "See response_text for details or contact Airship support"

    return base


def _extract_resource_from_url(url_path: str) -> Optional[str]:
    """
    Extract resource identifier from URL path.

    Args:
        url_path: URL path string

    Returns:
        Resource identifier or None
    """
    if not url_path:
        return None

    # Common Airship API path patterns
    parts = url_path.rstrip('/').split('/')
    if len(parts) >= 2:
        resource_type = parts[-2]
        resource_id = parts[-1]

        # Map API paths to friendly names
        type_map = {
            "channels": "channel",
            "segments": "segment",
            "named_users": "named_user",
            "push": "push"
        }

        friendly_type = type_map.get(resource_type, resource_type)
        return f"{friendly_type} '{resource_id}'"

    return None

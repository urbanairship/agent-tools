"""
Pydantic validators for Airship API payloads.
Provides client-side validation to catch errors before API calls.
"""

from pydantic import BaseModel, field_validator, model_validator, ValidationError
from typing import Literal


# Valid platform types for push notifications
VALID_PLATFORMS = {"ios", "android", "web", "sms", "email", "open"}


class PushToTagPayload(BaseModel):
    """
    Validates payload for tag-based push notifications.
    Used by send_push_to_tag convenience tool.
    """
    tag: str
    alert: str
    title: str | None = None
    platforms: list[str] = ["ios", "android"]

    @field_validator('tag')
    @classmethod
    def tag_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Tag cannot be empty")
        return v.strip()

    @field_validator('alert')
    @classmethod
    def alert_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Alert message cannot be empty")
        return v.strip()

    @field_validator('platforms')
    @classmethod
    def validate_platforms(cls, v):
        if not v:
            raise ValueError("Must specify at least one platform")
        invalid = set(v) - VALID_PLATFORMS
        if invalid:
            raise ValueError(f"Invalid platforms: {', '.join(sorted(invalid))}. Valid: {', '.join(sorted(VALID_PLATFORMS))}")
        return v


class PushToChannelPayload(BaseModel):
    """
    Validates payload for channel-based push notifications.
    Used by send_push_to_channel convenience tool.
    """
    channel_id: str
    platform: Literal["ios", "android", "web", "sms", "email", "open"]
    alert: str
    title: str | None = None

    @field_validator('channel_id')
    @classmethod
    def channel_id_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Channel ID cannot be empty")
        return v.strip()

    @field_validator('alert')
    @classmethod
    def alert_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Alert message cannot be empty")
        return v.strip()


class MessageCenterPayload(BaseModel):
    """
    Validates message center message structure.
    Used by send_message_center_message tool.
    """
    title: str  # Required - shows in inbox list
    body_html: str  # Required - HTML content
    tag: str | None = None  # Target tag (one of tag/channel_id/named_user required)
    channel_id: str | None = None
    named_user: str | None = None
    send_alert: bool = False  # Whether to also send push notification
    alert_text: str | None = None  # Required if send_alert=True
    expiry: str | None = None  # Optional: "+7d", timestamp, etc.

    @field_validator('title', 'body_html')
    @classmethod
    def not_empty(cls, v, info):
        if not v or not v.strip():
            raise ValueError(f"{info.field_name} cannot be empty")
        return v

    @model_validator(mode='after')
    def check_audience_and_alert(self):
        # Must have at least one audience selector
        if not any([self.tag, self.channel_id, self.named_user]):
            raise ValueError("Must specify at least one of: tag, channel_id, named_user")
        # If send_alert, must have alert_text
        if self.send_alert and not self.alert_text:
            raise ValueError("alert_text is required when send_alert=True")
        return self


def transform_validation_error(e: ValidationError) -> dict:
    """
    Convert Pydantic ValidationError to user-friendly format.

    Args:
        e: Pydantic ValidationError

    Returns:
        Dictionary with structured error information
    """
    errors = e.errors()
    field_errors = []

    for error in errors:
        # Build dot-path from error location
        field_path = ".".join(str(loc) for loc in error["loc"])
        field_errors.append({
            "field": field_path,
            "error": error["msg"],
            "type": error["type"]
        })

    return {
        "status": "error",
        "error": "validation_failed",
        "message": "Payload validation failed before API call",
        "field_errors": field_errors,
        "suggestion": "Fix the field errors above and try again"
    }

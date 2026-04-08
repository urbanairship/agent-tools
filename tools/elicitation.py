"""
Elicitation wrapper with parameter-based fallbacks.

Provides graceful degradation for MCP clients that don't support elicitation
(e.g., Claude Desktop, Claude Code as of 2026-01).

Usage pattern:
    1. Tool defines optional fallback parameters
    2. Tool calls elicit_with_fallback() for each interactive field
    3. If client supports elicitation: interactive prompt is shown
    4. If client doesn't support elicitation:
       - If fallback_value provided: uses fallback, logs info message
       - If no fallback: raises ValueError with clear instructions

Example:
    @mcp.tool
    async def my_tool(
        ctx: Context,
        platform: str = None  # Fallback parameter
    ) -> dict:
        platform_value, status = await elicit_with_fallback(
            ctx=ctx,
            message="Which platform?",
            response_type=["iOS", "Android"],
            fallback_value=platform,
            param_name="platform"
        )

        if status in ("declined", "cancelled"):
            return {"status": status}

        # platform_value is now available (either elicited or from fallback)
        return {"platform": platform_value}
"""

from typing import TypeVar, Optional, Union, Tuple, List
from fastmcp import Context
from fastmcp.server.elicitation import (
    AcceptedElicitation,
    DeclinedElicitation,
    CancelledElicitation
)


T = TypeVar('T')


async def elicit_with_fallback(
    ctx: Context,
    message: str,
    response_type: Union[type, List[str]],
    fallback_value: Optional[T] = None,
    param_name: str = "value"
) -> Tuple[Optional[T], str]:
    """
    Try elicitation, fall back to parameter if client doesn't support it.

    This wrapper handles all elicitation outcomes:
    - AcceptedElicitation: User provided a response
    - DeclinedElicitation: User declined to answer
    - CancelledElicitation: User cancelled the interaction
    - Exception: Client doesn't support elicitation (use fallback or error)

    Args:
        ctx: FastMCP Context for elicitation and logging
        message: Prompt message to show the user
        response_type: Type for response validation (type or list of options)
        fallback_value: Optional value to use if elicitation is unavailable
        param_name: Name of the fallback parameter (for error messages)

    Returns:
        Tuple of (value, status) where status is one of:
        - "elicited": Value came from user interaction
        - "fallback": Value came from fallback parameter
        - "declined": User declined to provide a value
        - "cancelled": User cancelled the interaction

    Raises:
        ValueError: If elicitation unavailable AND no fallback provided.
                   Error message instructs user to provide the parameter.

    Example:
        # With options list
        platform, status = await elicit_with_fallback(
            ctx,
            "Which platform?",
            ["iOS", "Android"],
            fallback_value=platform_param,
            param_name="platform"
        )

        # With type
        name, status = await elicit_with_fallback(
            ctx,
            "What is your class name?",
            str,
            fallback_value=class_name_param,
            param_name="class_name"
        )
    """
    try:
        result = await ctx.elicit(message, response_type=response_type)

        if isinstance(result, AcceptedElicitation):
            value = result.data
            # If user submitted empty/whitespace and we have a fallback, use it.
            # Report "fallback" so callers know the value wasn't actively chosen.
            if isinstance(value, str) and not value.strip() and fallback_value is not None:
                return fallback_value, "fallback"
            return value, "elicited"
        elif isinstance(result, DeclinedElicitation):
            return None, "declined"
        elif isinstance(result, CancelledElicitation):
            return None, "cancelled"
        else:
            # Unknown result type - treat as declined
            return None, "declined"

    except Exception as e:
        # Elicitation not supported by client
        if fallback_value is not None:
            await ctx.info(f"Using {param_name}={fallback_value} (elicitation not supported by client)")
            return fallback_value, "fallback"

        # No fallback provided - raise helpful error
        raise ValueError(
            f"This tool requires interactive input ('{message}'), "
            f"but your client doesn't support elicitation. "
            f"Please provide the '{param_name}' parameter."
        ) from e

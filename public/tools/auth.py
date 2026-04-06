"""
Authentication module for Airship API.
Prefers Bearer token auth; falls back to Basic Auth (app key + master secret).

Bearer tokens are the preferred credential for all currently implemented
endpoints. Basic Auth is retained as a fallback for endpoints that do not
support Bearer (e.g. message deletion, compliance events) and for users who
have not yet configured a token.

Environment variables
---------------------
AIRSHIP_REGION         — "us" (default) or "eu"
AIRSHIP_BEARER_TOKEN   — preferred; obtain from go.airship.com > APIs & Integrations
AIRSHIP_APP_KEY        — required alongside bearer token (used for admin URL construction);
                         also required for Basic Auth fallback
AIRSHIP_MASTER_SECRET  — required only when falling back to Basic Auth

AIRSHIP_API_URL        — overrides the derived Go API base URL entirely (staging, proxies, etc.)
                         Does not affect Connect or Wallet URLs.

Base URLs by product, region, and auth method
---------------------------------------------
Go API (push, channels, named users, segments, …)
  HTTP auth (basic or bearer):  go.urbanairship.com  /  go.airship.eu
  OAuth 2.0 token:              api.asnapius.com     /  api.asnapieu.com

Connect (RTDS):                 connect.urbanairship.com  /  connect.asnapieu.com

Wallet:                         wallet-api.urbanairship.com/v1  /  wallet-api.asnapieu.com/v1

OAuth token endpoint:           oauth2.asnapius.com  /  oauth2.asnapieu.com
"""

import base64
import os
from typing import Literal, Optional
import httpx


# ---------------------------------------------------------------------------
# Base URL table
# ---------------------------------------------------------------------------

# Keys are (api, region, auth_type).
# auth_type is "http" for Basic/Bearer, "oauth" for OAuth 2.0 JWT.
# The Go API uses different hostnames depending on which of those is in use.
_BASE_URLS: dict[tuple[str, str, str], str] = {
    ("go",      "us", "http"):  "https://go.urbanairship.com",
    ("go",      "eu", "http"):  "https://go.airship.eu",
    ("go",      "us", "oauth"): "https://api.asnapius.com",
    ("go",      "eu", "oauth"): "https://api.asnapieu.com",
    ("connect", "us", "http"):  "https://connect.urbanairship.com",
    ("connect", "eu", "http"):  "https://connect.asnapieu.com",
    ("wallet",  "us", "http"):  "https://wallet-api.urbanairship.com/v1",
    ("wallet",  "eu", "http"):  "https://wallet-api.asnapieu.com/v1",
    ("oauth",   "us", "http"):  "https://oauth2.asnapius.com",
    ("oauth",   "eu", "http"):  "https://oauth2.asnapieu.com",
}

ApiProduct = Literal["go", "connect", "wallet", "oauth"]
Region = Literal["us", "eu"]


def get_base_url(
    api: ApiProduct,
    region: Region,
    oauth_token: bool = False,
    override: Optional[str] = None,
) -> str:
    """Return the correct base URL for a given API product and region.

    Args:
        api:         The API product ("go", "connect", "wallet", "oauth").
        region:      "us" or "eu".
        oauth_token: True if using an OAuth 2.0 JWT (affects Go API hostname).
                     Has no effect on Connect, Wallet, or the OAuth endpoint itself.
        override:    If set, returned as-is. Use for staging/proxy environments.
    """
    if override:
        return override

    auth_type = "oauth" if (api == "go" and oauth_token) else "http"
    key = (api, region, auth_type)

    if key not in _BASE_URLS:
        raise ValueError(f"No base URL defined for api={api!r}, region={region!r}, auth_type={auth_type!r}")

    return _BASE_URLS[key]


# ---------------------------------------------------------------------------
# Auth class
# ---------------------------------------------------------------------------

class AirshipAuth:
    """Handles authentication for Airship API requests."""

    def __init__(
        self,
        app_key: Optional[str] = None,
        master_secret: Optional[str] = None,
        bearer_token: Optional[str] = None,
        region: Optional[Region] = None,
    ):
        self.bearer_token = bearer_token or os.environ.get("AIRSHIP_BEARER_TOKEN")
        self.app_key = app_key or os.environ.get("AIRSHIP_APP_KEY")
        self.master_secret = master_secret or os.environ.get("AIRSHIP_MASTER_SECRET")
        self.region: Region = region or os.environ.get("AIRSHIP_REGION", "us").lower()  # type: ignore[assignment]

        if self.region not in ("us", "eu"):
            raise ValueError(
                f"Invalid AIRSHIP_REGION {self.region!r}. Must be 'us' or 'eu'."
            )

        if not self.bearer_token and (not self.app_key or not self.master_secret):
            raise ValueError(
                "Airship credentials not provided. "
                "Set AIRSHIP_BEARER_TOKEN (preferred) or both AIRSHIP_APP_KEY and "
                "AIRSHIP_MASTER_SECRET environment variables."
            )

    @property
    def using_bearer(self) -> bool:
        return bool(self.bearer_token)

    def get_basic_auth_header(self) -> str:
        """Generate Basic Auth header value."""
        credentials = f"{self.app_key}:{self.master_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    def get_headers(self) -> dict:
        """Get complete headers for Airship API requests.

        Uses Bearer token when available; falls back to Basic Auth.
        """
        if self.bearer_token:
            auth_header = f"Bearer {self.bearer_token}"
        else:
            auth_header = self.get_basic_auth_header()

        return {
            "Authorization": auth_header,
            "Accept": "application/vnd.urbanairship+json; version=3",
            "Content-Type": "application/json",
        }

    def get_basic_auth_headers(self) -> dict:
        """Get headers that force Basic Auth, for endpoints that require it.

        Use this only for endpoints that explicitly do not support Bearer tokens
        (e.g. /api/user/messages batch-delete, Connect compliance events).
        Raises ValueError if Basic Auth credentials are not configured.
        """
        if not self.app_key or not self.master_secret:
            raise ValueError(
                "This endpoint requires Basic Auth (app key + master secret), "
                "but only a Bearer token is configured. "
                "Set AIRSHIP_APP_KEY and AIRSHIP_MASTER_SECRET."
            )
        return {
            "Authorization": self.get_basic_auth_header(),
            "Accept": "application/vnd.urbanairship+json; version=3",
            "Content-Type": "application/json",
        }

    def create_client(
        self,
        api: ApiProduct = "go",
        force_basic: bool = False,
        oauth_token: bool = False,
    ) -> httpx.AsyncClient:
        """Create an authenticated HTTP client for the given Airship API product.

        The base URL is derived from the configured region and auth method.
        Set AIRSHIP_API_URL to override the Go API URL (e.g. for staging).

        Args:
            api:         Which API product to target ("go", "connect", "wallet", "oauth").
            force_basic: Force Basic Auth headers regardless of configured credentials.
                         Use for endpoints that do not accept Bearer tokens.
            oauth_token: Set True when using an OAuth 2.0 JWT; selects the correct
                         Go API hostname. Has no effect on other products.
        """
        url_override = os.environ.get("AIRSHIP_API_URL") if api == "go" else None
        base_url = get_base_url(api, self.region, oauth_token=oauth_token, override=url_override)
        headers = self.get_basic_auth_headers() if force_basic else self.get_headers()

        return httpx.AsyncClient(
            base_url=base_url,
            headers=headers,
            timeout=60.0,
        )


# ---------------------------------------------------------------------------
# Credential validation
# ---------------------------------------------------------------------------

def validate_credentials() -> bool:
    """Validate that usable Airship credentials are available in the environment."""
    has_bearer = bool(os.environ.get("AIRSHIP_BEARER_TOKEN"))
    has_basic = bool(os.environ.get("AIRSHIP_APP_KEY")) and bool(os.environ.get("AIRSHIP_MASTER_SECRET"))

    if not has_bearer and not has_basic:
        print(
            "Airship credentials not configured. "
            "Set AIRSHIP_BEARER_TOKEN (preferred), or both AIRSHIP_APP_KEY and AIRSHIP_MASTER_SECRET."
        )
        return False
    return True

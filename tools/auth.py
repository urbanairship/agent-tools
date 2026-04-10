"""
Authentication module for Airship API - OAuth 2.0 client credentials.

Exchanges AIRSHIP_CLIENT_ID + AIRSHIP_CLIENT_SECRET for a short-lived access
token from the Airship OAuth token endpoint using the client_credentials grant
with client_secret_basic authentication.

Call ``fetch_oauth_token()`` at server startup to obtain the initial token.
Use ``seconds_until_expiry()`` to schedule proactive renewal before expiry
(typically ~1 hour).

Environment variables
---------------------
AIRSHIP_REGION         - "us" (default) or "eu"
AIRSHIP_CLIENT_ID      - OAuth 2.0 client ID; from your project Settings > OAuth in the Airship dashboard
AIRSHIP_CLIENT_SECRET  - OAuth 2.0 client secret
AIRSHIP_APP_KEY        - Required as the token subject (sub claim)

AIRSHIP_API_URL        - Overrides the Go API base URL entirely (staging/proxy environments)

Base URLs by product and region
--------------------------------
Go API (OAuth):  api.asnapius.com    / api.asnapieu.com
OAuth token:     oauth2.asnapius.com / oauth2.asnapieu.com
Connect (RTDS):  connect.urbanairship.com / connect.asnapieu.com
Wallet:          wallet-api.urbanairship.com/v1 / wallet-api.asnapieu.com/v1
"""

import base64
import json
import os
import sys
import time
from typing import Literal, Optional
import httpx


# ---------------------------------------------------------------------------
# Base URL table
# ---------------------------------------------------------------------------

_BASE_URLS: dict[tuple[str, str], str] = {
    ("go",      "us"): "https://api.asnapius.com",
    ("go",      "eu"): "https://api.asnapieu.com",
    ("connect", "us"): "https://connect.urbanairship.com",
    ("connect", "eu"): "https://connect.asnapieu.com",
    ("wallet",  "us"): "https://wallet-api.urbanairship.com/v1",
    ("wallet",  "eu"): "https://wallet-api.asnapieu.com/v1",
    ("oauth",   "us"): "https://oauth2.asnapius.com",
    ("oauth",   "eu"): "https://oauth2.asnapieu.com",
}

ApiProduct = Literal["go", "connect", "wallet", "oauth"]
Region = Literal["us", "eu"]


def get_base_url(
    api: ApiProduct,
    region: Region,
    override: Optional[str] = None,
) -> str:
    """Return the correct base URL for a given API product and region.

    Args:
        api:      The API product ("go", "connect", "wallet", "oauth").
        region:   "us" or "eu".
        override: If set, returned as-is. Use for staging/proxy environments.
    """
    if override:
        return override

    key = (api, region)
    if key not in _BASE_URLS:
        raise ValueError(f"No base URL defined for api={api!r}, region={region!r}")
    return _BASE_URLS[key]


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

def _parse_jwt_exp(token: str) -> Optional[float]:
    """Extract the 'exp' claim from a JWT without verifying the signature.

    Returns None and logs a warning if the token is malformed or missing the
    claim. The refresh loop treats None as unknown expiry and falls back to a
    conservative refresh interval.
    """
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError(f"expected 3 parts, got {len(parts)}")
        payload = parts[1]
        payload += "=" * (-len(payload) % 4)
        data = json.loads(base64.urlsafe_b64decode(payload))
        if "exp" not in data:
            raise ValueError("missing 'exp' claim")
        return float(data["exp"])
    except Exception as exc:
        print(f"Warning: could not parse JWT expiry ({exc}); token lifetime unknown.", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# Auth class
# ---------------------------------------------------------------------------

class AirshipAuth:
    """Handles OAuth 2.0 client credentials authentication for Airship API."""

    def __init__(
        self,
        app_key: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        region: Optional[Region] = None,
    ):
        self.app_key = app_key or os.environ.get("AIRSHIP_APP_KEY")
        self.client_id = client_id or os.environ.get("AIRSHIP_CLIENT_ID")
        self.client_secret = client_secret or os.environ.get("AIRSHIP_CLIENT_SECRET")
        self.region: Region = region or os.environ.get("AIRSHIP_REGION", "us").lower()  # type: ignore[assignment]

        self.bearer_token: Optional[str] = None
        self.token_expires_at: Optional[float] = None

        if self.region not in ("us", "eu"):
            raise ValueError(
                f"Invalid AIRSHIP_REGION {self.region!r}. Must be 'us' or 'eu'."
            )

        if not self.client_id:
            raise ValueError(
                "AIRSHIP_CLIENT_ID must be set. "
                "Obtain OAuth credentials from your project Settings > OAuth in the Airship dashboard."
            )
        if not self.client_secret:
            raise ValueError(
                "AIRSHIP_CLIENT_SECRET must be set (paired with AIRSHIP_CLIENT_ID). "
                "Obtain OAuth credentials from your project Settings > OAuth in the Airship dashboard."
            )
        if not self.app_key:
            raise ValueError(
                "AIRSHIP_APP_KEY must be set (required as the OAuth token subject)."
            )

    def seconds_until_expiry(self) -> Optional[float]:
        """Return seconds until the current token expires, or None if unknown."""
        if self.token_expires_at is None:
            return None
        return self.token_expires_at - time.time()

    async def fetch_oauth_token(self) -> str:
        """Fetch an OAuth 2.0 access token using client_secret_basic.

        POSTs to the OAuth token endpoint with grant_type=client_credentials,
        authenticating with the client ID and secret via HTTP Basic auth.
        Stores the resulting token and its expiry.

        Returns:
            The access token string.

        Raises:
            httpx.HTTPStatusError: If the token endpoint returns an error.
        """
        from urllib.parse import quote_plus

        token_base = get_base_url("oauth", self.region)
        credentials = base64.b64encode(
            f"{quote_plus(self.client_id)}:{quote_plus(self.client_secret)}".encode()
        ).decode()

        async with httpx.AsyncClient() as http:
            response = await http.post(
                f"{token_base}/token",
                headers={
                    "Authorization": f"Basic {credentials}",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                },
                data={"grant_type": "client_credentials", "sub": f"app:{self.app_key}"},
                timeout=30.0,
            )
            response.raise_for_status()
            body = response.json()
            if "access_token" not in body:
                raise ValueError(
                    f"OAuth token endpoint returned an unexpected response "
                    f"(missing 'access_token'): {body}"
                )
            token = body["access_token"]
            expires_in = body.get("expires_in")

        self.bearer_token = token
        self.token_expires_at = (
            time.time() + float(expires_in)
            if expires_in is not None
            else _parse_jwt_exp(token)
        )
        return token

    def get_headers(self) -> dict:
        """Get authorization headers for Airship API requests."""
        if not self.bearer_token:
            raise RuntimeError(
                "OAuth token not yet fetched. Call fetch_oauth_token() at server startup."
            )
        return {
            "Authorization": f"Bearer {self.bearer_token}",
            "Accept": "application/vnd.urbanairship+json; version=3",
            "Content-Type": "application/json",
        }

    def create_client(
        self,
        api: ApiProduct = "go",
    ) -> httpx.AsyncClient:
        """Create an authenticated HTTP client for the given Airship API product.

        Args:
            api: Which API product to target ("go", "connect", "wallet", "oauth").
        """
        url_override = os.environ.get("AIRSHIP_API_URL") if api == "go" else None
        base_url = get_base_url(api, self.region, override=url_override)
        return httpx.AsyncClient(
            base_url=base_url,
            headers=self.get_headers(),
            timeout=60.0,
        )



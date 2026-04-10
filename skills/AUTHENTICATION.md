# Airship API Authentication

Three authentication methods are supported. Choose based on your security requirements.

| Method | Endpoint | When to use |
|---|---|---|
| **OAuth** (recommended) | `api.asnapius.com` / `api.asnapieu.com` | Production — short-lived tokens, no long-lived secrets in config |
| **Bearer token** | `go.urbanairship.com` / `go.airship.eu` | Quick testing or integrations using a dashboard-generated token |
| **Basic auth** | `go.urbanairship.com` / `go.airship.eu` | Legacy integrations only — not recommended for production |

---

## OAuth Client Credentials

### 1. Create credentials

In the Airship dashboard: next to your project name, select the dropdown → **Settings** → **Project settings** → **OAuth**. Enable **Allow Basic Auth** when creating credentials to generate a Client Secret. Enable the scopes your integration needs (see [Scopes reference](#scopes-reference) below).

### 2. Request a token

The client ID and secret must be **URL-encoded** before base64-encoding, then sent as a `Basic` Authorization header:

```bash
ENCODED=$(python3 -c "
import urllib.parse, base64
cid = urllib.parse.quote('YOUR_CLIENT_ID', safe='')
csec = urllib.parse.quote('YOUR_CLIENT_SECRET', safe='')
print(base64.b64encode(f'{cid}:{csec}'.encode()).decode())
")

curl -X POST "https://oauth2.asnapius.com/token" \
  -H "Authorization: Basic $ENCODED" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Accept: application/json" \
  -d "grant_type=client_credentials&sub=app:YOUR_APP_KEY&scope=psh"
```

> EU region: use `https://oauth2.asnapieu.com/token`

The `sub=app:<app_key>` parameter scopes the token to your app. Replace `scope=psh` with the scope required by the skill you're using — see [Scopes reference](#scopes-reference).

**Response:**
```json
{
  "access_token": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "psh"
}
```

Tokens expire after 1 hour. Cache the token and refresh it when `expires_in` is approaching.

### 3. Use the token

```
Authorization: Bearer <access_token>
```

Use `api.asnapius.com` (US) or `api.asnapieu.com` (EU) as the base URL.

---

## Bearer Token (Dashboard-Generated)

### 1. Generate a token

In the Airship dashboard: next to your project name, select the dropdown → **Settings** → **Project settings** → **Tokens**. Create a token with the roles your integration needs.

### 2. Use the token

```
Authorization: Bearer <token>
```

Use `go.urbanairship.com` (US) or `go.airship.eu` (EU) as the base URL.

---

## Basic Auth

> **Not recommended for production.** The master secret grants full account access.

```
Authorization: Basic <base64(app_key:master_secret)>
```

Use `go.urbanairship.com` (US) or `go.airship.eu` (EU) as the base URL.

---

## Scopes Reference

| Skill | OAuth scope |
|---|---|
| push-notification | `psh` |
| channel-listing | `chn` |
| custom-events | `evt` |
| email-lookup | `chn` |
| email-registration | `chn` |
| email-replace | `chn` |
| named-users | `nu` |
| open-channel-registration | `chn` |
| sms-lookup | `chn` |
| sms-registration | `chn` |
| tags (named user tags) | `nu` |
| tags (channel tags) | `chn` |
| create-pipeline | `pln` |
| list-pipelines | `pln` |

Multiple scopes can be requested in one token: `scope=psh chn nu`

---

## X-UA-Appkey Header

`X-UA-Appkey` is **not** a general authentication header — it is only required by specific endpoints:

- `POST /api/custom-events` — required for all auth methods
- `POST /api/sms/custom-response` — required
- `POST /api/sms/{msisdn}/keywords` — required
- `POST https://connect.urbanairship.com/api/events` (RTDS) — required

All other endpoints do not require it.

---

## MCP Server Setup

Add to your assistant's MCP config:

```json
{
  "mcpServers": {
    "airship-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/agent-tools", "airship-mcp"],
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

Alternative credential options:

| Env var | Auth method |
|---|---|
| `AIRSHIP_CLIENT_ID` + `AIRSHIP_CLIENT_SECRET` | OAuth (recommended) |
| `AIRSHIP_BEARER_TOKEN` | Dashboard Bearer token |
| `AIRSHIP_MASTER_SECRET` | Basic auth |

`AIRSHIP_REGION` accepts `us` (default) or `eu`.

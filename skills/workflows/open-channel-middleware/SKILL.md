---
name: open-channel-middleware
description: Build a proof-of-concept middleware server that bridges a custom delivery platform (e.g., WhatsApp, Slack) to Airship Open Channels. Generates working code for GCP Cloud Run or AWS Lambda that handles inbound channel registration, Airship webhook validation, and push payload delivery. Use when a customer or technical resource needs to stand up an Open Channels integration quickly.
---

# Open Channel Middleware Workflow

This workflow guides an agent through building a complete proof-of-concept middleware server for Airship Open Channels. The resulting server handles all three Open Channels integration points: channel registration, webhook validation, and push delivery.

## Overview

Open Channels let Airship deliver notifications to any platform with a webhook — WhatsApp, Slack, smart devices, custom apps, etc. Because there is no Airship SDK on these platforms, a middleware server is required to:

1. **Register channels** — Accept new delivery addresses from your system and register them with Airship.
2. **Validate the webhook** — Respond to Airship's validation handshake during dashboard setup.
3. **Receive and deliver pushes** — Accept Airship's push payloads and route them to the actual delivery mechanism.

```
Your System ──POST /register──► Middleware ──POST /api/channels/open──► Airship
                                     ▲
Airship ──GET  /airship/validate──►  │
Airship ──POST /airship/push    ──►  │
                                     └──► Your delivery mechanism (WhatsApp API, Slack, etc.)
```

## Prerequisites

- Airship project with API access (app key + master secret)
- Airship dashboard access to configure the Open Channel and retrieve the validation code
- GCP project (for Cloud Run) or AWS account (for Lambda) with deployment access
- Node.js 18+ (examples below use Node.js; Python equivalents noted where useful)

## Skills Required

- [Open Channel Registration](../../api/open-channel-registration/SKILL.md)
- [Named Users](../../api/named-users/SKILL.md) (optional, for named user association)
- [Tags](../../api/tags/SKILL.md) (optional, for post-registration tagging)

---

## Phase 1: Discovery

Before generating any code, ask the customer these questions. Answers shape the generated output.

1. **Platform name** — What will you name this open channel platform? This becomes the `open_platform_name` in Airship (e.g., `whatsapp`, `slack`, `alexa`). Lowercase, no spaces.

2. **Address concept** — What does the delivery address represent? (e.g., phone number, Slack user ID, device serial number). This shapes the inbound registration contract and documentation.

3. **Deployment target** — Where will this middleware run? GCP Cloud Run and AWS Lambda are common starting points and both have full implementations below, but any environment that can serve HTTP works — container platforms, VMs, existing Node.js/Python services, etc.

4. **Language preference** — Node.js or Python? (Node.js shown below; Python structure noted at end.)

5. **Inbound auth** — How should callers authenticate to the `/register` endpoint, and what value will they use? Options:
   - **API key** (recommended for PoC): Callers supply a secret in the `X-API-Key` header. You'll need an actual value for this — either provide one or the agent can generate a random one for you. This becomes the `INBOUND_API_KEY` environment variable.
   - **No auth** (dev/testing only): Skip authentication entirely — remove the check before going anywhere near production.

6. **Named user association** — Should registration automatically associate the channel with a named user? If yes, what field in the inbound request body carries the named user ID?

7. **Delivery stub** — For this PoC, the push delivery handler can be a stub that logs payloads (you wire up the real delivery SDK later). Or do you have a specific delivery API in mind?

---

## Phase 2: Environment Variables

All sensitive values are injected via environment variables — never hardcoded.

| Variable | Required | Description |
|---|---|---|
| `AIRSHIP_APP_KEY` | Yes | Your Airship project app key |
| `AIRSHIP_MASTER_SECRET` | Yes (or OAuth) | Your Airship master secret — used for Basic auth |
| `AIRSHIP_CLIENT_ID` | Yes (or master secret) | OAuth client ID — preferred over master secret |
| `AIRSHIP_CLIENT_SECRET` | Yes (or master secret) | OAuth client secret |
| `AIRSHIP_OPEN_PLATFORM_NAME` | Yes | The `open_platform_name` configured in the dashboard |
| `AIRSHIP_VALIDATION_CODE` | Yes | The 36-character UUID from the Airship dashboard (after saving the open channel config) |
| `AIRSHIP_WEBHOOK_SECRET` | Yes (if using Signature Hash auth) | The secret key configured in the dashboard for `X-UA-SIGNATURE` verification |
| `INBOUND_API_KEY` | Recommended | API key callers must supply in `X-API-Key` to reach `/register` |

For Cloud Run: store secrets in GCP Secret Manager and expose as env vars in the Cloud Run service configuration.
For Lambda: store secrets in AWS Secrets Manager or SSM Parameter Store and inject as Lambda environment variables.

---

## Phase 3: Cloud Run Implementation (Node.js/Express)

### File Structure

```
open-channel-middleware/
├── src/
│   └── index.js        # Main server
├── package.json
├── Dockerfile
└── .env.example
```

### `package.json`

```json
{
  "name": "open-channel-middleware",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "start": "node src/index.js",
    "dev": "node --watch src/index.js"
  },
  "dependencies": {
    "express": "^4.19.0"
  }
}
```

### `src/index.js`

```javascript
import express from 'express';
import { createHmac, timingSafeEqual } from 'crypto';
import { gunzip } from 'zlib';
import { promisify } from 'util';

const gunzipAsync = promisify(gunzip);
const app = express();

const {
  AIRSHIP_APP_KEY,
  AIRSHIP_MASTER_SECRET,
  AIRSHIP_CLIENT_ID,
  AIRSHIP_CLIENT_SECRET,
  AIRSHIP_OPEN_PLATFORM_NAME,
  AIRSHIP_VALIDATION_CODE,
  AIRSHIP_WEBHOOK_SECRET,
  INBOUND_API_KEY,
  PORT = '8080',
} = process.env;

const AIRSHIP_BASE_URL = 'https://api.asnapius.com'; // US; use https://api.asnapieu.com for EU
// Basic auth — used when AIRSHIP_MASTER_SECRET is provided
const AIRSHIP_AUTH = AIRSHIP_MASTER_SECRET
  ? Buffer.from(`${AIRSHIP_APP_KEY}:${AIRSHIP_MASTER_SECRET}`).toString('base64')
  : null;

// OAuth token cache — used when AIRSHIP_CLIENT_ID + AIRSHIP_CLIENT_SECRET are provided
let _tokenCache = { token: null, expiresAt: 0 };

async function getOAuthToken() {
  if (_tokenCache.token && Date.now() < _tokenCache.expiresAt) {
    return _tokenCache.token;
  }
  const res = await fetch('https://oauth2.asnapius.com/token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      Accept: 'application/json',
    },
    body: new URLSearchParams({
      grant_type: 'client_credentials',
      client_id: AIRSHIP_CLIENT_ID,
      client_secret: AIRSHIP_CLIENT_SECRET,
      scope: 'chn nu',
    }),
  });
  if (!res.ok) throw new Error(`OAuth token request failed: ${res.status}`);
  const data = await res.json();
  _tokenCache = { token: data.access_token, expiresAt: Date.now() + (data.expires_in - 60) * 1000 };
  return _tokenCache.token;
}

// Returns the Authorization header value — Bearer (OAuth) if client creds present, else Basic
async function getAuthHeader() {
  if (AIRSHIP_CLIENT_ID && AIRSHIP_CLIENT_SECRET) {
    return `Bearer ${await getOAuthToken()}`;
  }
  return `Basic ${AIRSHIP_AUTH}`;
}

// ─── Raw body middleware ──────────────────────────────────────────────────────
// Must read raw bytes before any parsing — needed for gzip decompression
// and Airship signature verification (signature is over the compressed bytes).
app.use((req, res, next) => {
  const chunks = [];
  req.on('data', chunk => chunks.push(chunk));
  req.on('end', async () => {
    try {
      req.rawBody = Buffer.concat(chunks);
      const isGzip = req.headers['content-encoding'] === 'gzip';
      const bodyBytes = isGzip ? await gunzipAsync(req.rawBody) : req.rawBody;
      req.body = JSON.parse(bodyBytes.toString('utf8'));
    } catch {
      req.body = {};
    }
    next();
  });
});

// ─── Auth: inbound registration requests ─────────────────────────────────────
function requireInboundApiKey(req, res, next) {
  if (!INBOUND_API_KEY) return next(); // skip if not configured (dev only)
  if (req.headers['x-api-key'] !== INBOUND_API_KEY) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  next();
}

// ─── Auth: Airship webhook signature ─────────────────────────────────────────
// Signature = HMAC-SHA256(secret_key, "{X-UA-TIMESTAMP}:{raw_body_bytes}")
// The signature covers the raw (compressed) bytes, not the decompressed body.
function verifyAirshipSignature(req, res, next) {
  if (!AIRSHIP_WEBHOOK_SECRET) return next(); // skip if not configured (dev only)

  const timestamp = req.headers['x-ua-timestamp'];
  const signature = req.headers['x-ua-signature'];

  if (!timestamp || !signature) {
    return res.status(401).json({ error: 'Missing Airship signature headers' });
  }

  // Reject requests older than 5 minutes (replay attack prevention)
  const age = Math.abs(Date.now() / 1000 - parseInt(timestamp, 10));
  if (age > 300) {
    return res.status(401).json({ error: 'Request timestamp too old' });
  }

  const message = Buffer.from(`${timestamp}:${req.rawBody.toString('utf8')}`);
  const expected = createHmac('sha256', AIRSHIP_WEBHOOK_SECRET).update(message).digest('hex');

  // Constant-time comparison to prevent timing attacks
  try {
    const match = timingSafeEqual(Buffer.from(signature, 'hex'), Buffer.from(expected, 'hex'));
    if (!match) return res.status(401).json({ error: 'Invalid signature' });
  } catch {
    return res.status(401).json({ error: 'Invalid signature' });
  }

  next();
}

// ─── Airship API helpers ──────────────────────────────────────────────────────
async function registerOpenChannel({ address, optIn = true, identifiers, tags, timezone, localeCountry, localeLanguage }) {
  const channel = {
    type: 'open',
    opt_in: optIn,
    address,
    open: {
      open_platform_name: AIRSHIP_OPEN_PLATFORM_NAME,
      ...(identifiers && { identifiers }),
    },
    ...(tags?.length && { tags }),
    ...(timezone && { timezone }),
    ...(localeCountry && { locale_country: localeCountry }),
    ...(localeLanguage && { locale_language: localeLanguage }),
  };

  const res = await fetch(`${AIRSHIP_BASE_URL}/api/channels/open`, {
    method: 'POST',
    headers: {
      Authorization: await getAuthHeader(),
      'Content-Type': 'application/json',
      Accept: 'application/vnd.urbanairship+json; version=3',
    },
    body: JSON.stringify({ channel }),
  });

  return { status: res.status, data: await res.json() };
}

async function associateNamedUser(channelId, namedUserId) {
  const res = await fetch(`${AIRSHIP_BASE_URL}/api/named_users/associate`, {
    method: 'POST',
    headers: {
      Authorization: await getAuthHeader(),
      'Content-Type': 'application/json',
      Accept: 'application/vnd.urbanairship+json; version=3',
    },
    body: JSON.stringify({ channel_id: channelId, named_user_id: namedUserId }),
  });

  return { status: res.status, data: await res.json() };
}

// ─── Route 1: Inbound channel registration ───────────────────────────────────
// Called by your system when a new user/address should be registered.
//
// Request body:
//   address      (required) — the delivery address, e.g. a phone number
//   opt_in       (optional, default true) — consent status
//   named_user_id (optional) — associate channel with this named user
//   identifiers  (optional) — string:string map stored on the channel
//   tags         (optional) — array of strings for segmentation
//   timezone     (optional) — IANA timezone string
//   locale_country (optional) — ISO 3166 two-letter code
//   locale_language (optional) — ISO 639-1 two-letter code
app.post('/register', requireInboundApiKey, async (req, res) => {
  const { address, opt_in, named_user_id, identifiers, tags, timezone, locale_country, locale_language } = req.body;

  if (!address) {
    return res.status(400).json({ error: '`address` is required' });
  }

  const { status, data } = await registerOpenChannel({
    address,
    optIn: opt_in ?? true,
    identifiers,
    tags,
    timezone,
    localeCountry: locale_country,
    localeLanguage: locale_language,
  });

  if (status !== 200 && status !== 201) {
    console.error('Airship registration failed', { status, data });
    return res.status(502).json({ error: 'Channel registration failed', details: data });
  }

  const channelId = data.channel_id;

  if (named_user_id && channelId) {
    const assoc = await associateNamedUser(channelId, named_user_id);
    if (assoc.status !== 200 && assoc.status !== 201) {
      console.warn('Named user association failed', assoc.data);
      // Non-fatal — channel was registered; return partial success
      return res.status(207).json({ ok: true, channel_id: channelId, named_user_association: 'failed' });
    }
  }

  res.status(status === 201 ? 201 : 200).json({ ok: true, channel_id: channelId });
});

// ─── Route 2: Airship webhook validation ─────────────────────────────────────
// Airship GETs this endpoint when you enable the open channel in the dashboard.
// Must return the exact confirmation_code UUID shown in the dashboard.
app.get('/airship/validate', (req, res) => {
  res.json({ confirmation_code: AIRSHIP_VALIDATION_CODE });
});

// ─── Route 3: Airship push delivery ──────────────────────────────────────────
// Airship POSTs here when a push is sent to this open channel platform.
// Body is gzip-compressed JSON (handled by raw body middleware above).
// Must return 200 quickly — Airship will retry on non-2xx.
//
// TODO: Replace the stub delivery logic with your platform's SDK/API call.
app.post('/airship/push', verifyAirshipSignature, (req, res) => {
  // Acknowledge immediately — do heavy work async or in a queue in production
  res.sendStatus(200);

  const { values = [] } = req.body;

  for (const send of values) {
    const { send_id, target, payload } = send;
    const { address, channel_id, identifiers } = target;
    const { alert, title, extra } = payload;

    console.log('Delivering push', {
      send_id,
      address,
      channel_id,
      alert,
      title,
      extra,
      identifiers,
    });

    // TODO: call your delivery mechanism here
    // Example for WhatsApp via Meta Cloud API:
    // await sendWhatsAppMessage({ to: address, text: alert });
  }
});

// ─── Health check ─────────────────────────────────────────────────────────────
app.get('/health', (req, res) => res.json({ ok: true }));

app.listen(PORT, () => {
  console.log(`open-channel-middleware listening on port ${PORT}`);
  console.log(`Platform: ${AIRSHIP_OPEN_PLATFORM_NAME}`);
});
```

### `Dockerfile`

```dockerfile
FROM node:22-slim
WORKDIR /app
COPY package.json .
RUN npm install --omit=dev
COPY src/ src/
ENV PORT=8080
EXPOSE 8080
CMD ["node", "src/index.js"]
```

### `.env.example`

```
AIRSHIP_APP_KEY=your_app_key
# Auth option 1: Basic (app key + master secret)
AIRSHIP_MASTER_SECRET=your_master_secret
# Auth option 2: OAuth client credentials (preferred)
AIRSHIP_CLIENT_ID=your_oauth_client_id
AIRSHIP_CLIENT_SECRET=your_oauth_client_secret
AIRSHIP_OPEN_PLATFORM_NAME=whatsapp
AIRSHIP_VALIDATION_CODE=          # fill in after step 4 below
AIRSHIP_WEBHOOK_SECRET=           # fill in after step 4 below
INBOUND_API_KEY=your_inbound_api_key
```

### Deploying to Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/open-channel-middleware

# Deploy (inject secrets from Secret Manager)
gcloud run deploy open-channel-middleware \
  --image gcr.io/PROJECT_ID/open-channel-middleware \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-secrets="AIRSHIP_APP_KEY=airship-app-key:latest,AIRSHIP_MASTER_SECRET=airship-master-secret:latest,AIRSHIP_WEBHOOK_SECRET=airship-webhook-secret:latest,INBOUND_API_KEY=inbound-api-key:latest" \
  --set-env-vars="AIRSHIP_OPEN_PLATFORM_NAME=whatsapp,AIRSHIP_VALIDATION_CODE=<uuid-from-dashboard>"
```

After deployment, note the Cloud Run service URL — you'll need it for the Airship dashboard.

---

## Phase 4: Lambda Implementation (Node.js)

Lambda receives API Gateway proxy events. The key differences from Cloud Run:
- No persistent HTTP server — each invocation is a function call.
- API Gateway may base64-encode the body — handle both cases.
- Return a structured response object instead of calling `res.send()`.

### File Structure

```
open-channel-middleware/
├── src/
│   └── handler.js      # Lambda handler
├── package.json
└── template.yaml       # AWS SAM template (optional)
```

### `src/handler.js`

```javascript
import { createHmac, timingSafeEqual } from 'crypto';
import { gunzipSync } from 'zlib';

const {
  AIRSHIP_APP_KEY,
  AIRSHIP_MASTER_SECRET,
  AIRSHIP_CLIENT_ID,
  AIRSHIP_CLIENT_SECRET,
  AIRSHIP_OPEN_PLATFORM_NAME,
  AIRSHIP_VALIDATION_CODE,
  AIRSHIP_WEBHOOK_SECRET,
  INBOUND_API_KEY,
} = process.env;

const AIRSHIP_BASE_URL = 'https://api.asnapius.com'; // US; use https://api.asnapieu.com for EU
// Basic auth — used when AIRSHIP_MASTER_SECRET is provided
const AIRSHIP_AUTH = AIRSHIP_MASTER_SECRET
  ? Buffer.from(`${AIRSHIP_APP_KEY}:${AIRSHIP_MASTER_SECRET}`).toString('base64')
  : null;

// OAuth token cache — used when AIRSHIP_CLIENT_ID + AIRSHIP_CLIENT_SECRET are provided
let _tokenCache = { token: null, expiresAt: 0 };

async function getOAuthToken() {
  if (_tokenCache.token && Date.now() < _tokenCache.expiresAt) {
    return _tokenCache.token;
  }
  const res = await fetch('https://oauth2.asnapius.com/token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      Accept: 'application/json',
    },
    body: new URLSearchParams({
      grant_type: 'client_credentials',
      client_id: AIRSHIP_CLIENT_ID,
      client_secret: AIRSHIP_CLIENT_SECRET,
      scope: 'chn nu',
    }),
  });
  if (!res.ok) throw new Error(`OAuth token request failed: ${res.status}`);
  const data = await res.json();
  _tokenCache = { token: data.access_token, expiresAt: Date.now() + (data.expires_in - 60) * 1000 };
  return _tokenCache.token;
}

// Returns the Authorization header value — Bearer (OAuth) if client creds present, else Basic
async function getAuthHeader() {
  if (AIRSHIP_CLIENT_ID && AIRSHIP_CLIENT_SECRET) {
    return `Bearer ${await getOAuthToken()}`;
  }
  return `Basic ${AIRSHIP_AUTH}`;
}

function ok(body, statusCode = 200) {
  return { statusCode, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) };
}

function err(message, statusCode = 400) {
  return { statusCode, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ error: message }) };
}

function parseBody(event) {
  // API Gateway sends binary bodies as base64 when isBase64Encoded is true
  let rawBytes = event.isBase64Encoded
    ? Buffer.from(event.body ?? '', 'base64')
    : Buffer.from(event.body ?? '', 'utf8');

  const headers = Object.fromEntries(
    Object.entries(event.headers ?? {}).map(([k, v]) => [k.toLowerCase(), v])
  );

  if (headers['content-encoding'] === 'gzip') {
    rawBytes = gunzipSync(rawBytes);
  }

  return {
    rawBytes,
    body: JSON.parse(rawBytes.toString('utf8')),
    headers,
  };
}

function verifyAirshipSignature(headers, rawBytes) {
  if (!AIRSHIP_WEBHOOK_SECRET) return true;

  const timestamp = headers['x-ua-timestamp'];
  const signature = headers['x-ua-signature'];

  if (!timestamp || !signature) return false;

  const age = Math.abs(Date.now() / 1000 - parseInt(timestamp, 10));
  if (age > 300) return false;

  const message = Buffer.from(`${timestamp}:${rawBytes.toString('utf8')}`);
  const expected = createHmac('sha256', AIRSHIP_WEBHOOK_SECRET).update(message).digest('hex');

  try {
    return timingSafeEqual(Buffer.from(signature, 'hex'), Buffer.from(expected, 'hex'));
  } catch {
    return false;
  }
}

async function handleRegistration(body) {
  const { address, opt_in, named_user_id, identifiers, tags, timezone, locale_country, locale_language } = body;

  if (!address) return err('`address` is required');

  const channel = {
    type: 'open',
    opt_in: opt_in ?? true,
    address,
    open: {
      open_platform_name: AIRSHIP_OPEN_PLATFORM_NAME,
      ...(identifiers && { identifiers }),
    },
    ...(tags?.length && { tags }),
    ...(timezone && { timezone }),
    ...(locale_country && { locale_country }),
    ...(locale_language && { locale_language }),
  };

  const regRes = await fetch(`${AIRSHIP_BASE_URL}/api/channels/open`, {
    method: 'POST',
    headers: {
      Authorization: await getAuthHeader(),
      'Content-Type': 'application/json',
      Accept: 'application/vnd.urbanairship+json; version=3',
    },
    body: JSON.stringify({ channel }),
  });

  const regData = await regRes.json();
  if (!regRes.ok) return { statusCode: 502, body: JSON.stringify({ error: 'Registration failed', details: regData }) };

  const channelId = regData.channel_id;

  if (named_user_id && channelId) {
    const assocRes = await fetch(`${AIRSHIP_BASE_URL}/api/named_users/associate`, {
      method: 'POST',
      headers: {
        Authorization: await getAuthHeader(),
        'Content-Type': 'application/json',
        Accept: 'application/vnd.urbanairship+json; version=3',
      },
      body: JSON.stringify({ channel_id: channelId, named_user_id }),
    });

    if (!assocRes.ok) {
      return ok({ ok: true, channel_id: channelId, named_user_association: 'failed' }, 207);
    }
  }

  return ok({ ok: true, channel_id: channelId }, regRes.status === 201 ? 201 : 200);
}

function handlePushDelivery(body) {
  const { values = [] } = body;

  for (const send of values) {
    const { send_id, target, payload } = send;
    console.log('Delivering push', { send_id, address: target.address, alert: payload.alert });

    // TODO: call your delivery mechanism here
    // await sendWhatsAppMessage({ to: target.address, text: payload.alert });
  }

  return { statusCode: 200, body: '' };
}

export const handler = async (event) => {
  const method = (event.httpMethod || event.requestContext?.http?.method || '').toUpperCase();
  const path = event.path || event.rawPath || '/';
  const headers = Object.fromEntries(
    Object.entries(event.headers ?? {}).map(([k, v]) => [k.toLowerCase(), v])
  );

  // Health check
  if (method === 'GET' && path === '/health') {
    return ok({ ok: true });
  }

  // Airship validation handshake
  if (method === 'GET' && path === '/airship/validate') {
    return ok({ confirmation_code: AIRSHIP_VALIDATION_CODE });
  }

  // Inbound channel registration
  if (method === 'POST' && path === '/register') {
    if (INBOUND_API_KEY && headers['x-api-key'] !== INBOUND_API_KEY) {
      return err('Unauthorized', 401);
    }
    const { body } = parseBody(event);
    return handleRegistration(body);
  }

  // Airship push delivery
  if (method === 'POST' && path === '/airship/push') {
    const { rawBytes, body } = parseBody(event);
    if (!verifyAirshipSignature(headers, rawBytes)) {
      return err('Invalid signature', 401);
    }
    return handlePushDelivery(body);
  }

  return { statusCode: 404, body: 'Not Found' };
};
```

### `template.yaml` (AWS SAM)

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Globals:
  Function:
    Runtime: nodejs22.x
    Timeout: 30
    Environment:
      Variables:
        AIRSHIP_APP_KEY: !Sub '{{resolve:ssm:/open-channel/airship-app-key}}'
        AIRSHIP_MASTER_SECRET: !Sub '{{resolve:ssm:/open-channel/airship-master-secret}}'
        AIRSHIP_WEBHOOK_SECRET: !Sub '{{resolve:ssm:/open-channel/airship-webhook-secret}}'
        INBOUND_API_KEY: !Sub '{{resolve:ssm:/open-channel/inbound-api-key}}'
        AIRSHIP_OPEN_PLATFORM_NAME: whatsapp
        AIRSHIP_VALIDATION_CODE: FILL_IN_AFTER_DASHBOARD_SETUP

Resources:
  OpenChannelMiddleware:
    Type: AWS::Serverless::Function
    Properties:
      Handler: src/handler.handler
      Events:
        ApiGateway:
          Type: HttpApi
          Properties:
            Path: /{proxy+}
            Method: ANY
```

```bash
# Deploy
sam build && sam deploy --guided
```

After deployment, note the API Gateway endpoint URL — you'll need it for the Airship dashboard.

---

## Phase 5: Airship Dashboard Setup

Do this **after** deploying the server (the dashboard requires a live URL).

1. In the Airship dashboard, select the dropdown next to your project name → **Settings**.
2. Under **Channels**, select **Open Channels**.
3. Click **+ Configure new Open Channel** and complete the form:
   - **Display Name**: Human-friendly name (e.g., "WhatsApp PoC")
   - **Name**: Your `open_platform_name` value (e.g., `whatsapp`) — must match `AIRSHIP_OPEN_PLATFORM_NAME` exactly.
   - **Webhook URL**: Your deployed service URL + `/airship` as the root (e.g., `https://your-service.run.app/airship`). Airship will call `/airship/validate` and `/airship/push` relative to this.
   - **Authentication**: Select **Signature Hash** and enter a secret key → set this as `AIRSHIP_WEBHOOK_SECRET` in your environment.
4. Click **Save**. A **Validation Code** UUID appears — set this as `AIRSHIP_VALIDATION_CODE` in your environment and redeploy/update the service.
5. Check the **Enabled** box and click **Update**. Airship will call `GET /airship/validate` — it must return the validation code UUID.

> **Note**: Airship re-validates the endpoint every time you update the configuration. The channel must be enabled for pushes to be delivered.

---

## Phase 6: End-to-End Test

### Step 1 — Verify validation endpoint

```bash
curl https://your-service/airship/validate
# Expected: {"confirmation_code":"<your-uuid>"}
```

### Step 2 — Register a channel

```bash
curl -X POST https://your-service/register \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_inbound_api_key" \
  -d '{
    "address": "+15035556789",
    "opt_in": true,
    "named_user_id": "user_001",
    "tags": ["test"]
  }'
# Expected: {"ok":true,"channel_id":"<uuid>"}
```

### Step 3 — Send a push via Airship API

```bash
curl -X POST https://api.asnapius.com/api/push \
  -H "Authorization: Basic <base64(app_key:master_secret)>" \
  -H "Content-Type: application/json" \
  -H "Accept: application/vnd.urbanairship+json; version=3" \
  -d '{
    "audience": { "open_channel": "<channel_id from step 2>" },
    "device_types": ["open::whatsapp"],
    "notification": { "alert": "Hello from Airship!" }
  }'
```

### Step 4 — Verify delivery log

Check your service logs for the delivery log entry:
- Cloud Run: `gcloud run services logs read open-channel-middleware`
- Lambda: CloudWatch Logs → `/aws/lambda/open-channel-middleware`

Expected log output:
```json
{
  "send_id": "<uuid>",
  "address": "+15035556789",
  "alert": "Hello from Airship!"
}
```

---

## Python Notes

If the customer prefers Python, the same structure applies using **FastAPI** (Cloud Run) or the standard Lambda handler pattern.

Key equivalents:
- Gzip decompression: `import gzip; body = gzip.decompress(raw_bytes)`
- HMAC-SHA256: `import hmac, hashlib; hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()`
- Constant-time compare: `hmac.compare_digest(a, b)`
- Airship API calls: `httpx.AsyncClient` or `requests`

---

## Production Considerations

This workflow produces a **proof of concept**. Before going to production, consider:

- **Async delivery**: The push delivery handler should return 200 immediately and process sends asynchronously (Cloud Tasks, SQS, etc.) to avoid Airship retry storms on slow downstream APIs.
- **Idempotency**: Use `send_id` for deduplication — Airship may retry delivery on non-2xx responses.
- **Batching**: Airship delivers up to 1,000 send objects per request. Batch your downstream API calls accordingly.
- **Monitoring**: Add structured logging and alerting on 502 errors from Airship registration.
- **Secrets rotation**: Use Secret Manager / Secrets Manager with automatic rotation rather than static env vars.

## Related Skills

- [Open Channel Registration](../../api/open-channel-registration/SKILL.md)
- [Named Users](../../api/named-users/SKILL.md)
- [Tags](../../api/tags/SKILL.md)
- [Push Notification](../../api/push-notification/SKILL.md)

# Sora API Observation Document (Phase 4A)

> **Purpose**: Document observed Sora API behavior BEFORE integration.
> **Scope**: Read-only observation. NO code changes in this phase.

---

## 1. Access Methods

### Official API (OpenAI)
| Method | Description |
|--------|-------------|
| Bearer Token | `Authorization: Bearer {API_KEY}` in headers |
| API Keys | Generated from OpenAI dashboard after approval |
| Status | Preview access, requires application |

### Web Interface (sora.com)
| Method | Description |
|--------|-------------|
| Session Cookies | Cookie-based auth after login with OpenAI/ChatGPT account |
| Relevant Cookies | `__cf_bm`, `__Secure-next-auth.session-token`, etc. |
| Session Duration | Unknown, likely hours to days |

---

## 2. Observed Endpoints

### Video Generation
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/videos` or `/videos` | POST | Create new video generation job |
| `/v1/videos/{video_id}` | GET | Get video metadata |
| `/v1/videos/{video_id}/status` | GET | Poll generation status |
| `/v1/videos/{video_id}/content` | GET | Download completed video (MP4) |
| `/v1/videos/{video_id}` | DELETE | Delete a video |

### History / Idempotency
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/videos/history` or `/videos` | GET | List recent generations |

### Request Format (Inferred)
```
POST /v1/videos
Content-Type: application/json
Authorization: Bearer {token} OR Cookie: {session}

{
  "prompt": "A cinematic video of...",
  "duration": 5,         // seconds (5, 10, 15, 20)
  "aspect_ratio": "16:9" // or "9:16", "1:1"
}
```

### Response Format (Inferred)
```json
{
  "id": "video_abc123",
  "status": "processing",
  "created_at": "2026-01-09T08:00:00Z",
  "prompt": "...",
  "video_url": null
}
```

---

## 3. Authentication Flow

### Web UI Flow (Cookie-based)
1. User visits sora.com
2. Redirects to OpenAI login (auth0/ChatGPT SSO)
3. After successful login, session cookies are set:
   - `__Secure-next-auth.session-token` (primary session)
   - `__cf_bm` (Cloudflare bot management)
   - `__Secure-next-auth.callback-url`
4. Cookies sent with all subsequent API requests
5. Session may expire (requires re-login)

### API Key Flow (Bearer Token)
1. Obtain API key from OpenAI dashboard
2. Include in all requests: `Authorization: Bearer sk-...`
3. No cookie management needed

---

## 4. Rate Limits & Quotas

### Observed Patterns
| Condition | Behavior |
|-----------|----------|
| 429 Too Many Requests | Returned when rate limit exceeded |
| Retry-After Header | May indicate wait time (seconds) |
| Daily Quota | Unknown exact limit, varies by plan |
| Concurrent Jobs | Likely limited (1-5 depending on plan) |

### Mitigation Strategies
- Exponential backoff on 429
- Track quota locally (pessimistic estimation)
- Rotate between multiple accounts
- Add delays between requests (2-5 seconds)

---

## 5. Error Patterns

| HTTP Code | Meaning | Action |
|-----------|---------|--------|
| 200 | Success | Process response |
| 401 | Unauthorized | Cookie/token expired, re-authenticate |
| 403 | Forbidden | Account suspended or feature restricted |
| 404 | Not Found | Video ID doesn't exist |
| 429 | Rate Limited | Backoff and retry |
| 500 | Server Error | Retry with backoff |
| 503 | Service Unavailable | Queue overloaded, retry later |

### Soft Ban Indicators (Heuristics)
- Consistently slow response times (>30s)
- Repeated 429s even with long delays
- Generation always fails with vague errors
- Captcha challenges appearing

---

## 6. Video Generation Flow

```
1. Create Request (POST /videos)
   ↓
2. Receive Job ID
   ↓
3. Poll Status (GET /videos/{id}/status)
   ├── "processing" → Continue polling (every 5-10s)
   ├── "completed" → Proceed to download
   └── "failed" → Log error, retry or fail
   ↓
4. Download Video (GET /videos/{id}/content)
   ↓
5. Save to local file
```

### Polling Observations
- Generation typically takes 30s - 5min depending on duration
- Status endpoint is lightweight (no rate limit concerns)
- Video URL may be temporary (signed URL with expiration)

---

## 7. Download Without Watermark

### Observations
- Official web UI may add watermark to some tiers
- Direct API downloads (via /content endpoint) may be unwatermarked
- Signed URLs may bypass watermarking
- Need to observe actual response headers for `Content-Disposition`

---

## 8. Security Considerations

| Concern | Mitigation |
|---------|------------|
| Cookie Expiration | Monitor 401s, prompt re-auth |
| Token Leakage | Store in secure local file, never log |
| Rate Limiting | Use conservative delays |
| IP Blocking | Consider proxy rotation if needed |
| TLS Fingerprinting | Use standard User-Agent strings |

---

## 9. Recommended Headers

```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
Accept: application/json
Content-Type: application/json
Accept-Language: en-US,en;q=0.9
Origin: https://sora.com
Referer: https://sora.com/
```

---

## 10. Integration Recommendations

### Before Enabling Real API
- [ ] Capture actual network traffic with browser DevTools
- [ ] Document exact endpoints for current Sora version
- [ ] Test cookie extraction from browser session
- [ ] Verify download URL format (signed vs permanent)
- [ ] Establish baseline request/response times

### Shadow Mode Testing
1. Enable shadow mode in tool
2. Capture real credentials via browser extension
3. Test read-only operations (get_history, get_status)
4. Verify auth is working before enabling create

### Canary Deployment
1. Single account, single job
2. Monitor full flow end-to-end
3. Check video quality and watermark status
4. Measure actual quotas and rate limits

---

## 11. Unknown / TBD

- [ ] Exact daily quota per account tier
- [ ] Precise cookie expiration timing
- [ ] Whether API key access differs from web UI access
- [ ] Video URL expiration timing
- [ ] Exact request body schema for image+text generation

---

*Document created: 2026-01-09*
*Last updated: Phase 4A Observation*

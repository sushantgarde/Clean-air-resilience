# Security Documentation

## Clean Air & Climate Resilience

**Version:** 1.0
**Last Updated:** August 2026

---

## Table of Contents

- [1. Purpose & Scope](#1-purpose--scope)
- [2. Data Handling](#2-data-handling)
- [3. Secrets Management](#3-secrets-management)
- [4. API Key Exposure History & Response](#4-api-key-exposure-history--response)
- [5. Authentication & Authorization](#5-authentication--authorization)
- [6. Third-Party Service Dependencies](#6-third-party-service-dependencies)
- [7. Application-Level Security Posture](#7-application-level-security-posture)
- [8. Known Limitations](#8-known-limitations)
- [9. Reporting a Security Issue](#9-reporting-a-security-issue)

---

## 1. Purpose & Scope

This document describes the security posture of Clean Air & Climate
Resilience as built for the hackathon: what data it handles, how secrets are
managed, what protections are (and are not) in place, and what a future
maintainer should address before any production-scale use. This is a
hackathon-scale project, not a hardened production system — that distinction
is stated explicitly throughout rather than implied.

## 2. Data Handling

### 2.1 What data the system processes

| Data type | Source | Sensitivity | Storage |
|---|---|---|---|
| Satellite aerosol readings | Sentinel-5P (public, open data) | None — publicly available environmental data | Summary stats in `data/day1_sentinel_sample.json` |
| Ground-station pollutant readings | OpenAQ (public, open data) | None — publicly available environmental data | `data/air_quality.db` (SQLite, committed to repo) |
| Citizen photos | Sample dataset (public Kaggle dataset, India/Nepal) | None in this build — no personally identifiable citizen submissions were collected, since the live upload endpoint is out of scope for this version | `data/sample_images/` (excluded from git via `.gitignore`) |
| API credentials | Copernicus, OpenAQ, Gemini | High — must not be exposed | `.env` (local only), Render environment variables (production) |

**No personal data, user accounts, or PII are collected or stored by this
system in its current version.** All environmental data (satellite,
ground-station) is inherently public and non-personal.

### 2.2 Data at rest

`data/air_quality.db` is committed to the public GitHub repository. This is
a **deliberate, disclosed decision** (see [TDD](./TECHNICAL_DESIGN_DOCUMENT.md)
§6) driven by Render's ephemeral free-tier filesystem — the data itself is
non-sensitive (public pollution readings), so committing it publicly carries
no confidentiality risk, only a git-hygiene consideration that was
consciously accepted for this deployment model.

### 2.3 Data in transit

- Calls to Copernicus Data Space, OpenAQ, and Gemini APIs occur over HTTPS
  (enforced by each provider's SDK/endpoint)
- The deployed Render service is served over HTTPS by default (Render
  provisions TLS automatically for all web services, including free tier)

## 3. Secrets Management

Four credentials are required by the system (see
[Configuration Guide](./CONFIGURATION_GUIDE.md) §2):

| Credential | Storage (local) | Storage (production) |
|---|---|---|
| `SENTINELHUB_CLIENT_ID` / `SECRET` | `.env` (gitignored) | Render Environment tab (encrypted at rest) |
| `OPENAQ_API_KEY` | `.env` (gitignored) | Render Environment tab |
| `GEMINI_API_KEY` | `.env` (gitignored) | Render Environment tab |

**Verification practice used throughout this build:** before every commit
touching configuration, `git check-ignore -v .env` was run to confirm the
secrets file would not be tracked — this check is documented as a required
step in both the [Deployment Guide](./DEPLOYMENT_GUIDE.md) and
[Configuration Guide](./CONFIGURATION_GUIDE.md).

**None of the four credentials are logged, printed to stdout in production,
or included in any committed file.** `sh_config.py` prints the Sentinel Hub
base/token *URLs* for debugging (not the secret values themselves) — this
debug print was added deliberately during troubleshooting and should be
removed or gated behind a debug flag before any wider distribution of the
codebase.

## 4. API Key Exposure History & Response

During development, no credential was ever committed to git — confirmed
via the `git check-ignore` practice above at every relevant commit. However,
two related incidents are worth recording for transparency:

1. **A GitHub push was rejected for an oversized file**
   (`data/weather_aqi_history.json`, 115MB+) — not a security incident, but
   resolved via the same "check before pushing" discipline that also
   protects secrets. See [CHANGELOG](./CHANGELOG.md) Phase 4.
2. **Demo video files were briefly staged for commit** (`Demo Video.mp4`,
   `Demo Video.zip`) before being caught in `git status` review and
   unstaged. No secrets were present in these files, but this reinforces the
   value of reviewing `git status` output before every commit — a practice
   followed throughout this project (see [CONTRIBUTING.md](./CONTRIBUTING.md) §7).

**If a credential is ever accidentally exposed** (committed, logged, or
shared), the response procedure is:
1. Immediately rotate the credential at its source (see
   [Configuration Guide](./CONFIGURATION_GUIDE.md) §6 for per-provider
   rotation steps)
2. Update `.env` locally and Render's Environment tab with the new value
3. If committed to git history, treat the old key as permanently compromised
   even after removal from the latest commit — git history retains it until
   explicitly purged (e.g. via `git filter-repo` or a fresh repo, as was
   done in this project when a large file needed removing from history —
   see [CHANGELOG](./CHANGELOG.md) Phase 4)

## 5. Authentication & Authorization

**The application itself has no authentication or authorization layer.**
All API endpoints (`/`, `/api/hotspots`, `/api/hotspots/<region>`,
`/docs/<filename>`) are fully public, by design — this is a public
information/alerting service, not a system handling user accounts or
private data.

**This means:**
- Anyone can call the API and trigger a live Gemini alert generation,
  consuming the project's free-tier Gemini quota
- There is no rate limiting on the application's own endpoints (only the
  upstream Gemini/OpenAQ free-tier limits apply, indirectly)

**If this project were extended toward production use with a live citizen
photo upload endpoint** (see Roadmap in [Architecture Document](./ARCHITECTURE.md)
§11), authentication/authorization and application-level rate limiting
would become a hard requirement before launch — an open, unauthenticated
image upload endpoint is a materially different risk profile than the
current read-only public data API.

## 6. Third-Party Service Dependencies

| Service | Data shared | Risk if compromised |
|---|---|---|
| Copernicus Data Space | OAuth credentials only; no user data sent | Low — public satellite data access only |
| OpenAQ | API key only; no user data sent | Low — public air quality data access only |
| Gemini API | API key; images (sample dataset) and text prompts (region/score/trend) sent for classification/generation | Low-Medium — no PII sent, but a leaked key could be used to consume the project owner's free-tier quota or, if a paid tier were ever attached, incur charges |
| Render | Full application code and environment variables | Medium — Render hosts both the app and its secrets; standard platform-level trust required, as with any PaaS |

No sub-processors or additional third parties receive data beyond the four
services above.

## 7. Application-Level Security Posture

| Control | Status |
|---|---|
| HTTPS in production | ✅ Provided by Render automatically |
| Secrets excluded from version control | ✅ Enforced via `.gitignore` + manual verification |
| Flask debug mode disabled in production | ✅ `debug=False` set explicitly for the Render deployment |
| Input validation on API parameters | ⚠️ Minimal — `region_key` is checked against a known dict (safe), but no other endpoint accepts user input in this version |
| Rate limiting (application-level) | ❌ Not implemented |
| Authentication/authorization | ❌ Not implemented (not required for current read-only public scope) |
| Dependency vulnerability scanning | ❌ Not configured (no `pip-audit`/Dependabot set up) |
| CORS policy | ⚠️ `flask-cors` is enabled broadly (`CORS(app)`); acceptable for a fully public read-only API, but should be scoped if any write/authenticated endpoint is added later |

## 8. Known Limitations

- No automated dependency vulnerability scanning is configured — a future
  contributor should add Dependabot or `pip-audit` to CI once CI exists (see
  [Testing Documentation](./TESTING_DOCUMENTATION.md) §8)
- No application-level rate limiting — acceptable at hackathon-demo traffic
  levels, not acceptable if this were exposed to genuine public load
- Debug print of internal service URLs in `sh_config.py` should be removed
  or gated before any broader code sharing
- The `data/air_quality.db` public-commit decision is safe *only* because
  the data is inherently public/non-personal — this decision would need to
  be revisited immediately if the system ever stores any personal or
  sensitive data (e.g. once a live citizen photo/location upload feature is
  added)

## 9. Reporting a Security Issue

For this hackathon-scale project, report security concerns directly to the
maintainer (Sushant Garde) via the contact listed in the [README](./README.md).
There is no formal bug bounty or disclosure program at this stage. Please do
not open a public GitHub issue for a credential-exposure finding — report it
privately first so it can be rotated before public disclosure.

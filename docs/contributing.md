# Contributing Guide

## Clean Air & Climate Resilience

**Version:** 1.0
**Last Updated:** August 2026

---

## Table of Contents

- [1. Welcome](#1-welcome)
- [2. Code of Conduct](#2-code-of-conduct)
- [3. Getting Started](#3-getting-started)
- [4. Project Structure Orientation](#4-project-structure-orientation)
- [5. Coding Standards](#5-coding-standards)
- [6. Branching Strategy](#6-branching-strategy)
- [7. Commit Message Conventions](#7-commit-message-conventions)
- [8. Pull Request Process](#8-pull-request-process)
- [9. Adding a New Region](#9-adding-a-new-region)
- [10. Testing Expectations](#10-testing-expectations)
- [11. Documentation Expectations](#11-documentation-expectations)
- [12. Reporting Issues](#12-reporting-issues)

---

## 1. Welcome

Thanks for your interest in contributing to Clean Air & Climate Resilience.
This project was originally built as a hackathon submission with a 5-day
timeline; this guide sets expectations for anyone extending it afterward.

## 2. Code of Conduct

Be respectful, constructive, and assume good faith in code review. This
project deals with environmental/public-health-adjacent data — accuracy and
honest disclosure of limitations (see the "What's Real vs. Simulated" table
in the README) matter more than polish. Don't misrepresent simulated or
illustrative data as live/real in any contribution.

## 3. Getting Started

1. Fork and clone the repository
2. Follow the [Deployment Guide](./DEPLOYMENT_GUIDE.md) §3–6 for local setup
3. Obtain your own free API credentials (Copernicus, OpenAQ, Gemini) — do
   not request or reuse the original maintainer's keys
4. Verify your setup by running the standalone module checks in
   [Testing Documentation](./TESTING_DOCUMENTATION.md) §6 before making changes

## 4. Project Structure Orientation

Read the [Architecture Document](./ARCHITECTURE.md) first — it explains the
five logical layers (data acquisition, storage, intelligence, API,
presentation) and where each file fits. Do not add new top-level
directories without updating that document.

## 5. Coding Standards

- **Docstrings required** for every function in `src/pipeline/` — follow the
  existing Google-style docstring format (`Args:` / `Returns:`) already used
  throughout the codebase
- **No hardcoded secrets** — anything credential-like goes through `.env`
  and `os.getenv()`, never inline in code
- **Comment non-obvious decisions inline**, especially anything working
  around a third-party API quirk (see the CDSE `DataCollection` rebinding in
  `sh_config.py`/`day1_checkpoint.py` as the existing style example)
- **Mark simulated/demo-only logic explicitly** with a `# DEMO NOTE:`
  comment, matching the convention already used for the `delhi-ncr` region's
  illustrative values in `app.py` — never let simulated data look
  indistinguishable from real data in code
- **Python style**: follow standard PEP 8; no linter is currently configured
  in CI, so use judgment and consistency with surrounding code
- **Frontend**: keep `index.html`/`style.css`/`script.js` dependency-free
  beyond the existing Leaflet.js CDN import — don't introduce a build step
  (webpack, bundlers, etc.) without discussing it first, since the project
  intentionally stays framework-free for deployment simplicity

## 6. Branching Strategy

This project currently uses a single `main` branch (no `develop`/release
branch structure, appropriate to its current scale). For contributions:

```bash
git checkout -b feature/short-description
# or
git checkout -b fix/short-description
```

Branch off `main`, and open a pull request back into `main`.

## 7. Commit Message Conventions

Follow the pattern already used in this repo's history — short, imperative,
descriptive:

```
Fix logo path with dedicated docs route, add icon-only favicon
Include SQLite database for deployment (Render filesystem is ephemeral)
Pin Python 3.11 for Render build compatibility
```

Avoid vague messages like `"update"` or `"fix bug"` — state *what* changed
and, where non-obvious, *why* (as in the second example above).

## 8. Pull Request Process

1. Ensure your branch runs cleanly end-to-end locally (see
   [Testing Documentation](./TESTING_DOCUMENTATION.md) §6 for verification commands)
2. Update relevant documentation if your change affects architecture, API
   shape, configuration, or deployment steps — this project treats docs as
   part of the change, not an afterthought
3. Open a PR against `main` with a clear description of:
   - What changed
   - Why (link to an issue if one exists)
   - How you verified it (manual test steps, since no CI exists yet)
4. No formal review SLA exists for this project currently — for a
   hackathon-origin solo project, expect asynchronous review

## 9. Adding a New Region

This is the most common extension point. Follow the exact steps in
[Configuration Guide](./CONFIGURATION_GUIDE.md) §4:

1. Add an entry to `REGIONS` in `app.py`
2. Add station coordinates to `REGION_STATIONS` in `script.js`
3. Add a map center/zoom entry to `REGION_CENTERS` in `script.js`
4. Add a toggle button in `index.html`

If the new region uses real (not illustrative) satellite/citizen data,
pull it using the same scripts used for Punjab-Haryana
(`day1_checkpoint.py` with updated bbox, `test_vision_batch.py` against
region-relevant sample images) rather than inventing static values — and
do **not** mark it real in documentation unless it genuinely is.

## 10. Testing Expectations

There is no CI pipeline or automated test suite yet (see
[Testing Documentation](./TESTING_DOCUMENTATION.md) §7 for the known gap and
§8 for the recommended priority order). Until one exists:

- Run the standalone verification commands for any module you touch
- Manually test the full request flow (`/api/hotspots/<region>`) after any
  change to the pipeline
- If you add automated tests, `pytest` is the natural choice given the
  existing pure-function structure of `hotspot_scoring.py` — this is the
  single highest-value place to start

## 11. Documentation Expectations

This project maintains a full documentation set (README, Architecture, API,
TDD, PRD, Deployment Guide, Configuration Guide, Runbook, Testing Docs, this
Contributing Guide). If your change affects:

| Change type | Update |
|---|---|
| New/changed API endpoint | `API_DOCUMENTATION.md` |
| New/changed component or data flow | `ARCHITECTURE.md`, `TECHNICAL_DESIGN_DOCUMENT.md` |
| New/changed environment variable or config | `CONFIGURATION_GUIDE.md` |
| New/changed deployment step | `DEPLOYMENT_GUIDE.md` |
| New known failure mode | `RUNBOOK.md` §8 |

## 12. Reporting Issues

When filing an issue, include:
- What you expected vs. what happened
- Whether it reproduces locally, on Render, or both
- Relevant log output (check Render's **Logs** tab for production issues,
  per [Runbook](./RUNBOOK.md) §6)
- Which free-tier service was involved, if applicable (Copernicus, OpenAQ,
  Gemini, Render) — several past issues in this project were upstream API
  quirks (rate limits, parameter caps, retired models) rather than bugs in
  this codebase, so identifying the source early helps triage

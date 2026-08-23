# Privacy & Data Policy

## Clean Air & Climate Resilience

**Version:** 1.0
**Last Updated:** August 2026

---

## Table of Contents

- [Privacy \& Data Policy](#privacy--data-policy)
  - [Clean Air \& Climate Resilience](#clean-air--climate-resilience)
  - [Table of Contents](#table-of-contents)
  - [1. Purpose](#1-purpose)
  - [2. Summary](#2-summary)
  - [3. What Data This System Collects](#3-what-data-this-system-collects)
  - [4. What Data This System Does NOT Collect](#4-what-data-this-system-does-not-collect)
  - [5. Data Sources \& Their Own Policies](#5-data-sources--their-own-policies)
  - [6. Data Sent to Third-Party AI Services](#6-data-sent-to-third-party-ai-services)
  - [7. Data Retention](#7-data-retention)
  - [8. Data Storage Location](#8-data-storage-location)
  - [9. User Rights](#9-user-rights)
  - [10. Children's Data](#10-childrens-data)
  - [11. Changes to This Policy](#11-changes-to-this-policy)
  - [12. Contact](#12-contact)

---

## 1. Purpose

This policy explains what data Clean Air & Climate Resilience collects,
processes, and stores, in plain language. It is written for a hackathon
submission context — a real production deployment handling live citizen
submissions would require a more formal, jurisdiction-specific policy (see
[Section 11](#11-changes-to-this-policy)).

## 2. Summary

**This system does not collect, store, or process any personal data about
any individual user or visitor.** Every dataset it works with — satellite
imagery, ground-station air quality readings, and sample citizen photos —
is either inherently public environmental data or a non-personal sample
dataset used for demonstration purposes.

## 3. What Data This System Collects

| Data | Personal? | Purpose |
|---|---|---|
| Satellite aerosol index readings (Sentinel-5P) | No — environmental/atmospheric measurement, no individual is identifiable | Detecting regional pollution levels |
| Ground-station pollutant readings (OpenAQ) | No — environmental measurement from fixed public monitoring stations | Detecting regional pollution levels |
| Sample citizen photos (public Kaggle dataset) | No — sourced from a published open dataset used for demonstrating the classification pipeline, not collected from real users of this system | Demonstrating photo-based smog/haze severity classification |

**Dashboard visitors:** this system does not use cookies, does not track
visitors, does not collect IP addresses beyond what Render's hosting
infrastructure logs by default for operational purposes (standard for any
web host, not specific to this application), and does not run any analytics
or advertising scripts.

## 4. What Data This System Does NOT Collect

- No user accounts, logins, or authentication data (the system has no
  auth layer — see [Security Documentation](./SECURITY.md) §5)
- No names, email addresses, phone numbers, or other direct identifiers
- No real citizen-submitted photos (the live upload feature is explicitly
  out of scope for this version — see [PRD](./PRD.md) §8)
- No location data tied to an individual person (only fixed, public
  monitoring station coordinates and satellite bounding boxes)
- No cookies or browser tracking
- No payment or financial information

## 5. Data Sources & Their Own Policies

This system pulls from three external data providers. Each governs its own
data under its own terms:

| Provider | Data used | Provider's own policy |
|---|---|---|
| Copernicus Data Space Ecosystem | Sentinel-5P satellite aerosol data | [Copernicus Data Access Policy](https://dataspace.copernicus.eu) — open data, free and full access under the Copernicus programme |
| OpenAQ | Ground-station pollutant measurements | [OpenAQ Terms of Use](https://openaq.org) — open environmental data aggregator |
| Kaggle (sample photo dataset) | Sample citizen-style photos used for classifier testing | Subject to the original dataset's Kaggle license terms |

This project does not modify, resell, or redistribute these providers' data
outside the scope of this demonstration application.

## 6. Data Sent to Third-Party AI Services

Two categories of data are sent to Google's Gemini API for processing:

1. **Sample images** (from the public Kaggle dataset) — sent for smog/haze
   severity classification
2. **Text prompts** containing region name, computed hotspot score, and
   forecast trend description — sent for alert text generation

**No personal data is included in either category.** Data sent to Gemini is
subject to [Google's Gemini API terms and data usage policies](https://ai.google.dev/gemini-api/terms).
This project does not send any user-identifying information to Gemini or
any other AI service.

## 7. Data Retention

| Data | Retention |
|---|---|
| Ground-station readings in `data/air_quality.db` | Retained indefinitely in the project's git history as a point-in-time evidence snapshot; refreshed manually, not on an automatic schedule (see [Runbook](./RUNBOOK.md) §9) |
| Satellite summary statistics | Retained indefinitely as project evidence (`data/day1_sentinel_sample.json`) |
| Vision classification results | Retained indefinitely as project evidence (`data/vision_test_results.json`) |
| Server logs (Render) | Subject to Render's own log retention policy, not controlled by this project |

Since no personal data is collected, there is no personal-data deletion
process to describe — the retained data described above is entirely
non-personal, aggregate environmental data.

## 8. Data Storage Location

- **Application code and committed data** (`data/air_quality.db`, JSON
  evidence files): stored in a public GitHub repository
- **Runtime hosting**: Render (region depends on Render's infrastructure at
  deploy time; not user-configurable on the free tier)
- **API credentials**: stored in Render's environment variable system
  (encrypted at rest per Render's platform security), never in the
  repository

## 9. User Rights

Because this system collects no personal data, there is no personal data to
access, correct, or delete on request. If this changes in a future version
(e.g. a live citizen photo upload feature that captures a submitter's
location or contact info), this policy will be revised to include a formal
data subject rights process before that feature is deployed.

## 10. Children's Data

This system does not knowingly collect data from or about children, and is
not directed at children. As it collects no personal data of any kind from
any user, this is inherently satisfied by the system's current design.

## 11. Changes to This Policy

This policy reflects the system as submitted for the "Build with AI — Code
for Communities" hackathon. **If this project is extended toward real-world
deployment** — particularly a live citizen photo/location submission
feature — this policy must be substantially revised before launch to
address: consent for photo submission, location data handling, retention
periods for user-submitted content, and compliance with applicable data
protection law in the deployment jurisdiction (e.g. India's Digital
Personal Data Protection Act, or GDPR if serving EU users). This version of
the policy should not be treated as sufficient for that future scenario.

## 12. Contact

For questions about this policy, contact the maintainer (Sushant Garde) via
the contact information in the [README](./README.md).
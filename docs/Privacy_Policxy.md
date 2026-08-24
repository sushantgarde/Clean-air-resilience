# Privacy & Data Policy

## Clean Air & Climate Resilience

**Version:** 1.0
**Last Updated:** August 2026

---

## Table of Contents

- [1. Purpose](#1-purpose)
- [2. Data We Collect](#2-data-we-collect)
- [3. Data We Do Not Collect](#3-data-we-do-not-collect)
- [4. How Data Is Used](#4-how-data-is-used)
- [5. Third-Party Data Sharing](#5-third-party-data-sharing)
- [6. Data Retention](#6-data-retention)
- [7. Data Storage & Location](#7-data-storage--location)
- [8. User Rights](#8-user-rights)
- [9. Children's Privacy](#9-childrens-privacy)
- [10. Future Data Collection (Roadmap)](#10-future-data-collection-roadmap)
- [11. Changes to This Policy](#11-changes-to-this-policy)
- [12. Contact](#12-contact)

---

## 1. Purpose

This document explains what data Clean Air & Climate Resilience collects,
processes, and stores, in the interest of transparency for users,
evaluators, and anyone reviewing or extending this project. It reflects the
system **as actually built** for this hackathon submission — not a
hypothetical future version.

## 2. Data We Collect

**In its current version, this system collects no personal data from
end users.** The dashboard is a read-only, public information display; it
does not require sign-up, login, or any user-submitted personal information.

The data the system stores and processes consists entirely of:

| Data | Nature | Personal? |
|---|---|---|
| Satellite aerosol readings (Sentinel-5P) | Public environmental data | No |
| Ground-station air quality readings (OpenAQ) | Public environmental data | No |
| Sample citizen photos (Kaggle dataset) | Publicly available research dataset images, used to demonstrate the vision classifier | No — not sourced from real end users of this application, and contains no identifying information about individuals |
| Computed outputs (hotspot scores, forecasts, generated alerts) | Derived entirely from the above public data | No |

## 3. Data We Do Not Collect

- No user accounts, sign-up, or login
- No cookies or browser tracking
- No location data from end users (the "regions" shown are fixed,
  predefined geographic areas, not derived from a visitor's device location)
- No analytics or usage tracking
- No personally identifiable information of any kind

## 4. How Data Is Used

The public environmental data described in Section 2 is used solely to:
1. Compute a hotspot risk score for each supported region
2. Generate a short-term pollution forecast
3. Generate a plain-language alert via the Gemini API
4. Display the above on the public dashboard

No data collected by this system is used for advertising, profiling, resale,
or any purpose beyond displaying regional air-quality information.

## 5. Third-Party Data Sharing

The system sends data to three external AI/data providers as part of its
core functionality:

| Provider | What is sent | Why |
|---|---|---|
| Copernicus Data Space | Bounding box coordinates, date range | To retrieve satellite aerosol readings |
| OpenAQ | Coordinates, radius, query parameters | To retrieve ground-station readings |
| Google Gemini API | Sample images (for classification), and region name/score/trend text (for alert generation) | To perform AI classification and text generation |

**None of the above transmissions include personal data**, since none is
collected by the system in the first place. Each provider's own privacy
policy governs their handling of the (non-personal) data sent to them:
- [Copernicus Data Space Terms](https://dataspace.copernicus.eu)
- [OpenAQ Terms](https://openaq.org)
- [Google AI/Gemini API Terms](https://ai.google.dev)

This system does not sell or share data with any party beyond these three
functional dependencies.

## 6. Data Retention

| Data | Retention |
|---|---|
| Ground-station readings in `air_quality.db` | Retained indefinitely as a point-in-time snapshot committed to the project's public GitHub repository; refreshed manually (see [Runbook](./RUNBOOK.md) §9) |
| Satellite summary statistics | Retained as committed evidence files (`data/day1_sentinel_sample.json`) |
| Generated alerts | Not persisted — computed fresh on each API request, not stored |
| Sample citizen photos | Retained in the repository as a fixed demonstration dataset |

## 7. Data Storage & Location

- **Source code and committed data**: GitHub (public repository)
- **Runtime hosting**: Render (United States-based infrastructure, per
  Render's own hosting regions)
- **No separate database service** is used — all persisted data lives in a
  single SQLite file within the deployed application's filesystem/repository

## 8. User Rights

Because this system collects no personal data, standard data-subject rights
(access, deletion, portability, etc. — e.g. under GDPR or similar
frameworks) do not apply in a meaningful sense, as there is no personal data
to access, delete, or port. If this changes in a future version (see
[Section 10](#10-future-data-collection-roadmap)), this policy will be
updated accordingly before that feature is deployed.

## 9. Children's Privacy

This system does not knowingly collect data from anyone, including children,
since it collects no personal data from any user at all in its current form.

## 10. Future Data Collection (Roadmap)

The [Architecture Document](./ARCHITECTURE.md) roadmap and
[PRD](./PRD.md) both note a **live citizen photo upload endpoint** as a
planned future feature, currently out of scope. If implemented, this would
represent a material change to this policy — it would likely involve:
- User-submitted photos (potentially containing incidental personal/location
  information)
- Possibly device or approximate location data, if submissions are
  geotagged

**This policy will be revised, and appropriate consent/disclosure
mechanisms added, before any such feature is deployed** — it will not be
added silently under the current policy's scope.

## 11. Changes to This Policy

This policy will be updated whenever the system's actual data practices
change. Material changes will be reflected in the [CHANGELOG](./CHANGELOG.md).

## 12. Contact

For questions about this policy, contact the project maintainer, Sushant
Garde, via the details in the [README](./README.md).

# Changelog

## Unreleased recording preparation

- Place My Meal Boxes directly below the finder and highlight access in navigation.
- Add visible view, rename, delete, save confirmation, and browser-storage guidance.
- Record the production catalog in four reproducible datasets.
- Update isolated staging to migration 0003.
- Add current AI evaluation, pipeline measurements, and the video demonstration checklist.
- Require frontend/backend checks and one approval on the public repository's main branch.

## v1.0.0

- Recommend meals from recorded menus using a budget and optional English or Tagalog preferences. Preserve explicitly requested sides such as rice.
- Save, view, rename, and delete personal Meal Boxes from the same browser.
- Provide readable messages for invalid requests, AI timeouts, provider failures, and unreadable responses. Visitors can clear the preference field to compare recorded prices.
- Limit write requests to 16 KiB and AI requests to six per client and thirty per backend process per minute.
- Keep CI independent of Groq and remove redundant demo seeding from the pipeline. The seed idempotency test remains in the suite.
- Rehearse rollback to the previous application revision while preserving the database schema and saved boxes. [Verification report](docs/verification/week-4-audit.json)

The original release began with five shops. The current production catalog and its remaining data gaps are documented in the catalog snapshot.

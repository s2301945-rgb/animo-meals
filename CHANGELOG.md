# Changelog

## v1.0.0

- Recommend meals from recorded menus using a budget and optional English or Tagalog preferences. Preserve explicitly requested sides such as rice.
- Save, view, rename, and delete personal Meal Boxes from the same browser.
- Provide readable messages for invalid requests, AI timeouts, provider failures, and unreadable responses. Visitors can clear the preference field to compare recorded prices.
- Limit write requests to 16 KiB and AI requests to six per client and thirty per backend process per minute.
- Keep CI independent of Groq and remove redundant demo seeding from the pipeline. The seed idempotency test remains in the suite.
- Rehearse rollback to the previous application revision while preserving the database schema and saved boxes. [Verification report](docs/verification/week-4-audit.json)

The initial release lists five shops. Real recommendations and Meal Box creation on the public site become available after the shop menus are imported.

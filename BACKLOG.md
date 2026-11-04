# Revised project backlog

The original Week 1 and Week 2 work established deployment, database access and CRUD. Administrator CRUD has been replaced by visitor meal-box CRUD. Old GitHub issue text may describe the earlier scope; use this file for the revision.

## Implemented in this revision

- Visitor budget and preference form; backend AI extraction and deterministic meal combinations.
- Exact decimal budget validation and no invented menu entries.
- Database-backed My Meal Boxes: save, view, rename, delete.
- Browser-key ownership isolation without accounts; stored price snapshots.
- Removal of admin UI, login, upload and catalog write APIs.
- Recorded-menu wording instead of real-time availability claims.
- Validated offline developer dataset import and blank five-shop template.
- API tests with mocked provider calls, migration and updated documentation.

## Next: supplied menu dataset

- Collect regular menu names, prices, categories and confirmed details from the five selected shops.
- Confirm Maria Rosa's location.
- Review dataset spelling and prices, then import into the intended environment.
- Add non-spicy/ingredient descriptions only when verified.
- Try the labeled AI acceptance cases against the real catalog; record limitations and results.

## Release and hardening

- Verify the revised production deployment after passing CI.
- Check real provider behavior through the public interface once affordable menu data exists.
- Measure pipeline timings before/after an optimization.
- Verify rollback, complete final release documentation and tag v1.0.0 with a changelog.
- Evaluate stronger persistent/global abuse limits if the app grows beyond the single-process course deployment.

Optional later: a random choice among saved boxes that fit today's budget. No daily stock tracking, vendor accounts, ordering or payments are planned.

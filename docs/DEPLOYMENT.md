# Deploy the revised recommender

The repository uses Vercel for the frontend, Render for the backend, and Supabase PostgreSQL. Existing GitHub Actions deployment hooks are reused. No new provider account or credential is required for this revision.

## Before merging

- Pass frontend lint/build and backend lint/tests on the pull request.
- Review the additive migration 0003. It creates saved_plans/saved_plan_items with PostgreSQL RLS and preserves menu records.
- Keep DATABASE_URL, GROQ_API_KEY, GROQ_MODEL and FRONTEND_ORIGIN in backend private environment settings.
- Keep VITE_API_BASE_URL pointing to the hosted API; Vite settings are public.
- Do not copy local fixture menus into production. Import only the supplied dataset after reviewing it.

## Automatic publication

After merging to main, GitHub Actions runs checks and triggers the existing private Vercel deployment hook. Render deploys backend changes after checks and runs `python -m app.start_server`, which applies migrations before serving requests. An empty dataset produces empty meal suggestions; this is intentional.

## Verify the release

1. GET /api/environment: check the production environment and backend release commit.
2. GET /api/health: confirm database connectivity.
3. GET /api/stalls and /api/menu-items: check the existing catalog was preserved.
4. Open the public website, check the AI request form and My Meal Boxes, and verify old #admin bookmarks redirect.
5. Confirm /api/admin/auth-config is 404 and public catalog writes are unavailable.
6. With the supplied dataset, request a real AI recommendation; save, rename, reload and delete a meal box. Until data arrives, verify the no-matches response instead.

Existing unused Supabase Auth variables, Auth accounts and old Storage objects are not automatically deleted. They do not enable old endpoints in the revised app. Do not publish `.env.render` or browser ownership keys.

## Main-branch protection

The public repository requires the frontend and backend checks, an up-to-date branch, one approving review, and resolved conversations before merge. Administrators are included. The recording-preparation PR must pass the same rules. [Verified settings](verification/recording-repository-rules.json)

## Supabase Data API configuration

The backend connects directly to PostgreSQL. The disabled Supabase Data API produced repeated missing-schema log entries. On November 20, 2026, the documented empty-schema workaround was applied using pgrst_no_exposed_schemas and the authenticator role's pgrst.db_schemas setting, followed by a PostgREST reload. Database connectivity and public API health passed afterward. Follow Supabase's reversal steps if the Data API is re-enabled. [Supabase troubleshooting guide](https://supabase.com/kb/troubleshooting/schema-pg_pgrst_no_exposed_schemas-does-not-exist)

Frontend/backend free-host cold starts can delay verification. Avoid claiming a successful deployment until the public endpoints and site have been checked.

## Rollback plan

Redeploy the previous verified frontend and backend revisions. Keep database migration 0003 in place to preserve saved boxes. Verify the backend revision, database health, shop listing, and a saved box before restoring the candidate. Downgrading migration 0003 deletes saved boxes.

The Week 4 rehearsal ran the candidate, the previous production backend, and the candidate again against the same isolated database. The shop and saved box survived all three phases. [Rollback and Git history audit](verification/week-4-audit.json)

Historical evidence for the earlier administrator release is retained under docs/verification and in pull requests #20/#21. It does not prove deployment of this revised application.

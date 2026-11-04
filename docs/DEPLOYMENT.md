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

Frontend/backend free-host cold starts can delay verification. Avoid claiming a successful deployment until the public endpoints and site have been checked.

## Rollback plan

Redeploy the previous reviewed application commit on both hosts. Migration 0003 is additive; the earlier app can run with its unused saved-box tables still present. Downgrading that migration deletes saved boxes, so do not downgrade it automatically. A production rollback exercise and final tagged release remain Week 4 work.

Historical evidence for the earlier administrator release is retained under docs/verification and in pull requests #20/#21. It does not prove deployment of this revised application.

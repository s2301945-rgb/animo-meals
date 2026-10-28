# Week 1 deployment

The React frontend runs on Vercel Hobby. The FastAPI backend runs on Render Free,
with the existing Supabase PostgreSQL database and Groq account.

## Verified progress — October 29, 2026

The Render backend is live at https://animo-meals-api.onrender.com. A public
request to `/api/health` returned `status=ok` and `database=connected`.
`/api/menu-items` returned 10 records, and `?budget=75.50` returned 9 records,
all priced at or below PHP 75.50. These are fictional demonstration listings.

[Deployment pull request #15](https://github.com/s2301945-rgb/animo-meals/pull/15)
passed its frontend and backend checks before merge. The frontend hook job was
intentionally skipped while the hook is unconfigured. Render detected the main
branch checks and successfully deployed commit `c9fcac0` automatically
(Render deployment `dep-dbh28sbd9pos73c3huk0`).

The frontend is live at https://animo-meals.vercel.app. The production page loaded
all ten items from the hosted API. Submitting PHP 50 displayed six items, all
within that budget. This also verifies the configured production CORS origin.
The frontend allows 75 seconds for its first menu request so a sleeping Render
service can wake up; users see a loading explanation during that request.

The approved frontend deploy hook is stored as `VERCEL_DEPLOY_HOOK` in GitHub
Actions secrets and `DEPLOYMENT_ENABLED=true` is configured. Production workflow
[40729505099](https://github.com/s2301945-rgb/animo-meals/actions/runs/40729505099)
successfully ran frontend checks, backend checks, and the deploy job in that order.
Vercel deployment `9EG5yPo8pngE85u4hbT1crAiJ5rL` is Ready and identifies Deploy Hook
as its creator for the same `c105cca` commit. The public menu and PHP 50 filter
were checked after release; CORS matched the frontend origin and an invalid
negative budget returned HTTP 422. No credentials are included in this evidence.

## Backend

Connect the GitHub repository in Render and create a Python web service:

| Setting | Value |
| --- | --- |
| Branch | `main` |
| Root directory | `backend` |
| Build command | `pip install -r requirements.txt` |
| Start command | `python -m app.start_server` |
| Health check | `/api/health` |
| Auto-deploy | After CI Checks Pass |
| Plan / region | Free / Singapore |

Set `PYTHON_VERSION=3.13.15` and `APP_ENV=production`. Privately configure
`DATABASE_URL`, `GROQ_API_KEY`, `GROQ_MODEL`, and `FRONTEND_ORIGIN` (the exact
HTTPS production frontend origin, without a trailing slash).

The startup command applies committed Alembic migrations before starting the API
on Render's assigned port. It refuses a local database or HTTP frontend origin in
production. Migration failures stop startup without printing connection details.
Demonstration data is maintained in Supabase; startup does not replace it.
The root `render.yaml` records equivalent service settings for future setup.

## Frontend

Import this repository into Vercel with root directory `frontend`, framework
Vite, build command `npm run build`, and output directory `dist`.
Set `VITE_API_BASE_URL` to the actual HTTPS Render service URL.
Only this public API address belongs in frontend environment settings.

For a GitHub Actions deployment, create a Vercel deploy hook for `main`, save its
URL privately as the GitHub Actions secret `VERCEL_DEPLOY_HOOK`, and set repository
variable `DEPLOYMENT_ENABLED=true`. The deployment job runs only on `main` pushes
after both application check jobs succeed. Keep the flag unset until the hook is
configured. Never commit the hook URL.

`frontend/vercel.json` disables automatic commit-triggered Vercel deployments;
GitHub Actions uses the approved deploy hook after its checks instead. This
avoids publishing a production commit before validation finishes.

## Consultation evidence

Before closing the deployment issue, record the actual public URLs and verify:

- GitHub PR checks install, lint, build, migrate, and test successfully.
- The production pipeline triggers a successful hosting deployment.
- `/api/health` reports a connected database.
- `/api/menu-items` returns the existing demonstration items.
- The public frontend loads those items, including the budget filter.
- Frontend CORS access matches the actual deployed frontend origin.

Free Render services may sleep when idle. The frontend should be checked before
the consultation to allow the API to wake up. Hosting setup is complete only
after the live checks above pass.

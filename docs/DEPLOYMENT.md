# Week 1 deployment

## Week 2 live verification — October 31, 2026

[PR #20](https://github.com/s2301945-rgb/animo-meals/pull/20) merged and the
[main pipeline](https://github.com/s2301945-rgb/animo-meals/actions/runs/41171535799)
passed all three jobs: frontend, backend and deployment trigger. Its test report
contains 120 passing tests. The live Render `/api/environment` response matched
merge `e56da872116fb5ae41c5f02651c157ef4f0e9e67`, and `/api/health` confirmed PostgreSQL.

The [public frontend](https://animo-meals.vercel.app) now displays the five selected
shops, with empty menus ready for real data. The original three fictional shops
and sixteen menu items were backed up privately before the tested replacement.
Admin sign-in configuration matches the verified project; anonymous writes are
blocked. Live browser, mobile, CORS and malformed-budget checks passed. The
developer also confirmed successful private sign-in to the public admin dashboard. Non-secret results:
[Week 2 production evidence](verification/week-2-production.json).

## Week 2 rollout procedure

Week 2 is prepared in pull request #20. Before merging, add the verified local
`SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY` and `ADMIN_USER_ID` to Render's private
Environment settings. The ignored `backend/.env.render` file contains only those
three settings for bulk import; it does not contain the database password or Groq
key. Existing production database/Groq values remain unchanged. The committed
`render.yaml` declares equivalent placeholders.

The production catalog is backed up privately by `python -m app.publish_catalog`
without changing records. After the merged backend/frontend deploy successfully,
`python -m app.publish_catalog --apply` removes only recognized fictional demo
shops/items and adds missing selected shops without inventing meals or overwriting
existing real-shop records. Unknown data under a demo shop stops this operation.
The original backup stays in ignored `backend/.production-backups/`.

Merge only a passing, reviewed PR head. The main-branch pipeline runs checks and
triggers the existing Vercel deployment hook; Render deploys main after CI passes.
Backend startup applies nullable image migration `0002` before listening.
Verify `/api/environment` reports `production` and the actual merged commit SHA
from Render's `RENDER_GIT_COMMIT`, `/api/health` confirms the database, public shop
and menu reads work, CORS matches the public frontend, and anonymous mutations
remain unauthorized. Then verify the public UI and admin sign-in configuration.

This section describes the rollout procedure; it is not evidence that Week 2
has already been deployed. Final verification must be recorded after deployment.

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

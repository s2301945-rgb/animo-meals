# Pipeline and release process

## Gates and deployment

Feature branches target protected `main` through pull requests. Required checks are `frontend` and `backend`; the branch must be current, review conversations resolved, and administrators follow the same rules. Required human approvals are zero under the instructor-confirmed solo-developer exception. See [rules evidence](docs/verification/recording-repository-rules.json), [Meal Box PR 30](https://github.com/s2301945-rgb/animo-meals/pull/30), and [cover PR 31](https://github.com/s2301945-rgb/animo-meals/pull/31).

The [workflow](.github/workflows/ci.yml) runs frontend dependency installation, ESLint and Vite build alongside backend dependency installation, Ruff, compilation, Alembic migration and Pytest. CI uses isolated SQLite and mocked provider calls, not paid live AI. It uploads the JUnit report as `api-test-results`. Main pushes repeat checks before calling a private Vercel deployment hook. Render deploys backend changes after successful checks; `app.start_server` verifies the environment and migrates before serving.

## Measured timings

Historical comparison: [before run](https://github.com/s2301945-rgb/animo-meals/actions/runs/42041966473), [after run](https://github.com/s2301945-rgb/animo-meals/actions/runs/42042961394), [measurement JSON](docs/verification/recording-ci-timings.json).

| Measurement | Before | After |
| --- | --- | --- |
| npm install step | 4 s | 2 s |
| Frontend job | 15 s | 14 s |
| Backend job | 24 s | 25 s |
| Parallel job span | 24 s | 26 s |
| Demo-seed invocations | 2 | 0 |

npm installation fell 50%; overall parallel span rose 8.3%. These are two historical runs with differing work, not a controlled benchmark or evidence that the whole pipeline became faster. Caching is configured, npm audit/funding prompts are omitted from CI install, and redundant demo seeding was removed. There is no automated dependency-vulnerability scanner configured; the current secret scan is a separate manual check.

Current application baseline [run 45866255836](https://github.com/s2301945-rgb/animo-meals/actions/runs/45866255836) passed 110 tests, zero failures/errors/skips. Frontend took 12 s and backend 19 s; the deploy-hook job took 12 s. Job timestamps are in [current audit](docs/verification/final-project-audit.json). The measured deploy-hook duration does not include the full Vercel or Render deployment time. No long-term pipeline success rate is claimed.

## Environments and recovery

Production uses Vercel, Render and Supabase PostgreSQL. [Local staging](STAGING.md) has a restricted role/schema in the same Supabase project. Private environment files and dashboard variables hold keys and connection strings; Vite configuration is public. Runtime logs are available in the hosting dashboards, `/api/health` checks database connectivity, and `/api/environment` exposes backend revision. There is no separate analytics, uptime alerting or error-tracking service.

Release v1.1.0 identifies application source 8e5cf398f04c38a94583b61e83190686c683db48. The earlier v1.0.0 tag points to an older release. Roll back only to a verified quantity-aware backend/frontend while retaining migration 0004. A pre-0004 backend ignores quantities and is incompatible with edited boxes. The candidate/rollback/restore rehearsal in [historical audit](docs/verification/recording-audit.json) preserved catalog and saved records at schema 0003; it does not prove rollback of the new quantity feature. A fresh hosting rollback rehearsal for 0004 remains pending. Do not downgrade 0003 in production because it removes saved boxes.

## Recording

The developer supplied [this consultation recording folder](https://drive.google.com/drive/folders/1ZKTryG_lfVrOrqRCASA8FN6cy-cjMOjb). A screenshot shows `AI consultation.mp4`; connector access returned not found. Public/panel access, exact video URL, uninterrupted deployment-challenge coverage and lack of edits have not been verified. This link is submitted as provided, not as proof of a reviewed recording. The [recording checklist](docs/RECORDING.md) is guidance, not the recording itself.

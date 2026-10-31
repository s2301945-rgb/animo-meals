# Local staging environment

Staging is a separate local site backed by an isolated PostgreSQL schema and
restricted database role in the existing Supabase project. It is not a public
staging deployment or a second Supabase project. Production stays on its current
public URLs until Task 6 is approved.

| Environment | Frontend | Backend | Data | Photos |
| --- | --- | --- | --- | --- |
| Development preview | `http://127.0.0.1:5175` | `http://127.0.0.1:8001` | Existing local SQLite preview | `animo-meals-images` |
| Staging | `http://127.0.0.1:5177` | `http://127.0.0.1:8003` | Supabase schema/role `animomeals_staging` | `animo-meals-images-staging` |
| Production | `https://animo-meals.vercel.app` | `https://animo-meals-api.onrender.com` | Supabase `public` schema | `animo-meals-images`, when Week 2 is deployed |

Staging and production share the same Supabase Auth project and permitted admin
account. Data credentials, schemas and staging photo bucket are separate. This
is environment separation within one project, not complete account/infrastructure
isolation. Staging has an empty Groq key; it does not make live AI requests.

## Open staging

While the staging launcher is running, visit:

- [Staging shops](http://127.0.0.1:5177/#shops)
- [Staging administrator](http://127.0.0.1:5177/#admin)
- [Staging health](http://127.0.0.1:8003/api/health)

The yellow **STAGING** banner distinguishes it from the regular local preview.
Use your existing AnimoMeals admin account to sign in. Edits here affect staging
records only. It initially contains the five selected shops with no menus; do
not assume administrator-entered development records are also in staging.

## Start or stop later

From the repository folder:

```powershell
backend/.venv/Scripts/python.exe scripts/run_staging.py
```

Keep that terminal running. Ctrl+C stops both staging services. Development and
production remain independent. If a staging port is already in use, the launcher
stops rather than killing an unrelated process. Logs are in ignored `.staging-run/`.
The launcher removes inherited data/provider overrides before loading staging's
files, so a development `DATABASE_URL` cannot silently replace staging settings.

## Configuration and first-time setup

The actual backend `.env.staging` is ignored by Git and contains a generated
password for the restricted staging role. Frontend `.env.staging` contains only
the public local backend URL and `VITE_APP_ENV=staging`. The committed
`.env.staging.example` files are placeholders and contain no credentials.

On the configured laptop, initial setup is already done. To reproduce it with
your own configured Supabase project, from `backend` and using the existing
private privileged setup connection:

```powershell
.venv/Scripts/python.exe -m app.setup_staging
.venv/Scripts/python.exe -m app.setup_image_storage --staging
```

The setup creates a login role with no superuser, database-creation, role-creation,
replication or RLS-bypass privileges, and grants it CREATE/USAGE on the staging
schema only. Existing staging configuration is retained; credentials are not
rotated on rerun. No production menu records are copied or changed.

`ANIMOMEALS_ENV_FILE=.env.staging` selects staging backend settings. The backend
then uses that role's connection and sets its search path to the staging schema.
Before migrating or listening, staging startup checks the configured and actual
role/schema and the staging photo bucket. Production startup rejects staging
schema/bucket settings. The staging frontend checks `/api/environment` before
loading data or enabling sign-in and refuses a non-staging backend.

## Verified on October 31, 2026

- Connected through the restricted staging role and schema.
- Applied Alembic revision `0002` inside that schema.
- Seeded five shops and zero menu items, without fictional meals.
- A direct read of the production shop table was denied with PostgreSQL 42501.
- Created a staging test row, verified it, then rolled the transaction back.
- Production counts before and after remained three shops and sixteen menu items.
- Browser checked the banner, shop listings, empty menus, enabled sign-in
  configuration, and rejection of a mismatched production backend.
- Backend suite: 116 tests pass; frontend lint and production build pass.

Non-secret verification is saved locally as `outputs/week-2-staging-verification.json`
in the task workspace. The shared identity provider and public staging-hosting
limitation remain explicit; a hosted preview is not claimed.

References: [Supabase connections and custom pooler roles](https://supabase.com/docs/guides/database/connecting-to-postgres)
and [PostgreSQL schemas and privileges](https://www.postgresql.org/docs/17/ddl-schemas.html).

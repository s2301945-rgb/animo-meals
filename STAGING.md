# Local staging

The existing staging setup uses a restricted PostgreSQL role/schema `animomeals_staging` inside the same Supabase project. It has its own ignored `.env.staging`, database records and browser meal-box key (the key is namespaced by API URL). This is schema/role isolation, not a separate Supabase project. There is no public staging URL.

From the repository root:

```powershell
backend/.venv/Scripts/python.exe scripts/run_staging.py
```

Open http://127.0.0.1:5177. Backend: http://127.0.0.1:8003. Ctrl+C stops both. Logs are in ignored `.staging-run/`. The yellow STAGING banner and backend identity check prevent silently using production. The launcher applies migrations to the staging schema. No administrator sign-in is involved.

First-time provisioning, from `backend` using the existing private privileged PostgreSQL connection:

```powershell
.venv/Scripts/python.exe -m app.setup_staging
```

Existing staging settings are retained. The startup identity/schema guard remains; the legacy staging image-bucket setting is retained for compatibility with provisioned environments, but the app no longer uploads images. Historical Auth settings in private files are ignored.

Staging's Groq key is empty by default. Test price-only requests, saved-box CRUD and empty-menu behavior there. Text AI requires an intentionally configured staging provider key. To import real menu data into staging only:

```powershell
$env:ANIMOMEALS_ENV_FILE='.env.staging'
.venv/Scripts/python.exe -m app.import_menu data/menu-template.json
# Add --apply only after reviewing the dataset and environment.
```

The importer does not copy production data or overwrite locations/photos. Production and development are separate environments; no claim is made that a user-entered local test menu is present elsewhere.

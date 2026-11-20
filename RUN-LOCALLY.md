# Run AnimoMeals locally

Commands below use PowerShell. Open the repository folder in VS Code.

## Backend

```powershell
cd backend
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe -m alembic upgrade head
.venv/Scripts/python.exe -m app.shop_catalog
.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Without a private `.env`, the app uses local SQLite. An existing `.env` may point to Supabase; check the intended environment privately before importing data or applying migrations. The five selected shops start with blank menus. Do not run the old `app.seed` against production: it creates fictional demonstration menus for tests only.

## Frontend

Open a second terminal from the repository root:

```powershell
cd frontend
npm.cmd ci
npm.cmd run dev
```

Open http://localhost:5173. API documentation: http://localhost:8000/docs. Stop servers with Ctrl+C.

The frontend defaults to `http://localhost:8000`. Configure `VITE_API_BASE_URL` in an ignored frontend `.env` if needed. Match the backend's `FRONTEND_ORIGIN` to the website's exact origin. Vite variables are public; database passwords and Groq keys belong only on the backend.

## Try the revision

1. Browse the selected shops. A fresh local database begins with five empty shop menus.
2. Enter a budget and request suggestions. An empty catalog returns a clear message and makes no AI call.
3. Import the reviewed snapshots using [MENU-DATA.md](docs/MENU-DATA.md). The four files are campus-menu.json, la-salle-delivery-menu.json, potato-corner-menu.json, and unnamed-rice-bowls.json under backend/data. Together they reproduce the recorded nine-shop, 28-item catalog.
4. Try a budget-only request, then a request with preferences using the privately configured Groq key.
5. Save a suggestion, open My Meal Boxes, rename it, reload, and delete it.
6. Open a separate browser profile: the first profile's meal boxes must not appear there.

No admin account, publishable-key setup window or administrator password is needed.

## Checks

From `backend`:

```powershell
.venv/Scripts/python.exe -m ruff check .
.venv/Scripts/python.exe -m pytest -q
```

From `frontend`: `npm.cmd run lint` and `npm.cmd run build`.

Tests use isolated SQLite and mocked AI responses. They do not consume live Groq quota or modify the hosted catalog. [Staging instructions](STAGING.md) describe the separate local PostgreSQL environment.

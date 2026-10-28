# Run AnimoMeals on your laptop

## What works now

React displays menu records read from a database by FastAPI. You can search food/stalls, filter categories, and request individual items within a budget. The sample stalls, prices, and locations are fictional. A backend-only Groq extraction function and verification command are available; frontend AI and meal-combination recommendations are not implemented yet. See AI-SETUP.md.

Local development uses a real SQLite file, `backend/animomeals.db`, so no cloud account is required to try the app. Supabase PostgreSQL remains the planned deployment database. Both use the same SQLAlchemy models and Alembic migration; the original laptop now has a verified Supabase connection configured in its ignored backend/.env file.

## 1. Open the project

Open this repository folder in VS Code. Select **Terminal → New Terminal**. All commands below are PowerShell commands from the repository root unless indicated otherwise. Close/reopen VS Code after installing Node.js and Python.

## 2. Start the backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m app.seed
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Leave this terminal running. API docs: http://localhost:8000/docs

The virtual environment and initial local database have already been created on the original laptop. Running the migration and seed again is safe. Existing menu records are not overwritten by the seed command.

## 3. Start the frontend

Open a second terminal at the repository root:

```powershell
cd frontend
$env:NODE_USE_SYSTEM_CA = '1'
npm.cmd ci
npm.cmd run dev
```

Open **http://localhost:5173**. Keep both terminals running. Use **Ctrl+C** in each to stop.

The certificate setting uses Windows trusted certificates for npm requests on this laptop; HTTPS certificate verification remains enabled.

## 4. Try the working flow

1. Check that ten demonstration items load from the backend.
2. Enter a budget of `75` and select **Find food**.
3. Choose a category or search for `chicken`.
4. Clear search, choose **All items**, and clear the budget to restore every item.
5. Enter `1` as the budget to verify the empty-results message.

## Configuration

The backend loads `backend/.env` if present. Without it, it uses local SQLite. Do not copy the example PostgreSQL placeholder into `.env` unless you are ready to enter your real database settings.

The frontend defaults to `http://localhost:8000`. Override it with `VITE_API_BASE_URL` in `frontend/.env`. The backend allows the origin configured by `FRONTEND_ORIGIN` (default `http://localhost:5173`). Restart servers after changing configuration.

For Supabase, use its supplied connection method with the psycopg driver, configure SSL as required, then run the same migration and seed commands against that database. Do not commit passwords or API keys. An AI key is not needed for menu browsing. The Groq smoke test requires its own backend key.

## Checks

Frontend: `npm.cmd run lint` and `npm.cmd run build` from `frontend`.

Backend: `.\.venv\Scripts\python.exe -m ruff check .` and `.\.venv\Scripts\python.exe -m pytest -q` from `backend`.

GitHub Actions runs install, lint, frontend build, backend import checks, migration/seed smoke checks, and API tests on pull requests to main. CI does not contact an AI provider.

## Still required for Week 1

- Supabase PostgreSQL was configured and verified on the original laptop; new checkouts need their own private configuration.
- Verify one real Groq request from the backend using AI-SETUP.md.
- Deploy a live frontend/backend through a pipeline after successful checks.
- Collect consultation evidence. A running local app alone does not satisfy the live URL requirement.

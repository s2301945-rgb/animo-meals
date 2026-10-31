# Week 2, Task 1: CRUD API and request validation

Local implementation on `feature/week-2-admin-crud`. Not deployed yet.
Existing production menu data has not been changed. The admin UI is a separate,
unverified draft; completing Task 1 does not claim Week 2 is complete.

## Endpoints

| Method | Path | Access | Purpose |
| --- | --- | --- | --- |
| GET | `/api/stalls` | Public | List shops, including shops without menu items |
| GET | `/api/stalls/{id}` | Public | Read one shop |
| POST | `/api/stalls` | Admin | Create a shop |
| PUT | `/api/stalls/{id}` | Admin | Replace a shop's editable fields |
| DELETE | `/api/stalls/{id}` | Admin | Delete an empty shop |
| GET | `/api/menu-items` | Public | List menus with shop names/locations; optional budget |
| GET | `/api/menu-items/{id}` | Public | Read one menu record |
| POST | `/api/menu-items` | Admin | Create a menu item |
| PUT | `/api/menu-items/{id}` | Admin | Replace a menu item's editable fields |
| DELETE | `/api/menu-items/{id}` | Admin | Delete a menu item |
| GET | `/api/admin/me` | Admin | Verify administrator authorization |
| GET | `/api/admin/auth-config` | Public | Return only Supabase URL and publishable/anon key |

FastAPI also exposes request/response schemas at `/docs`. Successful creates
return 201, updates/reads 200, and deletes 204 with no response body. PUT requires
the editable fields; it is not a partial update.

## Validation and data integrity

- Shop names: trimmed, 1–100 characters. Locations: trimmed, 1–200 characters.
- Duplicate shop names, ignoring letter case, return 409 in normal CRUD requests.
- Menu names: trimmed, 1–120 characters; optional descriptions up to 2,000 characters.
- Prices: greater than zero, at most PHP 10,000, at most two decimal places.
  Use decimal strings such as `"65.50"` in requests. Decimal arithmetic and database
  Numeric columns preserve centavo precision.
- Categories: `Main dish`, `Drink`, `Snack`, or `Side`.
- Availability must be a JSON boolean. It represents an administrator's listing
  status, not automated stock detection.
- Shop IDs must be positive integers and reference an existing shop.
- Missing/invalid inputs, malformed JSON and unexpected fields return 422.
- Missing records return 404. A shop with menu items returns 409 on deletion;
  move/delete its items first. Database foreign keys provide a second safeguard.
- Failed validation does not change existing records. Database conflicts roll
  back and return a safe 409; database outages return a safe 503.
- Public menu responses now include `stall_id` so editors can select the actual
  related shop, while retaining the existing public response fields.

## Administrator authorization

All writes require `Authorization: Bearer <Supabase access token>`. The backend
verifies the token using Supabase Auth's `/auth/v1/user` endpoint over HTTPS and
compares the returned identity with the configured `ADMIN_USER_ID`. Client-supplied
roles and metadata cannot grant administrator access. Missing/expired credentials
return 401; authenticated non-admins receive 403. Provider failures return 503.

Supabase settings must be configured before a real administrator can sign in:

1. Create the administrator's Supabase Auth account through the dashboard.
2. Configure `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, and `ADMIN_USER_ID` in
   private backend settings; see `backend/.env.example` for placeholders.
3. Use a publishable or legacy anon key only. Secret/service-role keys are rejected
   by the public configuration endpoint. Database/provider secrets remain private.
4. Keep the existing Data API restrictions and table RLS. The backend uses its
   existing database connection; public visitors cannot call protected writes.

Without these settings, public browsing works and administrator operations fail
closed. No temporary administrator bypass or hardcoded password is supplied.
Live login and hosting configuration remain unverified at this stage.

Auth protocol reference: [Supabase Auth OpenAPI specification](https://github.com/supabase/auth/blob/master/openapi.yaml).

## Verification

From `backend`, run Ruff and Pytest with a temporary test database setting:

```powershell
$env:DATABASE_URL = 'sqlite://'
.venv/Scripts/python.exe -m ruff check .
.venv/Scripts/python.exe -m pytest -q
```

CRUD tests use disposable SQL tables with foreign keys enabled. Only the remote
identity provider is mocked; tests exercise the real routes, validation, writes,
reads, updates, deletes, authorization decisions and error handling. They never
call live Supabase Auth, Groq or the production database. Live PostgreSQL and admin
UI verification are separate remaining steps.

## Task 2: shop/menu relationship in visitor features

Implemented and checked locally after Task 1:

- Shop cards load from `/api/stalls`, including shops with no menu items yet.
- Shop selection uses `stall_id`, not a shop's display name. Meals remain linked
  to the same shop after a rename or location change.
- A selected-shop banner shows the shop name and location above its menu.
- Budget/category/search filters apply within the selected shop. Card summaries
  use the complete catalog, so entering a budget does not shrink shop totals.
- Empty shops show `Menu not added yet` and a dedicated empty-menu message;
  they do not display invented meals, prices, or an invalid minimum price.
- Returning to all shops clears shop selection. Selecting another shop's card
  resets the previous menu filters so the visitor can see its complete menu.

Verification: 98 backend tests pass; frontend lint/build pass. A local headless
browser checked shop/location mapping, budget-plus-shop filtering, full shop
counts, an empty shop, resetting selection, and a 390-pixel mobile viewport.
No JavaScript page errors were observed. Preview uses a separate SQLite demo
database, including one explicitly fictional empty shop; production is unchanged.

The administrator form's shop selector remains part of the Task 3 draft. Real
administrator login and UI editing have not been verified yet.

## Later tasks require the developer's approval

1. Complete and verify the administrator screens and real sign-in configuration.
2. Confirm the expanded API tests run in GitHub Actions.
3. Set up an isolated preview/staging environment.
4. Verify successful merges deploy automatically.

Real shop/menu datasets are pending. Do not assign fictional meals or prices to
Maria Rosa, Pritong Manok, Nene's, Crazy Crunch, or Lola Barbz.

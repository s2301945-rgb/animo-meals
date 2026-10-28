# AnimoMeals GitHub Issues

Status: prepared locally; these issues have not been created on GitHub. All tasks below start incomplete.

## 1. Set up repository foundation

Target: Week 1. Declare solo development responsibilities and establish repository conventions.

- [ ] README documents scope, developer roles, stack, setup, and branch strategy.
- [ ] Root `.gitignore` excludes credentials, dependencies, and generated files.
- [ ] Frontend and backend `.env.example` files are committed without secrets.
- [ ] This backlog is converted into GitHub Issues with acceptance criteria.
- [ ] Feature changes use branches and pull requests into `main`.

## 2. Implement relational database and migration

Target: Week 1. Requirement: real database and at least two related tables.

- [ ] Configure PostgreSQL connection through backend environment variables.
- [ ] Define `stalls`: id, name, location, created_at.
- [ ] Define `menu_items`: id, stall_id, name, description, price, category, is_available, updated_at.
- [ ] Add a foreign key from menu_items.stall_id to stalls.id.
- [ ] Use decimal prices and a nonnegative-price constraint.
- [ ] Commit an Alembic migration and successfully run `alembic upgrade head` on an empty database.
- [ ] Provide a repeatable seed process for three fictional stalls and ten demonstration menu items without duplicate records on rerun.

## 3. Build database-backed menu API

Target: Week 1. Requirement: separate REST backend.

- [ ] FastAPI exposes `GET /api/menu-items`.
- [ ] Response includes item name, price, category, availability, stall name, location, and update timestamp.
- [ ] Data comes from PostgreSQL, not a hardcoded response.
- [ ] Configure allowed frontend origins.
- [ ] Return safe errors without exposing database credentials or stack traces.

## 4. Build minimal frontend menu page

Target: Week 1. Requirement: functional frontend connected to backend. Depends on issue 3.

- [ ] Scaffold React with Vite and plain CSS.
- [ ] Read the backend address from VITE_API_BASE_URL.
- [ ] Fetch menu items from FastAPI and display prices in Philippine pesos.
- [ ] Display stall details, availability, and update timestamps.
- [ ] Include loading, empty, and failure states with a retry action.
- [ ] Clearly label fictional menus as demonstration data.
- [ ] Verify the page is usable on a narrow mobile screen.

## 5. Verify one backend Gemini request

Target: Week 1. Requirement: confirm AI provider credentials work.

- [ ] Configure an actual Gemini key and supported model only in the backend environment.
- [ ] Make one real request from a backend command or restricted development tool.
- [ ] Confirm a successful provider response for a sample budget extraction request.
- [ ] Handle missing credentials, timeouts, and provider errors clearly.
- [ ] Record redacted evidence of success; never include the key.
- [ ] Do not expose an unrestricted public AI test endpoint.

## 6. Add pull-request CI checks

Target: Week 1. Requirement: install, lint, and build on every pull request.

- [ ] GitHub Actions runs on pull requests targeting main.
- [ ] Install frontend dependencies from a committed lockfile, lint, and build.
- [ ] Install backend dependencies, lint, and validate application imports.
- [ ] Run relevant backend tests, including database/API behavior when implemented.
- [ ] CI uses temporary test settings and never calls the paid/live AI provider.
- [ ] A sample pull request shows passing checks.

## 7. Deploy and verify live walking skeleton

Target: Week 1. Requirement: deployment triggered by pipeline. Depends on issues 2–6.

- [ ] Configure frontend hosting, backend hosting, and persistent PostgreSQL.
- [ ] Store production secrets in deployment settings or GitHub secrets.
- [ ] Apply the schema migration to the deployment database.
- [ ] Trigger deployment from the pipeline after successful main-branch checks.
- [ ] Configure deployed API URL and allowed frontend origin.
- [ ] Verify the live frontend retrieves database records through the live backend.
- [ ] Add live URLs, passing PR check link, migration evidence, and deployment evidence to README.
- [ ] Confirm the AI call evidence from issue 5 is available for consultation.

## 8. Implement authenticated administrator CRUD

Target: After Week 1. Requirement: real database CRUD.

- [ ] Implement administrator authentication and backend authorization.
- [ ] Build create, read, update, and delete operations for stalls and menu items.
- [ ] Validate required fields, prices, categories, and foreign keys.
- [ ] Define safe behavior when deleting a stall with menu items.
- [ ] Verify unauthorized users cannot modify records.

## 9. Implement structured preference extraction

Target: After Week 1. Requirement: non-trivial AI feature.

- [ ] Extract budget, food preference, drink requirement, exclusions, and same-stall preference.
- [ ] Validate output against a defined schema before using it.
- [ ] Treat missing or ambiguous details as reviewable fields rather than inventing facts.
- [ ] Let the student review or correct extracted preferences.
- [ ] Reject invented menu data and handle malformed output.
- [ ] Evaluate extraction against manually labeled sample requests.

## 10. Calculate meal recommendations

Target: After Week 1. Core application behavior.

- [ ] Use available database menu items and recorded prices only.
- [ ] Calculate totals with decimal arithmetic, never model-generated prices.
- [ ] Return up to three distinct matching combinations within budget.
- [ ] Show itemized cost, stall location, remaining budget, and matching preferences.
- [ ] Explain no-match results and require user choice before relaxing preferences.
- [ ] Verify exact-budget boundaries and unavailable-item handling.

## 11. Complete error handling and secrets review

Target: Begin Week 1; complete with final features. Requirements: secure configuration and robust errors.

- [ ] Validate malformed requests, empty input, and invalid budgets.
- [ ] Handle AI rate limits, timeouts, invalid responses, and unavailable database connections.
- [ ] Return safe messages and useful HTTP status codes.
- [ ] Keep provider keys and database credentials out of browser bundles, Git, screenshots, and logs.
- [ ] Document environment variables and recovery steps.
- [ ] Keep manual budget/preference entry usable when AI is unavailable.

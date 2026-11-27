# AnimoMeals Final Technical Documentation

Project and section: AnimoMeals AI Food Budget Recommender | CSP221A | BSCS 4B

Member and roles: Lance Francis M. Gargaritano, solo developer and sole DevOps Engineer; frontend, backend, database, AI integration and QA.

Evidence: [Repository](https://github.com/s2301945-rgb/animo-meals) | [Production](https://animo-meals.vercel.app) | [v1.1.0](https://github.com/s2301945-rgb/animo-meals/releases/tag/v1.1.0) | source 8e5cf398f04c. Verified November 27, 2026.

## 1  Product status and architecture

Users and problem: Students compare recorded meals near La Salle against a PHP budget and optional food preferences, then save and customize their own Meal Boxes.

Working: database CRUD, real AI extraction, validated API, menu browsing and public deployment. The former pharmacy/canteen pitch evolved into a curated budget recommender without administrators or live-stock claims. Data completeness remains partial.

Flow: browser on Vercel calls FastAPI on Render; the backend alone accesses Supabase PostgreSQL and Groq, validates preferences, selects recorded meals and calculates decimal totals. [Architecture diagram](https://github.com/s2301945-rgb/animo-meals/blob/main/docs/ARCHITECTURE.md).

## 2  Technology and dependency disclosure

Exact package versions and sources: [frontend lockfile](https://github.com/s2301945-rgb/animo-meals/blob/main/frontend/package-lock.json), [backend pins](https://github.com/s2301945-rgb/animo-meals/blob/main/backend/requirements.txt) and [technology disclosure](https://github.com/s2301945-rgb/animo-meals/blob/main/docs/TECHNOLOGY.md). No embeddings, vector database, RAG, UI component library or active external authentication provider.

| Area | Disclosure |
| --- | --- |
| Frontend and UX | JavaScript, HTML/CSS, React/React DOM 19.3.1, Vite 7.3.7; custom CSS and inline SVG. Node 24 in CI; Vercel Hobby hosting. [Frontend](https://github.com/s2301945-rgb/animo-meals/blob/main/frontend/package-lock.json). |
| Backend and API | Python 3.13.15 configured on Render Free; FastAPI 0.162.0, Uvicorn 0.54.0, Pydantic 2.14.1, HTTPX 0.28.1. [Pinned dependencies](https://github.com/s2301945-rgb/animo-meals/blob/main/backend/requirements.txt). |
| Database and auth | Supabase PostgreSQL 17 family; SQLAlchemy 2.0.55, Psycopg 3.3.6, Alembic 1.20.1. SQLite in isolated tests. Browser bearer keys; Supabase Auth is retired. Current server patch version was not re-read. |
| AI and data tools | Groq chat-completions API, openai/gpt-oss-20b, strict JSON-schema extraction. Offline reviewed JSON imports; no embeddings, RAG, vector search or tool-calling agent. |
| DevOps and quality | Git/GitHub and Actions; Pytest 9.2.0, Ruff 0.17.3, ESLint 9.39.5, Vite build. Manual Chrome/Playwright checks. Render/Vercel logs and health endpoint; no dedicated analytics/APM. |
| Services and costs | Free host tiers and Groq free access; assistant subscription/billing not audited. Groq published limits: 30 RPM, 1,000 RPD, 8,000 TPM, 200,000 TPD for this model; account limits may differ. Render: 750 free hours/month, idle sleep; Supabase: 500 MB database. [Provider references](https://github.com/s2301945-rgb/animo-meals/blob/main/docs/TECHNOLOGY.md). |

## 3  Data model API and user workflow

Data: stalls.id links to menu_items.stall_id; saved_plans.id links to saved_plan_items.plan_id. Snapshots retain unit prices and quantities; the optional menu reference uses SET NULL. Alembic 0001-0004 persists changes; 0004 preserves old boxes as quantity one. [Schema and ERD](https://github.com/s2301945-rgb/animo-meals/blob/main/docs/SCHEMA.md).

API: GET /api/stalls and /api/menu-items browse; POST /api/recommendations accepts budget and text. POST/GET /api/plans and GET/PUT/DELETE /api/plans/{id} implement visitor CRUD with browser-key authorization. Inputs and totals are validated server-side. [API reference](https://github.com/s2301945-rgb/animo-meals/blob/main/docs/API.md).

CRUD: save a suggestion; view it; edit its name, budget, meals and quantities; reload to confirm persistence; delete it. Production browser checks exercised this flow with a temporary box and removed it. [Release verification](https://github.com/s2301945-rgb/animo-meals/blob/main/docs/verification/final-project-audit.json) and [implementation PR 30](https://github.com/s2301945-rgb/animo-meals/pull/30).

Implementation and Verification

## 4  AI feature design output processing and evidence

Task: Groq interprets multilingual, informal meal requests and clear typos into typed budget, food, drink, spice, same-shop and exclusion preferences. This language interpretation is the AI task; deterministic database matching and money arithmetic remain in the backend.

Processing: a system prompt and strict JSON schema request structured output from openai/gpt-oss-20b (no immutable provider snapshot recorded). Pydantic validates it; the backend rejects conflicting budgets and selects up to six real catalog combinations. [Prompt and parser](https://github.com/s2301945-rgb/animo-meals/blob/main/backend/app/ai.py); [selection logic](https://github.com/s2301945-rgb/animo-meals/blob/main/backend/app/recommendations.py).

Evaluation: 5/5 production examples passed on November 27: English, Tagalog, Hiligaynon, Bisaya and a typo. Acceptance required HTTP 200, nonempty recorded options, exact totals and total no greater than PHP 100. This small smoke set is not a general accuracy benchmark. [Prompts and measured results](https://github.com/s2301945-rgb/animo-meals/blob/main/docs/verification/final-ai-evaluation.json).

Risks and fallback: Schema validation cannot prove interpretation accuracy. Provider requests time out after 30 seconds, have no automatic retries and cap output at 2,048 tokens. Quota, timeout and invalid-output failures show safe messages. Blank preferences compare recorded prices without Groq; empty affordable catalogs also skip AI.

## 5  Security data protection and reliability

Secrets stay in ignored backend environment files and private host settings; Vite variables are public. No credentials are included here. A current Git-history scan found zero matches across 296 reachable blobs; this is not a complete vulnerability audit. [Example configuration](https://github.com/s2301945-rgb/animo-meals/blob/main/backend/.env.example); [scan evidence](https://github.com/s2301945-rgb/animo-meals/blob/main/docs/verification/final-secret-scan.json).

Access and data: A random 32-byte browser key authorizes boxes; only its SHA-256 hash is stored. All box routes filter ownership and PostgreSQL RLS remains enabled. Anyone using the same browser can access its boxes; clearing site data loses access. Records remain until deleted; automatic orphan cleanup is absent.

Guards: PHP 0.01-10,000; 1,000 preference characters; 16 KiB JSON writes; 20 boxes/key; 1-20 distinct meals and 1-20 portions each. AI limit: 6 requests/client and 30/process/minute. Malformed input, stale edits, over-budget saves and outages produce readable errors. Hosting logs and /api/health are used; no dedicated alerting service.

## 6  Testing actual counts and results

| Check | Result |
| --- | --- |
| Automated checks | 110 tests passed, 0 failures, 0 errors, 0 skips in the release CI JUnit artifact. Includes unit, mocked-provider API, ownership, stale-edit and migration tests; not 110 live-provider tests. [CI run](https://github.com/s2301945-rgb/animo-meals/actions/runs/45866255836). |
| AI evaluation | 5/5 current live-language examples passed; 7 manual acceptance specifications and an earlier 3-case fixture report are separate evidence. [Current evaluation](https://github.com/s2301945-rgb/animo-meals/blob/main/docs/verification/final-ai-evaluation.json). |
| Production checks | November 27: health/database connected, 9 shops/28 items, live add/remove/quantity/budget edits and reload persistence passed. Temporary test box deleted. Covers checked at desktop and phone widths. [Audit](https://github.com/s2301945-rgb/animo-meals/blob/main/docs/verification/final-project-audit.json). |
| Known limits | No blocking error observed in the exercised flows. Remaining data, account-recovery, rollback and video-verification gaps are listed in section 9; there is no load/stress or penetration-test claim. |

## 7  Engineering process and CI CD

Rules: Protected main requires frontend/backend checks, current branches and resolved conversations, including administrators. Human approvals are zero under the instructor-confirmed solo exception. [Rules](https://github.com/s2301945-rgb/animo-meals/blob/main/docs/verification/recording-repository-rules.json); [sample PR](https://github.com/s2301945-rgb/animo-meals/pull/31).

Flow: feature branch, PR, checks, merge, main checks, private Vercel hook; Render deploys backend changes after passing checks and migrates before serving. Staging is local with a restricted role/schema in the same Supabase project, not a public staging deployment. [Workflow](https://github.com/s2301945-rgb/animo-meals/blob/main/.github/workflows/ci.yml); [PIPELINE](https://github.com/s2301945-rgb/animo-meals/blob/main/PIPELINE.md).

Measured optimization: Historical npm install fell from 4 to 2 seconds and frontend job from 15 to 14 seconds; overall parallel span rose from 24 to 26 seconds. Redundant seed invocations fell from 2 to 0. These are two different historical runs; no overall speedup or long-term success rate is claimed.

Release and recovery: v1.1.0 identifies source 8e5cf398f04c; backend reports e879f3fd35fd, whose backend tree is identical. Keep schema 0004 and use a quantity-aware rollback target. Earlier schema-0003 rollback passed; a new hosting rollback rehearsal is pending. [Recovery evidence](https://github.com/s2301945-rgb/animo-meals/blob/main/PIPELINE.md).

Recording: [Developer-supplied consultation folder](https://drive.google.com/drive/folders/1ZKTryG_lfVrOrqRCASA8FN6cy-cjMOjb). Screenshot shows AI consultation.mp4; panel/public access and uninterrupted challenge coverage are not yet verified.

Ownership Limitations and Evidence

## 8  Contribution and external work disclosure

Ownership: Lance Francis M. Gargaritano owns the solo project, product scope, supplied campus menu inputs, integration review, demonstration and deployment responsibility. He is the single declared DevOps Engineer. Code contribution evidence is available in the repository history and pull requests.

AI assistance: OpenAI Codex and ChatGPT substantially assisted implementation, UI, test creation, debugging, deployment automation and documentation. The built-in image-generation tool created the current 12 food-cover designs. Outputs were checked through automated tests and browser verification; they are not claimed as unaided work.

Third-party content: instructor-provided documentation template; open-source packages listed in the manifests; Google Fonts DM Sans and Manrope; Foodpanda branch menu references; developer-supplied campus data. Food covers are synthetic and labeled. Dataset redistribution rights and the retained logo asset license have not been independently verified. [Sources and licenses](https://github.com/s2301945-rgb/animo-meals/blob/main/docs/TECHNOLOGY.md).

## 9  Current limitations and final status

Implemented: working full-stack API, related persistent tables, visitor CRUD with quantity and budget edits, processed AI output, validation/error handling, automated checks, staging isolation and automatic public deployment. Catalog contains nine shops and 28 menu items; 12 illustration designs cover those items.

Partial or missing: two shops lack menus; Maria Rosa and BAMSOYS need location confirmation; USLS Agora Potato Corner prices rely on a North Drive delivery reference. No live-stock, nutrition, allergy-safety, food-quality or complete-language-accuracy guarantee. Free hosting can cold-start. Browser-only access has no recovery or cross-device sync. Video access and new rollback proof remain pending.

Next steps: confirm local menus and counter prices, verify assessor access to the recording, rehearse rollback of the quantity-aware release, and expand the language evaluation. This handoff reports the tested application snapshot; later documentation-only commits may follow.

## 10  Reviewer evidence index

| Evidence | Link |
| --- | --- |
| Product and source | [Production](https://animo-meals.vercel.app) \| [Repository](https://github.com/s2301945-rgb/animo-meals) \| [Release v1.1.0](https://github.com/s2301945-rgb/animo-meals/releases/tag/v1.1.0) \| source 8e5cf398f04c; backend e879f3fd35fd. |
| Technical specs | [README](https://github.com/s2301945-rgb/animo-meals/blob/main/README.md) \| [Architecture diagram](https://github.com/s2301945-rgb/animo-meals/blob/main/docs/ARCHITECTURE.md) \| [Schema and ERD](https://github.com/s2301945-rgb/animo-meals/blob/main/docs/SCHEMA.md) \| [API](https://github.com/s2301945-rgb/animo-meals/blob/main/docs/API.md) \| [Local setup](https://github.com/s2301945-rgb/animo-meals/blob/main/RUN-LOCALLY.md). |
| AI and testing | [Current AI results](https://github.com/s2301945-rgb/animo-meals/blob/main/docs/verification/final-ai-evaluation.json) \| [110-test CI run](https://github.com/s2301945-rgb/animo-meals/actions/runs/45866255836) \| [Test source](https://github.com/s2301945-rgb/animo-meals/blob/main/backend/tests/test_recommender.py) \| [AI error handling](https://github.com/s2301945-rgb/animo-meals/blob/main/backend/app/ai.py). |
| DevOps and process | [PIPELINE](https://github.com/s2301945-rgb/animo-meals/blob/main/PIPELINE.md) \| [Timing evidence](https://github.com/s2301945-rgb/animo-meals/blob/main/docs/verification/recording-ci-timings.json) \| [PR 30](https://github.com/s2301945-rgb/animo-meals/pull/30) \| [PR 31](https://github.com/s2301945-rgb/animo-meals/pull/31) \| [Backlog](https://github.com/s2301945-rgb/animo-meals/blob/main/BACKLOG.md) \| [Milestone](https://github.com/s2301945-rgb/animo-meals/milestone/1). |
| Deployment video | [AI consultation folder supplied by developer](https://drive.google.com/drive/folders/1ZKTryG_lfVrOrqRCASA8FN6cy-cjMOjb). Exact video URL, assessor access and uninterrupted deployment-challenge coverage require verification. |
